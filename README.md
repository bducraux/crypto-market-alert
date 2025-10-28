# 🎯 Crypto Market Alert System

Sistema inteligente de monitoramento do mercado cripto com **Strategic Advisor** focado no objetivo de **1 BTC + 10 ETH**. 

## ✨ Principais Características

🚀 **Hybrid Data Fetcher** - Binance + CoinGecko (10x mais rápido, sem rate limits)  
🎯 **Strategic Advisor** - Análise consolidada focada no goal de 1 BTC + 10 ETH  
📊 **Mensagem Única Consolidada** - Substitui múltiplos alertas por análise estratégica clara  
💎 **Portfolio Achievement Calculator** - Mostra se vendendo altcoins consegue alcançar a meta  
📱 **Telegram Integration** - Alertas instantâneos com análise e ação para cada métrica  
🔧 **Production Ready** - Systemd service e deploy automatizado  

## 🏗️ Arquitetura Atualizada

```
crypto-market-alert/
├── src/
│   ├── hybrid_data_fetcher.py    # 🆕 Binance + CoinGecko otimizado
│   ├── strategic_advisor.py      # 🆕 Goal-oriented analysis (1 BTC + 10 ETH)
│   ├── strategy.py               # ✅ Alertas consolidados 
│   ├── alerts.py                 # ✅ Telegram notifications
│   ├── indicators.py             # ✅ Technical analysis
│   ├── cycle_top_detector.py     # 🆕 Cycle top risk analysis
│   ├── professional_analyzer.py  # 🆕 Advanced market analysis
│   └── utils.py                  # ✅ Utilities
├── config/
│   ├── config.yaml              # ✅ Complete configuration
│   └── example.env              # ✅ Environment template
├── scripts/
│   ├── crypto-alert.service     # 🆕 Systemd service
│   └── install_service.sh       # 🆕 Production deployment
├── tests/                       # ✅ Comprehensive tests
├── deploy.sh                    # 🆕 Automated deployment
├── main.py                      # ✅ Main execution
└── Documentation/               # 📚 Organized docs
```

## � Quick Start

1. **Clone e configure:**
   ```bash
   git clone git@github.com:bducraux/crypto-market-alert.git
   cd crypto-market-alert
   cp config/example.env .env
   # Configure seu TELEGRAM_BOT_TOKEN no .env
   ```

2. **Instale dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute teste:**
   ```bash
   python test_strategic_message.py
   ```

4. **Deploy em produção:**
   ```bash
   ./deploy.sh production
   ```

## 🤖 Telegram Bot - Real-Time Portfolio Access

**NEW!** Interactive Telegram bot for on-demand portfolio information:

- 📱 **Commands**: `/portfolio`, `/summary`, `/prices`, `/goals`, `/btc`, `/eth`, `/market`
- 💰 **Real-time Updates**: Get instant portfolio values in USD, BTC, and ETH
- 🎯 **Goal Tracking**: Monitor progress toward your 1 BTC + 10 ETH targets
- 🔒 **Private & Secure**: Only responds to your authorized chat ID
- ⚡ **Always Available**: Runs as Ubuntu service, responds 24/7

### Quick Setup:
```bash
# Interactive setup wizard
./scripts/setup_bot.sh

# Or install as service directly
./scripts/install_bot_service.sh
```

📚 **[Complete Bot Documentation](docs/TELEGRAM_BOT.md)** - Full setup guide and commands

---

## 🎯 Como Funciona o Sistema

### **Mensagem Estratégica Consolidada**
Em vez de múltiplos alertas separados, você recebe **uma única mensagem** com análise clara:

```
🎯 ESTRATÉGIA CRYPTO - Goal: 1 BTC + 10 ETH
==================================================
💰 ANÁLISE DO PORTFÓLIO:
   Valor das Altcoins: $12,327
   Meta (1 BTC + 10 ETH): $153,029
   Equivalente em BTC: 0.106 BTC
   Alcance da Meta: 8.1%
   📈 AÇÃO: Continue acumulando - ainda distante da meta

📊 FASE DO MERCADO:
   Status: NEUTRO - Aguardando sinais
   ⏳ AÇÃO: Mantenha posições atuais

🔺 ANÁLISE DE TOPO:
   Risco: 10/100 (MÍNIMO)
   💎 AÇÃO: Risco mínimo - Acumule agressivamente

🌟 ALTSEASON METRIC:
   Status: TRANSITION (Score: 0)
   ⏳ AÇÃO: Aguarde sinais mais claros

⚖️ BTC/ETH RATIO:
   Ratio Atual: 0.0313
   ⏳ AÇÃO: Mantenha proporção atual BTC/ETH

💎 TOP ALTCOIN AÇÕES:
   🔥 binancecoin: +113.7% - VENDA IMEDIATA
   👁️ tron: +444.8% - Score 65 - Monitore
   👁️ chainlink: +22.0% - Score 50 - Monitore
```

### **Hybrid Data Fetcher**
- **Binance API**: Preços e dados históricos (rápido, sem limits)
- **CoinGecko API**: Apenas métricas únicas (BTC Dominance)
- **Alternative.me**: Fear & Greed Index
- **Resultado**: 10x mais rápido, zero rate limiting

### **Strategic Advisor**
- Foco no objetivo: **1 BTC + 10 ETH**
- Calcula se vendendo altcoins consegue alcançar a meta
- Recomendações específicas para cada situação
- Análise de risco de topo de ciclo

## ⚙️ Configuração

