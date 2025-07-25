#!/usr/bin/env python3
"""
Teste rápido da mensagem estratégica consolidada
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config
from src.hybrid_data_fetcher import HybridDataFetcher
from src.strategic_advisor import StrategicAdvisor
from src.strategy import AlertStrategy

async def test_strategic_message():
    """Testa a geração da mensagem estratégica consolidada"""
    print("🔄 Iniciando teste da mensagem estratégica...")
    
    # Carregar configuração
    config = load_config()
    
    # Inicializar componentes
    data_fetcher = HybridDataFetcher()
    strategy = AlertStrategy(config)
    
    try:
        # Buscar dados
        print("📊 Coletando dados do mercado...")
        
        # Coletar IDs das moedas
        coin_ids = [coin['coingecko_id'] for coin in config.get('coins', [])]
        if not coin_ids:
            print("❌ Nenhuma moeda configurada")
            return
            
        # Buscar dados das moedas
        coin_data = data_fetcher.get_coin_market_data_batch(coin_ids)
        print(f"✅ Dados coletados para {len(coin_data)} moedas")
        
        # Buscar dados adicionais
        btc_dominance = data_fetcher.get_btc_dominance()
        eth_btc_ratio = data_fetcher.get_eth_btc_ratio()
        fear_greed = data_fetcher.get_fear_greed_index()
        
        # Montar estrutura de dados completa
        market_data = {
            'coins': coin_data,
            'btc_dominance': btc_dominance,
            'eth_btc_ratio': eth_btc_ratio,
            'fear_greed': fear_greed
        }
        
        # Executar análise estratégica
        print("🧠 Executando análise estratégica...")
        alerts = strategy.evaluate_all_alerts(coin_data, market_data)
        
        print(f"\n📱 Alertas gerados: {len(alerts)}")
        
        for alert in alerts:
            print(f"\n🎯 ALERTA: {alert['type']}")
            print(f"💬 Mensagem:")
            print("-" * 50)
            print(alert['message'])
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_strategic_message())
