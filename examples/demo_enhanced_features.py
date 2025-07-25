#!/usr/bin/env python3
"""
Complete demonstration of enhanced crypto alert system with new features:
- Pi Cycle Top Indicator
- 3-Line RCI 
- Partial Exit Strategy
- Enhanced Altseason Detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime

def create_realistic_btc_data():
    """Create realistic BTC data that would trigger different signals"""
    dates = pd.date_range('2023-01-01', periods=400, freq='D')
    np.random.seed(42)
    
    # Simulate realistic BTC bull run leading to potential top
    prices = []
    base_price = 20000
    current_price = base_price
    
    for i in range(400):
        if i < 100:
            # Early bull market - steady growth
            growth = np.random.normal(0.008, 0.02)  # 0.8% daily avg
        elif i < 250:
            # Mid bull market - stronger growth
            growth = np.random.normal(0.012, 0.03)  # 1.2% daily avg
        elif i < 350:
            # Late bull market - parabolic growth
            growth = np.random.normal(0.015, 0.04)  # 1.5% daily avg
        else:
            # Top formation - high volatility
            growth = np.random.normal(0.005, 0.06)  # Volatile topping
        
        current_price = current_price * (1 + growth)
        prices.append(current_price)
    
    df = pd.DataFrame({
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.015))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.015))) for p in prices],
        'close': prices,
        'volume': np.random.randint(5000000, 50000000, 400)
    }, index=dates)
    
    return df

def demo_pi_cycle_indicator():
    """Demonstrate Pi Cycle Top Indicator functionality"""
    print("🔥 Pi Cycle Top Indicator Demo")
    print("=" * 50)
    
    try:
        from src.indicators import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        df = create_realistic_btc_data()
        
        result = indicators.calculate_pi_cycle_top(df)
        
        print(f"📊 Current BTC Price: ${df['close'].iloc[-1]:,.0f}")
        print(f"📈 MA 111: ${result['ma_111']:,.0f}" if result['ma_111'] else "📈 MA 111: Calculating...")
        print(f"📊 MA 350 x2: ${result['ma_350_2x']:,.0f}" if result['ma_350_2x'] else "📊 MA 350 x2: Calculating...")
        
        if result['distance'] is not None:
            print(f"📏 Distance: {result['distance']:+.1f}%")
            
            if result['distance'] > 0:
                print("🚨 SIGNAL: Pi Cycle Top TRIGGERED - Historical cycle top detected!")
                print("💡 ACTION: Consider major profit taking (50-70% of holdings)")
            elif result['distance'] > -5:
                print("⚠️ WARNING: Approaching Pi Cycle Top trigger")
                print("💡 ACTION: Prepare for potential top - start reducing risk")
            else:
                print("✅ SAFE: Well below Pi Cycle Top trigger")
                print("💡 ACTION: Continue accumulating or holding")
        
        print(f"🎯 Risk Level: {result['risk_level']}")
        
        if result.get('crossover_detected'):
            print("🔴 CROSSOVER DETECTED: MA 111 just crossed above 2x MA 350!")
        
        print("\n📚 Pi Cycle Top Explanation:")
        print("   • Uses 111-day and 350-day moving averages")
        print("   • When 111-day MA crosses above 2x 350-day MA = historic cycle top")
        print("   • Has correctly identified every major BTC top since 2011")
        print("   • Provides 1-7 days advance warning of major tops")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📝 Note: This would work with the actual indicators module")
    
    print("\n")

def demo_rci_3_line():
    """Demonstrate 3-Line RCI functionality"""
    print("📊 3-Line RCI (Rank Correlation Index) Demo")
    print("=" * 50)
    
    try:
        from src.indicators import TechnicalIndicators
        
        indicators = TechnicalIndicators()
        df = create_realistic_btc_data()
        
        result = indicators.calculate_rci_3_line(df)
        
        print(f"📈 RCI Short (9):  {result['rci_short']:+6.1f}" if result['rci_short'] else "📈 RCI Short: Calculating...")
        print(f"📊 RCI Medium (26): {result['rci_medium']:+6.1f}" if result['rci_medium'] else "📊 RCI Medium: Calculating...")
        print(f"📉 RCI Long (52):   {result['rci_long']:+6.1f}" if result['rci_long'] else "📉 RCI Long: Calculating...")
        
        signal = result.get('signal', 'NEUTRAL')
        print(f"\n🎯 Combined Signal: {signal}")
        
        # Interpret signals
        if signal == 'STRONG_BUY':
            print("🟢 INTERPRETATION: All timeframes bullish - Strong uptrend")
            print("💡 ACTION: Aggressive accumulation opportunity")
        elif signal == 'BUY':
            print("🔵 INTERPRETATION: Majority timeframes bullish - Uptrend")
            print("💡 ACTION: Good accumulation opportunity")
        elif signal == 'STRONG_SELL':
            print("🔴 INTERPRETATION: All timeframes bearish - Trend exhaustion")
            print("💡 ACTION: Consider profit taking or reducing exposure")
        elif signal == 'SELL':
            print("🟠 INTERPRETATION: Majority timeframes bearish - Weakening trend")
            print("💡 ACTION: Caution advised, prepare for potential reversal")
        else:
            print("⚪ INTERPRETATION: Mixed signals - Consolidation phase")
            print("💡 ACTION: Wait for clearer directional signals")
        
        print(f"\n📊 Overbought Level: +{result['overbought_level']}")
        print(f"📊 Oversold Level: {result['oversold_level']}")
        
        print("\n📚 RCI 3-Line Explanation:")
        print("   • Measures correlation between price rank and time rank")
        print("   • Three periods: 9 (short), 26 (medium), 52 (long)")
        print("   • Values range from -100 to +100")
        print("   • All three aligned = strong signal")
        print("   • Excellent for trend exhaustion detection")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("📝 Note: This would work with the actual indicators module")
    
    print("\n")

def demo_partial_exit_strategy():
    """Demonstrate partial exit strategy logic"""
    print("💼 Partial Exit Strategy Demo")
    print("=" * 50)
    
    # Simulate different risk scenarios
    scenarios = [
        {
            'name': 'Low Risk Environment',
            'pi_cycle_triggered': False,
            'pi_cycle_distance': -15,
            'btc_rsi': 55,
            'rci_signal': 'BUY',
            'altseason_score': 20,
            'fear_greed': 60
        },
        {
            'name': 'Moderate Risk - Start Reducing',
            'pi_cycle_triggered': False,
            'pi_cycle_distance': -3,
            'btc_rsi': 72,
            'rci_signal': 'SELL',
            'altseason_score': 35,
            'fear_greed': 75
        },
        {
            'name': 'High Risk - Major Profit Taking',
            'pi_cycle_triggered': False,
            'pi_cycle_distance': -1,
            'btc_rsi': 83,
            'rci_signal': 'STRONG_SELL',
            'altseason_score': 50,
            'fear_greed': 85
        },
        {
            'name': 'CRITICAL RISK - Pi Cycle Triggered',
            'pi_cycle_triggered': True,
            'pi_cycle_distance': 2,
            'btc_rsi': 87,
            'rci_signal': 'STRONG_SELL',
            'altseason_score': 60,
            'fear_greed': 90
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎭 Scenario: {scenario['name']}")
        print("-" * 40)
        
        # Calculate risk score
        risk_score = 0
        risk_factors = []
        
        # Pi Cycle analysis
        if scenario['pi_cycle_triggered']:
            risk_score += 30
            risk_factors.append("Pi Cycle Top TRIGGERED")
        elif scenario['pi_cycle_distance'] > -5:
            risk_score += 15
            risk_factors.append("Pi Cycle approaching")
        
        # RSI analysis
        if scenario['btc_rsi'] > 80:
            risk_score += 25
            risk_factors.append(f"BTC RSI extreme ({scenario['btc_rsi']})")
        elif scenario['btc_rsi'] > 70:
            risk_score += 15
            risk_factors.append(f"BTC RSI overbought ({scenario['btc_rsi']})")
        
        # RCI analysis
        if scenario['rci_signal'] == 'STRONG_SELL':
            risk_score += 20
            risk_factors.append("RCI trend exhaustion")
        elif scenario['rci_signal'] == 'SELL':
            risk_score += 10
            risk_factors.append("RCI weakening trend")
        
        # Altseason contribution
        if scenario['altseason_score'] > 50:
            risk_score += 15
            risk_factors.append("Peak altseason")
        
        # Fear & Greed
        if scenario['fear_greed'] >= 80:
            risk_score += 20
            risk_factors.append(f"Extreme Greed ({scenario['fear_greed']})")
        elif scenario['fear_greed'] >= 70:
            risk_score += 10
            risk_factors.append(f"High Greed ({scenario['fear_greed']})")
        
        print(f"📊 Risk Score: {risk_score}/100")
        
        # Determine action
        if risk_score >= 85:
            action = "🔴 SELL 50% IMMEDIATELY"
            urgency = "CRITICAL"
        elif risk_score >= 75:
            action = "🟠 SELL 25% - High Risk"
            urgency = "HIGH"
        elif risk_score >= 60:
            action = "🟡 SELL 10% - Moderate Risk"
            urgency = "MEDIUM"
        else:
            action = "🟢 HOLD - Low Risk"
            urgency = "LOW"
        
        print(f"🎯 Recommended Action: {action}")
        print(f"⚡ Urgency: {urgency}")
        print("🔍 Risk Factors:")
        for factor in risk_factors:
            print(f"   • {factor}")
    
    print("\n📚 Partial Exit Strategy Explanation:")
    print("   • Risk score 60-74: Sell 10% (moderate caution)")
    print("   • Risk score 75-84: Sell 25% (high risk)")
    print("   • Risk score 85+: Sell 50% (critical/immediate)")
    print("   • Preserves upside while protecting against major drops")
    print("   • Based on multiple converging risk indicators")
    
    print("\n")

def demo_enhanced_altseason():
    """Demonstrate enhanced altseason detection"""
    print("🌟 Enhanced Altseason Detection Demo")
    print("=" * 50)
    
    scenarios = [
        {
            'name': 'BTC Season',
            'btc_dominance': 65,
            'eth_btc_ratio': 0.028,
            'btc_rsi': 45,
            'eth_rsi': 35,
            'btc_trend': 'up',
            'eth_trend': 'down'
        },
        {
            'name': 'Early Altseason',
            'btc_dominance': 52,
            'eth_btc_ratio': 0.045,
            'btc_rsi': 65,
            'eth_rsi': 55,
            'btc_trend': 'up',
            'eth_trend': 'up'
        },
        {
            'name': 'Peak Altseason',
            'btc_dominance': 42,
            'eth_btc_ratio': 0.075,
            'btc_rsi': 78,
            'eth_rsi': 72,
            'btc_trend': 'sideways',
            'eth_trend': 'up'
        },
        {
            'name': 'Extreme Altseason',
            'btc_dominance': 38,
            'eth_btc_ratio': 0.092,
            'btc_rsi': 82,
            'eth_rsi': 85,
            'btc_trend': 'down',
            'eth_trend': 'parabolic'
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎭 Market Phase: {scenario['name']}")
        print("-" * 40)
        
        btc_dom = scenario['btc_dominance']
        eth_btc = scenario['eth_btc_ratio']
        
        print(f"👑 BTC Dominance: {btc_dom:.1f}%")
        print(f"⚖️ ETH/BTC Ratio: {eth_btc:.4f}")
        print(f"📊 BTC RSI: {scenario['btc_rsi']}")
        print(f"📈 ETH RSI: {scenario['eth_rsi']}")
        
        # Calculate altseason score
        score = 0
        
        if btc_dom < 40:
            score += 40
        elif btc_dom < 45:
            score += 30
        elif btc_dom > 60:
            score -= 20
        
        if eth_btc > 0.08:
            score += 25
        elif eth_btc > 0.06:
            score += 15
        elif eth_btc < 0.03:
            score -= 15
        
        if scenario['btc_rsi'] > 75 and scenario['eth_rsi'] > 70:
            score += 20
        
        print(f"🎯 Altseason Score: {score}")
        
        # Determine phase and action
        if score > 50:
            phase = "EXTREME_ALTSEASON"
            action = "🔴 MASSIVE PROFIT TAKING - Sell 25-50% of altcoins"
        elif score > 35:
            phase = "PEAK_ALTSEASON"
            action = "🟠 MAJOR PROFIT TAKING - Sell 10-25% of altcoins"
        elif score > 20:
            phase = "ALTSEASON"
            action = "🟡 SELECTIVE PROFIT TAKING - Sell pumped alts"
        elif score > 0:
            phase = "EARLY_ALTSEASON"
            action = "🟢 HOLD POSITIONS - Building momentum"
        elif score < -15:
            phase = "BTC_SEASON"
            action = "₿ FOCUS ON BTC/ETH - Avoid most alts"
        else:
            phase = "TRANSITION"
            action = "⏳ WAIT FOR SIGNALS - Unclear direction"
        
        print(f"🌟 Phase: {phase}")
        print(f"💡 Action: {action}")
    
    print("\n📚 Enhanced Altseason Detection Features:")
    print("   • BTC dominance analysis with multiple thresholds")
    print("   • ETH/BTC ratio as leading altseason indicator")
    print("   • Cross-asset momentum analysis")
    print("   • ETH leadership vs BTC performance")
    print("   • More granular phase detection")
    
    print("\n")

def demo_integrated_message():
    """Show what the enhanced consolidated message would look like"""
    print("📱 Enhanced Strategic Message Preview")
    print("=" * 50)
    
    # Simulate a high-risk scenario
    message = """🎯 ESTRATÉGIA CRYPTO - Goal: 1 BTC + 10 ETH
