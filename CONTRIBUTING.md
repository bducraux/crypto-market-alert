# Contributing to Crypto Market Alert

## Desenvolvimento Local

### Setup Inicial
```bash
git clone git@github.com:bducraux/crypto-market-alert.git
cd crypto-market-alert
cp config/example.env .env
# Edite o .env com suas credenciais
pip install -r requirements.txt
```

### Estrutura de Commits
Usamos emojis para facilitar a identificação do tipo de commit:

- 🎯 **Features**: Novas funcionalidades
- 🐛 **Bug Fixes**: Correções de bugs
- 📊 **Data/Analytics**: Melhorias em análise de dados
- 🚀 **Performance**: Otimizações de performance
- 📝 **Documentation**: Atualizações na documentação
- 🔧 **Configuration**: Mudanças na configuração
- 🧪 **Tests**: Adição ou correção de testes
- 🎨 **Style**: Melhorias no código (formatação, etc.)

### Workflow de Desenvolvimento

1. **Criar branch para nova feature**:
   ```bash
   git checkout -b feature/nome-da-feature
   ```

2. **Fazer commits descritivos**:
   ```bash
   git commit -m "🎯 Add new strategic analysis feature"
   ```

3. **Testar antes do push**:
   ```bash
   python test_strategic_message.py
   python test_hybrid_fetcher.py
   ```

4. **Push e Pull Request**:
   ```bash
   git push origin feature/nome-da-feature
   ```

### Configuração do Ambiente

- **Python**: 3.8+
- **APIs necessárias**: Telegram Bot Token
- **Configuração**: Copy `config/example.env` to `.env`

### Testes

- `test_strategic_message.py`: Testa mensagem consolidada
- `test_hybrid_fetcher.py`: Testa data fetcher híbrido
- `test_strategic_advisor.py`: Testa advisor estratégico

### Arquitetura

- **HybridDataFetcher**: Binance + CoinGecko para otimizar rate limits
- **StrategicAdvisor**: Análise focada no goal de 1 BTC + 10 ETH  
- **AlertStrategy**: Coordenação de alertas consolidados
- **TelegramAlertsManager**: Integração com Telegram

## Issues e Feature Requests

Use o GitHub Issues para reportar bugs ou solicitar novas features.
