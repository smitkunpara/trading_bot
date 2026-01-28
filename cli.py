#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Trading Bot.
"""

import sys
import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from bot.logging_config import setup_logging, get_logger
from bot.orders import OrderManager, OrderResult
from bot.client import BinanceClientError


# Initialize Typer app 
app = typer.Typer(
    name="trading-bot",
    help="Binance Futures Testnet Trading Bot CLI",
    add_completion=False
)

# Rich console for pretty output
console = Console()


def display_order_result(result: OrderResult):
    """Display order result."""
    if result.success:
        table = Table(title="✅ Order Response", show_header=True, header_style="bold green")
        table.add_column("Field", style="green")
        table.add_column("Value", style="white")
        
        table.add_row("Order ID", str(result.order_id))
        table.add_row("Status", result.status or "N/A")
        table.add_row("Symbol", result.symbol or "N/A")
        table.add_row("Side", result.side or "N/A")
        table.add_row("Type", result.order_type or "N/A")
        table.add_row("Quantity", str(result.quantity))
        table.add_row("Executed Qty", str(result.executed_qty))
        
        if result.price:
            table.add_row("Price", str(result.price))
        
        if result.avg_price:
            table.add_row("Avg Price", str(result.avg_price))
        
        console.print(table)
        console.print(Panel("[bold green]Order placed successfully![/bold green]", border_style="green"))
    else:
        console.print(Panel(
            f"[bold red]Order Failed![/bold red]\n\n{result.error_message}",
            title="❌ Error",
            border_style="red"
        ))


@app.command()
def main(
    symbol: Optional[str] = typer.Option(None, help="Trading pair symbol (e.g., BTCUSDT)"),
    side: Optional[str] = typer.Option(None, help="Order side: BUY or SELL"),
    order_type: Optional[str] = typer.Option(None, "--type", help="Order type: MARKET, LIMIT, or STOP_LIMIT"),
    quantity: Optional[float] = typer.Option(None, help="Order quantity"),
    price: Optional[float] = typer.Option(None, help="Limit price (required for LIMIT/STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, help="Stop price (required for STOP_LIMIT)"),
    orders: Optional[str] = typer.Option(None, help="List orders: 'open', 'close', or 'all'"),
    cancel: Optional[int] = typer.Option(None, help="Order ID to cancel"),
    account: bool = typer.Option(False, "--account", help="Show account information"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug logging")
):
    """
    Binance Futures Trading Bot CLI.
    
    Actions are identified by the arguments provided:
    
    - Check Price: Provide only --symbol
    - Place Order: Provide --symbol, --side, --type, --quantity (plus --price/--stop-price if needed)
    - List Orders: Provide --symbol and --orders (open/close/all)
    - Cancel Order: Provide --symbol and --cancel (order ID)
    - Account Info: Provide --account
    """
    
    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(log_level)
    logger = get_logger()
    
    console.print()
    console.print(Panel.fit(
        "[bold blue]🤖 Binance Futures Trading Bot[/bold blue]",
        border_style="blue"
    ))
    console.print()
    
    try:
        manager = OrderManager()

        # --- 1. Account Information ---
        if account:
            from bot.client import BinanceClient
            client = BinanceClient()
            info = client.get_account_info()
            
            table = Table(title="📊 Account Information", show_header=True, header_style="bold cyan")
            table.add_column("Asset", style="cyan")
            table.add_column("Wallet Balance", style="yellow")
            table.add_column("Available Balance", style="green")
            
            for asset in info.get("assets", []):
                wallet_balance = float(asset.get("walletBalance", 0))
                if wallet_balance > 0:
                    table.add_row(
                        asset.get("asset"),
                        f"{wallet_balance:.4f}",
                        f"{float(asset.get('availableBalance', 0)):.4f}"
                    )
            console.print(table)
            return

        # --- 2. List Orders (Open / History) ---
        if orders:
            if not symbol:
                console.print(Panel("[bold red]Error:[/bold red] --symbol is required to list orders.", border_style="red"))
                sys.exit(1)
            
            orders_mode = orders.lower()
            if orders_mode == 'open':
                title = f"⏳ Open Orders ({symbol.upper()})"
                fetched_orders = manager.get_open_orders(symbol)
            elif orders_mode in ['close', 'all']:
                # Note: 'all' usually fetches everything (open + history). 'close' isn't explicitly distinct in API mostly, 
                # but we can treat 'close' and 'all' as fetching history for this implementation.
                title = f"📜 Order History ({symbol.upper()})"
                fetched_orders = manager.get_order_history(symbol)
            else:
                console.print(Panel(f"[bold red]Error:[/bold red] Invalid value for --orders. Use 'open', 'close', or 'all'.", border_style="red"))
                sys.exit(1)

            if not fetched_orders:
                console.print(Panel(f"No orders found for {symbol.upper()}", border_style="yellow"))
                return

            table = Table(title=title, show_header=True, header_style="bold cyan")
            table.add_column("Order ID", style="cyan")
            table.add_column("Type", style="white")
            table.add_column("Side", style="magenta")
            table.add_column("Price", style="green")
            table.add_column("Qty", style="yellow")
            table.add_column("Status", style="bold")
            table.add_column("Time", style="dim")
            
            for order in fetched_orders:
                ts = int(order.get("time", 0)) / 1000
                time_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
                
                order_side = order.get("side", "")
                side_style = "green" if order_side == "BUY" else "red"
                
                table.add_row(
                    str(order.get("orderId")),
                    order.get("type"),
                    f"[{side_style}]{order_side}[/{side_style}]",
                    str(order.get("price")),
                    str(order.get("origQty")),
                    order.get("status"),
                    time_str
                )
            console.print(table)
            return

        # --- 3. Cancel Order ---
        if cancel:
            if not symbol:
                console.print(Panel("[bold red]Error:[/bold red] --symbol is required to cancel an order.", border_style="red"))
                sys.exit(1)
            
            result = manager.cancel_order(symbol, cancel)
            display_order_result(result)
            sys.exit(0 if result.success else 1)

        # --- 4. Place Order ---
        if symbol and side and order_type and quantity:
            # Display summary
            table = Table(title="📝 Order Request Summary", show_header=True, header_style="bold cyan")
            table.add_column("Parameter", style="cyan")
            table.add_column("Value", style="yellow")
            
            table.add_row("Symbol", symbol.upper())
            table.add_row("Side", side.upper())
            table.add_row("Type", order_type.upper())
            table.add_row("Quantity", str(quantity))
            if price is not None:
                table.add_row("Price", str(price))
            if stop_price is not None:
                table.add_row("Stop Price", str(stop_price))
            console.print(table)
            console.print()

            logger.info(f"Processing order: {side} {quantity} {symbol} ({order_type})")
            
            result = manager.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
                stop_price=stop_price
            )
            display_order_result(result)
            sys.exit(0 if result.success else 1)

        # --- 5. Price Check & Suggestions ---
        if symbol:
            current_price = manager.get_current_price(symbol.upper())
            
            if current_price:
                console.print(Panel(
                    f"[bold cyan]{symbol.upper()}[/bold cyan]: [bold green]${current_price:,.2f}[/bold green]",
                    title="💰 Current Price",
                    border_style="cyan"
                ))
                
                # Show suggestions since only symbol was provided
                console.print("\n[dim]💡 Suggestions:[/dim]")
                console.print(f"[dim]To place an order:[/dim] [green]--symbol {symbol} --side BUY --type MARKET --quantity 0.002[/green]")
                console.print(f"[dim]To view orders:[/dim]    [green]--symbol {symbol} --orders open[/green]")
                console.print(f"[dim]To cancel order:[/dim]    [green]--symbol {symbol} --cancel <ID>[/green]")
            else:
                console.print(Panel(
                    f"[bold red]Could not fetch price for {symbol}[/bold red]",
                    border_style="red"
                ))
                sys.exit(1)
            return
            
        # If no arguments provided
        console.print("[yellow]No action specified. Use --help to see available options.[/yellow]")
        
    except BinanceClientError as e:
        logger.error(f"Binance API error: {e}")
        console.print(Panel(
            f"[bold red]API Error:[/bold red] {e}",
            border_style="red"
        ))
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        console.print(Panel(
            f"[bold red]Unexpected Error:[/bold red] {e}",
            border_style="red"
        ))
        sys.exit(1)


if __name__ == "__main__":
    app()