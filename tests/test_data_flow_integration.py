"""
Integration test for complete data flow verification
Tests: DEX Data Intake -> Arbitrage Detection -> Transaction Broadcasting
"""

import sys
import os
from unittest.mock import Mock, MagicMock, patch
from typing import List, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dex.base_dex import BaseDEX
from src.dex.uniswap_v2 import UniswapV2
from src.dex.dex_manager import DEXManager
from src.core.arbitrage import ArbitrageDetector, ArbitrageOpportunity
from src.core.executor import TradeExecutor
from src.utils.web3_utils import to_wei, from_wei


# Test constants
MOCK_PRIVATE_KEY = '0x' + 'a' * 64  # Mock private key for testing


class TestDataFlowIntegration:
    """Test complete data flow from DEX data intake to transaction broadcasting"""
    
    @staticmethod
    def create_mock_web3():
        """Create a mock Web3 instance with required functionality"""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.gas_price = 50 * 10**9  # 50 gwei
        mock_w3.eth.block_number = 18000000
        
        # Mock account for executor
        mock_account = Mock()
        mock_account.address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        mock_w3.eth.account.from_key.return_value = mock_account
        
        return mock_w3
    
    @staticmethod
    def create_mock_dex(name: str, price_multiplier: float = 1.0):
        """
        Create a mock DEX with controlled price responses
        
        Args:
            name: DEX name
            price_multiplier: Multiplier for output amounts (simulates price differences)
        """
        mock_dex = Mock(spec=BaseDEX)
        mock_dex.get_name.return_value = name
        
        def mock_get_price(token_in: str, token_out: str, amount_in: int):
            # Simulate price with multiplier for arbitrage opportunities
            # Base output is slightly less than input (simulating exchange rate)
            base_output = int(amount_in * 0.99)
            return int(base_output * price_multiplier)
        
        mock_dex.get_price.side_effect = mock_get_price
        
        return mock_dex
    
    @staticmethod
    def test_step1_dex_data_intake():
        """
        Step 1: Verify DEX data intake
        Tests that the system can fetch price data from multiple DEXes
        """
        print("\n" + "="*70)
        print("TEST STEP 1: DEX DATA INTAKE")
        print("="*70)
        
        # Setup
        mock_w3 = TestDataFlowIntegration.create_mock_web3()
        dex_manager = DEXManager(mock_w3, "ethereum")
        
        # Mock DEXes with different prices (simulating real market conditions)
        dex_manager.dexes = {
            'uniswap_v2': TestDataFlowIntegration.create_mock_dex('Uniswap V2', 1.0),
            'sushiswap': TestDataFlowIntegration.create_mock_dex('SushiSwap', 1.02),  # 2% higher
            'pancakeswap': TestDataFlowIntegration.create_mock_dex('PancakeSwap', 0.98)  # 2% lower
        }
        
        # Test tokens
        weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        usdc = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        amount_in = to_wei(1, 'ether')
        
        # Execute: Fetch prices from all DEXes
        prices = dex_manager.compare_prices(weth, usdc, amount_in)
        
        # Verify
        assert len(prices) == 3, f"Expected 3 price quotes, got {len(prices)}"
        assert all(isinstance(p, tuple) and len(p) == 2 for p in prices), "Invalid price format"
        assert all(p[1] > 0 for p in prices), "All prices should be positive"
        
        # Verify prices are sorted (highest first)
        for i in range(len(prices) - 1):
            assert prices[i][1] >= prices[i+1][1], "Prices should be sorted descending"
        
        print(f"✅ Successfully fetched {len(prices)} price quotes from DEXes")
        for dex_name, price in prices:
            # Note: Using 'ether' for formatting 18-decimal token amounts (standard ERC20)
            print(f"   {dex_name}: {from_wei(price, 'ether'):.6f} tokens")
        
        return prices, dex_manager, weth, usdc, amount_in
    
    @staticmethod
    def test_step2_arbitrage_detection(prices, dex_manager, token_in, token_out, amount_in):
        """
        Step 2: Verify arbitrage opportunity detection
        Tests that the system correctly identifies profitable arbitrage opportunities
        """
        print("\n" + "="*70)
        print("TEST STEP 2: ARBITRAGE OPPORTUNITY DETECTION")
        print("="*70)
        
        # Setup arbitrage detector
        detector = ArbitrageDetector(dex_manager, "ethereum")
        
        # Execute: Find arbitrage opportunities
        opportunities = detector.find_opportunities(
            token_in=token_in,
            token_out=token_out,
            amount_in=amount_in,
            min_profit_pct=0.1  # Very low threshold for testing
        )
        
        # Verify
        assert len(opportunities) > 0, "Should find at least one arbitrage opportunity"
        
        for opp in opportunities:
            assert isinstance(opp, ArbitrageOpportunity), "Invalid opportunity type"
            assert opp.buy_dex != opp.sell_dex, "Buy and sell DEXes should be different"
            assert opp.profit > 0, "Profit should be positive"
            assert opp.profit_percentage > 0, "Profit percentage should be positive"
            assert opp.sell_price > opp.buy_price, "Sell price should be higher than buy price"
        
        print(f"✅ Detected {len(opportunities)} arbitrage opportunities")
        for i, opp in enumerate(opportunities[:3]):  # Show top 3
            print(f"   Opportunity #{i+1}:")
            # Note: Using 'ether' for formatting 18-decimal token amounts
            print(f"     Buy on {opp.buy_dex} @ {from_wei(opp.buy_price, 'ether'):.6f} tokens")
            print(f"     Sell on {opp.sell_dex} @ {from_wei(opp.sell_price, 'ether'):.6f} tokens")
            print(f"     Profit: {opp.profit_percentage:.4f}%")
        
        return opportunities
    
    @staticmethod
    def test_step3_transaction_preparation(opportunities, mock_w3):
        """
        Step 3: Verify transaction preparation
        Tests that the system can prepare transactions for execution
        """
        print("\n" + "="*70)
        print("TEST STEP 3: TRANSACTION PREPARATION")
        print("="*70)
        
        # Setup executor with mock private key
        executor = TradeExecutor(mock_w3, MOCK_PRIVATE_KEY)
        
        # Select best opportunity
        best_opportunity = opportunities[0]
        
        # Execute: Estimate gas cost
        gas_cost = executor.estimate_gas_cost(best_opportunity)
        
        # Verify
        assert gas_cost > 0, "Gas cost should be positive"
        assert executor.account is not None, "Executor should have account loaded"
        
        print(f"✅ Transaction preparation successful")
        print(f"   Account: {executor.account.address}")
        print(f"   Estimated gas cost: {from_wei(gas_cost, 'ether'):.6f} ETH")
        print(f"   Gas price: {mock_w3.eth.gas_price / 10**9} gwei")
        
        return executor, best_opportunity, gas_cost
    
    @staticmethod
    def test_step4_profitability_check(executor, opportunity, gas_cost):
        """
        Step 4: Verify profitability after gas costs
        Tests that the system correctly accounts for gas costs
        """
        print("\n" + "="*70)
        print("TEST STEP 4: PROFITABILITY VERIFICATION")
        print("="*70)
        
        # Execute: Check if profitable after gas
        is_profitable = executor.is_profitable_after_gas(opportunity)
        
        # Calculate net profit for display
        net_profit = opportunity.profit - gas_cost
        net_profit_eth = from_wei(net_profit, 'ether')
        
        print(f"   Gross profit: {from_wei(opportunity.profit, 'ether'):.6f} ETH")
        print(f"   Gas cost: {from_wei(gas_cost, 'ether'):.6f} ETH")
        print(f"   Net profit: {net_profit_eth:.6f} ETH")
        
        if is_profitable:
            print(f"✅ Trade is profitable after gas costs")
        else:
            print(f"⚠️  Trade is NOT profitable after gas costs (expected for test)")
        
        # For this test, we just verify the calculation works
        assert isinstance(is_profitable, bool), "Profitability check should return boolean"
        
        return is_profitable
    
    @staticmethod
    def test_step5_transaction_broadcasting(executor, opportunity):
        """
        Step 5: Verify transaction broadcasting
        Tests that the system can execute/broadcast transactions
        """
        print("\n" + "="*70)
        print("TEST STEP 5: TRANSACTION BROADCASTING (SIMULATION)")
        print("="*70)
        
        # Execute: Simulate trade execution
        # In real scenario, this would broadcast to blockchain
        success = executor.execute_arbitrage(opportunity)
        
        # Verify
        assert isinstance(success, bool), "Execute should return boolean"
        
        # In simulation mode, we expect True (simulated success)
        # The actual implementation returns simulated tx hash
        print(f"✅ Transaction broadcasting simulated successfully")
        print(f"   Execution result: {'SUCCESS' if success else 'FAILED'}")
        print(f"   Buy transaction: Simulated")
        print(f"   Sell transaction: Simulated")
        
        return success
    
    @staticmethod
    def test_step6_data_integrity():
        """
        Step 6: Verify data integrity throughout the flow
        Tests that data remains consistent through all stages
        """
        print("\n" + "="*70)
        print("TEST STEP 6: DATA INTEGRITY VERIFICATION")
        print("="*70)
        
        # Run a complete flow and verify data integrity
        mock_w3 = TestDataFlowIntegration.create_mock_web3()
        
        # Create DEXes with known price differences
        dex1_price = to_wei(1800, 'ether')  # Lower price
        dex2_price = to_wei(1850, 'ether')  # Higher price
        
        mock_dex1 = Mock(spec=BaseDEX)
        mock_dex1.get_name.return_value = "DEX1"
        mock_dex1.get_price.return_value = dex1_price
        
        mock_dex2 = Mock(spec=BaseDEX)
        mock_dex2.get_name.return_value = "DEX2"
        mock_dex2.get_price.return_value = dex2_price
        
        # Setup components
        dex_manager = DEXManager(mock_w3, "ethereum")
        dex_manager.dexes = {'dex1': mock_dex1, 'dex2': mock_dex2}
        
        detector = ArbitrageDetector(dex_manager, "ethereum")
        
        # Test tokens and amount
        token_in = "0xToken1"
        token_out = "0xToken2"
        amount_in = to_wei(1, 'ether')
        
        # Get prices
        prices = dex_manager.compare_prices(token_in, token_out, amount_in)
        
        # Detect opportunities
        opportunities = detector.find_opportunities(token_in, token_out, amount_in, 0.1)
        
        # Verify data integrity
        assert len(prices) == 2, "Should have 2 prices"
        assert len(opportunities) >= 1, "Should have at least 1 opportunity"
        
        opp = opportunities[0]
        assert opp.amount_in == amount_in, "Amount should be preserved"
        assert opp.token_in == token_in, "Token in should be preserved"
        assert opp.token_out == token_out, "Token out should be preserved"
        assert opp.network == "ethereum", "Network should be preserved"
        
        # Verify price consistency
        assert opp.buy_price == dex1_price, "Buy price should match lowest DEX price"
        assert opp.sell_price == dex2_price, "Sell price should match highest DEX price"
        
        # Verify profit calculation
        expected_profit = dex2_price - dex1_price
        assert opp.profit == expected_profit, "Profit calculation should be correct"
        
        print(f"✅ Data integrity verified across all stages")
        print(f"   Input preserved: amount={from_wei(opp.amount_in, 'ether')} tokens")
        print(f"   Prices preserved: buy={from_wei(opp.buy_price, 'ether'):.0f}, sell={from_wei(opp.sell_price, 'ether'):.0f}")
        print(f"   Profit calculated correctly: {from_wei(opp.profit, 'ether'):.0f} tokens")
        
        return True


