"""
Configuration management for the DeFi arbitrage system
"""

import os
import yaml
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the arbitrage system"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration
        
        Args:
            config_path: Path to config.yaml file
        """
        self.config_path = config_path or os.getenv('CONFIG_PATH', 'config/config.yaml')
        self.config_data = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            'network': {
                'rpc_urls': {
                    'ethereum': os.getenv('ETH_RPC_URL', 'https://eth.llamarpc.com'),
                    'bsc': os.getenv('BSC_RPC_URL', 'https://bsc-dataseed.binance.org/'),
                    'polygon': os.getenv('POLYGON_RPC_URL', 'https://polygon-rpc.com'),
                },
                'chain_ids': {
                    'ethereum': 1,
                    'bsc': 56,
                    'polygon': 137,
                }
            },
            'dex': {
                'uniswap_v2': {
                    'router': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                    'factory': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
                },
                'sushiswap': {
                    'router': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
                    'factory': '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac',
                },
                'pancakeswap': {
                    'router': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
                    'factory': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
                }
            },
            'trading': {
                'min_profit_percentage': float(os.getenv('MIN_PROFIT_PCT', '0.5')),
                'max_trade_amount_usd': float(os.getenv('MAX_TRADE_USD', '1000')),
                'gas_price_multiplier': float(os.getenv('GAS_MULTIPLIER', '1.1')),
                'slippage_tolerance': float(os.getenv('SLIPPAGE_TOL', '0.5')),
            },
            'monitoring': {
                'check_interval_seconds': int(os.getenv('CHECK_INTERVAL', '5')),
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'network.rpc_urls')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_rpc_url(self, network: str) -> str:
        """Get RPC URL for a specific network"""
        return self.get(f'network.rpc_urls.{network}')
    
    def get_dex_config(self, dex_name: str) -> Dict[str, str]:
        """Get DEX configuration"""
        return self.get(f'dex.{dex_name}', {})
    
    def get_supported_networks(self) -> List[str]:
        """Get list of supported networks"""
        return list(self.get('network.rpc_urls', {}).keys())
    
    def get_supported_dexes(self) -> List[str]:
        """Get list of supported DEXes"""
        return list(self.get('dex', {}).keys())


# Global config instance
config = Config()
