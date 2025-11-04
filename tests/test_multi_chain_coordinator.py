"""
Tests for Multi-Chain Coordinator
"""

import pytest
from src.python.multi_chain_coordinator import (
    MultiChainArbitrageCoordinator,
    EthereumManager,
    BSCManager,
    PolygonManager,
    ArbitrumManager,
    OptimismManager
)


def test_chain_managers():
    """Test individual chain managers"""
    eth = EthereumManager()
    bsc = BSCManager()
    polygon = PolygonManager()
    arbitrum = ArbitrumManager()
    optimism = OptimismManager()
    
    assert eth.chain_name == "ethereum"
    assert bsc.chain_name == "bsc"
    assert polygon.chain_name == "polygon"
    assert arbitrum.chain_name == "arbitrum"
    assert optimism.chain_name == "optimism"


def test_coordinator_init():
    """Test MultiChainArbitrageCoordinator initialization"""
    coordinator = MultiChainArbitrageCoordinator()
    
    assert len(coordinator.chains) == 5
    assert 'ethereum' in coordinator.chains
    assert 'bsc' in coordinator.chains
    assert 'polygon' in coordinator.chains
    assert 'arbitrum' in coordinator.chains
    assert 'optimism' in coordinator.chains
    
    assert coordinator.flash_loan_pools is not None
    assert coordinator.cross_chain_bridges is not None


@pytest.mark.asyncio
async def test_execute_cross_chain_arbitrage():
    """Test cross-chain arbitrage execution"""
    coordinator = MultiChainArbitrageCoordinator()
    
    opportunity = {
        'source_chain': 'ethereum',
        'target_chains': ['bsc', 'polygon'],
        'required_capital': 100000
    }
    
    result = await coordinator.execute_cross_chain_arbitrage(opportunity)
    
    assert 'net_profit' in result
    assert 'execution_time' in result
    assert 'success' in result


def test_get_chain_status():
    """Test chain status retrieval"""
    coordinator = MultiChainArbitrageCoordinator()
    status = coordinator.get_chain_status()
    
    assert len(status) == 5
    assert all('manager' in s for s in status.values())
