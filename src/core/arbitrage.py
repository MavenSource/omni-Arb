"""
Arbitrage opportunity detection
"""

from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass
from src.utils.logger import logger
from src.utils.web3_utils import calculate_profit_percentage, from_wei
from src.dex.dex_manager import DEXManager


@dataclass
class ArbitrageOpportunity:
    """Represents an arbitrage opportunity"""
    buy_dex: str
    sell_dex: str
    token_in: str
    token_out: str
    amount_in: int
    buy_price: int
    sell_price: int
    profit: int
    profit_percentage: float
    network: str
    
    def __str__(self) -> str:
        """String representation of opportunity"""
        return (
            f"Arbitrage: Buy on {self.buy_dex} @ {self.buy_price}, "
            f"Sell on {self.sell_dex} @ {self.sell_price}, "
            f"Profit: {self.profit_percentage:.2f}%"
        )


class ArbitrageDetector:
    """Detects arbitrage opportunities across DEXes"""
    
    def __init__(self, dex_manager: DEXManager, network: str):
        """
        Initialize arbitrage detector
        
        Args:
            dex_manager: DEX manager instance
            network: Network name
        """
        self.dex_manager = dex_manager
        self.network = network
    
    def find_opportunities(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        min_profit_pct: float = 0.5
    ) -> List[ArbitrageOpportunity]:
        """
        Find arbitrage opportunities for a token pair
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount in wei
            min_profit_pct: Minimum profit percentage threshold
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        
        # Get prices from all DEXes
        prices = self.dex_manager.compare_prices(token_in, token_out, amount_in)
        
        if len(prices) < 2:
            return opportunities
        
        # Compare prices to find arbitrage
        for i, (buy_dex, buy_price) in enumerate(prices):
            for sell_dex, sell_price in prices[:i]:  # Only compare with better prices
                # Calculate profit
                profit = sell_price - buy_price
                profit_pct = calculate_profit_percentage(
                    float(from_wei(buy_price)),
                    float(from_wei(sell_price))
                )
                
                # Check if profitable
                if profit > 0 and profit_pct >= min_profit_pct:
                    opportunity = ArbitrageOpportunity(
                        buy_dex=buy_dex,
                        sell_dex=sell_dex,
                        token_in=token_in,
                        token_out=token_out,
                        amount_in=amount_in,
                        buy_price=buy_price,
                        sell_price=sell_price,
                        profit=profit,
                        profit_percentage=profit_pct,
                        network=self.network
                    )
                    opportunities.append(opportunity)
        
        # Sort by profit percentage
        opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
        
        return opportunities
    
    def scan_token_pairs(
        self,
        token_pairs: List[Tuple[str, str]],
        amount_in: int,
        min_profit_pct: float = 0.5
    ) -> List[ArbitrageOpportunity]:
        """
        Scan multiple token pairs for arbitrage opportunities
        
        Args:
            token_pairs: List of (token_in, token_out) tuples
            amount_in: Input amount in wei
            min_profit_pct: Minimum profit percentage threshold
            
        Returns:
            List of all found arbitrage opportunities
        """
        all_opportunities = []
        
        for token_in, token_out in token_pairs:
            try:
                opportunities = self.find_opportunities(
                    token_in,
                    token_out,
                    amount_in,
                    min_profit_pct
                )
                all_opportunities.extend(opportunities)
            except Exception as e:
                logger.debug(f"Error scanning {token_in}/{token_out}: {e}")
        
        # Sort all opportunities by profit percentage
        all_opportunities.sort(key=lambda x: x.profit_percentage, reverse=True)
        
        return all_opportunities
