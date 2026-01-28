#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Trading Bot.
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

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


def display_order_summary(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None
):
    """Display order request summary."""
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


@app.command("order")
def place_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair symbol (e.g., BTCUSDT)"),
    side: str = typer.Option(..., "--side", "-side", help="Order side: BUY or SELL"),
    order_type: str = typer.Option(..., "--type", "-t", help="Order type: MARKET, LIMIT, or STOP_LIMIT"),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Limit price (required for LIMIT/STOP_LIMIT)"),
    stop_price: Optional[float] = typer.Option(None, "--stop-price", "-sp", help="Stop price (required for STOP_LIMIT)"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging")
):
    """
    Place an order on Binance Futures Testnet.
    
    Examples:
    
        # Market order
        uv run python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
        
        # Limit order
        uv run python cli.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000
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
    
    # Display order summary
    display_order_summary(symbol, side, order_type, quantity, price, stop_price)
    
    try:
        # Create order manager and place order
        manager = OrderManager()
        
        logger.info(f"Processing order: {side} {quantity} {symbol} ({order_type})")
        
        result = manager.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
        # Display result
        display_order_result(result)
        
        # Exit with appropriate code
        sys.exit(0 if result.success else 1)
        
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


@app.command("price")
def get_price(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair symbol (e.g., BTCUSDT)")
):
    """
    Get current price for a trading pair.
    
    Example:
        uv run python cli.py price --symbol BTCUSDT
    """
    setup_logging("INFO")
    
    try:
        manager = OrderManager()
        price = manager.get_current_price(symbol.upper())
        
        if price:
            console.print(Panel(
                f"[bold cyan]{symbol.upper()}[/bold cyan]: [bold green]${price:,.2f}[/bold green]",
                title="💰 Current Price",
                border_style="cyan"
            ))
        else:
            console.print(Panel(
                f"[bold red]Could not fetch price for {symbol}[/bold red]",
                border_style="red"
            ))
            sys.exit(1)
            
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)


@app.command("account")
def get_account():
    """
    Get account information.
    
    Example:
        uv run python cli.py account
    """
    setup_logging("INFO")
    
    try:
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
        
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)


@app.command("cancel")
def cancel_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair symbol"),
    order_id: int = typer.Option(..., "--order-id", "-id", help="Order ID to cancel")
):
    """
    Cancel an existing order.
    
    Example:
        uv run python cli.py cancel --symbol BTCUSDT --order-id 12345678
    """
    setup_logging("INFO")
    
    try:
        manager = OrderManager()
        result = manager.cancel_order(symbol, order_id)
        display_order_result(result)
        sys.exit(0 if result.success else 1)
        
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)


@app.command("orders")
def list_orders(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair symbol"),
    history: bool = typer.Option(False, "--history", "-h", help="Show order history instead of open orders"),
    limit: int = typer.Option(10, "--limit", "-l", help="Limit number of history orders")
):
    """
    List orders (Open orders by default).
    
    Examples:
        uv run python cli.py orders --symbol BTCUSDT
        uv run python cli.py orders --symbol BTCUSDT --history
    """
    setup_logging("INFO")
    
    try:
        manager = OrderManager()
        
        if history:
            title = f"📜 Order History ({symbol.upper()})"
            orders = manager.get_order_history(symbol, limit)
        else:
            title = f"⏳ Open Orders ({symbol.upper()})"
            orders = manager.get_open_orders(symbol)
            
        if not orders:
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
        
        for order in orders:
            # Format time
            import datetime
            ts = int(order.get("time", 0)) / 1000
            time_str = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
            
            # Colorize side
            side = order.get("side", "")
            side_style = "green" if side == "BUY" else "red"
            
            table.add_row(
                str(order.get("orderId")),
                order.get("type"),
                f"[{side_style}]{side}[/{side_style}]",
                str(order.get("price")),
                str(order.get("origQty")),
                order.get("status"),
                time_str
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)


@app.command("positions")
def list_positions(
    symbol: Optional[str] = typer.Option(None, "--symbol", "-s", help="Optional trading pair symbol")
):
    """
    List open positions.
    
    Example:
        uv run python cli.py positions
        uv run python cli.py positions --symbol BTCUSDT
    """
    setup_logging("INFO")
    
    try:
        manager = OrderManager()
        positions = manager.get_positions(symbol)
        
        if not positions:
            console.print(Panel("No open positions found.", border_style="yellow"))
            return

        table = Table(title="📈 Open Positions", show_header=True, header_style="bold cyan")
        table.add_column("Symbol", style="cyan")
        table.add_column("Size", style="yellow")
        table.add_column("Entry Price", style="white")
        table.add_column("Mark Price", style="blue")
        table.add_column("PNL (USDT)", style="bold")
        
        for pos in positions:
            pnl = float(pos.get("unRealizedProfit", 0))
            pnl_style = "green" if pnl >= 0 else "red"
            
            table.add_row(
                pos.get("symbol"),
                str(pos.get("positionAmt")),
                str(round(float(pos.get("entryPrice", 0)), 2)),
                str(round(float(pos.get("markPrice", 0)), 2)),
                f"[{pnl_style}]{pnl:.2f}[/{pnl_style}]"
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(Panel(f"[bold red]Error:[/bold red] {e}", border_style="red"))
        sys.exit(1)


@app.callback()
def main():
    """
    Binance Futures Testnet Trading Bot
    
    A CLI tool for placing orders on Binance Futures Testnet.
    """
    pass


if __name__ == "__main__":
    app()
