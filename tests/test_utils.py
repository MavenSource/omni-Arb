"""
Tests for utility functions
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.web3_utils import (
    calculate_profit_percentage,
    format_token_amount,
    parse_token_amount,
    is_address
)


def test_calculate_profit_percentage():
    """Test profit percentage calculation"""
    # Basic profit calculation
    profit_pct = calculate_profit_percentage(100, 110)
    assert profit_pct == 10.0
    
    # With gas cost
    profit_pct = calculate_profit_percentage(100, 110, 5)
    assert profit_pct == 5.0
    
    # Loss scenario
    profit_pct = calculate_profit_percentage(100, 90)
    assert profit_pct < 0
    
    print("✓ Profit percentage calculation test passed")


def test_format_token_amount():
    """Test token amount formatting"""
    # Standard 18 decimals
    formatted = format_token_amount(1000000000000000000, 18)
    assert formatted == "1.00000000"
    
    # 6 decimals (like USDC)
    formatted = format_token_amount(1000000, 6)
    assert formatted == "1.00000000"
    
    print("✓ Token amount formatting test passed")


def test_parse_token_amount():
    """Test token amount parsing"""
    # Standard 18 decimals
    amount = parse_token_amount("1.0", 18)
    assert amount == 1000000000000000000
    
    # 6 decimals
    amount = parse_token_amount("1.0", 6)
    assert amount == 1000000
    
    print("✓ Token amount parsing test passed")


def test_is_address():
    """Test address validation"""
    # Valid Ethereum address
    assert is_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    
    # Invalid address
    assert not is_address("0xinvalid")
    assert not is_address("not_an_address")
    
    print("✓ Address validation test passed")


if __name__ == '__main__':
    print("Running utility tests...\n")
    test_calculate_profit_percentage()
    test_format_token_amount()
    test_parse_token_amount()
    test_is_address()
    print("\n✅ All utility tests passed!")