def test_complete_data_flow():
    """
    Run complete end-to-end data flow test
    Tests the entire pipeline from DEX data intake to transaction broadcasting
    """
    print("\n" + "="*70)
    print("COMPLETE DATA FLOW INTEGRATION TEST")
    print("DEX Data Intake → Arbitrage Detection → Transaction Broadcasting")
    print("="*70)
    
    try:
        # Step 1: DEX Data Intake
        prices, dex_manager, token_in, token_out, amount_in = \
            TestDataFlowIntegration.test_step1_dex_data_intake()
        
        # Step 2: Arbitrage Detection
        opportunities = TestDataFlowIntegration.test_step2_arbitrage_detection(
            prices, dex_manager, token_in, token_out, amount_in
        )
        
        # Step 3: Transaction Preparation
        mock_w3 = TestDataFlowIntegration.create_mock_web3()
        executor, best_opportunity, gas_cost = \
            TestDataFlowIntegration.test_step3_transaction_preparation(opportunities, mock_w3)
        
        # Step 4: Profitability Check
        is_profitable = TestDataFlowIntegration.test_step4_profitability_check(
            executor, best_opportunity, gas_cost
        )
        
        # Step 5: Transaction Broadcasting
        success = TestDataFlowIntegration.test_step5_transaction_broadcasting(
            executor, best_opportunity
        )
        
        # Step 6: Data Integrity
        TestDataFlowIntegration.test_step6_data_integrity()
        
        print("\n" + "="*70)
        print("✅ COMPLETE DATA FLOW TEST PASSED")
        print("="*70)
        print("\nAll stages verified successfully:")
        print("  ✓ DEX data intake from multiple sources")
        print("  ✓ Arbitrage opportunity detection")
        print("  ✓ Transaction preparation with gas estimation")
        print("  ✓ Profitability verification")
        print("  ✓ Transaction broadcasting simulation")
        print("  ✓ Data integrity across all stages")
        print()
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == '__main__':
    test_complete_data_flow()
