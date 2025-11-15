"""
Tests for Dynamic Fee Handler
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from decimal import Decimal
from web3 import Web3

from src.core.dynamic_fee_handler import DynamicFeeHandler


class TestDynamicFeeHandler(unittest.TestCase):
    """Test cases for DynamicFeeHandler"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_w3 = Mock(spec=Web3)
        self.mock_w3.eth = Mock()
        self.mock_w3.eth.chain_id = 1
        self.handler = DynamicFeeHandler(self.mock_w3)
    
    def test_initialization(self):
        """Test handler initialization"""
        self.assertIsNotNone(self.handler)
        self.assertEqual(self.handler.w3, self.mock_w3)
        self.assertEqual(self.handler.max_priority_fee_multiplier, 1.2)
        self.assertEqual(self.handler.max_fee_multiplier, 2.0)
    
    def test_get_optimal_gas_params(self):
        """Test optimal gas parameter calculation"""
        # Mock latest block with base fee
        mock_block = {
            'baseFeePerGas': 30000000000,  # 30 Gwei
            'number': 12345
        }
        self.mock_w3.eth.get_block.return_value = mock_block
        self.mock_w3.eth.max_priority_fee = 2000000000  # 2 Gwei
        
        # Get gas params
        params = self.handler.get_optimal_gas_params()
        
        # Verify calculations
        self.assertIn('maxFeePerGas', params)
        self.assertIn('maxPriorityFeePerGas', params)
        self.assertIn('baseFee', params)
        self.assertEqual(params['baseFee'], 30000000000)
        self.assertGreater(params['maxFeePerGas'], params['baseFee'])
        self.assertGreater(params['maxPriorityFeePerGas'], 0)
    
    def test_build_transaction(self):
        """Test transaction building"""
        # Mock gas estimation and params
        mock_block = {
            'baseFeePerGas': 30000000000,
            'number': 12345
        }
        self.mock_w3.eth.get_block.return_value = mock_block
        self.mock_w3.eth.max_priority_fee = 2000000000
        self.mock_w3.eth.get_transaction_count.return_value = 5
        self.mock_w3.eth.estimate_gas.return_value = 100000
        
        # Build transaction
        tx = self.handler.build_transaction(
            from_address='0x1234567890123456789012345678901234567890',
            to_address='0x0987654321098765432109876543210987654321',
            data='0xabcd',
            value=0
        )
        
        # Verify transaction structure
        self.assertIn('from', tx)
        self.assertIn('to', tx)
        self.assertIn('data', tx)
        self.assertIn('value', tx)
        self.assertIn('gas', tx)
        self.assertIn('maxFeePerGas', tx)
        self.assertIn('maxPriorityFeePerGas', tx)
        self.assertIn('nonce', tx)
        self.assertIn('chainId', tx)
        self.assertEqual(tx['type'], 2)  # EIP-1559
        self.assertEqual(tx['nonce'], 5)
    
    def test_estimate_gas_cost(self):
        """Test gas cost estimation"""
        # Mock gas params
        mock_block = {
            'baseFeePerGas': 30000000000,
            'number': 12345
        }
        self.mock_w3.eth.get_block.return_value = mock_block
        self.mock_w3.eth.max_priority_fee = 2000000000
        
        # Estimate cost
        cost = self.handler.estimate_gas_cost(gas_limit=200000)
        
        # Verify cost is positive and reasonable
        self.assertIsInstance(cost, Decimal)
        self.assertGreater(cost, Decimal('0'))
        self.assertLess(cost, Decimal('1'))  # Should be less than 1 ETH
    
    def test_fallback_on_error(self):
        """Test fallback to defaults when API calls fail"""
        # Mock failures
        self.mock_w3.eth.get_block.side_effect = Exception("RPC error")
        
        # Should still return valid params
        params = self.handler.get_optimal_gas_params()
        
        self.assertIn('maxFeePerGas', params)
        self.assertIn('maxPriorityFeePerGas', params)
        self.assertGreater(params['maxFeePerGas'], 0)


if __name__ == '__main__':
    unittest.main()
