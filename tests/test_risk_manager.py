"""
Tests for Risk Manager
"""

import pytest
from src.python.risk_manager import (
    AdvancedRiskManager,
    SlippagePredictor,
    VolatilityMonitor,
    CircuitBreakerSystem
)


def test_circuit_breaker_system():
    """Test CircuitBreakerSystem"""
    breaker = CircuitBreakerSystem()
    
    assert breaker.thresholds['max_loss_per_trade'] == 10000
    assert breaker.thresholds['max_daily_loss'] == 50000
    assert breaker.thresholds['min_success_rate'] == 0.80
    
    # Test max threshold
    assert breaker.check_breaker('max_loss_per_trade', 15000) is True
    assert breaker.check_breaker('max_loss_per_trade', 5000) is False
    
    # Test min threshold
    assert breaker.check_breaker('min_success_rate', 0.70) is True
    assert breaker.check_breaker('min_success_rate', 0.90) is False


def test_circuit_breaker_activation():
    """Test circuit breaker activation and reset"""
    breaker = CircuitBreakerSystem()
    
    breaker.activate_breaker('high_loss')
    assert 'high_loss' in breaker.breakers_active
    
    breaker.reset_breaker('high_loss')
    assert 'high_loss' not in breaker.breakers_active


@pytest.mark.asyncio
async def test_slippage_predictor():
    """Test SlippagePredictor"""
    predictor = SlippagePredictor()
    slippage = await predictor.predict('uniswap', 10000)
    
    assert isinstance(slippage, float)
    assert slippage > 0


def test_volatility_monitor():
    """Test VolatilityMonitor"""
    monitor = VolatilityMonitor()
    risk = monitor.assess_risk('ETH/USDC')
    
    assert isinstance(risk, float)
    assert risk >= 0


def test_risk_manager_init():
    """Test AdvancedRiskManager initialization"""
    manager = AdvancedRiskManager()
    
    assert manager.slippage_predictor is not None
    assert manager.volatility_monitor is not None
    assert manager.circuit_breakers is not None


@pytest.mark.asyncio
async def test_assess_opportunity_risk():
    """Test opportunity risk assessment"""
    manager = AdvancedRiskManager()
    
    opportunity = {
        'dex': 'uniswap',
        'trade_size': 50000,
        'token_pair': 'ETH/USDC',
        'pool': {'size': 500000},
        'target_chains': ['ethereum', 'bsc']
    }
    
    assessment = await manager.assess_opportunity_risk(opportunity)
    
    assert 'risk_score' in assessment
    assert 'factors' in assessment
    assert 'recommended_action' in assessment
    assert assessment['recommended_action'] in ['execute', 'review']
