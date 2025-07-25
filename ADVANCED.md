# Advanced Configuration Guide

## 📊 Technical Indicators Configuration

### RSI (Relative Strength Index)
```yaml
indicators:
  rsi_period: 14  # Standard is 14 periods
```
- **Oversold**: Typically < 30 (potential buying opportunity)
- **Overbought**: Typically > 70 (potential selling signal)

### MACD (Moving Average Convergence Divergence)
```yaml
indicators:
  macd_fast: 12    # Fast EMA period
  macd_slow: 26    # Slow EMA period
  macd_signal: 9   # Signal line EMA period
```
- **Bullish Signal**: MACD line crosses above signal line
- **Bearish Signal**: MACD line crosses below signal line

### Moving Averages
```yaml
indicators:
  ma_short: 50     # Short-term MA (Golden/Death Cross)
  ma_long: 200     # Long-term MA (Golden/Death Cross)
```
- **Golden Cross**: Short MA crosses above Long MA (bullish)
- **Death Cross**: Short MA crosses below Long MA (bearish)

## 🎯 Alert Configuration Examples

### Conservative Settings (Fewer Alerts)
```yaml
coins:
  - symbol: "bitcoin"
    name: "BTC"
    coingecko_id: "bitcoin"
    alerts:
      price_above: 100000  # Only alert at major levels
      price_below: 30000
      rsi_oversold: 20     # More extreme oversold
      rsi_overbought: 80   # More extreme overbought

alert_cooldown:
  price_alert: 120        # 2 hours between price alerts
  indicator_alert: 60     # 1 hour between indicator alerts
```

### Aggressive Settings (More Alerts)
```yaml
coins:
  - symbol: "bitcoin"
    name: "BTC"
    coingecko_id: "bitcoin"
    alerts:
      price_above: 48000   # Closer to current price
      price_below: 42000
      rsi_oversold: 35     # Less extreme levels
      rsi_overbought: 65

alert_cooldown:
  price_alert: 30         # 30 minutes between alerts
  indicator_alert: 15     # 15 minutes between alerts
```

## 🌍 Market Metrics Explained

### BTC Dominance
- **High (>60%)**: Bitcoin is outperforming altcoins
- **Low (<40%)**: "Alt season" - altcoins performing well
- **Typical Range**: 40-60%

### ETH/BTC Ratio
- **High (>0.08)**: Ethereum outperforming Bitcoin
- **Low (<0.04)**: Bitcoin outperforming Ethereum
- **Typical Range**: 0.04-0.08

### Fear & Greed Index
- **0-25**: Extreme Fear (potential buying opportunity)
- **25-45**: Fear
- **45-55**: Neutral
- **55-75**: Greed
- **75-100**: Extreme Greed (potential selling signal)

## 🔄 Scheduling and Automation

### Check Intervals
```yaml
general:
  check_interval: 300  # 5 minutes (recommended)
  # check_interval: 900  # 15 minutes (conservative)
  # check_interval: 60   # 1 minute (aggressive, higher API usage)
```

### Running as Cron Job (Alternative to systemd)
```bash
# Edit crontab
crontab -e

# Add line to run every 5 minutes
*/5 * * * * cd /path/to/crypto-market-alert && ./venv/bin/python run.py --once >> logs/cron.log 2>&1
```

## 🛡️ Security Best Practices

### Environment Variables
```bash
# .env file permissions
chmod 600 .env

# Never commit .env to git
echo ".env" >> .gitignore
```

### Telegram Bot Security
1. **Restrict bot commands**: Use BotFather to disable unnecessary commands
2. **Private chat only**: Only use the bot in private chats, not groups
3. **Regular token rotation**: Regenerate bot token periodically

### API Key Management
```bash
# CoinGecko API (optional but recommended for higher limits)
COINGECKO_API_KEY=your_key_here

# Telegram (required)
TELEGRAM_BOT_TOKEN=bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id
```

## 📈 Customizing Alert Messages

### Message Templates (in src/alerts.py)
You can customize message formats by modifying the `format_alert_message` method:

```python
def format_alert_message(self, alert: Dict[str, Any]) -> str:
    # Custom message formatting logic
    message = alert.get('message', 'Unknown alert')
    
    # Add custom emojis or formatting
    if alert.get('type') == 'price_above':
        message = f"🚀🚀🚀 {message}"
    
    return message
```

