# 📊 Price History Tracking System

## Overview

The price tracking system automatically records coin prices every hour and uses this historical data to calculate 24-hour price changes when the API doesn't provide them.

## 🎯 Why This Feature?

**Problem**: APIs don't always provide 24h price change data, especially for newly tracked coins or during API issues.

**Solution**: Track prices locally every hour in simple JSON files. After 24 hours, we can calculate our own 24h change from historical data.

## 📁 How It Works

### Components

1. **`src/price_history.py`** - Price history tracker module
   - Records prices in JSON files
   - Calculates 24h change from history
   - Enhances coin data with historical changes
   - Keeps 30 days of price history

2. **`price_tracker.py`** - Background service
   - Runs continuously
   - Tracks prices every hour (at :00)
   - Records all coin prices automatically
   - Runs as systemd service

3. **`data/price_history/`** - Storage directory
   - One JSON file per coin
   - Simple, readable format
   - Easy to inspect and backup

### Data Storage

Each coin has its own JSON file:
```
data/price_history/
├── bitcoin.json
├── ethereum.json
├── binancecoin.json
├── chainlink.json
└── ... (one file per coin)
```

**File format**:
```json
[
  {
    "timestamp": "2025-10-28T16:56:28.410092",
    "price": 113718.0
  },
  {
    "timestamp": "2025-10-28T17:00:00.123456",
    "price": 114250.5
  }
]
```

- **Timestamp**: ISO format with date and time
- **Price**: USD price at that moment
- **Retention**: Automatically keeps last 30 days

## 🚀 Services Running

You now have **3 services** running:

| Service | Purpose | Frequency |
|---------|---------|-----------|
| **crypto-alert** | Market alerts | Configurable (e.g., every 4 hours) |
| **crypto-bot** | Telegram bot commands | Real-time (on demand) |
| **crypto-price-tracker** | Price history recording | Every hour at :00 |

### Service Management

**Price Tracker**:
```bash
# Start
sudo systemctl start crypto-price-tracker.service

# Stop
sudo systemctl stop crypto-price-tracker.service

# Status
sudo systemctl status crypto-price-tracker.service

# Logs
sudo journalctl -u crypto-price-tracker.service -f

# Restart
sudo systemctl restart crypto-price-tracker.service
```

**All services**:
```bash
# Check all crypto services
systemctl list-units 'crypto-*' --all

# Status of all
sudo systemctl status crypto-alert crypto-bot crypto-price-tracker
```

## 📊 How 24h Change Is Calculated

### Priority System

1. **API Data First**: If API provides 24h change, use it
2. **Historical Data Fallback**: If API doesn't provide it, calculate from our history
3. **Graceful Degradation**: If neither available, show as 0% or N/A

### Calculation Method

```python
# Find price from 24 hours ago (within 2-hour tolerance)
price_24h_ago = get_price_24h_ago(coin_id)

# Calculate percentage change
change_pct = ((current_price - price_24h_ago) / price_24h_ago) * 100
```

### When Will It Work?

- **Immediately**: Bot will record prices when commands are used
- **After 1 hour**: First scheduled recording at top of hour
- **After 24 hours**: Full 24h change calculation available
- **After 30 days**: Complete historical dataset

## 🤖 Bot Integration

The Telegram bot now:

1. **Records prices** every time you use a command
2. **Enhances data** with historical 24h change if API missing
3. **Shows accurate** 24h changes even when API fails

**No action needed** - it works automatically!

## 📈 Data Flow

```
┌─────────────────────┐
│  Telegram Command   │ (/portfolio, /prices, etc.)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Fetch API Data     │ (Binance/CoinGecko/CMC)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Enhance with       │ (Add historical 24h change
│  Price History      │  if API doesn't provide)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Record Current     │ (Save to JSON for future)
│  Prices             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Display to User    │ (With accurate 24h change)
└─────────────────────┘
```

## 🔍 Monitoring

### Check Price History Stats

The bot logs show statistics:
```bash
sudo journalctl -u crypto-price-tracker -n 20
```

