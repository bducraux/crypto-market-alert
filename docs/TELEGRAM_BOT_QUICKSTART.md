# 🚀 Telegram Bot - Quick Getting Started Guide

## 📱 What You're Getting

A private Telegram bot that gives you **instant access** to your crypto portfolio:
- 💰 Real-time portfolio values (USD, BTC, ETH)
- 📊 Individual coin details with P&L
- 🎯 Progress toward your 1 BTC + 10 ETH goals
- 🌍 Market insights (dominance, Fear & Greed)
- ⚡ Fast responses (2-5 seconds per command)

---

## 🎯 5-Minute Setup

### Step 1: Create Your Telegram Bot (2 minutes)

1. Open Telegram and search for: `@BotFather`
2. Send: `/newbot`
3. Enter a name: `My Crypto Portfolio Bot`
4. Enter a username: `my_crypto_portfolio_bot` (must end with `bot`)
5. **Copy the Bot Token** - looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### Step 2: Get Your Chat ID (1 minute)

1. Search for: `@userinfobot` on Telegram
2. Start the bot
3. **Copy your Chat ID** - looks like: `123456789`

### Step 3: Configure Environment (1 minute)

Run the setup wizard:

```bash
cd /home/bruno/Projects/crypto-market-alert
./scripts/setup_bot.sh
```

It will:
- ✅ Ask for your Bot Token
- ✅ Ask for your Chat ID
- ✅ Update your `.env` file
- ✅ Install dependencies
- ✅ Optionally test the bot

**OR** manually edit `.env`:

```bash
nano .env
```

Add these lines:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Save with `Ctrl+X`, `Y`, `Enter`

### Step 4: Test the Bot (1 minute)

```bash
python test_bot.py
```

This verifies:
- ✅ Credentials are correct
- ✅ Dependencies are installed
- ✅ Data fetching works
- ✅ Portfolio analysis works

If all tests pass, you're ready!

### Step 5: Install as Service (Optional)

To run the bot 24/7 automatically:

```bash
./scripts/install_bot_service.sh
```

This will:
- ✅ Create systemd service
- ✅ Enable auto-start on boot
- ✅ Start the bot immediately

---

## 🎮 Using the Bot

### First Contact

1. Open Telegram
2. Find your bot (search for the name you gave it)
3. Send: `/start`
4. You'll see the welcome message with all commands!

### Essential Commands

Start with these:

```
/summary    - Quick overview (fastest)
/portfolio  - Full detailed report
/prices     - Current prices
/market     - Market sentiment
```

### Daily Usage Examples

**Morning Check**:
```
/summary
/market
```

**During Bull Run**:
```
/prices
/goals
/btc
/eth
```

**Investment Decision**:
```
/portfolio
/market
/goals
```

---

## 🔧 Service Management

### If You Installed as Service

**Start the bot**:
```bash
sudo systemctl start crypto-bot.service
```

**Stop the bot**:
```bash
sudo systemctl stop crypto-bot.service
```

**Check if running**:
```bash
sudo systemctl status crypto-bot.service
```

**View logs** (see what's happening):
```bash
sudo journalctl -u crypto-bot.service -f
```

Press `Ctrl+C` to exit logs.

**Restart** (after config changes):
```bash
sudo systemctl restart crypto-bot.service
```

### If Running Manually

**Start**:
```bash
python telegram_bot.py
```

Keep the terminal open. Press `Ctrl+C` to stop.

---

## ⚡ Quick Troubleshooting

### Bot Not Responding?

1. **Check if running**:
   ```bash
   sudo systemctl status crypto-bot.service
   ```

2. **Check logs**:
   ```bash
   sudo journalctl -u crypto-bot.service -n 50
   ```

3. **Restart**:
   ```bash
   sudo systemctl restart crypto-bot.service
   ```

### "Unauthorized Access" Error?

Your Chat ID is wrong.

1. Get correct ID: [@userinfobot](https://t.me/userinfobot)
2. Update `.env`:
   ```bash
   nano .env
   # Update TELEGRAM_CHAT_ID=your_correct_id
   ```
3. Restart:
   ```bash
   sudo systemctl restart crypto-bot.service
   ```

### "Failed to Fetch Data" Error?

Wait 1 minute and try again. Usually API rate limits or network hiccup.

### Python Module Errors?

Install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎯 What Commands Give You

### `/summary` - Quick Snapshot
**Use when**: Quick morning check, fast overview

**Shows**:
- Total portfolio value
- BTC and ETH holdings
- Altcoins value
- Goal progress %

**Response time**: ~2 seconds

---

### `/portfolio` - Full Report
**Use when**: Making decisions, weekly review

**Shows**:
- All coins with amounts
- USD values
- BTC/ETH equivalents
- P&L for each coin
- Goal progress with bars
- How much more BTC/ETH needed

**Response time**: ~3-5 seconds

---

### `/prices` - Price Check
**Use when**: Price alerts from main system, quick verification

**Shows**:
- Current price for all your coins
- 24h change %
- Color-coded (🟢 up, 🔴 down)

**Response time**: ~2-3 seconds

---

### `/goals` - Progress Tracker
**Use when**: Planning next purchase, tracking progress

**Shows**:
- Visual progress bars
- Current vs target amounts
- USD value of holdings
- How much more needed
- Investment required

**Response time**: ~2-3 seconds

---

### `/btc` or `/eth` - Coin Details
**Use when**: Checking specific coin performance

**Shows**:
- Current price
- 24h change
- Your holdings
- Total value
- Average buy price
- P&L in % and USD

**Response time**: ~1-2 seconds

---

### `/market` - Market Context
**Use when**: Checking overall market sentiment

**Shows**:
- BTC Dominance
- ETH/BTC ratio
- Fear & Greed Index
- Market phase (Altseason/BTC Season)

**Response time**: ~2-3 seconds

---

## 📚 More Help

- **Full Documentation**: [docs/TELEGRAM_BOT.md](TELEGRAM_BOT.md)
- **Command Reference**: [docs/BOT_QUICK_REFERENCE.md](BOT_QUICK_REFERENCE.md)
- **Implementation Details**: [docs/BOT_IMPLEMENTATION_SUMMARY.md](docs/BOT_IMPLEMENTATION_SUMMARY.md)

---

## ✅ Checklist

Before asking for help, verify:

- [ ] Bot Token is correct in `.env`
- [ ] Chat ID is correct in `.env`
- [ ] Virtual environment is activated
- [ ] Dependencies are installed: `pip install -r requirements.txt`
- [ ] `test_bot.py` passes all tests
- [ ] Service is running: `sudo systemctl status crypto-bot.service`
- [ ] No errors in logs: `sudo journalctl -u crypto-bot.service -n 50`

---

## 🎉 You're All Set!

Your bot is now ready to provide **instant portfolio information** anytime you need it!

**First thing to try**: Send `/start` to your bot right now! 🚀

---

**Pro Tip**: Bookmark your bot chat in Telegram and pin `/summary` for fastest access to your portfolio! 📌

