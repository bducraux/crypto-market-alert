#!/usr/bin/env python3
"""
Script de demonstração dos alertas profissionais
Mostra exemplos dos tipos de alertas que o sistema gera
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy
from src.utils import load_config
from dotenv import load_dotenv

load_dotenv()

async def demonstrate_professional_alerts():
    """Demonstra os alertas profissionais em ação"""
    
    print("🔍 DEMONSTRAÇÃO DOS ALERTAS PROFISSIONAIS")
    print("=" * 60)
    
    # Carregar configuração
    config = load_config()
    
    # Inicializar componentes
    data_fetcher = DataFetcher(api_key=os.getenv('COINGECKO_API_KEY'))
    strategy = AlertStrategy(config)
    
    print("📊 Coletando dados do mercado...")
    
    # Obter dados das moedas configuradas
    coin_ids = [coin['coingecko_id'] for coin in config['coins'][:5]]  # Apenas primeiras 5 para demo
    coin_data = data_fetcher.get_coin_market_data_batch(coin_ids)
    
    # Obter dados de mercado
    market_data = {
        'btc_dominance': data_fetcher.get_btc_dominance(),
        'eth_btc_ratio': data_fetcher.get_eth_btc_ratio(),
        'fear_greed_index': data_fetcher.get_fear_greed_index()
    }
    
    print(f"📈 Contexto do Mercado:")
    print(f"   BTC Dominance: {market_data['btc_dominance']:.2f}%")
    print(f"   ETH/BTC Ratio: {market_data['eth_btc_ratio']:.6f}")
    print(f"   Fear & Greed: {market_data['fear_greed_index']['value']}/100 ({market_data['fear_greed_index']['value_classification']})")
    print()
    
    # Gerar alertas
    alerts = strategy.evaluate_all_alerts(coin_data, market_data)
    
    if not alerts:
        print("ℹ️  Nenhum alerta significativo no momento.")
        return
    
    print(f"🚨 ALERTAS GERADOS ({len(alerts)}):")
    print("=" * 60)
    
    for i, alert in enumerate(alerts[:10], 1):  # Mostrar apenas top 10
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }
        
        emoji = priority_emoji.get(alert.get('priority', 'low'), '📊')
        
        print(f"\n{i}. {emoji} {alert.get('type', 'ALERTA').upper()}")
        print(f"   Moeda: {alert.get('coin', 'N/A')}")
        print(f"   Prioridade: {alert.get('priority', 'N/A').upper()}")
        
        if 'confidence' in alert:
            print(f"   Confiança: {alert['confidence']:.0f}/100")
        
        if 'signal_strength' in alert:
            strength = alert['signal_strength']
            direction = "COMPRA" if strength > 0 else "VENDA" if strength < 0 else "NEUTRO"
            print(f"   Força do Sinal: {strength:+.0f}/100 ({direction})")
        
        print(f"   📝 Mensagem: {alert.get('message', 'N/A')}")
        print(f"   🎯 Ação: {alert.get('action', 'Sem ação específica')}")
        
        if 'market_context' in alert:
            print(f"   🌍 Contexto: {alert['market_context']}")
        
        print("-" * 50)
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA")
    print("\n🎯 INTERPRETAÇÃO DOS ALERTAS:")
    print("🔴 Alta Prioridade = Ação Imediata Recomendada")
    print("🟡 Média Prioridade = Monitore de Perto") 
    print("🟢 Baixa Prioridade = Informativo")
    print("\n📊 Força do Sinal:")
    print("+60 a +100 = COMPRA FORTE")
    print("+30 a +59 = COMPRA GRADUAL") 
    print("-30 a -59 = VENDA PARCIAL")
    print("-60 a -100 = VENDA IMEDIATA")

if __name__ == "__main__":
    asyncio.run(demonstrate_professional_alerts())
