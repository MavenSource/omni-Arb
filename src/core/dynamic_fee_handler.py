"""
Dynamic Fee Transaction Handler for EIP-1559 Transactions
Handles dynamic fee calculations and transaction building
"""

from typing import Dict, Any, Optional
from decimal import Decimal
from web3 import Web3
from eth_account import Account
from eth_utils import to_wei, from_wei

from src.utils.logger import logger


class DynamicFeeHandler:
    """
    Handles EIP-1559 dynamic fee transactions for optimal gas pricing
    """
    
    def __init__(self, w3: Web3, config: Optional[Dict[str, Any]] = None):
        """
        Initialize dynamic fee handler
        
        Args:
            w3: Web3 instance
            config: Optional configuration dictionary
        """
        self.w3 = w3
        self.config = config or {}
        self.max_priority_fee_multiplier = self.config.get('max_priority_fee_multiplier', 1.2)
        self.max_fee_multiplier = self.config.get('max_fee_multiplier', 2.0)
        logger.info("Dynamic Fee Handler initialized")
    
    def get_optimal_gas_params(self) -> Dict[str, int]:
        """
        Calculate optimal gas parameters for EIP-1559 transaction
        
        Returns:
            Dictionary with maxFeePerGas and maxPriorityFeePerGas
        """
        try:
            # Get current base fee
            latest_block = self.w3.eth.get_block('latest')
            base_fee = latest_block.get('baseFeePerGas', 0)
            
            # Get suggested priority fee
            max_priority_fee = self.w3.eth.max_priority_fee
            
            # Calculate optimal fees with multipliers
            suggested_priority_fee = int(max_priority_fee * self.max_priority_fee_multiplier)
            suggested_max_fee = int((base_fee * self.max_fee_multiplier) + suggested_priority_fee)
            
            return {
                'maxFeePerGas': suggested_max_fee,
                'maxPriorityFeePerGas': suggested_priority_fee,
                'baseFee': base_fee
            }
            
        except Exception as e:
            logger.warning(f"Error calculating optimal gas params: {e}, using defaults")
            # Fallback to safe defaults
            return {
                'maxFeePerGas': to_wei(100, 'gwei'),
                'maxPriorityFeePerGas': to_wei(2, 'gwei'),
                'baseFee': 0
            }
    
    def build_transaction(
        self,
        from_address: str,
        to_address: str,
        data: str,
        value: int = 0,
        gas_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build an EIP-1559 transaction with optimal gas parameters
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            data: Transaction data
            value: Transaction value in Wei
            gas_limit: Optional gas limit
            
        Returns:
            Transaction dictionary
        """
        try:
            # Get optimal gas parameters
            gas_params = self.get_optimal_gas_params()
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(from_address)
            
            # Estimate gas if not provided
            if gas_limit is None:
                try:
                    gas_limit = self.w3.eth.estimate_gas({
                        'from': from_address,
                        'to': to_address,
                        'data': data,
                        'value': value
                    })
                    gas_limit = int(gas_limit * 1.2)  # Add 20% buffer
                except Exception as e:
                    logger.warning(f"Gas estimation failed: {e}, using default")
                    gas_limit = 500000
            
            # Build transaction
            transaction = {
                'from': from_address,
                'to': to_address,
                'value': value,
                'data': data,
                'gas': gas_limit,
                'maxFeePerGas': gas_params['maxFeePerGas'],
                'maxPriorityFeePerGas': gas_params['maxPriorityFeePerGas'],
                'nonce': nonce,
                'chainId': self.w3.eth.chain_id,
                'type': 2  # EIP-1559
            }
            
            logger.debug(f"Built EIP-1559 transaction: {transaction}")
            return transaction
            
        except Exception as e:
            logger.error(f"Error building transaction: {e}")
            raise
    
    def estimate_gas_cost(self, gas_limit: int) -> Decimal:
        """
        Estimate the gas cost in ETH for a transaction
        
        Args:
            gas_limit: Gas limit for the transaction
            
        Returns:
            Estimated cost in ETH
        """
        try:
            gas_params = self.get_optimal_gas_params()
            max_fee = gas_params['maxFeePerGas']
            cost_wei = gas_limit * max_fee
            cost_eth = Decimal(str(from_wei(cost_wei, 'ether')))
            return cost_eth
        except Exception as e:
            logger.error(f"Error estimating gas cost: {e}")
            return Decimal('0.01')  # Safe default
    
    def sign_and_send_transaction(
        self,
        transaction: Dict[str, Any],
        private_key: str
    ) -> str:
        """
        Sign and send a transaction
        
        Args:
            transaction: Transaction dictionary
            private_key: Private key for signing
            
        Returns:
            Transaction hash
        """
        try:
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logger.error(f"Error signing and sending transaction: {e}")
            raise
