# Changelog - Enhanced Features Release

## 🎉 Version 2.1 - Portfolio Value History Tables

**Release Date**: October 29, 2025

### 📊 **New Portfolio History Feature**

#### Portfolio Value Tracking
- **Purpose**: Track portfolio value evolution over time using historical price data
- **Data Source**: Local price history stored in `data/price_history/`
- **Implementation**: `calculate_portfolio_value_history()` and `generate_portfolio_table()` in `src/price_history.py`
- **Storage**: 30 days of hourly price data per coin

#### Clean Table Visualization
- **Display**: Professional table format optimized for Telegram
- **Performance Summary**: Start/end values, change %, high/low, average, volatility
- **Key Data Points**: Timestamped values with percentage changes
- **Smart Sampling**: More frequent data points for shorter periods
- **Indicators**: 📈 for gains, 📉 for losses

#### Telegram Bot Integration
- **Auto-include**: `/portfolio` command now includes 7-day history automatically
- **Dedicated Command**: `/history [period]` for custom time periods
  - `/history 24h` - Last 24 hours
  - `/history 3d` - Last 3 days
  - `/history 7d` - Last 7 days (default)
  - `/history 30d` - Last 30 days
- **Performance**: < 1 second generation, no API calls needed

#### Documentation
- **Updated**: README.md and TELEGRAM_BOT.md with history feature info
- **Updated**: BOT_CHEATSHEET.txt with history command

### 🔧 **Technical Improvements**
- Efficient portfolio value calculation using existing price history
- No additional API calls required
- Automatic data retention (30 days)
- Graceful handling of missing data

---

## 🎉 Version 2.0 - Advanced Technical Indicators & Enhanced Exit Strategy

**Release Date**: July 25, 2025

### 📊 **New Technical Indicators**

#### Pi Cycle Top Indicator
- **Purpose**: Historical Bitcoin cycle top detection using 111-day SMA vs 2x 350-day SMA
- **Accuracy**: Successfully identified every major BTC top since 2011
- **Implementation**: `calculate_pi_cycle_top()` in `src/indicators.py`
- **Configuration**: Enable with `enable_pi_cycle: true` in config

#### 3-Line RCI (Rank Correlation Index)
- **Purpose**: Advanced trend analysis with periods [9, 26, 52]
- **Signals**: STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
- **Implementation**: `calculate_rci_3_line()` in `src/indicators.py`
- **Configuration**: Enable with `enable_rci: true` in config

### 🎯 **Enhanced Exit Strategy**

#### Partial Exit System
- **Risk Score 60-74**: Sell 10% (Moderate Risk)
- **Risk Score 75-84**: Sell 25% (High Risk)
- **Risk Score 85+**: Sell 50% (Critical Risk)

#### Risk Scoring Factors
- Pi Cycle Top proximity and triggers
- BTC RSI overbought levels
- RCI trend exhaustion signals
- Altseason peak detection
- Fear & Greed extreme readings

### 🌟 **Improved Altseason Detection**

#### Multi-Factor Analysis
- **BTC Dominance**: Multiple threshold analysis
- **ETH/BTC Ratio**: Leading altseason indicator
- **Cross-Asset Momentum**: ETH vs BTC performance
- **Phase Detection**: 5 distinct market phases

### ⚙️ **Configuration Changes**

#### New Configuration Sections
```yaml
indicators:
  enable_pi_cycle: true
  enable_rci: true
  rci_periods: [9, 26, 52]

partial_exit:
  enabled: true
  risk_thresholds:
    moderate: 60
    high: 75
    critical: 85

altseason_detection:
  enhanced: true
```

### 🧪 **Testing & Quality**

#### Test Coverage
- `tests/test_new_indicators.py` - Pi Cycle Top & RCI tests
- `tests/test_partial_exit_strategy.py` - Exit strategy tests
- **12/12 tests passing** ✅

#### Demo Scripts
- `demo_enhanced_features.py` - Complete feature demonstration
- `test_new_features.py` - Integration testing
- `simple_test.py` - Core logic validation

### 🔧 **System Improvements**

#### Enhanced Connection Testing
- Separate Binance and CoinGecko API testing
- Improved `run.py --test` functionality
- Better error reporting and status feedback

#### Bug Fixes
- Fixed malformed coin entries in config.yaml
- Corrected missing 'symbol' field validation
- Improved error handling in indicator calculations

### 📚 **Documentation Updates**

#### Updated Files
- `docs/PROJECT_SUMMARY.md` - Complete feature overview
- `docs/ADVANCED.md` - Configuration examples
- `README.md` - Updated feature list
- `docs/CHANGELOG.md` - This file

### 🚀 **Production Ready**

#### Key Benefits
- Earlier risk detection with Pi Cycle Top
- Better position management with partial exits
- Improved market timing with enhanced altseason detection
- Comprehensive risk scoring (0-100 scale)
- Multiple converging signals to reduce false positives

#### Backward Compatibility
- All new features are optional and configurable
- Existing functionality remains unchanged
- Enhanced Telegram messages include new data
- Strategic advisor incorporates new risk factors

---

### 📋 **Migration Guide**

To use the new features:

1. **Update Configuration**: Add new indicator sections to `config/config.yaml`
2. **Test System**: Run `python run.py --test` to verify all connections
3. **Enable Features**: Set `enable_pi_cycle: true` and `enable_rci: true`
4. **Configure Exits**: Adjust `partial_exit` thresholds as needed
5. **Monitor Results**: Watch for new indicator data in Telegram alerts

### 🎯 **Next Steps**

1. Monitor performance of new indicators
2. Fine-tune risk thresholds based on market conditions
3. Consider adding volume-based indicators
4. Expand partial exit strategy with more granular levels

---

**Happy Trading! 🚀📈**
