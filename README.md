# Omni-Arb: Multi-Chain DeFi Arbitrage System

A sophisticated DeFi arbitrage bot that detects and executes profitable trading opportunities across multiple decentralized exchanges (DEXes) and blockchain networks.

## 🌟 Features

- **Multi-Chain Support**: Monitor arbitrage opportunities across Ethereum, BSC, and Polygon
- **Multiple DEX Integration**: Support for Uniswap V2, SushiSwap, and PancakeSwap
- **Real-time Price Monitoring**: Continuous scanning of token prices across DEXes
- **Smart Arbitrage Detection**: Automated detection of profitable price differences
- **Gas Cost Analysis**: Evaluates profitability after accounting for gas fees
- **Configurable Parameters**: Easily adjust profit thresholds, slippage, and more
- **Comprehensive Logging**: Color-coded logging for easy monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- Access to RPC endpoints for supported networks (Infura, Alchemy, or public RPCs)
- (Optional) Private key for executing trades

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MavenSource/omni-Arb.git
   cd omni-Arb
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Review and update configuration**
   ```bash
   # Edit config/config.yaml to customize settings
   ```

## ⚙️ Configuration

### Environment Variables (.env)

Create a `.env` file based on `.env.example`:

```bash
# Private key for trade execution (optional for monitoring only)
PRIVATE_KEY=your_private_key_here

# Custom RPC URLs (optional)
ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_API_KEY
BSC_RPC_URL=https://bsc-dataseed.binance.org/
POLYGON_RPC_URL=https://polygon-rpc.com

# Trading parameters
MIN_PROFIT_PCT=0.5
MAX_TRADE_USD=1000
GAS_MULTIPLIER=1.1

# Monitoring
CHECK_INTERVAL=5
LOG_LEVEL=INFO
```

### Configuration File (config/config.yaml)

The main configuration file contains:

- **Network settings**: RPC URLs and chain IDs
- **DEX configurations**: Router and factory addresses
- **Trading parameters**: Profit thresholds, slippage tolerance
- **Monitoring settings**: Check intervals and logging levels

## 📖 Usage

### Monitoring Mode (Read-Only)

Run the bot in monitoring mode to detect opportunities without executing trades:

```bash
python main.py
```

This mode:
- Connects to configured blockchain networks
- Monitors token prices across multiple DEXes
- Detects arbitrage opportunities
- Calculates potential profits
- Does NOT execute trades (safe for testing)

### Trading Mode (Requires Private Key)

To enable automatic trade execution:

1. Add your private key to the `.env` file:
   ```bash
   PRIVATE_KEY=your_private_key_here
   ```

2. Run the bot:
   ```bash
   python main.py
   ```

⚠️ **Warning**: Trading mode will execute real transactions. Start with small amounts and test thoroughly.

### Demo Mode

Run the interactive demonstration to see how the system works without blockchain connectivity:

```bash
python demo.py
```

This demo shows:
- Configuration management
- Utility functions (token conversions, profit calculations)
- Arbitrage detection logic
- Gas cost analysis

### Running Tests

Execute the test suite to verify the system:

```bash
python tests/run_tests.py
```

## 🏗️ Project Structure

```
omni-Arb/
├── src/
│   ├── core/
│   │   ├── blockchain.py      # Blockchain connection management
│   │   ├── arbitrage.py       # Arbitrage opportunity detection
│   │   └── executor.py        # Trade execution logic
│   ├── dex/
│   │   ├── base_dex.py        # Base DEX interface
│   │   ├── uniswap_v2.py      # Uniswap V2 compatible DEXes
│   │   └── dex_manager.py     # DEX management
│   ├── config/
│   │   └── config.py          # Configuration management
│   └── utils/
│       ├── logger.py          # Logging utilities
│       └── web3_utils.py      # Web3 helper functions
├── tests/
│   ├── test_config.py         # Configuration tests
│   ├── test_utils.py          # Utility function tests
│   └── run_tests.py           # Test runner
├── config/
│   └── config.yaml            # Main configuration file
├── main.py                    # Application entry point
├── demo.py                    # Interactive demonstration
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── LICENSE                   # MIT License
└── README.md                 # This file
```

## 🔧 Key Components

### 1. Blockchain Connector
Manages connections to multiple blockchain networks and provides Web3 interfaces.

### 2. DEX Manager
Handles integration with multiple decentralized exchanges, providing a unified interface for price queries.

### 3. Arbitrage Detector
Scans token prices across DEXes to identify profitable arbitrage opportunities.

### 4. Trade Executor
Executes arbitrage trades when profitable opportunities are detected (requires private key).

## 📊 How It Works

1. **Connection**: Establishes connections to configured blockchain networks
2. **DEX Initialization**: Sets up connections to multiple DEXes on each network
3. **Price Monitoring**: Continuously queries token prices across all DEXes
4. **Opportunity Detection**: Compares prices to identify arbitrage opportunities
5. **Profit Calculation**: Calculates potential profit after accounting for gas costs
6. **Execution** (optional): Executes profitable trades automatically

## 🛡️ Security Considerations

- **Never commit your private key** to version control
- Store private keys in `.env` file (already in `.gitignore`)
- Start with small trade amounts to test the system
- Use testnet for initial testing when possible
- Monitor gas prices to avoid unprofitable trades
- Review all transactions before enabling automatic execution

## ⚠️ Disclaimer

This software is provided for educational purposes only. Cryptocurrency trading carries significant risk. The authors are not responsible for any financial losses incurred through the use of this software. Always:

- Test thoroughly on testnets first
- Start with small amounts
- Understand the risks involved
- Do your own research (DYOR)
- Never invest more than you can afford to lose

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Web3.py for blockchain interactions
- Supports Uniswap V2 compatible DEXes
- Inspired by the DeFi arbitrage community

## 📞 Support

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Happy Trading! 🚀**