#!/usr/bin/env python3
"""
Script para testar formatação das mensagens do Telegram
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy
from src.utils import load_config
from src.alerts import TelegramAlertsManager
from dotenv import load_dotenv

load_dotenv()

async def test_telegram_formatting():
    """Testa a formatação das mensagens do Telegram"""
    
    print("🧪 TESTANDO FORMATAÇÃO DAS MENSAGENS...")
    print("=" * 60)
    
    # Verificar se tem configuração do Telegram
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("❌ Configuração do Telegram não encontrada!")
        return
    
    # Carregar configuração
    config = load_config()
    
    # Inicializar componentes
    data_fetcher = DataFetcher(api_key=os.getenv('COINGECKO_API_KEY'))
    strategy = AlertStrategy(config)
    telegram_manager = TelegramAlertsManager(bot_token, chat_id)
    
    print("📊 Coletando dados para teste...")
    
    # Obter dados das primeiras 3 moedas para teste
    coin_ids = [coin['coingecko_id'] for coin in config['coins'][:3]]
    coin_data = data_fetcher.get_coin_market_data_batch(coin_ids)
    
    # Obter dados de mercado
    market_data = {
        'btc_dominance': data_fetcher.get_btc_dominance(),
        'eth_btc_ratio': data_fetcher.get_eth_btc_ratio(),
        'fear_greed_index': data_fetcher.get_fear_greed_index()
    }
    
    print("🚀 Gerando alertas de teste...")
    
    # Gerar alertas
    alerts = strategy.evaluate_all_alerts(coin_data, market_data)
    
    if not alerts:
        print("ℹ️  Nenhum alerta gerado para teste.")
        return
    
    print(f"📨 Enviando {len(alerts[:3])} alertas de teste para o Telegram...")
    
    # Enviar apenas os 3 primeiros alertas como teste
    for i, alert in enumerate(alerts[:3], 1):
        message = alert.get('message', 'Alerta sem mensagem')
        
        print(f"\n📤 Enviando alerta {i}:")
        print("─" * 40)
        print(f"Tipo: {alert.get('type', 'N/A')}")
        print(f"Moeda: {alert.get('coin', 'N/A')}")
        print(f"Prioridade: {alert.get('priority', 'N/A')}")
        print("\n📝 MENSAGEM (como aparecerá no Telegram):")
        print("─" * 40)
        
        # Mostrar como a mensagem aparecerá (sem formatação HTML)
        display_message = message.replace('<b>', '**').replace('</b>', '**')
        print(display_message)
        print("─" * 40)
        
        # Enviar para o Telegram
        success = await telegram_manager.send_message(message)
        
        if success:
            print("✅ Enviado com sucesso!")
        else:
            print("❌ Falha no envio!")
        
        # Pausa entre mensagens
        await asyncio.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ TESTE DE FORMATAÇÃO CONCLUÍDO!")
    print("\n📱 Verifique seu Telegram para ver como as mensagens ficaram formatadas.")
    print("\n💡 DICAS:")
    print("- Texto em **negrito** aparece destacado")
    print("- Emojis ajudam na identificação rápida")
    print("- Quebras de linha organizam a informação")
    print("- Seções claras facilitam a leitura")

if __name__ == "__main__":
    asyncio.run(test_telegram_formatting())
