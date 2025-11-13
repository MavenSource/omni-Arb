"""
Multi-Hop Routing System for Advanced Arbitrage Opportunities
Supports 2-4 hop arbitrage paths across multiple DEXes
"""

import asyncio
import itertools
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

from src.utils.logger import logger
from src.utils.web3_utils import to_wei, from_wei


@dataclass
class SwapStep:
    """Single swap step in a multi-hop route"""
    dex: str
    token_in: str
    token_out: str
    amount_in: Decimal
    amount_out: Decimal
    price: Decimal
    fee: Decimal
    slippage_percent: float


@dataclass
class MultiHopRoute:
    """Complete multi-hop arbitrage route"""
    route_id: str
    token_path: List[str]
    dex_path: List[str]
    hops: int
    steps: List[SwapStep]
    initial_amount: Decimal
    final_amount: Decimal
    total_fees: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    profit_percent: float
    gas_estimate: int
    confidence: float
    timestamp: datetime


class MultiHopRouter:
    """
    Advanced multi-hop routing system for finding optimal arbitrage paths
    """
    
    def __init__(self, dex_manager, price_fetcher, config: Optional[Dict] = None):
        """
        Initialize multi-hop router
        
        Args:
            dex_manager: DEX manager instance
            price_fetcher: Price fetcher instance
            config: Optional configuration dictionary
        """
        self.dex_manager = dex_manager
        self.price_fetcher = price_fetcher
        self.config = config or {}
        self.max_hops = self.config.get('max_hops', 3)
        self.min_profit_threshold = Decimal(str(self.config.get('min_profit_usd', 50)))
        self.routes_cache = []
        logger.info(f"Multi-Hop Router initialized (max hops: {self.max_hops})")
    
    async def find_profitable_routes(
        self,
        start_token: str,
        end_token: str,
        amount: Decimal,
        max_hops: Optional[int] = None
    ) -> List[MultiHopRoute]:
        """
        Find all profitable multi-hop routes
        
        Args:
            start_token: Starting token address
            end_token: Ending token address  
            amount: Amount to trade
            max_hops: Maximum number of hops (default: from config)
            
        Returns:
            List of profitable routes sorted by net profit
        """
        max_hops = max_hops or self.max_hops
        logger.info(f"Scanning for {max_hops}-hop routes: {start_token} -> {end_token}")
        
        all_routes = []
        
        # Find 2-hop routes
        if max_hops >= 2:
            routes_2hop = await self._find_2hop_routes(start_token, end_token, amount)
            all_routes.extend(routes_2hop)
        
        # Find 3-hop routes
        if max_hops >= 3:
            routes_3hop = await self._find_3hop_routes(start_token, end_token, amount)
            all_routes.extend(routes_3hop)
        
        # Find 4-hop routes
        if max_hops >= 4:
            routes_4hop = await self._find_4hop_routes(start_token, end_token, amount)
            all_routes.extend(routes_4hop)
        
        # Filter profitable routes
        profitable_routes = [
            route for route in all_routes 
            if route.net_profit > self.min_profit_threshold
        ]
        
        # Sort by net profit
        profitable_routes.sort(key=lambda x: x.net_profit, reverse=True)
        
        logger.info(f"Found {len(profitable_routes)} profitable routes")
        return profitable_routes
    
    async def _find_2hop_routes(
        self,
        token_in: str,
        token_out: str,
        amount: Decimal
    ) -> List[MultiHopRoute]:
        """Find 2-hop routes with intermediate token"""
        routes = []
        
        # Get available tokens as intermediates
        available_tokens = self.dex_manager.get_available_tokens()
        intermediate_tokens = [
            t for t in available_tokens 
            if t not in [token_in, token_out]
        ][:10]  # Limit to top 10
        
        # Try each DEX combination
        dexes = self.dex_manager.get_available_dexes()
        
        for intermediate in intermediate_tokens:
            for dex1, dex2 in itertools.product(dexes, repeat=2):
                try:
                    # Step 1: token_in -> intermediate
                    price1 = await self._get_swap_quote(dex1, token_in, intermediate, amount)
                    if not price1:
                        continue
                    
                    mid_amount = price1['amount_out']
                    fee1 = price1['fee']
                    
                    # Step 2: intermediate -> token_out
                    price2 = await self._get_swap_quote(dex2, intermediate, token_out, mid_amount)
                    if not price2:
                        continue
                    
                    final_amount = price2['amount_out']
                    fee2 = price2['fee']
                    
                    # Calculate profitability
                    total_fees = fee1 + fee2
                    gross_profit = final_amount - amount
                    net_profit = gross_profit - total_fees
                    profit_percent = float((net_profit / amount) * 100)
                    
                    if net_profit > Decimal('10'):  # Minimum $10 profit threshold
                        route = MultiHopRoute(
                            route_id=f"2hop_{token_in}_{intermediate}_{token_out}",
                            token_path=[token_in, intermediate, token_out],
                            dex_path=[dex1, dex2],
                            hops=2,
                            steps=[
                                SwapStep(
                                    dex=dex1,
                                    token_in=token_in,
                                    token_out=intermediate,
                                    amount_in=amount,
                                    amount_out=mid_amount,
                                    price=price1['price'],
                                    fee=fee1,
                                    slippage_percent=0.3
                                ),
                                SwapStep(
                                    dex=dex2,
                                    token_in=intermediate,
                                    token_out=token_out,
                                    amount_in=mid_amount,
                                    amount_out=final_amount,
                                    price=price2['price'],
                                    fee=fee2,
                                    slippage_percent=0.3
                                )
                            ],
                            initial_amount=amount,
                            final_amount=final_amount,
                            total_fees=total_fees,
                            gross_profit=gross_profit,
                            net_profit=net_profit,
                            profit_percent=profit_percent,
                            gas_estimate=250000,
                            confidence=0.85,
                            timestamp=datetime.now()
                        )
                        routes.append(route)
                
                except Exception as e:
                    logger.debug(f"Error evaluating 2-hop route: {e}")
                    continue
        
        logger.info(f"Found {len(routes)} profitable 2-hop routes")
        return routes
    
    async def _find_3hop_routes(
        self,
        token_in: str,
        token_out: str,
        amount: Decimal
    ) -> List[MultiHopRoute]:
        """Find 3-hop routes (triangle arbitrage)"""
        routes = []
        
        available_tokens = self.dex_manager.get_available_tokens()
        other_tokens = [t for t in available_tokens if t not in [token_in, token_out]][:8]
        
        dexes = self.dex_manager.get_available_dexes()[:3]  # Top 3 DEXes
        
        # Try combinations of 2 intermediate tokens
        for int1, int2 in itertools.permutations(other_tokens, 2):
            for dex in dexes:
                try:
                    current_amount = amount
                    steps = []
                    total_fees = Decimal('0')
                    
                    # Execute 3-hop path
                    for next_token in [int1, int2, token_out]:
                        quote = await self._get_swap_quote(
                            dex,
                            steps[-1].token_out if steps else token_in,
                            next_token,
                            current_amount
                        )
                        
                        if not quote:
                            break
                        
                        steps.append(SwapStep(
                            dex=dex,
                            token_in=steps[-1].token_out if steps else token_in,
                            token_out=next_token,
                            amount_in=current_amount,
                            amount_out=quote['amount_out'],
                            price=quote['price'],
                            fee=quote['fee'],
                            slippage_percent=0.3
                        ))
                        
                        total_fees += quote['fee']
                        current_amount = quote['amount_out']
                    
                    if len(steps) == 3:
                        final_amount = current_amount
                        gross_profit = final_amount - amount
                        net_profit = gross_profit - total_fees
                        profit_percent = float((net_profit / amount) * 100)
                        
                        if net_profit > Decimal('20'):
                            route = MultiHopRoute(
                                route_id=f"3hop_{token_in}_{int1}_{int2}_{token_out}",
                                token_path=[token_in, int1, int2, token_out],
                                dex_path=[dex] * 3,
                                hops=3,
                                steps=steps,
                                initial_amount=amount,
                                final_amount=final_amount,
                                total_fees=total_fees,
                                gross_profit=gross_profit,
                                net_profit=net_profit,
                                profit_percent=profit_percent,
                                gas_estimate=350000,
                                confidence=0.75,
                                timestamp=datetime.now()
                            )
                            routes.append(route)
                
                except Exception as e:
                    logger.debug(f"Error evaluating 3-hop route: {e}")
                    continue
        
        logger.info(f"Found {len(routes)} profitable 3-hop routes")
        return routes
    
    async def _find_4hop_routes(
        self,
        token_in: str,
        token_out: str,
        amount: Decimal
    ) -> List[MultiHopRoute]:
        """Find 4-hop routes (quadrangle arbitrage)"""
        routes = []
        
        available_tokens = self.dex_manager.get_available_tokens()
        other_tokens = [t for t in available_tokens if t not in [token_in, token_out]][:5]
        
        dexes = self.dex_manager.get_available_dexes()[:2]  # Top 2 DEXes
        
        # Try combinations of 3 intermediate tokens (limited due to complexity)
        for combo in itertools.permutations(other_tokens, 3):
            int1, int2, int3 = combo
            for dex in dexes:
                try:
                    current_amount = amount
                    steps = []
                    total_fees = Decimal('0')
                    
                    # Execute 4-hop path
                    for next_token in [int1, int2, int3, token_out]:
                        quote = await self._get_swap_quote(
                            dex,
                            steps[-1].token_out if steps else token_in,
                            next_token,
                            current_amount
                        )
                        
                        if not quote:
                            break
                        
                        steps.append(SwapStep(
                            dex=dex,
                            token_in=steps[-1].token_out if steps else token_in,
                            token_out=next_token,
                            amount_in=current_amount,
                            amount_out=quote['amount_out'],
                            price=quote['price'],
                            fee=quote['fee'],
                            slippage_percent=0.3
                        ))
                        
                        total_fees += quote['fee']
                        current_amount = quote['amount_out']
                    
                    if len(steps) == 4:
                        final_amount = current_amount
                        gross_profit = final_amount - amount
                        net_profit = gross_profit - total_fees
                        profit_percent = float((net_profit / amount) * 100)
                        
                        if net_profit > Decimal('30'):
                            route = MultiHopRoute(
                                route_id=f"4hop_{token_in}_{int1}_{int2}_{int3}_{token_out}",
                                token_path=[token_in, int1, int2, int3, token_out],
                                dex_path=[dex] * 4,
                                hops=4,
                                steps=steps,
                                initial_amount=amount,
                                final_amount=final_amount,
                                total_fees=total_fees,
                                gross_profit=gross_profit,
                                net_profit=net_profit,
                                profit_percent=profit_percent,
                                gas_estimate=450000,
                                confidence=0.65,
                                timestamp=datetime.now()
                            )
                            routes.append(route)
                
                except Exception as e:
                    logger.debug(f"Error evaluating 4-hop route: {e}")
                    continue
        
        logger.info(f"Found {len(routes)} profitable 4-hop routes")
        return routes
    
    async def _get_swap_quote(
        self,
        dex: str,
        token_in: str,
        token_out: str,
        amount_in: Decimal
    ) -> Optional[Dict]:
        """
        Get swap quote from a specific DEX
        
        Returns:
            Dictionary with amount_out, price, fee, or None if unavailable
        """
        try:
            # This would integrate with your existing DEX manager
            # For now, returning a placeholder structure
            dex_instance = self.dex_manager.get_dex(dex)
            if not dex_instance:
                return None
            
            # Get quote from DEX
            amount_out = await dex_instance.get_amount_out(token_in, token_out, amount_in)
            
            if not amount_out or amount_out <= 0:
                return None
            
            # Calculate effective price and fee
            price = amount_out / amount_in if amount_in > 0 else Decimal('0')
            fee = amount_in * Decimal('0.003')  # 0.3% typical fee
            
            return {
                'amount_out': amount_out,
                'price': price,
                'fee': fee
            }
        
        except Exception as e:
            logger.debug(f"Error getting swap quote: {e}")
            return None
