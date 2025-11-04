"""
DEX Manager - Manages multiple DEX integrations
"""

from typing import Dict, List, Optional, Tuple
from web3 import Web3
from src.config import config
from src.utils.logger import logger
from .base_dex import BaseDEX
from .uniswap_v2 import UniswapV2, SushiSwap, PancakeSwap


class DEXManager:
    """Manages multiple DEX integrations"""
    
    def __init__(self, w3: Web3, network: str):
        """
        Initialize DEX manager
        
        Args:
            w3: Web3 instance
            network: Network name
        """
        self.w3 = w3
        self.network = network
        self.dexes: Dict[str, BaseDEX] = {}
        self._initialize_dexes()
    
    def _initialize_dexes(self):
        """Initialize all configured DEXes"""
        supported_dexes = config.get_supported_dexes()
        
        for dex_name in supported_dexes:
            try:
                dex_config = config.get_dex_config(dex_name)
                if not dex_config:
                    continue
                
                router = dex_config.get('router')
                factory = dex_config.get('factory')
                
                if not router or not factory:
                    continue
                
                # Initialize appropriate DEX class
                if 'uniswap' in dex_name.lower():
                    dex = UniswapV2(self.w3, router, factory)
                elif 'sushi' in dex_name.lower():
                    dex = SushiSwap(self.w3, router, factory)
                elif 'pancake' in dex_name.lower():
                    dex = PancakeSwap(self.w3, router, factory)
                else:
                    continue
                
                self.dexes[dex_name] = dex
                logger.info(f"Initialized {dex.get_name()} on {self.network}")
                
            except Exception as e:
                logger.error(f"Error initializing {dex_name}: {e}")
    
    def get_dex(self, dex_name: str) -> Optional[BaseDEX]:
        """
        Get a specific DEX instance
        
        Args:
            dex_name: DEX name
            
        Returns:
            DEX instance or None
        """
        return self.dexes.get(dex_name)
    
    def get_all_dexes(self) -> Dict[str, BaseDEX]:
        """
        Get all initialized DEXes
        
        Returns:
            Dictionary of DEX name to DEX instance
        """
        return self.dexes
    
    def compare_prices(self, token_in: str, token_out: str, amount_in: int) -> List[Tuple[str, int]]:
        """
        Compare prices across all DEXes
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount in wei
            
        Returns:
            List of tuples (dex_name, output_amount)
        """
        prices = []
        
        for dex_name, dex in self.dexes.items():
            try:
                output_amount = dex.get_price(token_in, token_out, amount_in)
                if output_amount:
                    prices.append((dex_name, output_amount))
            except Exception as e:
                logger.debug(f"Error getting price from {dex_name}: {e}")
        
        # Sort by output amount (descending)
        prices.sort(key=lambda x: x[1], reverse=True)
        return prices
    
    def find_best_price(self, token_in: str, token_out: str, amount_in: int) -> Optional[Tuple[str, int]]:
        """
        Find the best price across all DEXes
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount in wei
            
        Returns:
            Tuple of (dex_name, output_amount) or None
        """
        prices = self.compare_prices(token_in, token_out, amount_in)
        return prices[0] if prices else None
