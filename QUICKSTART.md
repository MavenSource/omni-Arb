# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MavenSource/omni-Arb.git
cd omni-Arb
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Verification

### Run Tests

```bash
pytest tests/ -v
```

Expected output: All 25 tests should pass.

### Run the System

```bash
python main.py
```

Expected output: System status display showing all components initialized.

## Configuration

### Basic Configuration

Edit `config/system_config.json` to configure:

```json
{
  "profit_targets": {
    "daily_target": 33333,
    "monthly_target": 1000000
  },
  "risk_management": {
    "max_drawdown": 0.05,
    "min_success_rate": 0.95
  }
}
```

### Blockchain Configuration

**⚠️ Important**: Before running on mainnet, update RPC endpoints in `config/system_config.json`:

```json
{
  "chains": {
    "ethereum": {
      "enabled": true,
      "rpc_url": "YOUR_ETHEREUM_RPC_URL"
    }
  }
}
```

## Usage Examples

### Check System Status

```python
from src.python.system_architecture import SystemArchitecture

system = SystemArchitecture()
status = system.get_status()
print(status)
```

### Monitor Opportunities

```python
import asyncio
from src.python.ultra_low_latency_engine import UltraLowLatencyEngine

async def monitor():
    engine = UltraLowLatencyEngine()
    opportunities = await engine.detect_opportunities()
    print(f"Found {len(opportunities)} opportunities")

asyncio.run(monitor())
```

### Check Risk Assessment

```python
import asyncio
from src.python.risk_manager import AdvancedRiskManager

async def assess_risk():
    manager = AdvancedRiskManager()
    
    opportunity = {
        'dex': 'uniswap',
        'trade_size': 50000,
        'token_pair': 'ETH/USDC',
        'pool': {'size': 500000}
    }
    
    assessment = await manager.assess_opportunity_risk(opportunity)
    print(f"Risk Score: {assessment['risk_score']}")
    print(f"Action: {assessment['recommended_action']}")

asyncio.run(assess_risk())
```

## Development Workflow

### 1. Make Changes

Edit files in `src/python/`

### 2. Run Tests

```bash
pytest tests/ -v
```

### 3. Check Code Style

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/
```

### 4. Run Type Checking

```bash
mypy src/python/
```

## Project Structure

```
omni-Arb/
├── src/python/              # Core Python modules
│   ├── system_architecture.py
│   ├── ultra_low_latency_engine.py
│   ├── multi_chain_coordinator.py
│   ├── ai_profit_maximizer.py
│   ├── risk_manager.py
│   ├── enterprise_infrastructure.py
│   └── profit_optimization_engine.py
├── tests/                   # Test suite
├── config/                  # Configuration files
├── main.py                  # Main entry point
└── requirements.txt         # Dependencies
```

## Common Tasks

### View System KPIs

```bash
python -c "from src.python.profit_optimization_engine import ProfitOptimizationEngine; engine = ProfitOptimizationEngine(); print(engine.get_kpis())"
```

### Check Infrastructure Status

```bash
python -c "from src.python.enterprise_infrastructure import EnterpriseInfrastructure; infra = EnterpriseInfrastructure(); print(infra.get_infrastructure_status())"
```

### Test Chain Connections

```bash
python -c "from src.python.multi_chain_coordinator import MultiChainArbitrageCoordinator; coord = MultiChainArbitrageCoordinator(); print(coord.get_chain_status())"
```

## Troubleshooting

### Tests Fail

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (should be 3.8+)
3. Try running tests individually: `pytest tests/test_system_architecture.py -v`

### Import Errors

Make sure you're in the project root directory and the virtual environment is activated.

### Configuration Issues

Verify `config/system_config.json` is valid JSON. You can check with:
```bash
python -c "import json; json.load(open('config/system_config.json'))"
```

## Next Steps

1. ✅ Installation and verification complete
2. 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design details
3. 📋 Review [ROADMAP.md](ROADMAP.md) for implementation phases
4. 🔒 Check [SECURITY.md](SECURITY.md) for security considerations
5. 🧪 Deploy to testnet for real-world testing

## Getting Help

- Review documentation in the repository
- Check existing issues on GitHub
- Open a new issue for bugs or feature requests

## Safety Reminders

⚠️ **Important Safety Notes**:
- Start with testnet environments
- Use small amounts initially
- Never commit private keys or secrets
- Conduct thorough testing before mainnet
- Understand the risks of cryptocurrency trading
- Comply with local regulations

---

**Happy Trading! 🚀**
