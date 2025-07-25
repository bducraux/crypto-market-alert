# Crypto Market Alert System

A Python-based cryptocurrency market monitoring system that sends Telegram alerts based on technical indicators and custom conditions.

## 🚀 Features

- **Multi-coin monitoring**: BTC, ETH, and configurable altcoins
- **Technical indicators**: RSI, MACD, Moving Averages, BTC Dominance, ETH/BTC ratio
- **Custom price alerts**: Set specific price targets
- **Telegram notifications**: Real-time alerts when conditions are met
- **Modular design**: Clean, maintainable code structure
- **Configurable**: Easy setup via YAML configuration
- **No trading execution**: Alert-only system for manual decision making

## 📁 Project Structure

```
crypto-market-alert/
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py      # API data collection
│   ├── indicators.py        # Technical indicator calculations
│   ├── strategy.py          # Alert condition logic
│   ├── alerts.py            # Telegram notification system
│   └── utils.py             # Utility functions
├── tests/
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   ├── test_indicators.py
│   └── test_strategy.py
├── config/
│   ├── config.yaml          # Main configuration
│   └── example.env          # Environment variables template
├── logs/                    # Application logs
├── main.py                  # Main execution script
├── requirements.txt
└── README.md
```

## 🛠️ Installation

1. **Clone and navigate to the project:**
   ```bash
   cd crypto-market-alert
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp config/example.env .env
   # Edit .env with your actual values
   ```

5. **Configure the system:**
   ```bash
   # Edit config/config.yaml to customize monitoring settings
   ```

## 🔧 Configuration

### Environment Variables (.env)
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
COINGECKO_API_KEY=your_api_key_here  # Optional for free tier
```

### Main Configuration (config/config.yaml)
```yaml
coins:
  - symbol: "bitcoin"
    name: "BTC"
    alerts:
      price_above: 125000
      price_below: 80000
      rsi_oversold: 30
      rsi_overbought: 70

indicators:
  rsi_period: 14
  ma_short: 50
  ma_long: 200
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9

general:
  check_interval: 300  # seconds
  data_points: 100     # number of historical data points
```

## 🤖 Telegram Bot Setup

1. **Create a Telegram bot:**
   - Message @BotFather on Telegram
   - Send `/newbot` and follow instructions
   - Save the bot token

2. **Get your chat ID:**
   - Start a chat with your bot
   - Send a message
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

## 🚀 Usage

### Run the monitoring system:
```bash
python main.py
```

### Run tests:
```bash
pytest tests/ -v
```

### Run specific test files:
```bash
pytest tests/test_indicators.py -v
```

## 📊 Supported Indicators

- **RSI (Relative Strength Index)**: Momentum oscillator (0-100)
- **MACD**: Moving Average Convergence Divergence
- **Moving Averages**: Simple and Exponential (configurable periods)
- **BTC Dominance**: Bitcoin's market cap percentage
- **ETH/BTC Ratio**: Ethereum to Bitcoin price ratio
- **Custom Price Targets**: Set specific price levels

## 🔔 Alert Types

- **Price Alerts**: When price crosses configured thresholds
- **RSI Alerts**: Oversold/overbought conditions
- **MACD Signals**: Bullish/bearish crossovers
- **MA Crossovers**: Golden cross and death cross signals
- **Market Metrics**: BTC dominance changes, ETH/BTC ratio shifts

## 📝 Logging

All alerts and system activities are logged to:
- Console output
- `logs/crypto_alerts.log` file

## 🧪 Testing

The project includes comprehensive tests:
- Mock data for reliable testing
- Indicator calculation validation
- Alert condition testing
- API error handling

## 🔒 Security Notes

- Store sensitive data in `.env` file (never commit to git)
- Use environment variables for API keys and tokens
- The system only monitors and alerts - no trading execution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is for educational and personal use. Please respect API rate limits and terms of service.

## ⚠️ Disclaimer

This system is for informational purposes only. Always do your own research before making investment decisions. The developers are not responsible for any financial losses.
