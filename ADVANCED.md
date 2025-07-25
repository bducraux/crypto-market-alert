# 🔧 Configuração Avançada do Sistema

## 🎯 Strategic Alerts - Configuração Consolidada

### Configuração Principal do Strategic Advisor
```yaml
strategic_alerts:
  enabled: true
  send_daily_report: true
  consolidate_alerts: true              # 🆕 Mensagem única consolidada
  min_opportunity_score: 60             # Score mínimo para alertas de altcoins
  eth_btc_swap_confidence: "MEDIUM"     # Confiança mínima para swaps BTC/ETH
  altcoin_exit_threshold: 70            # Score mínimo para sugerir saída de altcoins
  priority_focus: "BTC_ETH_MAXIMIZATION" # Foco principal da estratégia

# Metas do Strategic Advisor  
strategic_goals:
  target_btc: 1                         # Goal: 1 BTC
  target_eth: 10                        # Goal: 10 ETH
```

### Configuração de Moedas com Preços Médios
```yaml
coins:
- symbol: bitcoin
  name: BTC
  coingecko_id: bitcoin
  avg_price: 18355.268                  # 🆕 Seu preço médio de compra
  alerts:
    price_above: 125000
    price_below: 80000
    
- symbol: ethereum
  name: ETH  
  coingecko_id: ethereum
  avg_price: 354.572                    # 🆕 Seu preço médio de compra
  alerts:
    price_above: 5000
    price_below: 2000

# Altcoins com preços médios para cálculo de P&L
- symbol: binancecoin
  name: BNB
  coingecko_id: binancecoin
  avg_price: 362.83                     # 🆕 Para calcular lucro/perda
  alerts:
    price_above: 800
    price_below: 450
```

## 🚀 Hybrid Data Fetcher - Configuração

### Otimização de APIs
```yaml
# O HybridDataFetcher não precisa de configuração adicional
# Ele automaticamente:
# - Usa Binance para preços e histórico (rápido, sem limits)
# - Usa CoinGecko apenas para BTC Dominance
# - Usa Alternative.me para Fear & Greed Index

data_fetcher:
  retry_attempts: 3                     # Tentativas de retry
  retry_delay: 2                        # Delay entre retries (segundos)
  binance_limit: 500                    # Períodos históricos do Binance
```

### Mapeamento de Moedas (Automático)
O sistema mapeia automaticamente CoinGecko ID para símbolo Binance:
```python
# Mapeamento interno (não precisa configurar)
coin_mapping = {
    'bitcoin': 'BTCUSDT',
    'ethereum': 'ETHUSDT', 
    'binancecoin': 'BNBUSDT',
    'chainlink': 'LINKUSDT',
    'ondo-finance': 'ONDOUSDT',
    # ... outros mapeamentos automáticos
}
```

## 📊 Configuração de Indicadores Técnicos

### Indicadores Padrão (Otimizados)
```yaml
indicators:
  rsi_period: 14                        # RSI padrão
  ma_short: 50                          # Média móvel curta
  ma_long: 200                          # Média móvel longa  
  macd_fast: 12                         # MACD rápido
  macd_slow: 26                         # MACD lento
  macd_signal: 9                        # Linha de sinal MACD
  
# Configuração adicional para análise de ciclo
cycle_analysis:
  lookback_days: 365                    # Análise de 1 ano
  risk_threshold: 60                    # Threshold para alto risco
```

## ⚙️ Configurações de Sistema

### Intervalos e Performance
```yaml
general:
  check_interval: 300                   # Verificação a cada 5 minutos
  data_points: 500                      # Pontos históricos (aumentado para análise)
  enable_debug_logs: false              # Logs detalhados
  max_message_length: 4096              # Limite do Telegram

# Configuração de log
logging:
  level: INFO                           # DEBUG, INFO, WARNING, ERROR
  file: "logs/crypto_alert.log"
  max_size: "10MB"
  backup_count: 5
```

### Configuração do Telegram
```yaml
telegram:
  parse_mode: "Markdown"                # Formatação das mensagens
  disable_web_page_preview: true       # Não mostrar preview de links
  timeout: 30                           # Timeout para envio de mensagens
```

