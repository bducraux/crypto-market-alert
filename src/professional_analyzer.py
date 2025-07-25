"""
Analisador profissional de criptoativos com alertas extremamente claros e acionáveis
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime


class ProfessionalCryptoAnalyzer:
    """
    Analisador profissional que gera alertas com ações específicas baseadas em 
    análise técnica e fundamentalista combinadas
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_market_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise do sentimento geral do mercado"""
        
        btc_dominance = market_data.get('btc_dominance', 50)
        fear_greed = market_data.get('fear_greed_index', {}).get('value', 50)
        eth_btc_ratio = market_data.get('eth_btc_ratio', 0.05)
        
        sentiment = {
            'phase': 'NEUTRAL',
            'risk_level': 'MÉDIO',
            'action_bias': 'HOLD',
            'confidence': 50,
            'description': ''
        }
        
        # Análise de fases do mercado
        if fear_greed <= 20 and btc_dominance > 60:
            sentiment.update({
                'phase': 'CAPITULAÇÃO',
                'risk_level': 'BAIXO',
                'action_bias': 'COMPRA AGRESSIVA',
                'confidence': 85,
                'description': 'Pânico extremo + BTC dominance alta = Oportunidade de acumulação'
            })
        
        elif fear_greed <= 30 and btc_dominance > 55:
            sentiment.update({
                'phase': 'ACUMULAÇÃO',
                'risk_level': 'BAIXO-MÉDIO',
                'action_bias': 'COMPRA GRADUAL',
                'confidence': 75,
                'description': 'Medo no mercado com BTC forte = Momento para DCA'
            })
        
        elif fear_greed >= 80 and btc_dominance < 45:
            sentiment.update({
                'phase': 'EUFORIA ALTCOINS',
                'risk_level': 'MUITO ALTO',
                'action_bias': 'VENDA PARCIAL',
                'confidence': 90,
                'description': 'Ganância extrema + Altcoin mania = Risco de correção iminente'
            })
        
        elif fear_greed >= 75:
            sentiment.update({
                'phase': 'DISTRIBUIÇÃO',
                'risk_level': 'ALTO',
                'action_bias': 'TOME LUCROS',
                'confidence': 80,
                'description': 'Mercado ganancioso = Realize lucros parciais'
            })
        
        elif btc_dominance < 45 and eth_btc_ratio > 0.07:
            sentiment.update({
                'phase': 'ALTSEASON',
                'risk_level': 'MÉDIO',
                'action_bias': 'ROTAÇÃO ALTCOINS',
                'confidence': 70,
                'description': 'BTC dominance baixa + ETH forte = Altseason ativa'
            })
        
        return sentiment
    
    def analyze_coin_signals(self, coin_data: Dict[str, Any], coin_config: Dict[str, Any], 
                           market_sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Análise detalhada de sinais para uma moeda específica"""
        
        coin_name = coin_config.get('name', 'Unknown')
        current_price = coin_data.get('usd', 0)
        indicators = coin_data.get('indicators', {})
        
        rsi = indicators.get('rsi')
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        ma_short = indicators.get('ma_short')
        ma_long = indicators.get('ma_long')
        
        analysis = {
            'coin': coin_name,
            'price': current_price,
            'signal_strength': 0,  # -100 a +100
            'action': 'HOLD',
            'urgency': 'BAIXA',
            'description': '',
            'specific_actions': [],
            'risk_reward': 'N/A',
            'timeframe': 'MÉDIO PRAZO'
        }
        
        signal_score = 0
        signals = []
        actions = []
        
        # Análise RSI
        if rsi:
            if rsi <= 25:
                signal_score += 40
                signals.append(f"RSI extremamente oversold ({rsi:.1f})")
                actions.append(f"COMPRE {coin_name} imediatamente - RSI em zona de pânico")
            elif rsi <= 35:
                signal_score += 25
                signals.append(f"RSI oversold ({rsi:.1f})")
                actions.append(f"Considere acumular {coin_name} gradualmente")
            elif rsi >= 75:
                signal_score -= 40
                signals.append(f"RSI extremamente overbought ({rsi:.1f})")
                actions.append(f"VENDA parcial de {coin_name} - zona de risco")
            elif rsi >= 65:
                signal_score -= 25
                signals.append(f"RSI overbought ({rsi:.1f})")
                actions.append(f"Considere realizar lucros em {coin_name}")
        
        # Análise MACD
        if macd and macd_signal:
            macd_diff = macd - macd_signal
            if macd > macd_signal and macd_diff > 0.1:
                signal_score += 30
                signals.append("MACD bullish crossover forte")
                actions.append(f"Momentum de alta confirmado em {coin_name}")
            elif macd < macd_signal and macd_diff < -0.1:
                signal_score -= 30
                signals.append("MACD bearish crossover forte")
                actions.append(f"Momentum de baixa confirmado em {coin_name}")
        
        # Análise Moving Averages
        if ma_short and ma_long:
            ma_diff_pct = ((ma_short - ma_long) / ma_long) * 100
            if ma_short > ma_long and ma_diff_pct > 5:
                signal_score += 25
                signals.append(f"Golden Cross ativo (+{ma_diff_pct:.1f}%)")
                actions.append(f"Tendência de alta estabelecida em {coin_name}")
            elif ma_short < ma_long and ma_diff_pct < -5:
                signal_score -= 25
                signals.append(f"Death Cross ativo ({ma_diff_pct:.1f}%)")
                actions.append(f"Tendência de baixa estabelecida em {coin_name}")
        
        # Contexto do mercado
        market_bias = market_sentiment.get('action_bias', 'HOLD')
        market_risk = market_sentiment.get('risk_level', 'MÉDIO')
        
        # Ajustar sinal baseado no contexto do mercado
        if market_bias == 'COMPRA AGRESSIVA' and signal_score > 0:
            signal_score *= 1.5  # Amplificar sinais de compra em mercado de oportunidade
        elif market_bias == 'VENDA PARCIAL' and signal_score < 0:
            signal_score *= 1.5  # Amplificar sinais de venda em mercado de risco
        elif market_risk == 'MUITO ALTO':
            signal_score = min(signal_score, 20)  # Limitar sinais de compra em alto risco
        
        # Calcular P&L (Profit & Loss)
        avg_price = coin_config.get('avg_price', 0)
        pnl_percentage = 0
        if avg_price > 0:
            pnl_percentage = ((current_price - avg_price) / avg_price) * 100
        
        # Configurações de P&L
        pnl_config = self.config.get('professional_alerts', {}).get('pnl_consideration', {})
        min_profit_for_sell = pnl_config.get('min_profit_for_sell', 5.0)
        max_loss_for_sell = pnl_config.get('max_loss_for_sell', -15.0)
        hodl_on_loss = pnl_config.get('hodl_on_loss', True)
        altseason_patience = pnl_config.get('altseason_patience', True)
        
        # Determinar ação final considerando P&L
        analysis['signal_strength'] = max(-100, min(100, signal_score))
        analysis['pnl_percentage'] = pnl_percentage
        analysis['avg_price'] = avg_price
        
        # Lógica de decisão com P&L
        is_altseason = market_sentiment.get('phase') in ['ALTSEASON', 'ALTCOIN_EUPHORIA']
        is_in_loss = pnl_percentage < 0
        is_significant_loss = pnl_percentage < max_loss_for_sell
        is_good_profit = pnl_percentage >= min_profit_for_sell
        
        if signal_score >= 60:  # Sinais de COMPRA FORTE
            analysis.update({
                'action': 'COMPRA FORTE',
                'urgency': 'ALTA',
                'risk_reward': 'FAVORÁVEL',
                'timeframe': 'CURTO PRAZO'
            })
        elif signal_score >= 40:  # Sinais de COMPRA GRADUAL
            analysis.update({
                'action': 'COMPRA GRADUAL',
                'urgency': 'MÉDIA',
                'risk_reward': 'POSITIVO',
                'timeframe': 'MÉDIO PRAZO'
            })
        elif signal_score <= -70:  # Sinais de VENDA muito fortes
            if is_good_profit or is_significant_loss:
                # Venda se estiver em bom lucro OU prejuízo muito grande (stop loss)
                analysis.update({
                    'action': 'VENDA IMEDIATA',
                    'urgency': 'ALTA',
                    'risk_reward': 'PROTEÇÃO CAPITAL',
                    'timeframe': 'IMEDIATO'
                })
            elif hodl_on_loss and is_in_loss and (is_altseason or altseason_patience):
                # HODL se estiver no prejuízo e puder aguardar altseason
                analysis.update({
                    'action': 'AGUARDAR ALTSEASON',
                    'urgency': 'BAIXA',
                    'risk_reward': 'PACIÊNCIA ESTRATÉGICA',
                    'timeframe': 'LONGO PRAZO'
                })
            else:
                analysis.update({
                    'action': 'VENDA IMEDIATA',
                    'urgency': 'ALTA',
                    'risk_reward': 'PROTEÇÃO CAPITAL',
                    'timeframe': 'IMEDIATO'
                })
        elif signal_score <= -40:  # Sinais de VENDA moderados
            if is_good_profit:
                # Venda parcial apenas se estiver em lucro
                analysis.update({
                    'action': 'VENDA PARCIAL',
                    'urgency': 'MÉDIA',
                    'risk_reward': 'DEFENSIVO',
                    'timeframe': 'CURTO PRAZO'
                })
            elif hodl_on_loss and is_in_loss:
                # HODL se estiver no prejuízo
                analysis.update({
                    'action': 'HODL NO PREJUÍZO',
                    'urgency': 'BAIXA',
                    'risk_reward': 'AGUARDAR RECUPERAÇÃO',
                    'timeframe': 'MÉDIO PRAZO'
                })
            else:
                analysis.update({
                    'action': 'VENDA PARCIAL',
                    'urgency': 'MÉDIA',
                    'risk_reward': 'DEFENSIVO',
                    'timeframe': 'CURTO PRAZO'
                })
        else:
            # Para casos neutros, marcar como HOLD mas o generate_alert vai filtrar
            analysis.update({
                'action': 'HOLD/OBSERVE',
                'urgency': 'BAIXA',
                'risk_reward': 'NEUTRO',
                'timeframe': 'MÉDIO PRAZO'
            })
        
        analysis['description'] = ' | '.join(signals)
        analysis['specific_actions'] = actions
        
        return analysis
    
    def generate_professional_alert(self, analysis: Dict[str, Any], 
                                  market_sentiment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Gera alerta profissional extremamente claro com formatação para Telegram"""
        
        coin_name = analysis['coin']
        action = analysis['action']
        urgency = analysis['urgency']
        signal_strength = analysis['signal_strength']
        price = analysis['price']
        
        # Só gerar alertas para sinais significativos QUE REQUEREM AÇÃO
        if abs(signal_strength) < 30:  # Aumentei de 25 para 30
            return None
        
        # NÃO gerar alerta para HOLD/OBSERVE - só desperdiça atenção
        if action == 'HOLD/OBSERVE':
            return None
        
        # Emojis baseados na ação
        emoji_map = {
            'COMPRA FORTE': '🚀',
            'COMPRA GRADUAL': '💰',
            'VENDA IMEDIATA': '🔴',
            'VENDA PARCIAL': '⚠️',
            'HOLD/OBSERVE': '✋'
        }
        
        priority_map = {
            'ALTA': 'high',
            'MÉDIA': 'medium',
            'BAIXA': 'low'
        }
        
        emoji = emoji_map.get(action, '📊')
        
        # Construir mensagem formatada para Telegram HTML com separação simples
        signal_direction = "📈" if signal_strength > 0 else "📉"
        
        # Intensidade em texto ao invés de símbolos
        abs_strength = abs(signal_strength)
        if abs_strength >= 80:
            intensity_text = "MUITO FORTE"
        elif abs_strength >= 60:
            intensity_text = "FORTE"
        elif abs_strength >= 40:
            intensity_text = "MODERADA"
        else:
            intensity_text = "FRACA"
        
        # Traduzir contexto para português mais claro
        context_pt = {
            'NEUTRAL': 'Mercado Neutro',
            'CAPITULAÇÃO': 'Capitulação (COMPRE!)',
            'ACUMULAÇÃO': 'Zona de Compra',
            'DISTRIBUIÇÃO': 'Zona de Venda', 
            'ALTSEASON': 'Altseason Ativa',
            'GANÂNCIA': 'Mercado Ganancioso',
            'MEDO': 'Mercado com Medo',
            'ALTCOIN_EUPHORIA': 'Euforia - RISCO!'
        }
        
        context_description = context_pt.get(market_sentiment['phase'], market_sentiment['phase'])
        
        # Informações de P&L
        pnl_percentage = analysis.get('pnl_percentage', 0)
        avg_price = analysis.get('avg_price', 0)
        pnl_emoji = "📈" if pnl_percentage > 0 else "📉" if pnl_percentage < 0 else "➡️"
        pnl_text = f"{pnl_percentage:+.1f}%" if avg_price > 0 else "N/A"
        
        message = f"""<b>{emoji} {action}: {coin_name}</b>


💵 <b>Preço:</b> ${price:,.4f}
💰 <b>P&L:</b> {pnl_emoji} {pnl_text}
📊 <b>Força:</b> {signal_strength:+.0f}/100 {signal_direction}
📈 <b>Intensidade:</b> {intensity_text}
🌍 <b>Mercado:</b> {context_description}
⏰ <b>Urgência:</b> {urgency}"""
        
        # Ação específica super clara com formatação
        action_text = ""
        if action == 'COMPRA FORTE':
            action_text = f"""
<b>🎯 AÇÃO RECOMENDADA:</b>
✅ Compre <b>{coin_name}</b> AGORA
💰 Use 30-50% do capital disponível
📈 Sinais técnicos muito favoráveis
⏱️ Execute dentro de 1-2 horas"""
        
        elif action == 'COMPRA GRADUAL':
            action_text = f"""
<b>🎯 AÇÃO RECOMENDADA:</b>
📈 Acumule <b>{coin_name}</b> gradualmente (DCA)
💰 Entre com 10-25% agora
📅 Resto ao longo da semana
🎯 Zona de acumulação identificada"""
        
        elif action == 'VENDA IMEDIATA':
            action_text = f"""
<b>🎯 AÇÃO RECOMENDADA:</b>
🔴 VENDA <b>{coin_name}</b> IMEDIATAMENTE
💵 Converta para USDC
⚠️ Risco de correção iminente
⏱️ Execute AGORA"""
        
        elif action == 'VENDA PARCIAL':
            pnl_info = f" (Lucro: +{pnl_percentage:.1f}%)" if pnl_percentage > 0 else ""
            action_text = f"""
<b>🎯 AÇÃO RECOMENDADA:</b>
⚠️ Considere vender parte da posição em <b>{coin_name}</b>{pnl_info}
💰 Venda 25-40% se estiver no lucro
📊 Sinais de fraqueza detectados
🎯 Proteja parte dos ganhos"""
        
        elif action == 'AGUARDAR ALTSEASON':
            action_text = f"""
<b>🎯 AÇÃO RECOMENDADA:</b>
⏳ AGUARDE - <b>{coin_name}</b> no prejuízo ({pnl_percentage:.1f}%)
🌟 Altseason pode recuperar posição
💎 HODL até reversão do mercado
🎯 Paciência estratégica recomendada"""
        
        elif action == 'HODL NO PREJUÍZO':
            action_text = f"""
<b>🎯 AÇÃO RECOMENDADA:</b>
💎 HODL <b>{coin_name}</b> - Prejuízo atual: {pnl_percentage:.1f}%
📈 Aguarde reversão de tendência
⏳ Não venda no vermelho
🎯 Aguarde recuperação ou altseason"""
        
        else:
            action_text = f"""
<b>🎯 AÇÃO RECOMENDADA:</b>
✋ Mantenha posição atual em <b>{coin_name}</b>
👀 Aguarde sinais mais claros
📊 Mercado neutro
⏳ Paciência recomendada"""
        
        # Combinar mensagem e ação
        full_message = message + action_text
        
        return {
            'type': 'professional_signal',
            'coin': coin_name,
            'message': full_message,
            'action': action_text,
            'priority': priority_map.get(urgency, 'low'),
            'urgency': urgency,
            'signal_strength': signal_strength,
            'market_context': market_sentiment['phase'],
            'confidence': abs(signal_strength),
            'timeframe': analysis['timeframe'],
            'risk_reward': analysis['risk_reward']
        }