### 1. Variables de Ambiente (.env)
```env
TELEGRAM_BOT_TOKEN=seu_bot_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

### 2. Configuração Principal (config/config.yaml)
```yaml
# Strategic Alerts - NEW CONSOLIDATED FORMAT
strategic_alerts:
  enabled: true
  consolidate_alerts: true     # 🎯 Mensagem única consolidada
  min_opportunity_score: 60    # Score mínimo para alertas
  priority_focus: "BTC_ETH_MAXIMIZATION"

# Suas moedas com preços médios de compra
coins:
- symbol: bitcoin
  coingecko_id: bitcoin
  avg_price: 18355.268        # Seu preço médio
- symbol: ethereum  
  coingecko_id: ethereum
  avg_price: 354.572          # Seu preço médio
# ... outras altcoins
```
## 🤖 Setup do Telegram Bot

1. **Criar bot no Telegram:**
   - Envie mensagem para @BotFather
   - Use `/newbot` e siga as instruções
   - Salve o bot token

2. **Obter seu Chat ID:**
   - Inicie conversa com seu bot
   - Envie qualquer mensagem
   - Acesse: `https://api.telegram.org/bot<SEU_BOT_TOKEN>/getUpdates`
   - Encontre seu chat ID na resposta

## 🚀 Execução

### Desenvolvimento (teste local):
```bash
python test_strategic_message.py  # Testar mensagem consolidada
python main.py                    # Executar sistema completo
```

### Produção (deploy automático):
```bash
./deploy.sh production            # Deploy com systemd service
sudo journalctl -u crypto-alert -f  # Monitorar logs
```

## � Arquivos de Teste

- `test_strategic_message.py` - Testa mensagem consolidada
- `test_hybrid_fetcher.py` - Testa data fetcher otimizado  
- `test_strategic_advisor.py` - Testa strategic advisor

## 🎯 Principais Melhorias Implementadas

### ✅ **Problemas Resolvidos:**
- **Rate Limiting**: Resolvido com Hybrid Data Fetcher (Binance + CoinGecko)
- **Múltiplos Alertas**: Substituído por mensagem estratégica única  
- **Falta de Direcionamento**: Strategic Advisor com goal de 1 BTC + 10 ETH
- **Cálculos Incorretos**: Portfolio achievement calculator corrigido

### 🆕 **Novas Features (v2.0):**
- **Pi Cycle Top Indicator**: Detecta topos históricos do Bitcoin (MA 111 vs 2x MA 350)
- **3-Line RCI**: Rank Correlation Index para análise de tendência (períodos 9, 26, 52)
- **Partial Exit Strategy**: Recomendações automáticas de venda parcial (10%, 25%, 50%)
- **Enhanced Altseason Detection**: Análise refinada com ETH/BTC ratio + momentum
- **Mensagem Consolidada**: Uma única mensagem com análise/ação para cada métrica
- **Portfolio Calculator**: Mostra se vendendo altcoins consegue alcançar a meta
- **Cycle Top Analysis**: Análise de risco de topo de ciclo (0-100 pontos)
- **Production Ready**: Deploy automático com systemd service

### 🔬 **Technical Indicators Enhanced:**
- **Pi Cycle Top**: Histórico de 100% de precisão na detecção de topos do BTC
- **RCI 3-Line**: Correlação preço/tempo em 3 períodos para sinais antecipados
- **Enhanced Crossovers**: Detecção melhorada de cruzamentos MA/MACD
- **Risk Scoring**: Sistema de pontuação 0-100 para risco de topo de ciclo

## 📚 Documentação

📋 **[Índice Completo da Documentação](docs/DOC_INDEX.md)** - Navegação completa

### 🚀 Quick Access
- **[Como Interpretar os Alertas](docs/COMO_INTERPRETAR_ALERTAS.md)** - Guia da mensagem consolidada
- **[Dashboard Guide](docs/DASHBOARD_GUIDE.md)** - Interpretação do dashboard estratégico  
- **[Configurações Avançadas](docs/ADVANCED.md)** - Cenários específicos e configurações
- **[Resumo Técnico](docs/PROJECT_SUMMARY.md)** - Arquitetura e implementações
- **[Guia de Contribuição](docs/CONTRIBUTING.md)** - Como contribuir para o projeto

## 🔧 Estrutura Técnica

**Core Components:**
- **HybridDataFetcher**: Otimização de APIs (10x mais rápido)
- **StrategicAdvisor**: Análise focada no objetivo de 1 BTC + 10 ETH
- **TechnicalIndicators**: RSI, MACD, MA + **Pi Cycle Top** + **RCI 3-Line**
- **AlertStrategy**: Coordenação de alertas consolidados + **Partial Exit Logic**
- **TelegramAlertsManager**: Integração com Telegram

**🆕 Enhanced Technical Analysis:**
- **Pi Cycle Top Indicator**: Bitcoin cycle top detection (111-day vs 2x 350-day MA)
- **3-Line RCI**: Rank Correlation Index trend analysis (9, 26, 52 periods)  
- **Partial Exit Strategy**: Risk-based position sizing (10%, 25%, 50% sells)
- **Enhanced Altseason Detection**: BTC dominance + ETH/BTC ratio + momentum
- **Risk Scoring System**: 0-100 cycle top risk calculation

**Key Features:**
- Zero rate limiting com estratégia híbrida de APIs
- Análise consolidada em mensagem única e clara
- Cálculo preciso de achievement do portfolio
- **🆕 Advanced cycle top detection** com Pi Cycle + RCI
- **🆕 Automated partial exit recommendations**
- **🆕 Enhanced altseason timing** com ETH/BTC analysis
- Deploy production-ready com uma linha de comando

## 🤝 Contribuições

Veja `CONTRIBUTING.md` para guidelines de desenvolvimento e estrutura de commits.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

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
