"""
Tests for System Architecture
"""

import pytest
from src.python.system_architecture import (
    SystemArchitecture,
    RustExecutionEngine,
    PythonAIModels,
    TypeScriptDashboard,
    MultiChainCoordinator
)


def test_rust_execution_engine():
    """Test RustExecutionEngine initialization"""
    engine = RustExecutionEngine()
    assert engine.name == "RustExecutionEngine"


def test_python_ai_models():
    """Test PythonAIModels initialization"""
    ai_models = PythonAIModels()
    assert ai_models.name == "PythonAIModels"


def test_typescript_dashboard():
    """Test TypeScriptDashboard initialization"""
    dashboard = TypeScriptDashboard()
    assert dashboard.name == "TypeScriptDashboard"


def test_multi_chain_coordinator():
    """Test MultiChainCoordinator initialization"""
    coordinator = MultiChainCoordinator()
    assert coordinator.name == "MultiChainCoordinator"


def test_system_architecture():
    """Test SystemArchitecture integration"""
    system = SystemArchitecture()
    
    assert system.execution_layer is not None
    assert system.intelligence_layer is not None
    assert system.monitoring_layer is not None
    assert system.integration_layer is not None
    
    status = system.get_status()
    assert status['execution'] == "RustExecutionEngine"
    assert status['intelligence'] == "PythonAIModels"
    assert status['monitoring'] == "TypeScriptDashboard"
    assert status['integration'] == "MultiChainCoordinator"