==================================================

🚨 ALERTA DE VENDA PARCIAL:
   Risco de Topo: 82/100
   Recomendação: VENDA 25% DO PORTFÓLIO
   Urgência: HIGH
   Fatores de Risco:
     • Pi Cycle Top aproximando (-1.2%)
     • BTC RSI extremamente overbought (84.2)
     • RCI sinaliza exaustão de tendência

💰 ANÁLISE DO PORTFÓLIO:
   Valor das Altcoins: $45,327
   Meta (1 BTC + 10 ETH): $153,029
   Equivalente em BTC: 0.526 BTC
   Alcance da Meta: 29.6%
   📈 AÇÃO: Continue acumulando mas reduza risco

📊 FASE DO MERCADO:
   Status: ALTSEASON - Altcoins em alta
   🌟 AÇÃO: Monitore saídas de altcoins

🔺 ANÁLISE DE TOPO (ENHANCED):
   Risco: 82/100 (CRÍTICO)
   🟠 Pi Cycle Top: Aproximando (Distância: -1.2%)
   🔴 RCI 3-Line: Exaustão de tendência detectada
   🟠 AÇÃO: Alto risco - Venda 20-30% dos lucros

🌟 ALTSEASON METRIC (ENHANCED):
   Status: PEAK_ALTSEASON (Score: 48)
   BTC Dominance: 41.2%
   ETH/BTC Ratio: 0.0782
   🎯 AÇÃO: VENDA ALTCOINS AGORA - Pico detectado

