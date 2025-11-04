"""
Tests for configuration module
"""

import os
import sys
import tempfile
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.config import Config


def test_default_config():
    """Test that default configuration loads properly"""
    config = Config()
    
    # Test network configuration
    assert 'ethereum' in config.get_supported_networks()
    assert 'bsc' in config.get_supported_networks()
    assert 'polygon' in config.get_supported_networks()
    
    # Test DEX configuration
    assert 'uniswap_v2' in config.get_supported_dexes()
    assert 'sushiswap' in config.get_supported_dexes()
    
    print("✓ Default config test passed")


def test_config_get():
    """Test configuration getter with dot notation"""
    config = Config()
    
    # Test dot notation access
    min_profit = config.get('trading.min_profit_percentage')
    assert min_profit is not None
    assert isinstance(min_profit, (int, float))
    
    # Test default value
    non_existent = config.get('non.existent.key', 'default')
    assert non_existent == 'default'
    
    print("✓ Config getter test passed")


def test_config_with_yaml():
    """Test loading configuration from YAML file"""
    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        test_config = {
            'trading': {
                'min_profit_percentage': 1.5,
            }
        }
        yaml.dump(test_config, f)
        temp_path = f.name
    
    try:
        config = Config(temp_path)
        min_profit = config.get('trading.min_profit_percentage')
        assert min_profit == 1.5
        print("✓ YAML config test passed")
    finally:
        os.unlink(temp_path)


if __name__ == '__main__':
    print("Running configuration tests...\n")
    test_default_config()
    test_config_get()
    test_config_with_yaml()
    print("\n✅ All configuration tests passed!")
