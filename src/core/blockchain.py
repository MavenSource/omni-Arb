"""
Blockchain connection manager
"""

from web3 import Web3
from typing import Optional, Dict
from src.utils.logger import logger
from src.config import config


class BlockchainConnector:
    """Manages connections to multiple blockchain networks"""
    
    def __init__(self):
        """Initialize blockchain connector"""
        self.connections: Dict[str, Web3] = {}
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize Web3 connections for all configured networks"""
        networks = config.get_supported_networks()
        
        for network in networks:
            try:
                rpc_url = config.get_rpc_url(network)
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                
                if w3.is_connected():
                    self.connections[network] = w3
                    logger.info(f"Connected to {network} network")
                else:
                    logger.warning(f"Failed to connect to {network} network")
                    
            except Exception as e:
                logger.error(f"Error connecting to {network}: {e}")
    
    def get_connection(self, network: str) -> Optional[Web3]:
        """
        Get Web3 connection for a specific network
        
        Args:
            network: Network name (ethereum, bsc, polygon, etc.)
            
        Returns:
            Web3 instance or None
        """
        return self.connections.get(network)
    
    def is_connected(self, network: str) -> bool:
        """
        Check if connected to a specific network
        
        Args:
            network: Network name
            
        Returns:
            True if connected, False otherwise
        """
        w3 = self.get_connection(network)
        return w3 is not None and w3.is_connected()
    
    def get_block_number(self, network: str) -> Optional[int]:
        """
        Get current block number for a network
        
        Args:
            network: Network name
            
        Returns:
            Current block number or None
        """
        w3 = self.get_connection(network)
        if w3:
            try:
                return w3.eth.block_number
            except Exception as e:
                logger.error(f"Error getting block number for {network}: {e}")
        return None
    
    def get_gas_price(self, network: str) -> Optional[int]:
        """
        Get current gas price for a network
        
        Args:
            network: Network name
            
        Returns:
            Gas price in wei or None
        """
        w3 = self.get_connection(network)
        if w3:
            try:
                return w3.eth.gas_price
            except Exception as e:
                logger.error(f"Error getting gas price for {network}: {e}")
        return None
    
    def get_balance(self, network: str, address: str) -> Optional[int]:
        """
        Get native token balance for an address
        
        Args:
            network: Network name
            address: Wallet address
            
        Returns:
            Balance in wei or None
        """
        w3 = self.get_connection(network)
        if w3:
            try:
                checksum_address = Web3.to_checksum_address(address)
                return w3.eth.get_balance(checksum_address)
            except Exception as e:
                logger.error(f"Error getting balance for {address} on {network}: {e}")
        return None
    
    def get_all_connections(self) -> Dict[str, Web3]:
        """
        Get all active Web3 connections
        
        Returns:
            Dictionary of network name to Web3 instance
        """
        return self.connections


# Global blockchain connector instance
blockchain = BlockchainConnector()
