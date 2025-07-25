"""
Detector de Topo de Ciclo do Bitcoin
Usa apenas dados gratuitos da CoinGecko para identificar possíveis topos de ciclo
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import numpy as np


class CycleTopDetector:
    """
    Detector de topo de ciclo usando indicadores gratuitos
    Foco em identificar sinais de distribuição e euforia extrema
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config  # Guardar a configuração completa
        self.cycle_config = config.get('professional_alerts', {}).get('cycle_top_detection', {})
        self.logger = logging.getLogger(__name__)
        
        # Histórico para detectar streaks
        self.fear_greed_history = []
        self.btc_dominance_history = []
        
    def analyze_cycle_top(self, data_dict, market_data):
        """
        Análise principal do risco de topo de ciclo
        
        Returns:
            dict: {
                'risk_score': int (0-100),
                'risk_level': str,
                'signals': dict,
                'dashboard': dict,  # Dados para dashboard
                'should_alert': bool
            }
        """
        try:
            btc_data = data_dict.get('bitcoin', {})
            signals = {}
            dashboard = {}
            
            # 1. Análise BTC Overextension
            btc_signals = self._analyze_btc_overextension(btc_data)
            signals['btc_overextension'] = btc_signals
            
            # 2. Análise Extreme Euphoria
            euphoria_signals = self._analyze_extreme_euphoria(btc_data, market_data)
            signals['extreme_euphoria'] = euphoria_signals
            
            # 3. Análise Market Structure
            structure_signals = self._analyze_market_structure(market_data, data_dict)
            signals['market_structure'] = structure_signals
            
            # 4. Análise Technical Signals
            tech_signals = self._analyze_technical_signals(btc_data, data_dict)
            signals['technical_signals'] = tech_signals
            
            # 5. Calcular Score Total
            risk_score = self._calculate_risk_score(signals)
            
            # 6. Preparar Dashboard Completo
            dashboard = self._prepare_dashboard(btc_data, market_data, data_dict, signals, risk_score)
            
            # 7. Determinar se deve alertar
            should_alert = self._should_send_alert(risk_score)
            
            return {
                'risk_score': risk_score,
                'risk_level': self._get_risk_level(risk_score),
                'signals': signals,
                'dashboard': dashboard,
                'should_alert': should_alert
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de topo de ciclo: {e}")
            return self._get_default_result()
    
    def _analyze_btc_overextension(self, btc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa se BTC está sobre-estendido vs médias móveis"""
        result = {
            'active_signals': 0,
            'score': 0,
            'details': {},
            'signals': [],
            'warnings': []
        }
        
        # Usar as chaves corretas dos dados recebidos
        current_price = btc_data.get('usd', btc_data.get('current_price', 0))
        
        # Para as médias móveis, tentar primeiro indicators, depois as chaves diretas
        indicators = btc_data.get('indicators', {})
        ma200 = indicators.get('ma_long', btc_data.get('ma_200', btc_data.get('ma_long', 0)))
        ma50 = indicators.get('ma_short', btc_data.get('ma_50', btc_data.get('ma_short', 0)))
        
        if not ma200 or not current_price:
            return result
        
        # Múltiplo da MA200
        ma200_multiple = current_price / ma200
        threshold = self.cycle_config.get('btc_overextension', {}).get('ma200_multiple', 4.0)
        
        result['details']['ma200_multiple'] = ma200_multiple
        result['details']['threshold'] = threshold
        
        if ma200_multiple > threshold:
            result['score'] += 40
            result['active_signals'] += 1
            result['signals'].append(f"BTC {ma200_multiple:.1f}x acima da MA200 (limite: {threshold}x)")
            
        if ma200_multiple > threshold * 1.5:  # 6x = muito extremo
            result['score'] += 20
            result['active_signals'] += 1
            result['warnings'].append("BTC extremamente sobre-estendido vs MA200")
        
        # Divergência da MA50 (ficando plana em alta)
        historical = btc_data.get('historical')
        if historical is not None and len(historical) >= 10:
            try:
                # Calcular inclinação da MA50 nos últimos 10 dias
                ma50_values = []
                for i in range(-10, 0):
                    if abs(i) <= len(historical):
                        row = historical.iloc[i]
                        close = row.get('close', 0)
                        if close > 0:
                            ma50_values.append(close)
                
                if len(ma50_values) >= 5:
                    slope = np.polyfit(range(len(ma50_values)), ma50_values, 1)[0]
                    daily_change = slope / ma50_values[-1] * 100  # % daily change
                    
                    if daily_change < 0.1:  # MA50 quase plana
                        result['score'] += 15
                        result['active_signals'] += 1
                        result['signals'].append("MA50 perdendo momentum (ficando plana)")
                        
            except Exception as e:
                self.logger.warning(f"Error calculating MA50 slope: {e}")
        
        return result
    
    def _analyze_extreme_euphoria(self, btc_data: Dict[str, Any], 
                                  market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa sinais de euforia extrema do mercado"""
        result = {
            'active_signals': 0,
            'score': 0,
            'details': {},
            'signals': [],
            'warnings': []
        }
        
        fear_greed_data = market_data.get('fear_greed_index', {})
        fear_greed = fear_greed_data.get('value', 50) if isinstance(fear_greed_data, dict) else 50
        threshold = self.cycle_config.get('extreme_euphoria', {}).get('fear_greed_threshold', 85)
        
        result['details']['fear_greed'] = fear_greed
        result['details']['threshold'] = threshold
        
        # Atualizar histórico
        self.fear_greed_history.append({
            'date': datetime.now(),
            'value': fear_greed
        })
        
        # Manter apenas últimos 7 dias
        cutoff = datetime.now() - timedelta(days=7)
        self.fear_greed_history = [h for h in self.fear_greed_history if h['date'] > cutoff]
        
        # Fear & Greed atual
        if fear_greed > threshold:
            result['score'] += 25
            result['active_signals'] += 1
            result['signals'].append(f"Fear & Greed extremo: {fear_greed}")
            
        # Streak de dias extremos
        required_days = self.cycle_config.get('extreme_euphoria', {}).get('fear_greed_days', 3)
        extreme_days = sum(1 for h in self.fear_greed_history if h['value'] > threshold)
        
        if extreme_days >= required_days:
            result['score'] += 25
            result['active_signals'] += 1
            result['warnings'].append(f"Fear & Greed >{threshold} por {extreme_days} dias")
        
        result['details']['extreme_days'] = extreme_days
        result['details']['required_days'] = required_days
        
        # TODO: Análise de volume (quando tivermos dados de volume global)
        
        return result
    
    def _analyze_market_structure(self, market_data: Dict[str, Any], 
                                  data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa estrutura do mercado (dominance, rotações)"""
        result = {
            'active_signals': 0,
            'score': 0,
            'details': {},
            'signals': [],
            'warnings': []
        }
        
        btc_dominance = market_data.get('btc_dominance', 50)
        result['details']['btc_dominance'] = btc_dominance
        
        # Atualizar histórico de dominance
        self.btc_dominance_history.append({
            'date': datetime.now(),
            'value': btc_dominance
        })
        
        # Manter apenas últimos 30 dias
        cutoff = datetime.now() - timedelta(days=30)
        self.btc_dominance_history = [h for h in self.btc_dominance_history 
                                      if h['date'] > cutoff]
        
        config = self.config.get('professional_alerts', {}).get('cycle_top_detection', {}).get('market_structure', {})
        
        # BTC Dominance muito alta (topo clássico)
        peak_threshold = config.get('btc_dominance_peak', 65)
        if btc_dominance > peak_threshold:
            result['score'] += 20
            result['active_signals'] += 1
            result['signals'].append(f"BTC Dominance alta: {btc_dominance:.1f}%")
            
        # OU Dominance muito baixa (alt mania)
        alt_mania_threshold = config.get('alt_euphoria', 35)
        if btc_dominance < alt_mania_threshold:
            result['score'] += 30
            result['active_signals'] += 1
            result['warnings'].append(f"Possível ALT MANIA: Dominance {btc_dominance:.1f}%")
        
        # Reversão de dominance (se houver dados históricos)
        if len(self.btc_dominance_history) >= 7:
            recent_avg = sum(h['value'] for h in self.btc_dominance_history[-7:]) / 7
            older_avg = sum(h['value'] for h in self.btc_dominance_history[-14:-7]) / 7 if len(self.btc_dominance_history) >= 14 else recent_avg
            
            dominance_change = recent_avg - older_avg
            result['details']['dominance_trend'] = dominance_change
            
            if config.get('dominance_reversal', True):
                if btc_dominance > peak_threshold and dominance_change < -2:
                    result['score'] += 15
                    result['active_signals'] += 1
                    result['signals'].append("BTC Dominance começando a cair do pico")
        
        result['details']['peak_threshold'] = peak_threshold
        result['details']['alt_mania_threshold'] = alt_mania_threshold
        
        return result
    
    def _analyze_technical_signals(self, btc_data: Dict[str, Any], 
                                   data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa sinais técnicos extremos"""
        result = {
            'active_signals': 0,
            'score': 0,
            'details': {},
            'signals': [],
            'warnings': []
        }
        
        # RSI extremo do BTC
        indicators = btc_data.get('indicators', {})
        btc_rsi = indicators.get('rsi', btc_data.get('rsi', 50))
        rsi_threshold = self.cycle_config.get('technical_signals', {}).get('rsi_extreme', 80)
        
        result['details']['btc_rsi'] = btc_rsi
        result['details']['rsi_threshold'] = rsi_threshold
        
        if btc_rsi > rsi_threshold:
            result['score'] += 20
            result['active_signals'] += 1
            result['signals'].append(f"BTC RSI extremo: {btc_rsi:.1f}")
        
        # Múltiplas moedas overbought
        overbought_count = 0
        high_risk_count = 0  # RSI > 70
        total_coins = 0
        
        for coin_id, data in data_dict.items():
            if coin_id == 'bitcoin':  # Já analisamos
                continue
                
            coin_indicators = data.get('indicators', {})
            rsi = coin_indicators.get('rsi', data.get('rsi'))
            if rsi:
                total_coins += 1
                if rsi > 75:
                    overbought_count += 1
                elif rsi > 70:  # Adicionar categoria de risco alto
                    high_risk_count += 1
        
        min_overbought = self.cycle_config.get('technical_signals', {}).get('multiple_coins_overbought', 2)  # Reduzir para 2
        result['details']['overbought_count'] = overbought_count
        result['details']['high_risk_count'] = high_risk_count
        result['details']['total_coins'] = total_coins
        result['details']['min_overbought'] = min_overbought
        
        # Score baseado em múltiplas condições
        total_risky = overbought_count + high_risk_count
        risky_percentage = (total_risky / total_coins) if total_coins > 0 else 0
        
        # Score escalonado baseado na porcentagem de moedas de risco
        if risky_percentage >= 0.5:  # 50%+ = muito perigoso
            result['score'] += 30
            result['active_signals'] += 1
            result['warnings'].append(f"{(risky_percentage*100):.1f}% das moedas em risco alto - PERIGO")
        elif risky_percentage >= 0.3:  # 30%+ = perigoso
            result['score'] += 20
            result['active_signals'] += 1
            result['warnings'].append(f"{(risky_percentage*100):.1f}% das moedas em risco alto")
        elif risky_percentage >= 0.2:  # 20%+ = atenção
            result['score'] += 15
            result['active_signals'] += 1
            result['warnings'].append(f"{(risky_percentage*100):.1f}% das moedas em risco")
        elif risky_percentage >= 0.1:  # 10%+ = sinal precoce
            result['score'] += 10
            result['active_signals'] += 1
            result['warnings'].append(f"{(risky_percentage*100):.1f}% das moedas em risco (sinal precoce)")
        elif total_risky >= min_overbought:  # Pelo menos 2 moedas
            result['score'] += 5
            result['active_signals'] += 1
            result['warnings'].append(f"{total_risky} moedas com RSI alto")
        
        # Bonus extra para moedas extremamente overbought (RSI > 75)
        if overbought_count > 0:
            result['score'] += overbought_count * 5  # 5 pontos por moeda extrema
            result['warnings'].append(f"{overbought_count} moedas extremamente overbought")
        
        return result
    
    def _calculate_risk_score(self, signals: Dict[str, Any]) -> int:
        """Calcula score total de risco de topo de ciclo"""
        total_score = 0
        
        # Somar scores de cada categoria
        for category, category_signals in signals.items():
            if isinstance(category_signals, dict):
                category_score = category_signals.get('score', 0)
                total_score += category_score
        
        # Ajustar normalização para ser mais sensível
        max_possible_score = 120  # Score máximo mais realista (4 categorias * ~30 cada)
        normalized_score = min(100, (total_score / max_possible_score) * 100)
        
        return int(normalized_score)
    
    def _get_risk_level(self, risk_score: int) -> str:
        """Converte score numérico em nível de risco textual"""
        if risk_score >= 85:
            return "EXTREMO"
        elif risk_score >= 70:
            return "ALTO"
        elif risk_score >= 50:
            return "MÉDIO"
        elif risk_score >= 30:
            return "BAIXO"
        else:
            return "MÍNIMO"
    
    def should_send_alert(self, analysis: Dict[str, Any]) -> bool:
        """Determina se deve enviar alerta de topo de ciclo"""
        if not analysis or analysis.get('cycle_top_risk', 0) < 50:
            return False
            
        # TODO: Implementar cooldown de 24h
        return True
    
    def format_cycle_alert(self, analysis: Dict[str, Any]) -> str:
        """Formata alerta de topo de ciclo para Telegram"""
        if not self.should_send_alert(analysis):
            return ""
        
        risk_score = analysis.get('cycle_top_risk', 0)
        recommendation = analysis.get('recommendation', 'CONTINUE')
        confidence = analysis.get('confidence', 0)
        
        # Emoji baseado no risco
        if risk_score >= 80:
            emoji = "🚨🔴"
            urgency = "CRÍTICO"
        elif risk_score >= 65:
            emoji = "⚠️🟡"
            urgency = "ALTO"
        else:
            emoji = "📊🟠"
            urgency = "MÉDIO"
        
        message = f"""<b>{emoji} ALERTA DE TOPO DE CICLO</b>

🎯 <b>Risco de Topo:</b> {risk_score:.0f}/100
📈 <b>Recomendação:</b> {recommendation}
⚡ <b>Confiança:</b> {confidence}%
🚨 <b>Urgência:</b> {urgency}

<b>🔍 SINAIS DETECTADOS:</b>"""

        # Adicionar sinais
        for signal in analysis.get('signals', []):
            message += f"\n• {signal}"
            
        # Adicionar warnings
        for warning in analysis.get('warnings', []):
            message += f"\n⚠️ {warning}"
        
        # Ação recomendada
        if recommendation == 'SAÍDA IMEDIATA':
            message += f"""

<b>🎯 AÇÃO URGENTE:</b>
🔴 VENDA POSIÇÕES PRINCIPAIS
💰 Converta para USDC/USDT
⏰ Execute nas próximas horas
🎯 Possível topo de ciclo próximo"""
        
        elif recommendation == 'VENDA PARCIAL':
            message += f"""

<b>🎯 AÇÃO RECOMENDADA:</b>
⚠️ Venda 30-50% das posições
💰 Realize lucros principais
📊 Mantenha exposição reduzida
🎯 Mercado em zona perigosa"""
        
        elif recommendation == 'CAUTELA EXTREMA':
            message += f"""

<b>🎯 AÇÃO RECOMENDADA:</b>
👀 Monitore MUITO de perto
🛑 Não faça novas compras
📊 Prepare-se para saídas
⏰ Topo pode estar próximo"""
        
        return message
    
    def _prepare_dashboard(self, btc_data, market_data, data_dict, signals, risk_score):
        """Prepara dashboard completo com todas as métricas relevantes"""
        try:
            # Usar as chaves corretas dos dados recebidos
            current_price = btc_data.get('usd', btc_data.get('current_price', 0))
            
            # Para as médias móveis e RSI, tentar primeiro indicators, depois as chaves diretas
            indicators = btc_data.get('indicators', {})
            ma200 = indicators.get('ma_long', btc_data.get('ma_200', btc_data.get('ma_long', 0)))
            ma50 = indicators.get('ma_short', btc_data.get('ma_50', btc_data.get('ma_short', 0)))
            rsi = indicators.get('rsi', btc_data.get('rsi', 50))
            
            # Contagem de moedas sobrecompradas
            overbought_count = 0  # RSI > 75
            high_risk_count = 0   # RSI > 70
            total_coins = 0
            portfolio_info = []
            
            for coin_id, coin_data in data_dict.items():
                coin_indicators = coin_data.get('indicators', {})
                coin_rsi = coin_indicators.get('rsi', coin_data.get('rsi'))
                
                if coin_rsi is not None:
                    total_coins += 1
                    coin_price = coin_data.get('usd', coin_data.get('current_price', 0))
                    
                    if coin_rsi > 75:
                        overbought_count += 1
                        status = 'Extrema'
                    elif coin_rsi > 70:
                        high_risk_count += 1
                        status = 'Sobrecomprada'
                    else:
                        status = 'Normal'
                    
                    # Info do portfólio
                    portfolio_info.append({
                        'symbol': coin_id.upper(),
                        'price': coin_price,
                        'rsi': coin_rsi,
                        'status': status
                    })
            
            dashboard = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'risk_score': risk_score,
                'risk_level': self._get_risk_level(risk_score),
                
                # Métricas BTC
                'btc_metrics': {
                    'price': f"${current_price:,.0f}",
                    'ma200_multiple': round(current_price / ma200, 2) if ma200 > 0 else 0,
                    'ma50_trend': self._get_ma_trend(btc_data),
                    'rsi': round(rsi, 1),
                    'distance_from_ma200': f"{((current_price / ma200 - 1) * 100):.1f}%" if ma200 > 0 else "N/A"
                },
                
                # Métricas de Mercado
                'market_metrics': {
                    'fear_greed': market_data.get('fear_greed_index', {}).get('value', 'N/A'),
                    'fear_greed_level': self._get_fear_greed_level(market_data.get('fear_greed_index', {}).get('value', 50)),
                    'btc_dominance': f"{market_data.get('btc_dominance', 0):.1f}%",
                    'eth_btc_ratio': f"{market_data.get('eth_btc_ratio', 0):.4f}",
                    'market_cap_trend': self._get_market_trend(market_data)
                },
                
                # Estatísticas do Portfólio
                'portfolio_stats': {
                    'total_coins_tracked': total_coins,
                    'overbought_coins': overbought_count,  # RSI > 75
                    'high_risk_coins': high_risk_count,    # RSI > 70
                    'total_risky_coins': overbought_count + high_risk_count,
                    'overbought_percentage': round(((overbought_count + high_risk_count) / total_coins * 100), 1) if total_coins > 0 else 0,
                    'top_risky_coins': sorted(portfolio_info, key=lambda x: x['rsi'], reverse=True)[:5]
                },
                
                # Sinais Detalhados
                'signal_breakdown': {
                    'btc_overextension': signals.get('btc_overextension', {}),
                    'extreme_euphoria': signals.get('extreme_euphoria', {}),
                    'market_structure': signals.get('market_structure', {}),
                    'technical_signals': signals.get('technical_signals', {})
                },
                
                # Recomendação
                'recommendation': self._get_recommendation(risk_score, market_data)
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Erro ao preparar dashboard: {e}")
            return {}
    
    def _get_ma_trend(self, btc_data):
        """Determina tendência da MA50"""
        try:
            # Usar as chaves corretas dos dados recebidos
            current_price = btc_data.get('usd', btc_data.get('current_price', 0))
            
            # Para as médias móveis, tentar primeiro indicators, depois as chaves diretas
            indicators = btc_data.get('indicators', {})
            ma50 = indicators.get('ma_short', btc_data.get('ma_50', btc_data.get('ma_short', 0)))
            ma200 = indicators.get('ma_long', btc_data.get('ma_200', btc_data.get('ma_long', 0)))
            
            if ma50 > ma200 * 1.1:
                return "📈 Forte Alta"
            elif ma50 > ma200:
                return "📈 Alta"
            elif ma50 < ma200 * 0.9:
                return "📉 Forte Baixa"
            else:
                return "📊 Lateral"
        except:
            return "N/A"
    
    def _get_fear_greed_level(self, fg_value):
        """Converte valor F&G em texto descritivo"""
        try:
            if fg_value >= 80:
                return "🔥 Ganância Extrema"
            elif fg_value >= 60:
                return "😃 Ganância"
            elif fg_value >= 40:
                return "😐 Neutro"
            elif fg_value >= 20:
                return "😰 Medo"
            else:
                return "😱 Medo Extremo"
        except:
            return "N/A"
    
    def _get_market_trend(self, market_data):
        """Analisa tendência geral do mercado"""
        try:
            fear_greed_data = market_data.get('fear_greed_index', {})
            fg = fear_greed_data.get('value', 50) if isinstance(fear_greed_data, dict) else 50
            btc_dom = market_data.get('btc_dominance', 50)
            
            if fg > 70 and btc_dom > 60:
                return "🚀 Bull Market BTC"
            elif fg > 70 and btc_dom < 45:
                return "🌈 Altseason"
            elif fg < 30:
                return "🐻 Bear Market"
            else:
                return "📊 Consolidação"
        except:
            return "N/A"
    
    def _get_recommendation(self, risk_score, market_data):
        """Gera recomendação baseada no risco"""
        try:
            if risk_score >= 85:
                return "🚨 RISCO EXTREMO - Considere realizar lucros imediatamente"
            elif risk_score >= 70:
                return "⚠️ RISCO ALTO - Prepare estratégia de saída"
            elif risk_score >= 50:
                return "🟡 RISCO MÉDIO - Monitore de perto"
            elif risk_score >= 30:
                return "🟢 RISCO BAIXO - Mercado saudável"
            else:
                return "💎 RISCO MÍNIMO - Boa oportunidade de acumular"
        except:
            return "N/A"
    
    def _should_send_alert(self, risk_score):
        """Determina se deve enviar alerta baseado nas configurações"""
        try:
            # Se relatório diário habilitado, sempre enviar
            send_daily = self.cycle_config.get('send_daily_report', False)
            min_risk = self.cycle_config.get('min_risk_for_alert', 30)
            
            if send_daily:
                return True
            
            # Senão, só enviar se atingir score mínimo
            return risk_score >= min_risk
            
        except:
            return risk_score >= 80  # Fallback
    
    def format_cycle_dashboard_alert(self, analysis):
        """
        Formata alerta de dashboard de topo de ciclo
        
        Args:
            analysis: Resultado da análise com dashboard
            
        Returns:
            str: Mensagem formatada para Telegram
        """
        try:
            dashboard = analysis.get('dashboard', {})
            risk_score = analysis.get('risk_score', 0)
            risk_level = analysis.get('risk_level', 'BAIXO')
            
            # Determinar emoji e cor do risco
            if risk_score >= 85:
                risk_emoji = "🚨"
                risk_color = "CRÍTICO"
            elif risk_score >= 70:
                risk_emoji = "⚠️"
                risk_color = "ALTO"
            elif risk_score >= 50:
                risk_emoji = "🟡"
                risk_color = "MÉDIO"
            elif risk_score >= 30:
                risk_emoji = "🟢"
                risk_color = "BAIXO"
            else:
                risk_emoji = "💎"
                risk_color = "MÍNIMO"
            
            # Header do Dashboard
            message = f"""📊 <b>DASHBOARD TOPO DE CICLO</b> 📊

{risk_emoji} <b>RISCO DE TOPO: {risk_score}/100</b> ({risk_color})
🕐 {dashboard.get('timestamp', 'N/A')}

━━━━━━━━━━━━━━━━━━━━

💰 <b>MÉTRICAS BITCOIN:</b>
💵 Preço: {dashboard.get('btc_metrics', {}).get('price', 'N/A')}
📊 MA200 Múltiplo: {dashboard.get('btc_metrics', {}).get('ma200_multiple', 'N/A')}x
📈 MA50 Tendência: {dashboard.get('btc_metrics', {}).get('ma50_trend', 'N/A')}
📋 RSI: {dashboard.get('btc_metrics', {}).get('rsi', 'N/A')}
📏 Distância MA200: {dashboard.get('btc_metrics', {}).get('distance_from_ma200', 'N/A')}

━━━━━━━━━━━━━━━━━━━━

🌍 <b>MÉTRICAS DE MERCADO:</b>
😰 Fear & Greed: {dashboard.get('market_metrics', {}).get('fear_greed', 'N/A')} - {dashboard.get('market_metrics', {}).get('fear_greed_level', 'N/A')}
👑 BTC Dominance: {dashboard.get('market_metrics', {}).get('btc_dominance', 'N/A')}
⚖️ ETH/BTC Ratio: {dashboard.get('market_metrics', {}).get('eth_btc_ratio', 'N/A')}
📊 Tendência Geral: {dashboard.get('market_metrics', {}).get('market_cap_trend', 'N/A')}

━━━━━━━━━━━━━━━━━━━━

📈 <b>ESTATÍSTICAS DO PORTFÓLIO:</b>
🎯 Moedas Rastreadas: {dashboard.get('portfolio_stats', {}).get('total_coins_tracked', 0)}
🔥 Sobrecompradas: {dashboard.get('portfolio_stats', {}).get('overbought_coins', 0)} ({dashboard.get('portfolio_stats', {}).get('overbought_percentage', 0)}%)"""

            # Top 3 moedas mais arriscadas
            risky_coins = dashboard.get('portfolio_stats', {}).get('top_risky_coins', [])[:3]
            if risky_coins:
                message += "\n\n🎯 <b>TOP RISCO (RSI):</b>"
                for coin in risky_coins:
                    status_emoji = "🔥" if coin.get('rsi', 0) > 75 else "📊"
                    message += f"\n{status_emoji} {coin.get('symbol', 'N/A')}: RSI {coin.get('rsi', 0):.1f}"

            message += "\n\n━━━━━━━━━━━━━━━━━━━━"

            # Recomendação principal
            recommendation = dashboard.get('recommendation', 'N/A')
            message += f"\n\n💡 <b>RECOMENDAÇÃO:</b>\n{recommendation}"

            # Quebra de sinais resumida
            signals = analysis.get('signals', {})
            active_signals = []
            
            # Verificar sinais ativos
            if signals.get('btc_overextension', {}).get('active_signals', 0) > 0:
                active_signals.append("📈 BTC Sobreestendido")
            
            if signals.get('extreme_euphoria', {}).get('active_signals', 0) > 0:
                active_signals.append("🔥 Euforia Extrema")
                
            if signals.get('market_structure', {}).get('active_signals', 0) > 0:
                active_signals.append("🏗️ Estrutura Perigosa")
                
            if signals.get('technical_signals', {}).get('active_signals', 0) > 0:
                active_signals.append("⚡ Sinais Técnicos")

            if active_signals:
                message += f"\n\n🚨 <b>SINAIS ATIVOS:</b>"
                for signal in active_signals:
                    message += f"\n• {signal}"
            else:
                message += f"\n\n✅ <b>Nenhum sinal crítico ativo</b>"

            # Footer com próxima atualização
            config = self.config.get('professional_alerts', {}).get('cycle_top_detection', {})
            cooldown = config.get('cooldown_hours', 6)
            message += f"\n\n🔄 Próxima atualização em ~{cooldown}h"
            message += f"\n📱 Bot: Crypto Market Alert v2.0"
            
            return message
            
        except Exception as e:
            self.logger.error(f"Erro ao formatar dashboard: {e}")
            return f"❌ Erro ao gerar dashboard de topo de ciclo: {e}"
    
    def _get_default_result(self):
        """Retorna resultado padrão em caso de erro"""
        return {
            'risk_score': 0,
            'risk_level': 'BAIXO',
            'signals': {},
            'dashboard': {},
            'should_alert': False
        }
