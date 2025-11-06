"""
Example demonstration of the Omni-Arb system

This example demonstrates the key components and how they work together.
Note: This is a simulation since we don't have access to real blockchain networks.
"""

import sys
from src.config import config
from src.utils.logger import logger, setup_logger
from src.utils.web3_utils import to_wei, from_wei, calculate_profit_percentage

# Setup logger
setup_logger('demo', 'INFO')

def demo_configuration():
    """Demonstrate configuration management"""
    print("\n" + "="*60)
    print("CONFIGURATION DEMONSTRATION")
    print("="*60)
    
    # Show supported networks
    networks = config.get_supported_networks()
    logger.info(f"Supported networks: {', '.join(networks)}")
    
    # Show supported DEXes
    dexes = config.get_supported_dexes()
    logger.info(f"Supported DEXes: {', '.join(dexes)}")
    
    # Show trading parameters
    min_profit = config.get('trading.min_profit_percentage')
    logger.info(f"Minimum profit threshold: {min_profit}%")
    
    max_trade = config.get('trading.max_trade_amount_usd')
    logger.info(f"Maximum trade amount: ${max_trade}")
    
    print()


def demo_utilities():
    """Demonstrate utility functions"""
    print("\n" + "="*60)
    print("UTILITY FUNCTIONS DEMONSTRATION")
    print("="*60)
    
    # Token amount conversions
    amount_wei = to_wei(1.5, 'ether')
    logger.info(f"1.5 ETH = {amount_wei} wei")
    
    amount_eth = from_wei(amount_wei, 'ether')
    logger.info(f"{amount_wei} wei = {amount_eth} ETH")
    
    # Profit calculation
    buy_price = 1000.0
    sell_price = 1050.0
    gas_cost = 25.0
    
    profit_pct = calculate_profit_percentage(buy_price, sell_price, gas_cost)
    logger.info(f"Buy at ${buy_price}, Sell at ${sell_price}, Gas ${gas_cost}")
    logger.info(f"Net profit: {profit_pct}%")
    
    print()


def demo_arbitrage_logic():
    """Demonstrate arbitrage detection logic"""
    print("\n" + "="*60)
    print("ARBITRAGE DETECTION DEMONSTRATION")
    print("="*60)
    
    # Simulated prices from different DEXes
    dex_prices = {
        'Uniswap V2': 1800.50,
        'SushiSwap': 1805.75,
        'PancakeSwap': 1798.25,
    }
    
    logger.info("Simulated ETH/USDC prices across DEXes:")
    for dex, price in dex_prices.items():
        logger.info(f"  {dex}: ${price}")
    
    # Find arbitrage opportunity
    sorted_prices = sorted(dex_prices.items(), key=lambda x: x[1])
    cheapest_dex, cheapest_price = sorted_prices[0]
    most_expensive_dex, highest_price = sorted_prices[-1]
    
    profit_pct = calculate_profit_percentage(cheapest_price, highest_price)
    
    logger.info(f"\nArbitrage opportunity detected:")
    logger.info(f"  Buy on {cheapest_dex} @ ${cheapest_price}")
    logger.info(f"  Sell on {most_expensive_dex} @ ${highest_price}")
    logger.info(f"  Potential profit: {profit_pct}%")
    
    # Check against minimum threshold
    min_profit = config.get('trading.min_profit_percentage', 0.5)
    if profit_pct >= min_profit:
        logger.info(f"  ✅ Profit exceeds minimum threshold of {min_profit}%")
    else:
        logger.info(f"  ❌ Profit below minimum threshold of {min_profit}%")
    
    print()


def demo_gas_cost_analysis():
    """Demonstrate gas cost analysis"""
    print("\n" + "="*60)
    print("GAS COST ANALYSIS DEMONSTRATION")
    print("="*60)
    
    # Simulated arbitrage scenario
    buy_price = 1800.0
    sell_price = 1810.0
    amount = 1.0  # 1 ETH
    
    gross_profit = (sell_price - buy_price) * amount
    logger.info(f"Trading {amount} ETH:")
    logger.info(f"  Buy price: ${buy_price}")
    logger.info(f"  Sell price: ${sell_price}")
    logger.info(f"  Gross profit: ${gross_profit}")
    
    # Simulate different gas scenarios
    gas_scenarios = {
        'Low congestion (30 gwei)': 15.0,
        'Medium congestion (50 gwei)': 25.0,
        'High congestion (100 gwei)': 50.0,
    }
    
    logger.info("\nNet profit under different gas conditions:")
    for scenario, gas_cost in gas_scenarios.items():
        net_profit = gross_profit - gas_cost
        profit_pct = (net_profit / (buy_price * amount)) * 100
        
        if net_profit > 0:
            logger.info(f"  {scenario}: ${net_profit:.2f} ({profit_pct:.2f}%) ✅")
        else:
            logger.info(f"  {scenario}: ${net_profit:.2f} ({profit_pct:.2f}%) ❌")
    
    print()


def main():
    """Run all demonstrations"""
    print("""
    ╔═══════════════════════════════════════╗
    ║   Omni-Arb System Demonstration       ║
    ║   DeFi Arbitrage Components           ║
    ╚═══════════════════════════════════════╝
    """)
    
    demo_configuration()
    demo_utilities()
    demo_arbitrage_logic()
    demo_gas_cost_analysis()
    
    print("="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nThis demonstration shows how the Omni-Arb system components")
    print("work together to detect and analyze arbitrage opportunities.")
    print("\nTo run the full system with real blockchain data:")
    print("  1. Configure your RPC endpoints in .env or config/config.yaml")
    print("  2. Run: python main.py")
    print()


if __name__ == '__main__':
    main()