## 🔍 Monitoring and Logging

### Log Levels
```yaml
logging:
  level: "DEBUG"  # Verbose logging for troubleshooting
  # level: "INFO"   # Standard logging (recommended)
  # level: "WARNING"  # Only warnings and errors
```

### Log Rotation
```yaml
logging:
  max_file_size: 10  # MB before rotation
  backup_count: 5    # Number of backup files to keep
```

### Viewing Logs
```bash
# Real-time log viewing
tail -f logs/crypto_alerts.log

# Search for specific alerts
grep "BTC" logs/crypto_alerts.log

# View systemd service logs
journalctl -u crypto-alert -f
```

## 🧪 Testing Strategies

### Backtesting Configuration
```python
# Create test data for backtesting
def create_test_scenario():
    # Simulate price movements
    dates = pd.date_range('2023-01-01', '2023-12-31', freq='H')
    prices = simulate_crypto_prices(dates)
    
    # Test alert conditions
    strategy = AlertStrategy(config)
    alerts = strategy.evaluate_all_alerts(prices, market_data)
    
    return alerts
```

### Paper Trading Integration
While this system doesn't execute trades, you can extend it for paper trading:

```python
class PaperTradingExtension:
    def __init__(self, initial_balance=10000):
        self.balance = initial_balance
        self.positions = {}
    
    def simulate_trade(self, alert):
        if alert['type'] in ['golden_cross', 'rsi_oversold']:
            # Simulate buy
            pass
        elif alert['type'] in ['death_cross', 'rsi_overbought']:
            # Simulate sell
            pass
```

## 🔧 Performance Optimization

### API Rate Limiting
```python
# Adjust rate limiting in data_fetcher.py
self.min_request_interval = 1.5  # Slower requests for free tier
self.min_request_interval = 0.5  # Faster requests with API key
```

### Memory Management
```yaml
general:
  data_points: 50   # Fewer data points for lower memory usage
  # data_points: 200  # More data points for better accuracy
```

### Concurrent Processing
```python
# Process multiple coins concurrently
async def process_coins_concurrently(self, coins):
    tasks = [self.process_coin(coin) for coin in coins]
    results = await asyncio.gather(*tasks)
    return results
```

## 🌐 Multi-Exchange Support

### Adding New Data Sources
```python
class BinanceDataFetcher(DataFetcher):
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
    
    def get_coin_price(self, symbol):
        # Implement Binance API calls
        pass
```

### Configuration for Multiple Sources
```yaml
data_sources:
  primary: "coingecko"
  fallback: ["binance", "coinbase"]
  cross_validation: true  # Compare prices across sources
```

## 📱 Advanced Telegram Features

### Inline Keyboards
```python
# Add interactive buttons to alerts
keyboard = [
    [InlineKeyboardButton("View Chart", url=f"https://www.coingecko.com/en/coins/{coin_id}")],
    [InlineKeyboardButton("Dismiss", callback_data="dismiss")]
]
reply_markup = InlineKeyboardMarkup(keyboard)
```

### Rich Media Messages
```python
# Send charts or images with alerts
async def send_chart(self, coin_id, timeframe="24h"):
    chart_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/sparkline"
    await self.bot.send_photo(chat_id=self.chat_id, photo=chart_url)
```

## 🎯 Strategy Examples

### DCA (Dollar Cost Averaging) Alerts
```yaml
strategies:
  dca:
    enabled: true
    interval: "weekly"  # Alert for weekly DCA
    price_drop_threshold: 10  # Alert on 10% drops for extra DCA
```

### Swing Trading Alerts
```yaml
strategies:
  swing_trading:
    rsi_oversold: 30
    rsi_overbought: 70
    support_resistance: true
    volume_confirmation: true
```

### HODLer Alerts
```yaml
strategies:
  hodl:
    major_levels_only: true
    long_term_ma_only: true  # Only 200 MA signals
    extreme_rsi_only: true   # Only <20 or >80 RSI
```

This advanced guide provides comprehensive customization options for power users who want to fine-tune their crypto market monitoring system.