## 🎯 Cenários de Configuração

### 1. Configuração Conservadora (Menos Alertas)
```yaml
strategic_alerts:
  min_opportunity_score: 80             # Score mais alto = menos alertas
  altcoin_exit_threshold: 85            # Só sugere venda com score muito alto
  eth_btc_swap_confidence: "HIGH"       # Só sugere swaps com alta confiança

general:
  check_interval: 600                   # Verifica a cada 10 minutos
```

### 2. Configuração Agressiva (Mais Alertas)  
```yaml
strategic_alerts:
  min_opportunity_score: 40             # Score mais baixo = mais alertas
  altcoin_exit_threshold: 50            # Sugere vendas mais facilmente
  eth_btc_swap_confidence: "LOW"        # Aceita swaps com baixa confiança

general:
  check_interval: 180                   # Verifica a cada 3 minutos
```

### 3. Configuração para Acumulação
```yaml
strategic_alerts:
  priority_focus: "ACCUMULATION"        # Foco em acumular
  min_opportunity_score: 30             # Mais oportunidades de entrada
  send_daily_report: true               # Relatório diário sempre

# Desativar alertas de venda temporariamente
alert_filters:
  disable_sell_signals: true            # 🆕 Só alertas de compra
  focus_on_btc_eth: true               # Foco apenas em BTC e ETH
```

## 🔧 Configurações Avançadas de Portfolio

### Estimativa de Holdings (Para Cálculo Preciso)
```yaml
# Se você quiser cálculos mais precisos, adicione as quantidades reais:
portfolio_estimation:
  method: "investment_based"            # Baseado no valor investido
  total_altcoin_investment: 15000       # Total investido em altcoins (USD)
  
# OU configure valores individuais por moeda:
portfolio_holdings:
  binancecoin: 50                       # 50 BNB
  chainlink: 1000                       # 1000 LINK
  cardano: 5000                         # 5000 ADA
  # ... outros holdings
```

### Configuração de Risk Management
```yaml
risk_management:
  max_portfolio_risk: 70                # Risco máximo antes de alertar
  cycle_top_sensitivity: "MEDIUM"       # LOW, MEDIUM, HIGH
  btc_dominance_threshold: 60           # Threshold de dominância do BTC
  
# Configuração de stop loss automático (sugestões)
stop_loss:
  enabled: true
  default_percentage: 15                # 15% de stop loss
  trailing_stop: true                   # Stop loss dinâmico
```

## 🚀 Deploy em Produção

### Configuração do Systemd Service
```bash
# Instalar serviço automaticamente
sudo ./scripts/install_service.sh

# Ou configuração manual em /etc/systemd/system/crypto-alert.service
[Unit]
Description=Crypto Market Alert System
After=network.target

[Service]
Type=simple
User=crypto-alert
WorkingDirectory=/opt/crypto-market-alert
Environment=PATH=/opt/crypto-market-alert/venv/bin
ExecStart=/opt/crypto-market-alert/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Configuração de Monitoring
```yaml
monitoring:
  health_check_interval: 60            # Verificação de saúde a cada minuto
  alert_on_errors: true                # Alertar sobre erros do sistema
  performance_logging: true            # Log de performance das APIs
  
# Alertas do sistema (opcional)
system_alerts:
  api_failures: true                    # Alertar sobre falhas de API
  memory_usage: 80                      # Alertar se uso de memória > 80%
  disk_space: 90                        # Alertar se espaço em disco < 10%
```

## 🧪 Configuração para Testes

### Modo de Desenvolvimento
```yaml
development:
  mode: "test"                          # test, staging, production
  mock_data: false                      # Usar dados mockados
  dry_run: false                        # Não enviar mensagens reais
  test_chat_id: "123456789"            # Chat ID para testes

# Configuração específica para testes
testing:
  use_sample_data: true                 # Usar dados de exemplo
  fast_intervals: true                  # Intervalos reduzidos para teste
  verbose_logging: true                 # Logs detalhados
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
