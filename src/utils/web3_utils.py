"""
Web3 utilities for blockchain interactions
"""

from web3 import Web3
from typing import Optional, Dict, Any
from decimal import Decimal


def to_checksum_address(address: str) -> str:
    """
    Convert address to checksum format
    
    Args:
        address: Ethereum address
        
    Returns:
        Checksummed address
    """
    return Web3.to_checksum_address(address)


def to_wei(amount: float, unit: str = 'ether') -> int:
    """
    Convert amount to wei
    
    Args:
        amount: Amount to convert
        unit: Unit of the amount (ether, gwei, etc.)
        
    Returns:
        Amount in wei
    """
    return Web3.to_wei(amount, unit)


def from_wei(amount: int, unit: str = 'ether') -> Decimal:
    """
    Convert wei to other unit
    
    Args:
        amount: Amount in wei
        unit: Target unit (ether, gwei, etc.)
        
    Returns:
        Amount in target unit
    """
    return Web3.from_wei(amount, unit)


def is_address(address: str) -> bool:
    """
    Check if string is a valid Ethereum address
    
    Args:
        address: String to check
        
    Returns:
        True if valid address, False otherwise
    """
    return Web3.is_address(address)


def calculate_profit_percentage(buy_price: float, sell_price: float, gas_cost: float = 0) -> float:
    """
    Calculate profit percentage
    
    Args:
        buy_price: Purchase price
        sell_price: Selling price
        gas_cost: Estimated gas cost
        
    Returns:
        Profit percentage
    """
    if buy_price <= 0:
        return 0.0
    
    net_profit = sell_price - buy_price - gas_cost
    profit_pct = (net_profit / buy_price) * 100
    
    return round(profit_pct, 4)


def format_token_amount(amount: int, decimals: int = 18) -> str:
    """
    Format token amount from wei to human readable
    
    Args:
        amount: Amount in smallest unit (wei)
        decimals: Token decimals
        
    Returns:
        Formatted amount string
    """
    divisor = 10 ** decimals
    return f"{amount / divisor:.8f}"


def parse_token_amount(amount: str, decimals: int = 18) -> int:
    """
    Parse token amount from human readable to wei
    
    Args:
        amount: Amount as string
        decimals: Token decimals
        
    Returns:
        Amount in smallest unit
    """
    multiplier = 10 ** decimals
    return int(float(amount) * multiplier)