Look for:
```
✅ Tracked 18 coin prices at 2025-10-28 16:58:13
Total coins tracked: 18, Total data points: 36
```

### Inspect Price Files

```bash
# List all price history files
ls -lh data/price_history/

# View a coin's price history
cat data/price_history/bitcoin.json | jq .

# Count data points for a coin
cat data/price_history/bitcoin.json | jq '. | length'

# See latest price
cat data/price_history/bitcoin.json | jq '.[-1]'

# See price from 24h ago (if exists)
# (requires at least 24h of data)
```

### Check Disk Usage

```bash
# Check price history folder size
du -sh data/price_history/

# Expected: ~1-2KB per coin per 30 days
# Total: < 100KB for 50 coins
```

## 🛠️ Maintenance

### Automatic Cleanup

The system automatically:
- ✅ Keeps only last 30 days of data
- ✅ Removes old entries on each recording
- ✅ No manual cleanup needed

### Manual Cleanup (if needed)

```bash
# Remove all history (start fresh)
rm -rf data/price_history/*.json

# Remove specific coin
rm data/price_history/bitcoin.json

# The service will recreate files on next run
```

### Backup Price History

```bash
# Backup to archive
tar -czf price_history_backup_$(date +%Y%m%d).tar.gz data/price_history/

# Restore from backup
tar -xzf price_history_backup_20251028.tar.gz
```

## 📊 What Gets Tracked

Every hour, the service tracks:
- ✅ All coins in your `config/config.yaml`
- ✅ Current USD price
- ✅ Timestamp
- ✅ Automatic recording (no manual action needed)

**Currently tracking**: 18 coins (based on your config)

## 🎯 Benefits

1. **Reliability**: Never miss 24h change data
2. **Independence**: Don't rely 100% on API
3. **Historical**: Build your own price database
4. **Simple**: Just JSON files, easy to understand
5. **Lightweight**: Minimal disk space (~1-2KB per coin)
6. **Automatic**: Set it and forget it

## 🔧 Troubleshooting

### Price tracker not recording?

```bash
# Check if service is running
sudo systemctl status crypto-price-tracker

# Check logs for errors
sudo journalctl -u crypto-price-tracker -n 50

# Restart service
sudo systemctl restart crypto-price-tracker
```

### No 24h change showing?

**This is normal!** You need at least 24 hours of data:
- Hour 0: First recording (no 24h change yet)
- Hour 1: Second recording (no 24h change yet)
- ...
- Hour 24: Now we have 24h change! ✅

### Disk space concerns?

Very unlikely! Math:
- 1 entry per hour × 24 hours × 30 days = 720 entries
- ~100 bytes per entry × 720 = ~70KB per coin
- 50 coins × 70KB = ~3.5MB total (negligible!)

### Want to check historical changes?

```bash
# See all data for Bitcoin
cat data/price_history/bitcoin.json | jq '.'

# Count how many recordings
cat data/price_history/bitcoin.json | jq 'length'

# See price range
cat data/price_history/bitcoin.json | jq '[.[].price] | min, max'
```

## 📝 Configuration

The price tracker uses your existing `config/config.yaml`:
- Tracks all coins listed in `coins` section
- No additional configuration needed
- Uses same API clients as alert system

## 🎉 Status

✅ **System is operational!**

- Service installed: ✅
- Service running: ✅
- First prices recorded: ✅
- Bot integrated: ✅
- Hourly tracking: ✅

**Next steps**: Just wait! After 24 hours, you'll have complete 24h change data for all coins.

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `src/price_history.py` | Price tracking module |
| `price_tracker.py` | Background service script |
| `scripts/crypto-price-tracker.service` | Systemd service config |
| `data/price_history/*.json` | Price history storage |

## 🔐 Security

- Runs as your user (not root)
- Only reads/writes to `data/price_history/`
- No external connections except APIs
- Local storage only (no cloud)

---

**Summary**: Price tracking is now automatic. Your bot will have accurate 24h price changes even when APIs don't provide them. No action needed - it just works! 🚀

