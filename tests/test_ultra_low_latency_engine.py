"""
Tests for Ultra-Low Latency Engine
"""

import pytest
from src.python.ultra_low_latency_engine import (
    UltraLowLatencyEngine,
    ArbitrageOpportunity
)


def test_arbitrage_opportunity():
    """Test ArbitrageOpportunity dataclass"""
    opp = ArbitrageOpportunity(
        chain_id=1,
        dex_pairs=["uniswap", "sushiswap"],
        profit_potential=2000.0,
        gas_cost=50.0,
        execution_time=0.05,
        success_probability=0.9
    )
    
    assert opp.chain_id == 1
    assert len(opp.dex_pairs) == 2
    assert opp.profit_potential == 2000.0
    assert opp.gas_cost == 50.0
    assert opp.success_probability == 0.9


def test_ultra_low_latency_engine_init():
    """Test UltraLowLatencyEngine initialization"""
    engine = UltraLowLatencyEngine()
    
    assert engine.profit_target == 1000000
    assert isinstance(engine.websocket_connections, dict)
    assert isinstance(engine.mempool_monitors, dict)
    assert isinstance(engine.execution_history, list)


@pytest.mark.asyncio
async def test_detect_opportunities():
    """Test opportunity detection"""
    engine = UltraLowLatencyEngine()
    opportunities = await engine.detect_opportunities()
    
    # Should return a list (may be empty in test environment)
    assert isinstance(opportunities, list)


def test_get_stats():
    """Test statistics retrieval"""
    engine = UltraLowLatencyEngine()
    stats = engine.get_stats()
    
    assert 'profit_target' in stats
    assert 'execution_count' in stats
    assert 'active_monitors' in stats
    assert stats['profit_target'] == 1000000
