"""
Omni Strategy Engine - Multi-Strategy Profit Optimization
Combines multiple trading strategies for maximum profitability
"""

import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from src.utils.logger import logger


class StrategyType(Enum):
    """Available trading strategies"""
    FLASH_ARBITRAGE = "flash_arbitrage"
    MULTI_HOP = "multi_hop"
    CROSS_DEX = "cross_dex"
    LIQUIDITY_PROVISION = "liquidity_provision"
    MARKET_MAKING = "market_making"


@dataclass
class OpportunitySignal:
    """Signal for a trading opportunity"""
    strategy: StrategyType
    profit_estimate: Decimal
    confidence: float
    risk_score: float
    capital_required: Decimal
    execution_time: float
    gas_cost: Decimal
    net_profit: Decimal
    data: Dict[str, Any]
    timestamp: datetime
    
    def __hash__(self):
        """Make hashable for use as dict key"""
        return hash((self.strategy.value, str(self.timestamp), float(self.net_profit)))


class OmniStrategyEngine:
    """
    Master strategy orchestrator that manages multiple trading strategies
    and optimizes capital allocation for maximum profit
    """
    
    def __init__(
        self,
        arbitrage_detector,
        multihop_router,
        executor,
        initial_capital: Optional[Decimal] = None
    ):
        """
        Initialize omni strategy engine
        
        Args:
            arbitrage_detector: Arbitrage detection instance
            multihop_router: Multi-hop routing instance
            executor: Trade executor instance
            initial_capital: Initial capital amount
        """
        self.arbitrage_detector = arbitrage_detector
        self.multihop_router = multihop_router
        self.executor = executor
        self.capital = initial_capital or Decimal('100000')
        
        # Performance tracking
        self.total_profit = Decimal('0')
        self.trades_executed = 0
        self.success_rate = 0.0
        self.active_strategies = {}
        
        # Risk management
        self.max_position_size = self.capital * Decimal('0.2')  # 20% max per position
        self.max_daily_loss = self.capital * Decimal('0.05')  # 5% max daily loss
        self.daily_pnl = []
        
        logger.info(f"Omni Strategy Engine initialized with ${self.capital:,.2f} capital")
    
    async def scan_all_opportunities(self) -> List[OpportunitySignal]:
        """
        Scan all strategies for opportunities in parallel
        
        Returns:
            List of opportunity signals from all strategies
        """
        logger.info("Scanning all strategies for opportunities...")
        
        opportunities = []
        
        # Create scanning tasks for different strategies
        tasks = [
            self._scan_flash_arbitrage(),
            self._scan_multihop_routes(),
            self._scan_cross_dex_opportunities()
        ]
        
        # Execute scans in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect opportunities
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Strategy scan failed: {result}")
                continue
            
            if isinstance(result, list):
                opportunities.extend(result)
        
        logger.info(f"Found {len(opportunities)} total opportunities")
        return opportunities
    
    async def _scan_flash_arbitrage(self) -> List[OpportunitySignal]:
        """Scan for flash arbitrage opportunities"""
        try:
            opportunities = []
            
            # Get arbitrage opportunities from detector
            arb_opps = await self.arbitrage_detector.find_opportunities()
            
            for opp in arb_opps:
                # Calculate metrics
                profit_estimate = opp.get('profit', Decimal('0'))
                gas_cost = opp.get('gas_cost', Decimal('10'))
                net_profit = profit_estimate - gas_cost
                
                if net_profit > Decimal('20'):  # Minimum $20 profit
                    signal = OpportunitySignal(
                        strategy=StrategyType.FLASH_ARBITRAGE,
                        profit_estimate=profit_estimate,
                        confidence=0.85,
                        risk_score=0.3,
                        capital_required=opp.get('amount', Decimal('1000')),
                        execution_time=5.0,
                        gas_cost=gas_cost,
                        net_profit=net_profit,
                        data=opp,
                        timestamp=datetime.now()
                    )
                    opportunities.append(signal)
            
            logger.info(f"Found {len(opportunities)} flash arbitrage opportunities")
            return opportunities
        
        except Exception as e:
            logger.error(f"Error scanning flash arbitrage: {e}")
            return []
    
    async def _scan_multihop_routes(self) -> List[OpportunitySignal]:
        """Scan for multi-hop arbitrage opportunities"""
        try:
            opportunities = []
            
            # Get multi-hop routes
            routes = await self.multihop_router.find_profitable_routes(
                start_token="USDC",
                end_token="WETH",
                amount=Decimal('10000'),
                max_hops=3
            )
            
            for route in routes:
                signal = OpportunitySignal(
                    strategy=StrategyType.MULTI_HOP,
                    profit_estimate=route.gross_profit,
                    confidence=route.confidence,
                    risk_score=0.4,
                    capital_required=route.initial_amount,
                    execution_time=route.hops * 3.0,
                    gas_cost=Decimal(str(route.gas_estimate * 50 / 1e9)),  # Estimate gas cost
                    net_profit=route.net_profit,
                    data={'route': route},
                    timestamp=datetime.now()
                )
                opportunities.append(signal)
            
            logger.info(f"Found {len(opportunities)} multi-hop opportunities")
            return opportunities
        
        except Exception as e:
            logger.error(f"Error scanning multi-hop routes: {e}")
            return []
    
    async def _scan_cross_dex_opportunities(self) -> List[OpportunitySignal]:
        """Scan for cross-DEX arbitrage opportunities"""
        try:
            opportunities = []
            
            # This would integrate with your DEX manager
            # to find price differences across DEXes
            # Placeholder implementation
            
            logger.debug("Scanning cross-DEX opportunities...")
            return opportunities
        
        except Exception as e:
            logger.error(f"Error scanning cross-DEX opportunities: {e}")
            return []
    
    def rank_opportunities(
        self,
        opportunities: List[OpportunitySignal]
    ) -> List[OpportunitySignal]:
        """
        Rank opportunities by risk-adjusted return
        
        Args:
            opportunities: List of opportunity signals
            
        Returns:
            Ranked list of opportunities
        """
        # Calculate risk-adjusted score for each opportunity
        def score_opportunity(opp: OpportunitySignal) -> float:
            # Risk-adjusted return = (net_profit / capital_required) / risk_score * confidence
            if opp.capital_required == 0 or opp.risk_score == 0:
                return 0.0
            
            roi = float(opp.net_profit / opp.capital_required)
            risk_adjusted = (roi / opp.risk_score) * opp.confidence
            return risk_adjusted
        
        # Filter by minimum requirements
        filtered = [
            opp for opp in opportunities
            if (opp.confidence > 0.7 and 
                opp.net_profit > Decimal('20') and
                opp.capital_required <= self.max_position_size)
        ]
        
        # Sort by risk-adjusted score
        ranked = sorted(filtered, key=score_opportunity, reverse=True)
        
        logger.info(f"Ranked {len(ranked)} opportunities")
        return ranked
    
    def allocate_capital(
        self,
        opportunities: List[OpportunitySignal]
    ) -> Dict[OpportunitySignal, Decimal]:
        """
        Optimize capital allocation across opportunities
        
        Args:
            opportunities: Ranked list of opportunities
            
        Returns:
            Dictionary mapping opportunities to allocated capital
        """
        allocations = {}
        available_capital = self.capital * Decimal('0.8')  # Use 80% of capital
        
        for opp in opportunities:
            # Calculate optimal allocation
            max_allocation = min(
                self.max_position_size,
                opp.capital_required,
                available_capital
            )
            
            if max_allocation >= Decimal('100'):  # Minimum $100 position
                allocations[opp] = max_allocation
                available_capital -= max_allocation
                
                if available_capital < Decimal('100'):
                    break
        
        logger.info(f"Allocated capital to {len(allocations)} opportunities")
        return allocations
    
    async def execute_strategy(
        self,
        opportunity: OpportunitySignal,
        allocation: Decimal
    ) -> Dict[str, Any]:
        """
        Execute a specific strategy opportunity
        
        Args:
            opportunity: Opportunity signal
            allocation: Allocated capital
            
        Returns:
            Execution result dictionary
        """
        try:
            logger.info(f"Executing {opportunity.strategy.value} strategy with ${allocation:,.2f}")
            
            # Route to appropriate executor based on strategy type
            if opportunity.strategy == StrategyType.FLASH_ARBITRAGE:
                result = await self._execute_flash_arbitrage(opportunity, allocation)
            elif opportunity.strategy == StrategyType.MULTI_HOP:
                result = await self._execute_multihop(opportunity, allocation)
            else:
                result = await self._execute_generic(opportunity, allocation)
            
            # Update performance metrics
            if result.get('success'):
                self.trades_executed += 1
                profit = result.get('profit', Decimal('0'))
                self.total_profit += profit
                self.daily_pnl.append(profit)
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing strategy: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_flash_arbitrage(
        self,
        opportunity: OpportunitySignal,
        allocation: Decimal
    ) -> Dict[str, Any]:
        """Execute flash arbitrage opportunity"""
        try:
            opp_data = opportunity.data
            
            # Execute through trade executor
            result = await self.executor.execute_arbitrage(opp_data)
            
            return {
                'success': result.get('success', False),
                'profit': opportunity.net_profit if result.get('success') else Decimal('0'),
                'strategy': 'flash_arbitrage',
                'tx_hash': result.get('tx_hash')
            }
        
        except Exception as e:
            logger.error(f"Error executing flash arbitrage: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_multihop(
        self,
        opportunity: OpportunitySignal,
        allocation: Decimal
    ) -> Dict[str, Any]:
        """Execute multi-hop arbitrage opportunity"""
        try:
            route = opportunity.data.get('route')
            
            # Execute multi-hop route
            result = await self.executor.execute_multihop_route(route)
            
            return {
                'success': result.get('success', False),
                'profit': opportunity.net_profit if result.get('success') else Decimal('0'),
                'strategy': 'multi_hop',
                'tx_hash': result.get('tx_hash')
            }
        
        except Exception as e:
            logger.error(f"Error executing multi-hop: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_generic(
        self,
        opportunity: OpportunitySignal,
        allocation: Decimal
    ) -> Dict[str, Any]:
        """Execute generic opportunity"""
        logger.warning(f"No specific executor for {opportunity.strategy.value}")
        return {'success': False, 'error': 'No executor implemented'}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        roi_percent = float((self.total_profit / self.capital) * 100) if self.capital > 0 else 0.0
        
        return {
            'total_capital': float(self.capital),
            'total_profit': float(self.total_profit),
            'trades_executed': self.trades_executed,
            'success_rate': self.success_rate * 100,
            'roi_percent': roi_percent,
            'daily_pnl': float(sum(self.daily_pnl[-24:])) if self.daily_pnl else 0.0
        }
