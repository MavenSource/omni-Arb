"""
Base DEX interface
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from web3 import Web3


class BaseDEX(ABC):
    """Base class for DEX integrations"""
    
    def __init__(self, w3: Web3, router_address: str, factory_address: str):
        """
        Initialize DEX
        
        Args:
            w3: Web3 instance
            router_address: Router contract address
            factory_address: Factory contract address
        """
        self.w3 = w3
        self.router_address = Web3.to_checksum_address(router_address)
        self.factory_address = Web3.to_checksum_address(factory_address)
        
        # Minimal ABI for Uniswap V2 compatible routers
        self.router_abi = [
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"}
                ],
                "name": "getAmountsOut",
                "outputs": [
                    {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [],
                "name": "WETH",
                "outputs": [{"internalType": "address", "name": "", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        self.router_contract = self.w3.eth.contract(
            address=self.router_address,
            abi=self.router_abi
        )
    
    @abstractmethod
    def get_name(self) -> str:
        """Get DEX name"""
        pass
    
    def get_amounts_out(self, amount_in: int, path: List[str]) -> Optional[List[int]]:
        """
        Get expected output amounts for a trade
        
        Args:
            amount_in: Input amount in wei
            path: Token path for swap
            
        Returns:
            List of amounts or None if error
        """
        try:
            # Convert path to checksum addresses
            checksum_path = [Web3.to_checksum_address(addr) for addr in path]
            amounts = self.router_contract.functions.getAmountsOut(
                amount_in,
                checksum_path
            ).call()
            return amounts
        except Exception as e:
            return None
    
    def get_price(self, token_in: str, token_out: str, amount_in: int) -> Optional[int]:
        """
        Get price for swapping tokens
        
        Args:
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount in wei
            
        Returns:
            Output amount in wei or None
        """
        path = [token_in, token_out]
        amounts = self.get_amounts_out(amount_in, path)
        
        if amounts and len(amounts) >= 2:
            return amounts[-1]
        return None
    
    def get_weth_address(self) -> str:
        """
        Get WETH address for this DEX
        
        Returns:
            WETH contract address
        """
        try:
            return self.router_contract.functions.WETH().call()
        except Exception:
            # Default WETH addresses for different networks
            return "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
