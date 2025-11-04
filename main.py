"""
Omni-Arb: Multi-Chain DeFi Arbitrage System
Main application entry point
"""

import os
import time
import signal
import sys
from typing import List, Tuple

from src.config import config
from src.utils.logger import logger, setup_logger
from src.core.blockchain import blockchain
from src.core.arbitrage import ArbitrageDetector
from src.core.executor import TradeExecutor
from src.dex.dex_manager import DEXManager
from src.utils.web3_utils import to_wei, from_wei


class OmniArb:
    """Main arbitrage bot application"""
    
    def __init__(self):
        """Initialize the arbitrage bot"""
        self.running = False
        self.detectors = {}
        self.executors = {}
        
        # Setup logger
        log_level = config.get('monitoring.log_level', 'INFO')
        self.logger = setup_logger('omni-arb', log_level)
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._initialize()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received, stopping...")
        self.running = False
    
    def _initialize(self):
        """Initialize all components"""
        self.logger.info("Initializing Omni-Arb...")
        
        # Get private key if available (for trade execution)
        private_key = os.getenv('PRIVATE_KEY')
        
        # Initialize for each network
        for network in config.get_supported_networks():
            w3 = blockchain.get_connection(network)
            if not w3:
                self.logger.warning(f"Skipping {network}: Not connected")
                continue
            
            # Initialize DEX manager
            dex_manager = DEXManager(w3, network)
            
            # Initialize arbitrage detector
            detector = ArbitrageDetector(dex_manager, network)
            self.detectors[network] = detector
            
            # Initialize trade executor
            executor = TradeExecutor(w3, private_key)
            self.executors[network] = executor
            
            self.logger.info(f"Initialized components for {network}")
        
        if not self.detectors:
            self.logger.error("No networks initialized! Check your configuration.")
            sys.exit(1)
        
        self.logger.info("Initialization complete!")
    
    def get_default_token_pairs(self, network: str) -> List[Tuple[str, str]]:
        """
        Get default token pairs to monitor
        
        Args:
            network: Network name
            
        Returns:
            List of token pair tuples
        """
        # Common token addresses (these are examples - update with real addresses)
        tokens = {
            'ethereum': {
                'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
            },
            'bsc': {
                'WBNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                'BUSD': '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
                'USDT': '0x55d398326f99059fF775485246999027B3197955',
            },
            'polygon': {
                'WMATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
                'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
                'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
            }
        }
        
        network_tokens = tokens.get(network, {})
        if not network_tokens:
            return []
        
        # Create pairs
        pairs = []
        token_list = list(network_tokens.values())
        for i, token1 in enumerate(token_list):
            for token2 in token_list[i+1:]:
                pairs.append((token1, token2))
        
        return pairs
    
    def scan_for_opportunities(self):
        """Scan for arbitrage opportunities across all networks"""
        min_profit_pct = config.get('trading.min_profit_percentage', 0.5)
        check_interval = config.get('monitoring.check_interval_seconds', 5)
        
        self.logger.info(f"Starting arbitrage scanner (min profit: {min_profit_pct}%)")
        self.running = True
        
        while self.running:
            try:
                for network, detector in self.detectors.items():
                    # Get token pairs to scan
                    token_pairs = self.get_default_token_pairs(network)
                    
                    if not token_pairs:
                        self.logger.debug(f"No token pairs configured for {network}")
                        continue
                    
                    # Amount to trade (1 WETH equivalent)
                    amount_in = to_wei(1, 'ether')
                    
                    # Scan for opportunities
                    opportunities = detector.scan_token_pairs(
                        token_pairs,
                        amount_in,
                        min_profit_pct
                    )
                    
                    # Log opportunities
                    if opportunities:
                        self.logger.info(f"Found {len(opportunities)} opportunities on {network}")
                        for opp in opportunities[:3]:  # Show top 3
                            self.logger.info(f"  {opp}")
                            
                            # Check if profitable after gas
                            executor = self.executors.get(network)
                            if executor and executor.is_profitable_after_gas(opp):
                                self.logger.info(f"  -> Profitable after gas!")
                            else:
                                self.logger.info(f"  -> Not profitable after gas costs")
                    else:
                        self.logger.debug(f"No opportunities found on {network}")
                
                # Wait before next scan
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"Error during scan: {e}")
                time.sleep(check_interval)
        
        self.logger.info("Scanner stopped")
    
    def run(self):
        """Run the arbitrage bot"""
        try:
            self.scan_for_opportunities()
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            sys.exit(1)


def main():
    """Main entry point"""
    print("""
    ╔═══════════════════════════════════════╗
    ║      Omni-Arb DeFi Arbitrage Bot      ║
    ║    Multi-Chain Arbitrage Detection    ║
    ╚═══════════════════════════════════════╝
    """)
    
    bot = OmniArb()
    bot.run()


if __name__ == '__main__':
    main()
