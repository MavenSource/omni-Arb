"""
Trade execution module
"""

from typing import Optional, Dict, Any
from web3 import Web3
from src.utils.logger import logger
from .arbitrage import ArbitrageOpportunity


class TradeExecutor:
    """Executes arbitrage trades"""
    
    def __init__(self, w3: Web3, private_key: Optional[str] = None):
        """
        Initialize trade executor
        
        Args:
            w3: Web3 instance
            private_key: Private key for signing transactions (optional)
        """
        self.w3 = w3
        self.private_key = private_key
        self.account = None
        
        if private_key:
            try:
                self.account = self.w3.eth.account.from_key(private_key)
                logger.info(f"Trade executor initialized with account: {self.account.address}")
            except Exception as e:
                logger.error(f"Error loading private key: {e}")
    
    def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> bool:
        """
        Execute an arbitrage opportunity
        
        Args:
            opportunity: Arbitrage opportunity to execute
            
        Returns:
            True if successful, False otherwise
        """
        if not self.account:
            logger.warning("Cannot execute trade: No private key configured")
            return False
        
        logger.info(f"Executing arbitrage: {opportunity}")
        
        try:
            # Step 1: Buy on cheaper DEX
            buy_tx = self._execute_swap(
                dex=opportunity.buy_dex,
                token_in=opportunity.token_in,
                token_out=opportunity.token_out,
                amount_in=opportunity.amount_in,
                min_amount_out=opportunity.buy_price
            )
            
            if not buy_tx:
                logger.error("Buy transaction failed")
                return False
            
            logger.info(f"Buy transaction successful: {buy_tx}")
            
            # Step 2: Sell on expensive DEX
            sell_tx = self._execute_swap(
                dex=opportunity.sell_dex,
                token_in=opportunity.token_out,
                token_out=opportunity.token_in,
                amount_in=opportunity.buy_price,
                min_amount_out=opportunity.sell_price
            )
            
            if not sell_tx:
                logger.error("Sell transaction failed")
                return False
            
            logger.info(f"Sell transaction successful: {sell_tx}")
            logger.info(f"Arbitrage completed! Profit: {opportunity.profit_percentage:.2f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing arbitrage: {e}")
            return False
    
    def _execute_swap(
        self,
        dex: str,
        token_in: str,
        token_out: str,
        amount_in: int,
        min_amount_out: int
    ) -> Optional[str]:
        """
        Execute a token swap on a DEX
        
        Args:
            dex: DEX name
            token_in: Input token address
            token_out: Output token address
            amount_in: Input amount
            min_amount_out: Minimum output amount (slippage protection)
            
        Returns:
            Transaction hash or None
        """
        # This is a placeholder for actual swap execution
        # In a real implementation, this would:
        # 1. Build the swap transaction
        # 2. Estimate gas
        # 3. Sign the transaction
        # 4. Send the transaction
        # 5. Wait for confirmation
        
        logger.info(
            f"[SIMULATION] Swap on {dex}: "
            f"{amount_in} {token_in[:8]}... -> "
            f"{min_amount_out} {token_out[:8]}..."
        )
        
        # Return simulated transaction hash
        return "0x" + "0" * 64
    
    def estimate_gas_cost(self, opportunity: ArbitrageOpportunity) -> int:
        """
        Estimate gas cost for executing an arbitrage
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Estimated gas cost in wei
        """
        try:
            gas_price = self.w3.eth.gas_price
            # Estimate 2 swaps * ~150k gas per swap
            estimated_gas = 300000
            return gas_price * estimated_gas
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return 0
    
    def is_profitable_after_gas(
        self,
        opportunity: ArbitrageOpportunity,
        gas_cost_multiplier: float = 1.1
    ) -> bool:
        """
        Check if opportunity is profitable after gas costs
        
        Args:
            opportunity: Arbitrage opportunity
            gas_cost_multiplier: Safety multiplier for gas estimation
            
        Returns:
            True if still profitable, False otherwise
        """
        gas_cost = self.estimate_gas_cost(opportunity) * gas_cost_multiplier
        net_profit = opportunity.profit - gas_cost
        
        return net_profit > 0
