# 🤖 Crypto Portfolio Telegram Bot

Interactive Telegram bot for real-time crypto portfolio monitoring and management.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Available Commands](#available-commands)
- [Running the Bot](#running-the-bot)
- [Service Installation](#service-installation)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This Telegram bot provides real-time access to your cryptocurrency portfolio information through simple commands. It runs as a background service on your Ubuntu machine and responds instantly to your queries, giving you on-demand portfolio updates, price checks, and market insights.

**Key Benefits:**
- 📱 **Real-time Updates**: Get instant portfolio information anytime
- 🔒 **Private & Secure**: Only responds to your authorized Telegram chat ID
- 💰 **Comprehensive Data**: Values in USD, BTC, and ETH equivalents
- 🎯 **Goal Tracking**: Monitor progress toward your BTC/ETH accumulation targets
- 🌍 **Market Context**: Fear & Greed Index, BTC dominance, and altseason indicators

---

## ✨ Features

### Portfolio Management
- **Full Portfolio Report**: Complete overview with all holdings, values, and P&L
- **Quick Summary**: Fast snapshot of total value and main positions
- **Real-time Prices**: Current prices with 24h changes for all your coins
- **Goal Progress**: Track accumulation targets for BTC and ETH

### Individual Coin Information
- **Bitcoin Details**: Price, holdings, value, and profit/loss
- **Ethereum Details**: Price, holdings, value, and profit/loss
- **All Coins Pricing**: Quick price check for your entire portfolio

### Market Insights
- **Market Overview**: BTC dominance, ETH/BTC ratio
- **Fear & Greed Index**: Current sentiment indicator
- **Market Phase Detection**: Altseason vs BTC dominance identification

---

## 🚀 Installation

### Prerequisites

1. **Telegram Bot Token** - Get it from [@BotFather](https://t.me/botfather)
2. **Telegram Chat ID** - Get it from [@userinfobot](https://t.me/userinfobot)
3. **Python Environment** - Set up with `setup.sh`

### Step 1: Create Your Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the **Bot Token** provided by BotFather
5. Choose a memorable name like "My Crypto Portfolio Bot"

### Step 2: Get Your Chat ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start the bot
3. It will show your **Chat ID** (a number like `123456789`)
4. Save this number

### Step 3: Configure Environment Variables

Add to your `.env` file:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_from_userinfobot
```

### Step 4: Install Dependencies

The bot uses the `python-telegram-bot` library. Install it:

```bash
source venv/bin/activate
pip install python-telegram-bot
```

Or add to `requirements.txt` and run:
```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuration

Your portfolio is configured in `config/config.yaml`. Make sure each coin has:

```yaml
coins:
- symbol: bitcoin
  name: BTC
  coingecko_id: bitcoin
  binance_id: BTCUSDT
  avg_price: 18355.268      # Your average buy price
  current_amount: 0.54163911 # Amount you own
  alerts:
    # ... alert settings
```

### Accumulation Goals

Set your BTC/ETH targets in `config/config.yaml`:

```yaml
strategic_alerts:
  accumulation_targets:
    btc_target: 1.0    # Target: 1 full Bitcoin
    eth_target: 10.0   # Target: 10 Ethereum
```

---

## 📱 Available Commands

### Getting Started
- `/start` - Welcome message and command list
- `/help` - Show available commands

### Portfolio Commands
- `/portfolio` - **Full detailed portfolio report**
  - All coin holdings with amounts
  - USD values and BTC/ETH equivalents
  - Profit/Loss for each position
  - Goal progress with visual progress bars
  
- `/summary` - **Quick portfolio snapshot**
  - Total portfolio value
  - Main holdings (BTC, ETH, Altcoins)
  - Goal completion percentages
  
- `/prices` - **Current prices of all your coins**
  - Real-time prices
  - 24-hour change percentage
  - Color-coded indicators (🟢/🔴)

### Goal Tracking
- `/goals` - **Progress toward accumulation targets**
  - Visual progress bars
  - Current vs target amounts
  - How much more BTC/ETH needed
  - Investment required to reach goals

### Individual Coins
- `/btc` - **Bitcoin information**
  - Current BTC price
  - Your BTC holdings and value
  - Average buy price
  - Profit/Loss in USD and %
  
- `/eth` - **Ethereum information**
  - Current ETH price
  - Your ETH holdings and value
  - Average buy price
  - Profit/Loss in USD and %

### Market Information
- `/market` - **Market overview**
  - BTC Dominance percentage
  - ETH/BTC ratio
  - Fear & Greed Index
  - Market phase (Altseason/BTC Season/Balanced)

---

## 🏃 Running the Bot

### Manual Run (Testing)

Test the bot before installing as a service:

```bash
python telegram_bot.py
```

The bot will start and listen for commands. Keep the terminal open. Test by sending `/start` to your bot on Telegram.

**Stop with:** `Ctrl+C`

### Service Installation (Recommended)

Install as a systemd service to run automatically:

```bash
./scripts/install_bot_service.sh
```

The installer will:
1. ✅ Verify your environment and credentials
2. 📝 Create the service configuration
3. 🔧 Install and enable the service
4. 🚀 Optionally start the bot immediately

---

## 🛠️ Service Management

Once installed as a service:

### Start the Bot
```bash
sudo systemctl start crypto-bot.service
```

### Stop the Bot
```bash
sudo systemctl stop crypto-bot.service
```

### Restart the Bot
```bash
sudo systemctl restart crypto-bot.service
```

### Check Status
```bash
sudo systemctl status crypto-bot.service
```

### View Logs (Real-time)
```bash
sudo journalctl -u crypto-bot.service -f
```

### View Recent Logs
```bash
sudo journalctl -u crypto-bot.service -n 100
```

### Disable Auto-start
```bash
sudo systemctl disable crypto-bot.service
```

### Enable Auto-start
```bash
sudo systemctl enable crypto-bot.service
```

---

## 🔍 Troubleshooting

### Bot Not Responding

1. **Check if service is running:**
   ```bash
   sudo systemctl status crypto-bot.service
   ```

2. **Check logs for errors:**
   ```bash
   sudo journalctl -u crypto-bot.service -n 50
   ```

3. **Verify credentials in .env:**
   ```bash
   cat .env | grep TELEGRAM
   ```

4. **Test bot manually:**
   ```bash
   python telegram_bot.py
   ```

### "Unauthorized Access" Error

This means the Chat ID doesn't match. To fix:

1. Get your correct Chat ID from [@userinfobot](https://t.me/userinfobot)
2. Update `.env` file with correct `TELEGRAM_CHAT_ID`
3. Restart the service:
   ```bash
   sudo systemctl restart crypto-bot.service
   ```

### "Failed to fetch coin data"

This usually means API issues. Check:

1. **Internet connection**
2. **API rate limits** - Wait a few minutes and try again
3. **Service logs:**
   ```bash
   sudo journalctl -u crypto-bot.service -n 50
   ```

### Service Won't Start

1. **Check service file syntax:**
   ```bash
   sudo systemctl cat crypto-bot.service
   ```

2. **Verify paths are correct:**
   - Working directory should point to your project folder
   - Python path should point to your virtualenv

3. **Check permissions:**
   ```bash
   ls -la /home/bruno/Projects/crypto-market-alert/telegram_bot.py
   ```

4. **Manual test:**
   ```bash
   cd /home/bruno/Projects/crypto-market-alert
   source venv/bin/activate
   python telegram_bot.py
   ```

### Commands Are Slow

If commands take a long time to respond:

1. **First request is always slower** - The bot needs to fetch fresh data
2. **API rate limits** - Binance/CoinGecko may throttle requests
3. **Network issues** - Check your internet connection
4. **Too many coins** - Reduce the number of coins in `config.yaml` if you have many

### Updates Not Reflecting

If you update `config.yaml` but don't see changes:

```bash
sudo systemctl restart crypto-bot.service
```

The bot reads configuration on startup.

---

## 🔐 Security Notes

1. **Keep your .env file secure** - Never commit it to version control
2. **Bot Token is sensitive** - Don't share it publicly
3. **Chat ID authorization** - Only your chat ID can use the bot
4. **Service runs as your user** - Has same permissions as your account

---

## 📊 Example Usage

### Morning Routine Check
```
You: /summary
Bot: 💼 PORTFOLIO SUMMARY
     💰 Total Value: $45,234.56
     ₿0.523456 | Ξ12.3456
     
     📊 Main Holdings:
     BTC: 0.541639 ($41,234.56)
     ETH: 7.419691 ($17,856.23)
     Altcoins: $3,144.77
     
     🎯 Goals:
     BTC: 54.2% (0.542/1.0)
     ETH: 74.2% (7.42/10.0)
```

### Quick Price Check
```
You: /prices
Bot: 💵 CURRENT PRICES
     
     🟢 BTC: $76,123.45 (+2.34%)
     🟢 ETH: $2,408.67 (+3.12%)
     🟢 BNB: $598.23 (+1.45%)
     🔴 LINK: $14.56 (-0.87%)
     ...
```

### Goal Progress Check
```
You: /goals
Bot: 🎯 ACCUMULATION GOALS
     
     ₿ BITCOIN
     [██████░░░░] 54.2%
     
     Current: 0.541639 BTC
     Target: 1.0 BTC
     Value: $41,234.56
     
     🎯 Still Need:
     ₿0.458361 BTC
     $34,889.44
     
     ─────────────────────────────
     
     Ξ ETHEREUM
     [███████░░░] 74.2%
     
     Current: 7.4197 ETH
     Target: 10.0 ETH
     Value: $17,856.23
     
     🎯 Still Need:
     Ξ2.5803 ETH
     $6,212.34
```

---

## 🤝 Integration with Alert System

The bot works alongside the main alert system (`run.py`):

- **Alert System** (`crypto-alert.service`) - Sends automatic alerts based on market conditions
- **Bot** (`crypto-bot.service`) - Responds to your commands for on-demand information

Both services can run simultaneously and independently. They use the same configuration and data sources.

---

## 📚 Additional Resources

- [Main README](../README.md) - Full project documentation
- [Configuration Guide](../docs/ADVANCED.md) - Advanced configuration options
- [Project Summary](../docs/PROJECT_SUMMARY.md) - Project overview and architecture

---

## 💡 Tips

1. **Use `/summary` frequently** - Quick overview without too much detail
2. **Set up notifications** - Telegram will notify you when bot responds
3. **Bookmark commands** - Pin `/portfolio` and `/market` for easy access
4. **Check logs regularly** - Monitor service health with `journalctl`
5. **Update avg_price** - Keep your average buy prices updated in config.yaml for accurate P&L

---

## 🆘 Need Help?

If you encounter issues:

1. Check the logs first: `sudo journalctl -u crypto-bot.service -n 100`
2. Test manually: `python telegram_bot.py`
3. Verify configuration: `cat config/config.yaml`
4. Check environment: `cat .env`

---

## 🎉 Enjoy!

You now have a private, real-time crypto portfolio assistant in your pocket! 📱💰

Send `/start` to your bot and explore the commands. Your portfolio is always just one message away!

