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
    
    def get_available_tokens(self) -> List[str]:
        """
        Get list of available tokens from configuration
        
        Returns:
            List of token addresses
        """
        # Get tokens from config, or return common tokens
        common_tokens = config.get('common_tokens', [])
        if common_tokens:
            return common_tokens
        
        # Return default common tokens if not configured
        if self.network == 'ethereum':
            return [
                '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # WETH
                '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USDC
                '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT
                '0x6B175474E89094C44Da98b954EedeAC495271d0F',  # DAI
            ]
        elif self.network == 'polygon':
            return [
                '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',  # WMATIC
                '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',  # USDC
                '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',  # USDT
                '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',  # WETH
            ]
        elif self.network == 'bsc':
            return [
                '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',  # WBNB
                '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',  # USDC
                '0x55d398326f99059fF775485246999027B3197955',  # USDT
                '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',  # ETH
            ]
        return []
    
    def get_available_dexes(self) -> List[str]:
        """
        Get list of available DEX names
        
        Returns:
            List of DEX names
        """
        return list(self.dexes.keys())
    
    def get_common_pairs(self) -> List[Tuple[str, str]]:
        """
        Get common trading pairs for the network
        
        Returns:
            List of (token_in, token_out) tuples
        """
        tokens = self.get_available_tokens()
        pairs = []
        
        # Create pairs from available tokens
        for i, token1 in enumerate(tokens):
            for token2 in tokens[i+1:]:
                pairs.append((token1, token2))
        
        return pairs
