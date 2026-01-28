import click
import sys
from binance.exceptions import BinanceAPIException, BinanceRequestException
from bot.client import get_client
from bot.orders import place_order
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price
)
from bot.logging_config import logger

@click.command()
@click.option('--symbol', prompt='Symbol (e.g., BTCUSDT)', help='Trading Pair Symbol')
@click.option('--side', prompt='Side (BUY/SELL)', type=click.Choice(['BUY', 'SELL'], case_sensitive=False), help='Order Side')
@click.option('--type', 'order_type', prompt='Order Type (MARKET/LIMIT)', type=click.Choice(['MARKET', 'LIMIT'], case_sensitive=False), help='Order Type')
@click.option('--quantity', prompt='Quantity', type=float, help='Order Quantity')
@click.option('--price', required=False, type=float, default=None, help='Order Price (Required for LIMIT)')
def main(symbol, side, order_type, quantity, price):
    """
    CLI Tool to place orders on Binance Futures Testnet.
    """
    try:
        # Prompt for price if LIMIT order and price is missing
        if order_type.upper() == 'LIMIT' and price is None:
            price = click.prompt('Price (required for LIMIT)', type=float)

        # 1. Validation
        v_symbol = validate_symbol(symbol)
        v_side = validate_side(side)
        v_type = validate_order_type(order_type)
        v_qty = validate_quantity(quantity)
        v_price = validate_price(price, v_type)

        # 2. Summary
        click.echo("\n--- Order Request Summary ---")
        click.echo(f"Symbol:   {v_symbol}")
        click.echo(f"Side:     {v_side}")
        click.echo(f"Type:     {v_type}")
        click.echo(f"Quantity: {v_qty}")
        if v_price:
            click.echo(f"Price:    {v_price}")
        click.echo("-----------------------------")

        # 3. Execution
        client = get_client()
        order = place_order(client, v_symbol, v_side, v_type, v_qty, v_price)

        # 4. Response Output
        click.echo("\n>>> SUCCESS: Order Placed <<<")
        click.echo(f"Order ID:     {order.get('orderId')}")
        click.echo(f"Status:       {order.get('status')}")
        click.echo(f"Executed Qty: {order.get('executedQty')}")
        click.echo(f"Avg Price:    {order.get('avgPrice')}")
        click.echo("-----------------------------")
    
    except ValueError as e:
        click.echo(f"\n[!] Input Error: {e}", err=True)
        sys.exit(1)
    except BinanceAPIException as e:
        click.echo(f"\n[!] Binance API Error: Code {e.status_code}, {e.message}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n[!] Unexpected Error: {e}", err=True)
        logger.exception("Unexpected error in CLI")
        sys.exit(1)

if __name__ == '__main__':
    main()
