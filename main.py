"""
Main entry point for the omni-Arb system
"""

import asyncio
import json
from pathlib import Path
from src.python.system_architecture import SystemArchitecture
from src.python.ultra_low_latency_engine import UltraLowLatencyEngine
from src.python.multi_chain_coordinator import MultiChainArbitrageCoordinator
from src.python.ai_profit_maximizer import AIProfitMaximizer
from src.python.risk_manager import AdvancedRiskManager
from src.python.enterprise_infrastructure import EnterpriseInfrastructure
from src.python.profit_optimization_engine import ProfitOptimizationEngine


class OmniArbSystem:
    """Main system orchestrator"""
    
    def __init__(self, config_path: str = "config/system_config.json"):
        self.config = self._load_config(config_path)
        self.system_architecture = SystemArchitecture()
        self.execution_engine = UltraLowLatencyEngine()
        self.multi_chain_coordinator = MultiChainArbitrageCoordinator()
        self.ai_maximizer = AIProfitMaximizer()
        self.risk_manager = AdvancedRiskManager()
        self.infrastructure = EnterpriseInfrastructure()
        self.profit_optimizer = ProfitOptimizationEngine()
        
    def _load_config(self, config_path: str) -> dict:
        """Load system configuration"""
        try:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config from {config_path}: {e}")
        
        # Return default configuration
        return {
            'profit_targets': {
                'daily_target': 33333,
                'monthly_target': 1000000
            }
        }
    
    def display_status(self):
        """Display system status"""
        print("=" * 60)
        print("OMNI-ARB SYSTEM STATUS")
        print("=" * 60)
        
        # System Architecture
        status = self.system_architecture.get_status()
        print("\n[System Architecture]")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # Execution Engine
        stats = self.execution_engine.get_stats()
        print("\n[Execution Engine]")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Multi-Chain Coordinator
        chain_status = self.multi_chain_coordinator.get_chain_status()
        print("\n[Multi-Chain Coordinator]")
        for chain, info in chain_status.items():
            print(f"  {chain}: {info['manager']}")
        
        # Infrastructure
        infra_status = self.infrastructure.get_infrastructure_status()
        print("\n[Infrastructure]")
        for key, value in infra_status.items():
            print(f"  {key}: {value}")
        
        # KPIs
        kpis = self.profit_optimizer.get_kpis()
        print("\n[Key Performance Indicators]")
        for key, value in kpis.items():
            print(f"  {key}: {value}")
        
        print("\n" + "=" * 60)
    
    async def run(self):
        """Run the main system"""
        print("Starting omni-Arb system...")
        self.display_status()
        
        print("\nSystem initialized successfully!")
        print("Ready for arbitrage operations.")
        print("\nPress Ctrl+C to stop.")
        
        try:
            # In production, this would run the actual monitoring and execution
            await asyncio.sleep(3600)  # Run for 1 hour as demo
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")


def main():
    """Main entry point"""
    system = OmniArbSystem()
    asyncio.run(system.run())


if __name__ == "__main__":
    main()
