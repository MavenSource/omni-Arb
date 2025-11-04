"""
Tests for Profit Optimization Engine
"""

import pytest
from src.python.profit_optimization_engine import (
    ProfitOptimizationEngine,
    TimeSeriesDatabase,
    PerformanceAnalyzer,
    ContinuousOptimizer
)


def test_time_series_database():
    """Test TimeSeriesDatabase"""
    db = TimeSeriesDatabase()
    
    db.insert(1000.0, {'profit': 500})
    db.insert(2000.0, {'profit': 600})
    
    results = db.query(500.0, 1500.0)
    assert len(results) == 1
    assert results[0]['data']['profit'] == 500


def test_performance_analyzer():
    """Test PerformanceAnalyzer"""
    analyzer = PerformanceAnalyzer()
    
    data = [
        {'profit': 100, 'success': True},
        {'profit': 200, 'success': True},
        {'profit': -50, 'success': False}
    ]
    
    analysis = analyzer.analyze(data)
    
    assert analysis['total_trades'] == 3
    assert analysis['success_rate'] == 2/3
    assert analysis['avg_profit'] == 250/3


@pytest.mark.asyncio
async def test_continuous_optimizer():
    """Test ContinuousOptimizer"""
    optimizer = ContinuousOptimizer()
    
    performance_data = {
        'avg_daily_profit': 30000,
        'avg_success_rate': 0.92
    }
    
    result = await optimizer.optimize(performance_data)
    
    assert 'adjustments' in result
    assert 'expected_improvement' in result


def test_profit_optimization_engine_init():
    """Test ProfitOptimizationEngine initialization"""
    engine = ProfitOptimizationEngine()
    
    assert engine.profit_database is not None
    assert engine.performance_analyzer is not None
    assert engine.optimization_engine is not None


def test_calculate_target_profit():
    """Test target profit calculation"""
    engine = ProfitOptimizationEngine()
    targets = engine._calculate_target_profit()
    
    assert targets['daily_target'] == 33333
    assert targets['weekly_target'] == 233333
    assert targets['monthly_target'] == 1000000


def test_get_kpis():
    """Test KPI retrieval"""
    engine = ProfitOptimizationEngine()
    kpis = engine.get_kpis()
    
    assert kpis['daily_profit'] == 33333
    assert kpis['success_rate'] == 0.95
    assert kpis['execution_time'] == 0.1
    assert kpis['capital_turnover'] == 5
    assert kpis['max_drawdown'] == 0.05
    assert kpis['sharpe_ratio'] == 3.0