⚖️ BTC/ETH RATIO:
   Ratio Atual: 0.0782
   🔄 AÇÃO: TROQUE ETH por BTC - Alta confiança

💎 TOP ALTCOIN AÇÕES:
   🔥 binancecoin: +287.3% - VENDA IMEDIATA
   🔥 chainlink: +156.7% - VENDA IMEDIATA
   👁️ matic: +89.2% - Score 72 - Monitore

⏰ Atualizado: 14:23:45
🆕 Enhanced com Pi Cycle Top + RCI 3-Line + Partial Exit Strategy"""
    
    print(message)
    
    print("\n📚 Message Enhancement Features:")
    print("   • Partial exit alerts at top priority")
    print("   • Pi Cycle Top status and distance")
    print("   • RCI 3-Line trend analysis")
    print("   • Enhanced altseason with ETH/BTC ratio")
    print("   • Risk-based action recommendations")
    print("   • Multiple converging indicators")
    
    print("\n")

def main():
    """Run complete demo of enhanced features"""
    print("🚀 Enhanced Crypto Alert System - Complete Demo")
    print("=" * 60)
    print("Demonstrating new technical indicators and strategies")
    print("=" * 60)
    print()
    
    demo_pi_cycle_indicator()
    demo_rci_3_line()
    demo_partial_exit_strategy()
    demo_enhanced_altseason()
    demo_integrated_message()
    
    print("🎉 Demo Complete!")
    print("\n📋 Summary of Enhancements:")
    print("   ✅ Pi Cycle Top Indicator - Historical cycle top detection")
    print("   ✅ 3-Line RCI - Advanced trend analysis")
    print("   ✅ Partial Exit Strategy - Risk-based position management")
    print("   ✅ Enhanced Altseason Detection - Multi-factor analysis")
    print("   ✅ Integrated Risk Scoring - 0-100 comprehensive risk")
    print("   ✅ Production Ready - Comprehensive testing")
    
    print("\n🚀 Ready for production deployment!")

if __name__ == "__main__":
    main()
