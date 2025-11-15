# Advanced Features Guide

This document describes the advanced features integrated into Omni-Arb.

## Overview

The Omni-Arb system now includes several advanced features for maximizing arbitrage profitability:

1. **Dynamic Fee Transaction Handler** - EIP-1559 gas optimization
2. **Multi-Hop Routing System** - Advanced routing with 2-4 hop paths
3. **Omni Strategy Engine** - Multi-strategy profit optimization
4. **Enhanced Arbitrage Detection** - Async support and improved efficiency

## Features

### 1. Dynamic Fee Handler

The Dynamic Fee Handler optimizes transaction costs using EIP-1559 dynamic fees.

**Key Features:**
- Automatic calculation of optimal `maxFeePerGas` and `maxPriorityFeePerGas`
- Real-time base fee monitoring
- Gas cost estimation
- Transaction building and signing

**Usage:**
```python
from src.core.dynamic_fee_handler import DynamicFeeHandler

# Initialize
fee_handler = DynamicFeeHandler(w3)

# Get optimal gas parameters
gas_params = fee_handler.get_optimal_gas_params()
print(f"Max Fee: {gas_params['maxFeePerGas']}")
print(f"Priority Fee: {gas_params['maxPriorityFeePerGas']}")

# Build transaction with optimal fees
tx = fee_handler.build_transaction(
    from_address=account.address,
    to_address=contract_address,
    data=encoded_function_call,
    value=0
)
```

### 2. Multi-Hop Router

The Multi-Hop Router finds complex arbitrage paths across multiple DEXes.

**Key Features:**
- 2-hop routes (A → B → A)
- 3-hop routes (A → B → C → A) 
- 4-hop routes (A → B → C → D → A)
- Profitability analysis with fees and slippage
- Route ranking and optimization

**Usage:**
```python
from src.core.multihop_router import MultiHopRouter

# Initialize
router = MultiHopRouter(dex_manager, price_fetcher)

# Find profitable routes
routes = await router.find_profitable_routes(
    start_token="USDC",
    end_token="WETH",
    amount=Decimal('10000'),
    max_hops=3
)

# Examine routes
for route in routes[:5]:
    print(f"Path: {' → '.join(route.token_path)}")
    print(f"Profit: ${route.net_profit:,.2f}")
    print(f"ROI: {route.profit_percent:.2f}%")
```

**Route Structure:**
- `token_path`: List of tokens in the route
- `dex_path`: List of DEXes used
- `steps`: Detailed swap information for each hop
- `net_profit`: Profit after fees and slippage
- `gas_estimate`: Estimated gas cost

### 3. Omni Strategy Engine

The Omni Strategy Engine orchestrates multiple trading strategies simultaneously.

**Key Features:**
- Multi-strategy opportunity scanning
- Risk-adjusted ranking
- Capital allocation optimization
- Portfolio management
- Performance tracking

**Supported Strategies:**
- `FLASH_ARBITRAGE` - Flash loan arbitrage
- `MULTI_HOP` - Multi-hop arbitrage routing
- `CROSS_DEX` - Cross-DEX price differences
- `LIQUIDITY_PROVISION` - Liquidity mining
- `MARKET_MAKING` - Market making

**Usage:**
```python
from src.core.strategy_engine import OmniStrategyEngine

# Initialize
engine = OmniStrategyEngine(
    arbitrage_detector,
    multihop_router,
    executor,
    initial_capital=Decimal('100000')
)

# Scan all strategies
opportunities = await engine.scan_all_opportunities()

# Rank opportunities
ranked = engine.rank_opportunities(opportunities)

# Allocate capital
allocations = engine.allocate_capital(ranked)

# Execute top opportunity
for opp, allocation in allocations.items():
    result = await engine.execute_strategy(opp, allocation)
    print(f"Success: {result['success']}, Profit: ${result['profit']}")
```

**Performance Metrics:**
```python
# Get performance summary
perf = engine.get_performance_summary()
print(f"Total Profit: ${perf['total_profit']:,.2f}")
print(f"ROI: {perf['roi_percent']:.2f}%")
print(f"Success Rate: {perf['success_rate']:.1f}%")
```

