"""
Tests for Omni Strategy Engine
"""

import unittest
import asyncio
from unittest.mock import Mock, AsyncMock
from decimal import Decimal
from datetime import datetime

from src.core.strategy_engine import (
    OmniStrategyEngine,
    StrategyType,
    OpportunitySignal
)


class TestOmniStrategyEngine(unittest.TestCase):
    """Test cases for OmniStrategyEngine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_detector = Mock()
        self.mock_router = Mock()
        self.mock_executor = Mock()
        
        # Create engine with mocks
        self.engine = OmniStrategyEngine(
            self.mock_detector,
            self.mock_router,
            self.mock_executor,
            initial_capital=Decimal('100000')
        )
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.capital, Decimal('100000'))
        self.assertEqual(self.engine.total_profit, Decimal('0'))
        self.assertEqual(self.engine.trades_executed, 0)
        self.assertGreater(self.engine.max_position_size, Decimal('0'))
    
    def test_opportunity_signal_creation(self):
        """Test OpportunitySignal dataclass"""
        signal = OpportunitySignal(
            strategy=StrategyType.FLASH_ARBITRAGE,
            profit_estimate=Decimal('150'),
            confidence=0.85,
            risk_score=0.3,
            capital_required=Decimal('5000'),
            execution_time=5.0,
            gas_cost=Decimal('10'),
            net_profit=Decimal('140'),
            data={'test': 'data'},
            timestamp=datetime.now()
        )
        
        self.assertEqual(signal.strategy, StrategyType.FLASH_ARBITRAGE)
        self.assertGreater(signal.net_profit, Decimal('0'))
        self.assertLess(signal.confidence, 1.0)
        self.assertGreater(signal.confidence, 0.0)
    
    def test_rank_opportunities(self):
        """Test opportunity ranking"""
        opportunities = [
            OpportunitySignal(
                strategy=StrategyType.FLASH_ARBITRAGE,
                profit_estimate=Decimal('100'),
                confidence=0.9,
                risk_score=0.2,
                capital_required=Decimal('1000'),
                execution_time=3.0,
                gas_cost=Decimal('5'),
                net_profit=Decimal('95'),
                data={},
                timestamp=datetime.now()
            ),
            OpportunitySignal(
                strategy=StrategyType.MULTI_HOP,
                profit_estimate=Decimal('50'),
                confidence=0.8,
                risk_score=0.3,
                capital_required=Decimal('2000'),
                execution_time=5.0,
                gas_cost=Decimal('5'),
                net_profit=Decimal('45'),
                data={},
                timestamp=datetime.now()
            ),
            OpportunitySignal(
                strategy=StrategyType.CROSS_DEX,
                profit_estimate=Decimal('200'),
                confidence=0.6,  # Low confidence
                risk_score=0.4,
                capital_required=Decimal('5000'),
                execution_time=7.0,
                gas_cost=Decimal('10'),
                net_profit=Decimal('190'),
                data={},
                timestamp=datetime.now()
            )
        ]
        
        # Rank opportunities
        ranked = self.engine.rank_opportunities(opportunities)
        
        # Should filter out low confidence and rank by risk-adjusted return
        self.assertIsInstance(ranked, list)
        self.assertLessEqual(len(ranked), len(opportunities))
        
        # All ranked opportunities should meet minimum requirements
        for opp in ranked:
            self.assertGreater(opp.confidence, 0.7)
            self.assertGreater(opp.net_profit, Decimal('20'))
    
    def test_allocate_capital(self):
        """Test capital allocation"""
        opportunities = [
            OpportunitySignal(
                strategy=StrategyType.FLASH_ARBITRAGE,
                profit_estimate=Decimal('100'),
                confidence=0.9,
                risk_score=0.2,
                capital_required=Decimal('5000'),
                execution_time=3.0,
                gas_cost=Decimal('5'),
                net_profit=Decimal('95'),
                data={},
                timestamp=datetime.now()
            ),
            OpportunitySignal(
                strategy=StrategyType.MULTI_HOP,
                profit_estimate=Decimal('50'),
                confidence=0.85,
                risk_score=0.3,
                capital_required=Decimal('3000'),
                execution_time=5.0,
                gas_cost=Decimal('5'),
                net_profit=Decimal('45'),
                data={},
                timestamp=datetime.now()
            )
        ]
        
        # Allocate capital
        allocations = self.engine.allocate_capital(opportunities)
        
        # Verify allocations
        self.assertIsInstance(allocations, dict)
        
        # Total allocated should not exceed available capital
        total_allocated = sum(allocations.values())
        max_allowed = self.engine.capital * Decimal('0.8')
        self.assertLessEqual(total_allocated, max_allowed)
        
        # Each allocation should respect position limits
        for allocation in allocations.values():
            self.assertLessEqual(allocation, self.engine.max_position_size)
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        # Simulate some trades
        self.engine.trades_executed = 10
        self.engine.total_profit = Decimal('5000')
        self.engine.daily_pnl = [Decimal('500'), Decimal('300'), Decimal('200')]
        
        # Get summary
        summary = self.engine.get_performance_summary()
        
        # Verify summary structure
        self.assertIn('total_capital', summary)
        self.assertIn('total_profit', summary)
        self.assertIn('trades_executed', summary)
        self.assertIn('roi_percent', summary)
        self.assertIn('daily_pnl', summary)
        
        # Verify calculations
        self.assertEqual(summary['trades_executed'], 10)
        self.assertEqual(summary['total_profit'], 5000.0)
        self.assertGreater(summary['roi_percent'], 0)
    
    def test_scan_all_opportunities_async(self):
        """Test async opportunity scanning"""
        # Mock async detector
        self.mock_detector.find_opportunities_async = AsyncMock(return_value=[
            {
                'profit': 100,
                'gas_cost': 5,
                'amount': 1000
            }
        ])
        
        # Mock async router
        self.mock_router.find_profitable_routes = AsyncMock(return_value=[])
        
        async def run_test():
            opportunities = await self.engine.scan_all_opportunities()
            self.assertIsInstance(opportunities, list)
        
        asyncio.run(run_test())


if __name__ == '__main__':
    unittest.main()
