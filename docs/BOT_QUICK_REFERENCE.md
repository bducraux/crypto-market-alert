# 🤖 Telegram Bot - Quick Reference

## Available Commands

### 📊 Portfolio Commands
| Command | Description | Response Time |
|---------|-------------|---------------|
| `/portfolio` | Full detailed portfolio report with all coins, P&L, and goals | ~3-5 sec |
| `/summary` | Quick snapshot of total value and main positions | ~2-3 sec |
| `/prices` | Current prices of all your coins with change since last read | ~2-3 sec |

### 🎯 Goal & Coin Commands
| Command | Description | Response Time |
|---------|-------------|---------------|
| `/goals` | Progress toward BTC/ETH accumulation targets | ~2-3 sec |
| `/btc` | Bitcoin price, holdings, value, and P&L | ~1-2 sec |
| `/eth` | Ethereum price, holdings, value, and P&L | ~1-2 sec |

### 🌍 Market Commands
| Command | Description | Response Time |
|---------|-------------|---------------|
| `/market` | Market overview: dominance, F&G index, market phase | ~2-3 sec |

### ℹ️ Help Commands
| Command | Description |
|---------|-------------|
| `/start` | Welcome message and command list |
| `/help` | Show all available commands |

---

## 📱 Example Outputs

### `/summary` - Quick Overview
```
💼 PORTFOLIO SUMMARY

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

### `/prices` - Price Check
Shows current prices with change since your last price check.
```
💵 CURRENT PRICES
Change since last read

🟢 BTC: $76,123.45 (+2.34%)
🟢 ETH: $2,408.67 (+3.12%)
🟢 BNB: $598.23 (+1.45%)
🔴 LINK: $14.56 (-0.87%)
🟢 POL: $0.456 (+5.23%)
```

### `/btc` - Bitcoin Details
```
₿ BITCOIN (BTC)

💵 Current Price: $76,123.45
🟢 24h Change: +2.34%

📊 Your Holdings:
   Amount: 0.54163911 BTC
   Value: $41,234.56
   Avg Buy: $18,355.27
🟢 P&L: +314.8% (+$38,289.67)
```

### `/market` - Market Overview
```
🌍 MARKET OVERVIEW

🌟 ALTSEASON ACTIVE

📊 Market Metrics:
   BTC Dominance: 42.34%
   ETH/BTC Ratio: 0.031623

😊 Fear & Greed Index:
   Value: 65/100
   Status: Greed
```

---

## 🎯 Use Cases

### Morning Routine
1. `/summary` - Quick portfolio check
2. `/market` - Market sentiment check

### Price Alerts
- Get notified from main alert system
- Use `/prices` to verify
- Use `/btc` or `/eth` for specific coins

### Decision Making
1. `/goals` - Check progress toward targets
2. `/portfolio` - Full analysis with P&L
3. `/market` - Market context

### During Bull Run
- Frequent `/prices` checks
- `/market` to monitor F&G and dominance
- `/goals` to see how close to targets

### During Bear Market
- `/btc` and `/eth` to track accumulation prices
- `/goals` to see remaining target
- Less frequent checks (avoid panic)

---

## ⚡ Pro Tips

1. **Bookmark Commands**: Pin `/summary` and `/market` in Telegram
2. **Use Notifications**: Enable Telegram notifications for instant responses
3. **Multiple Checks**: Commands are fast, check as often as you like
4. **Combine with Alerts**: Bot is for on-demand, alerts notify you automatically
5. **Update Config**: Keep `avg_price` updated in `config.yaml` for accurate P&L

---

## 🔐 Security

- ✅ Only your authorized Chat ID can use the bot
- ✅ No data is stored outside your machine
- ✅ Bot token is kept in `.env` (never committed to git)
- ✅ Service runs with your user permissions only

---

## 🛠️ Service Management Cheatsheet

```bash
# Start
sudo systemctl start crypto-bot.service

# Stop
sudo systemctl stop crypto-bot.service

# Restart
sudo systemctl restart crypto-bot.service

# Status
sudo systemctl status crypto-bot.service

# Logs (live)
sudo journalctl -u crypto-bot.service -f

# Logs (last 100 lines)
sudo journalctl -u crypto-bot.service -n 100

# Enable auto-start
sudo systemctl enable crypto-bot.service

# Disable auto-start
sudo systemctl disable crypto-bot.service
```

---

## 📚 More Information

- **Full Documentation**: [docs/TELEGRAM_BOT.md](TELEGRAM_BOT.md)
- **Setup Guide**: Run `./scripts/setup_bot.sh`
- **Installation**: Run `./scripts/install_bot_service.sh`
- **Troubleshooting**: Check service logs with `journalctl`

---

## 🎉 Quick Start Reminder

```bash
# 1. Setup (interactive)
./scripts/setup_bot.sh

# 2. Install as service
./scripts/install_bot_service.sh

# 3. Send /start to your bot
# Done! 🚀
```

---

Made with ❤️ for crypto portfolio tracking