## Configuration

### Enabling Advanced Features

Edit `config/system_config.json`:

```json
{
  "advanced": {
    "use_strategy_engine": true,
    "use_multihop_routing": true,
    "use_dynamic_fees": true,
    "max_hops": 3,
    "enable_mev_protection": false
  },
  "trading": {
    "auto_execute": false,
    "min_profit_percentage": 0.5,
    "min_profit_usd": 50,
    "max_slippage_bps": 50
  },
  "risk_management": {
    "max_position_size_percent": 20,
    "max_strategy_allocation_percent": 30
  }
}
```

### Configuration Options

**Advanced Settings:**
- `use_strategy_engine`: Enable the multi-strategy engine (default: true)
- `use_multihop_routing`: Enable multi-hop route discovery (default: true)
- `use_dynamic_fees`: Enable EIP-1559 dynamic fee optimization (default: true)
- `max_hops`: Maximum number of hops in a route (2-4, default: 3)
- `enable_mev_protection`: Enable MEV protection (default: false)

**Trading Settings:**
- `auto_execute`: Automatically execute profitable opportunities (default: false)
- `min_profit_percentage`: Minimum profit percentage threshold (default: 0.5%)
- `min_profit_usd`: Minimum profit in USD (default: $50)
- `max_slippage_bps`: Maximum acceptable slippage in basis points (default: 50)

**Risk Management:**
- `max_position_size_percent`: Maximum capital per position (default: 20%)
- `max_strategy_allocation_percent`: Maximum capital per strategy (default: 30%)

## Running with Advanced Features

### Strategy Engine Mode (Recommended)

```bash
# Set strategy engine enabled in config
python main.py
```

The application will automatically use the strategy engine when `use_strategy_engine` is true in the configuration.

### Legacy Mode

To use traditional arbitrage detection without advanced features:

```json
{
  "advanced": {
    "use_strategy_engine": false
  }
}
```

## Example Output

When running with the strategy engine enabled:

```
================================================================================
Scanning ethereum with Strategy Engine
================================================================================
🔍 Found 15 total opportunities
📊 Ranked 12 high-quality opportunities

1. flash_arbitrage: Profit=$145.50, Confidence=85%, Capital=$5,000.00
2. multi_hop: Profit=$234.20, Confidence=75%, Capital=$10,000.00
3. cross_dex: Profit=$89.40, Confidence=90%, Capital=$3,000.00

✓ Execution successful! Profit: $145.50

Performance Summary:
  Total Profit: $1,245.80
  ROI: 1.25%
  Trades: 15
```

## Integration with Existing Code

The advanced features are designed to work seamlessly with existing code:

1. **Backward Compatible**: Legacy mode available when strategy engine is disabled
2. **Progressive Enhancement**: New features are opt-in via configuration
3. **Drop-in Replacement**: Enhanced modules extend existing interfaces

## Best Practices

1. **Start with Simulation**: Test with `auto_execute: false` first
2. **Monitor Performance**: Use performance metrics to track strategy effectiveness
3. **Adjust Parameters**: Tune min profit thresholds based on gas costs
4. **Risk Management**: Set appropriate position size limits
5. **Multi-Chain**: Enable multiple networks for more opportunities

## Troubleshooting

### No Opportunities Found

- Check network connectivity
- Verify DEX configurations
- Lower `min_profit_percentage` threshold
- Increase `max_hops` for more complex routes

### High Gas Costs

- Enable `use_dynamic_fees` for optimization
- Increase `min_profit_usd` threshold
- Monitor base fee during low-traffic periods

### Low Success Rate

- Check `confidence` scores in opportunities
- Verify `max_slippage_bps` settings
- Monitor execution timing

## Future Enhancements

Planned features:
- MEV bundle integration (from JavaScript modules)
- Cross-chain arbitrage
- Advanced market depth analysis
- Real-time mempool monitoring
- Flash loan optimization
- Machine learning price prediction

## Support

For issues or questions:
- Review the main README.md
- Check configuration examples
- Enable DEBUG logging for detailed information
