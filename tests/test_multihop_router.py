"""
Tests for Multi-Hop Router
"""

import unittest
import asyncio
from unittest.mock import Mock, MagicMock, AsyncMock
from decimal import Decimal
from datetime import datetime

from src.core.multihop_router import MultiHopRouter, MultiHopRoute, SwapStep


class TestMultiHopRouter(unittest.TestCase):
    """Test cases for MultiHopRouter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_dex_manager = Mock()
        self.mock_price_fetcher = Mock()
        
        # Mock available tokens
        self.mock_dex_manager.get_available_tokens.return_value = [
            'USDC', 'WETH', 'WMATIC', 'USDT', 'DAI'
        ]
        
        # Mock available DEXes
        self.mock_dex_manager.get_available_dexes.return_value = [
            'uniswap', 'sushiswap', 'quickswap'
        ]
        
        # Mock DEX instance
        self.mock_dex = AsyncMock()
        self.mock_dex.get_amount_out = AsyncMock(return_value=Decimal('1050'))
        self.mock_dex_manager.get_dex.return_value = self.mock_dex
        
        self.router = MultiHopRouter(self.mock_dex_manager, self.mock_price_fetcher)
    
    def test_initialization(self):
        """Test router initialization"""
        self.assertIsNotNone(self.router)
        self.assertEqual(self.router.dex_manager, self.mock_dex_manager)
        self.assertEqual(self.router.max_hops, 3)
        self.assertEqual(self.router.min_profit_threshold, Decimal('50'))
    
    def test_swap_step_dataclass(self):
        """Test SwapStep dataclass"""
        step = SwapStep(
            dex='uniswap',
            token_in='USDC',
            token_out='WETH',
            amount_in=Decimal('1000'),
            amount_out=Decimal('0.5'),
            price=Decimal('2000'),
            fee=Decimal('3'),
            slippage_percent=0.3
        )
        
        self.assertEqual(step.dex, 'uniswap')
        self.assertEqual(step.token_in, 'USDC')
        self.assertEqual(step.token_out, 'WETH')
        self.assertIsInstance(step.amount_in, Decimal)
    
    def test_multihop_route_dataclass(self):
        """Test MultiHopRoute dataclass"""
        route = MultiHopRoute(
            route_id='test_route',
            token_path=['USDC', 'WETH', 'USDC'],
            dex_path=['uniswap', 'sushiswap'],
            hops=2,
            steps=[],
            initial_amount=Decimal('1000'),
            final_amount=Decimal('1050'),
            total_fees=Decimal('5'),
            gross_profit=Decimal('50'),
            net_profit=Decimal('45'),
            profit_percent=4.5,
            gas_estimate=250000,
            confidence=0.85,
            timestamp=datetime.now()
        )
        
        self.assertEqual(route.hops, 2)
        self.assertEqual(len(route.token_path), 3)
        self.assertGreater(route.net_profit, Decimal('0'))
    
    def test_find_profitable_routes_async(self):
        """Test async route finding"""
        async def run_test():
            routes = await self.router.find_profitable_routes(
                start_token='USDC',
                end_token='WETH',
                amount=Decimal('1000'),
                max_hops=2
            )
            
            # Should return a list (possibly empty)
            self.assertIsInstance(routes, list)
        
        asyncio.run(run_test())
    
    def test_get_swap_quote_async(self):
        """Test async swap quote fetching"""
        async def run_test():
            quote = await self.router._get_swap_quote(
                'uniswap',
                'USDC',
                'WETH',
                Decimal('1000')
            )
            
            if quote:
                self.assertIn('amount_out', quote)
                self.assertIn('price', quote)
                self.assertIn('fee', quote)
        
        asyncio.run(run_test())
    
    def test_profit_filtering(self):
        """Test that unprofitable routes are filtered"""
        # Create mock routes with different profits
        routes = [
            Mock(net_profit=Decimal('100')),
            Mock(net_profit=Decimal('10')),  # Below threshold
            Mock(net_profit=Decimal('75')),
        ]
        
        # Filter using threshold
        profitable = [r for r in routes if r.net_profit > self.router.min_profit_threshold]
        
        self.assertEqual(len(profitable), 2)
        self.assertGreater(profitable[0].net_profit, Decimal('50'))


if __name__ == '__main__':
    unittest.main()
