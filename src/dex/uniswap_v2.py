"""
Uniswap V2 DEX implementation
"""

from web3 import Web3
from .base_dex import BaseDEX


class UniswapV2(BaseDEX):
    """Uniswap V2 DEX implementation"""
    
    def get_name(self) -> str:
        """Get DEX name"""
        return "Uniswap V2"


class SushiSwap(BaseDEX):
    """SushiSwap DEX implementation"""
    
    def get_name(self) -> str:
        """Get DEX name"""
        return "SushiSwap"


class PancakeSwap(BaseDEX):
    """PancakeSwap DEX implementation"""
    
    def get_name(self) -> str:
        """Get DEX name"""
        return "PancakeSwap"
