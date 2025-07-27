"""
Strategy module for defining alert conditions and rules
Implements various trading strategies and signal detection
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from src.indicators import TechnicalIndicators
from src.utils import CooldownManager
from src.professional_analyzer import ProfessionalCryptoAnalyzer
from src.cycle_top_detector import CycleTopDetector
from src.strategic_advisor import StrategicAdvisor


class AlertStrategy:
    """Define and evaluate alert conditions based on technical indicators and market data"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the alert strategy
        
        Args:
            config: Configuration dictionary containing strategy parameters
        """
        self.config = config
        self.indicators = TechnicalIndicators()
        self.cooldown_manager = CooldownManager()
        self.professional_analyzer = ProfessionalCryptoAnalyzer(config)
        self.cycle_top_detector = CycleTopDetector(config)
        # Use hybrid fetcher for strategic advisor to avoid rate limits
        self.strategic_advisor = StrategicAdvisor(config.get('config_path', 'config/config.yaml'))
        self.logger = logging.getLogger(__name__)
    
    def evaluate_price_alerts(self, coin_data: Dict[str, Any], coin_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate price-based alert conditions
        
        Args:
            coin_data: Current coin market data
            coin_config: Coin-specific configuration
            
        Returns:
            List of triggered price alerts
        """
        alerts = []
        current_price = coin_data.get('usd')
        coin_name = coin_config.get('name', 'Unknown')
        
        if not current_price:
            return alerts
        
        alert_config = coin_config.get('alerts', {})
        cooldown = self.config.get('alert_cooldown', {}).get('price_alert', 60)
        
        # Price above threshold
        price_above = alert_config.get('price_above')
        if price_above and current_price > price_above:
            if self.cooldown_manager.can_send_alert('price_above', coin_name, cooldown):
                alerts.append({
                    'type': 'price_above',
                    'coin': coin_name,
                    'message': f"🚀 {coin_name} price alert: ${current_price:,.2f} (above ${price_above:,.2f})",
                    'priority': 'high',
                    'current_price': current_price,
                    'threshold': price_above
                })
        
        # Price below threshold
        price_below = alert_config.get('price_below')
        if price_below and current_price < price_below:
            if self.cooldown_manager.can_send_alert('price_below', coin_name, cooldown):
                alerts.append({
                    'type': 'price_below',
                    'coin': coin_name,
                    'message': f"📉 {coin_name} price alert: ${current_price:,.2f} (below ${price_below:,.2f})",
                    'priority': 'high',
                    'current_price': current_price,
                    'threshold': price_below
                })
        
        return alerts
    
    def evaluate_rsi_alerts(self, indicators_data: Dict[str, float], coin_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate RSI-based alert conditions
        
        Args:
            indicators_data: Current indicator values
            coin_config: Coin-specific configuration
            
        Returns:
            List of triggered RSI alerts
        """
        alerts = []
        rsi = indicators_data.get('rsi')
        coin_name = coin_config.get('name', 'Unknown')
        
        if rsi is None:
            return alerts
        
        alert_config = coin_config.get('alerts', {})
        cooldown = self.config.get('alert_cooldown', {}).get('indicator_alert', 30)
        
        # RSI oversold condition
        rsi_oversold = alert_config.get('rsi_oversold', 30)
        if rsi <= rsi_oversold:
            if self.cooldown_manager.can_send_alert('rsi_oversold', coin_name, cooldown):
                alerts.append({
                    'type': 'rsi_oversold',
                    'coin': coin_name,
                    'message': f"💹 {coin_name} RSI oversold: {rsi:.2f} (≤ {rsi_oversold})",
                    'priority': 'medium',
                    'rsi_value': rsi,
                    'threshold': rsi_oversold
                })
        
        # RSI overbought condition
        rsi_overbought = alert_config.get('rsi_overbought', 70)
        if rsi >= rsi_overbought:
            if self.cooldown_manager.can_send_alert('rsi_overbought', coin_name, cooldown):
                alerts.append({
                    'type': 'rsi_overbought',
                    'coin': coin_name,
                    'message': f"🔥 {coin_name} RSI overbought: {rsi:.2f} (≥ {rsi_overbought})",
                    'priority': 'medium',
                    'rsi_value': rsi,
                    'threshold': rsi_overbought
                })
        
        return alerts
    
    def evaluate_macd_alerts(self, df, coin_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate MACD crossover alerts
        
        Args:
            df: Price data DataFrame
            coin_config: Coin-specific configuration
            
        Returns:
            List of triggered MACD alerts
        """
        alerts = []
        coin_name = coin_config.get('name', 'Unknown')
        cooldown = self.config.get('alert_cooldown', {}).get('indicator_alert', 30)
        
        # Calculate MACD
        macd_data = self.indicators.calculate_macd(df)
        if not macd_data or macd_data['macd'] is None or macd_data['signal'] is None:
            return alerts
        
        # Detect crossovers
        crossovers = self.indicators.detect_crossovers(macd_data['macd'], macd_data['signal'])
        
        # Bullish MACD crossover
        if crossovers['bullish_crossover']:
            if self.cooldown_manager.can_send_alert('macd_bullish', coin_name, cooldown):
                alerts.append({
                    'type': 'macd_bullish',
                    'coin': coin_name,
                    'message': f"📈 {coin_name} MACD bullish crossover detected",
                    'priority': 'medium',
                    'signal': 'bullish'
                })
        
        # Bearish MACD crossover
        if crossovers['bearish_crossover']:
            if self.cooldown_manager.can_send_alert('macd_bearish', coin_name, cooldown):
                alerts.append({
                    'type': 'macd_bearish',
                    'coin': coin_name,
                    'message': f"📉 {coin_name} MACD bearish crossover detected",
                    'priority': 'medium',
                    'signal': 'bearish'
                })
        
        return alerts
    
    def evaluate_ma_crossover_alerts(self, df, coin_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate Moving Average crossover alerts (Golden Cross / Death Cross)
        
        Args:
            df: Price data DataFrame
            coin_config: Coin-specific configuration
            
        Returns:
            List of triggered MA crossover alerts
        """
        alerts = []
        coin_name = coin_config.get('name', 'Unknown')
        cooldown = self.config.get('alert_cooldown', {}).get('indicator_alert', 30)
        
        # Calculate moving averages
        ma_data = self.indicators.calculate_moving_averages(df)
        if not ma_data or ma_data['ma_short'] is None or ma_data['ma_long'] is None:
            return alerts
        
        # Detect MA crossovers
        crossovers = self.indicators.detect_crossovers(ma_data['ma_short'], ma_data['ma_long'])
        
        # Golden Cross (bullish)
        if crossovers['bullish_crossover']:
            if self.cooldown_manager.can_send_alert('golden_cross', coin_name, cooldown):
                alerts.append({
                    'type': 'golden_cross',
                    'coin': coin_name,
                    'message': f"✨ {coin_name} Golden Cross detected (MA50 > MA200)",
                    'priority': 'high',
                    'signal': 'bullish'
                })
        
        # Death Cross (bearish)
        if crossovers['bearish_crossover']:
            if self.cooldown_manager.can_send_alert('death_cross', coin_name, cooldown):
                alerts.append({
                    'type': 'death_cross',
                    'coin': coin_name,
                    'message': f"💀 {coin_name} Death Cross detected (MA50 < MA200)",
                    'priority': 'high',
                    'signal': 'bearish'
                })
        
        return alerts
    
    def suggest_action(self, alert: Dict[str, Any]) -> str:
        """
        Suggest an action based on the alert type and context.

        Args:
            alert: The alert dictionary containing type and other details

        Returns:
            A human-readable action recommendation
        """
        alert_type = alert.get("type")
        
        if alert_type == "price_above":
            return "Consider selling or taking profit"
        elif alert_type == "price_below":
            return "Buy or reinforce position"
        elif alert_type == "rsi_oversold":
            return "Buy or reinforce position"
        elif alert_type == "rsi_overbought":
            return "Consider selling or taking profit"
        elif alert_type == "macd_bullish":
            return "Watch for uptrend, consider entering position"
        elif alert_type == "macd_bearish":
            return "Watch for downtrend, consider reducing position"
        elif alert_type == "golden_cross":
            return "Strong bullish signal, consider entering position"
        elif alert_type == "death_cross":
            return "Strong bearish signal, consider reducing position"
        elif alert_type == "btc_dominance_high":
            return "Focus on BTC, reduce altcoin exposure"
        elif alert_type == "btc_dominance_low":
            return "Rotate BTC into altcoins"
        elif alert_type == "eth_btc_ratio_high":
            return "Consider rotating ETH into BTC"
        elif alert_type == "eth_btc_ratio_low":
            return "Rotate BTC into ETH"
        elif alert_type == "extreme_fear":
            return "Possibly accumulate"
        elif alert_type == "extreme_greed":
            return "Evaluate profit taking"
        elif alert_type == "altseason":
            return "Rotate BTC into altcoins"
        elif alert_type == "exit_to_usdc":
            return "Convert to USDC to secure profits and avoid potential downturns"
        
        return "No action suggested"

    def evaluate_altseason(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate if the market is in an altseason phase.

        Args:
            market_data: Market-wide metric data

        Returns:
            An altseason alert dictionary if conditions are met, otherwise None
        """
        btc_dominance = market_data.get("btc_dominance")
        eth_btc_ratio = market_data.get("eth_btc_ratio")

        if btc_dominance is not None and eth_btc_ratio is not None:
            if btc_dominance < 45 and eth_btc_ratio > 0.07:
                return {
                    "type": "altseason",
                    "coin": "Market",
                    "message": "🌟 Altseason detected: BTC dominance < 45% and ETH/BTC ratio > 0.07",
                    "priority": "high",
                    "btc_dominance": btc_dominance,
                    "eth_btc_ratio": eth_btc_ratio,
                    "action": self.suggest_action({"type": "altseason"})
                }

        return None

    def evaluate_market_metric_alerts(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate market-wide metric alerts (BTC dominance, ETH/BTC ratio, etc.)

        Args:
            market_data: Market metric data

        Returns:
            List of triggered market metric alerts
        """
        alerts = []
        cooldown = self.config.get("alert_cooldown", {}).get("market_metric_alert", 120)
        metric_config = self.config.get("market_metrics", {})

        # BTC Dominance alerts
        btc_dominance = market_data.get("btc_dominance")
        if btc_dominance is not None:
            btc_config = metric_config.get("btc_dominance", {})

            # BTC dominance above threshold
            above_threshold = btc_config.get("above")
            if above_threshold and btc_dominance > above_threshold:
                if self.cooldown_manager.can_send_alert("btc_dom_high", "BTC", cooldown):
                    alert = {
                        "type": "btc_dominance_high",
                        "coin": "BTC",
                        "message": f"🔶 BTC Dominance high: {btc_dominance:.2f}% (above {above_threshold}%)",
                        "priority": "medium",
                        "value": btc_dominance,
                        "threshold": above_threshold
                    }
                    alert["action"] = self.suggest_action(alert)
                    alerts.append(alert)

            # BTC dominance below threshold
            below_threshold = btc_config.get("below")
            if below_threshold and btc_dominance < below_threshold:
                if self.cooldown_manager.can_send_alert("btc_dom_low", "BTC", cooldown):
                    alert = {
                        "type": "btc_dominance_low",
                        "coin": "BTC",
                        "message": f"🔷 BTC Dominance low: {btc_dominance:.2f}% (below {below_threshold}%)",
                        "priority": "medium",
                        "value": btc_dominance,
                        "threshold": below_threshold
                    }
                    alert["action"] = self.suggest_action(alert)
                    alerts.append(alert)

        # ETH/BTC ratio alerts
        eth_btc_ratio = market_data.get("eth_btc_ratio")
        if eth_btc_ratio is not None:
            ratio_config = metric_config.get("eth_btc_ratio", {})

            # ETH/BTC ratio above threshold
            above_threshold = ratio_config.get("above")
            if above_threshold and eth_btc_ratio > above_threshold:
                if self.cooldown_manager.can_send_alert("eth_btc_high", "ETH", cooldown):
                    alert = {
                        "type": "eth_btc_ratio_high",
                        "coin": "ETH",
                        "message": f"⚡ ETH/BTC ratio high: {eth_btc_ratio:.6f} (above {above_threshold})",
                        "priority": "medium",
                        "value": eth_btc_ratio,
                        "threshold": above_threshold
                    }
                    alert["action"] = self.suggest_action(alert)
                    alerts.append(alert)

            # ETH/BTC ratio below threshold
            below_threshold = ratio_config.get("below")
            if below_threshold and eth_btc_ratio < below_threshold:
                if self.cooldown_manager.can_send_alert("eth_btc_low", "ETH", cooldown):
                    alert = {
                        "type": "eth_btc_ratio_low",
                        "coin": "ETH",
                        "message": f"""<b>⚡ ETH/BTC RATIO BAIXO</b>

📊 <b>Ratio Atual:</b> {eth_btc_ratio:.6f}
📉 <b>Threshold:</b> {below_threshold}

<b>🎯 AÇÃO:</b>
🔄 Rode posição de BTC para ETH
💰 ETH está relativamente barato vs BTC
📈 Potencial de outperformance do ETH""",
                        "priority": "medium",
                        "value": eth_btc_ratio,
                        "threshold": below_threshold
                    }
                    alerts.append(alert)

        # Fear & Greed Index alerts
        fear_greed = market_data.get("fear_greed_index")
        if fear_greed is not None:
            fg_config = metric_config.get("fear_greed_index", {})
            value = fear_greed.get("value", 0)
            classification = fear_greed.get("value_classification", "Neutral")

            # Extreme Fear
            extreme_fear = fg_config.get("extreme_fear", 20)
            if value <= extreme_fear:
                if self.cooldown_manager.can_send_alert("fear_greed_fear", "Market", cooldown):
                    alert = {
                        "type": "extreme_fear",
                        "coin": "Market",
                        "message": f"😰 Extreme Fear detected: {value}/100 ({classification})",
                        "priority": "high",
                        "value": value,
                        "classification": classification
                    }
                    alert["action"] = self.suggest_action(alert)
                    alerts.append(alert)

            # Extreme Greed
            extreme_greed = fg_config.get("extreme_greed", 80)
            if value >= extreme_greed:
                if self.cooldown_manager.can_send_alert("fear_greed_greed", "Market", cooldown):
                    alert = {
                        "type": "extreme_greed",
                        "coin": "Market",
                        "message": f"🤑 Extreme Greed detected: {value}/100 ({classification})",
                        "priority": "high",
                        "value": value,
                        "classification": classification
                    }
                    alert["action"] = self.suggest_action(alert)
                    alerts.append(alert)

        # Altseason detection
        altseason_alert = self.evaluate_altseason(market_data)
        if altseason_alert:
            alerts.append(altseason_alert)

        return alerts
    
    def evaluate_exit_to_usdc(self, coin_data: Dict[str, Any], market_data: Dict[str, Any], coin_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate if it's a good moment to exit to USDC based on market conditions.

        Args:
            coin_data: Current coin market data
            market_data: Market-wide metric data
            coin_config: Coin-specific configuration

        Returns:
            An exit alert dictionary if conditions are met, otherwise None
        """
        coin_name = coin_config.get('name', 'Unknown')
        rsi = coin_data.get('indicators', {}).get('rsi')
        macd_signal = coin_data.get('indicators', {}).get('macd_signal')
        macd = coin_data.get('indicators', {}).get('macd')
        btc_dominance = market_data.get('btc_dominance')
        fear_greed = market_data.get('fear_greed_index', {}).get('value')

        # Conditions for exit
        if (
            rsi is not None and rsi > 70 and  # RSI overbought
            macd is not None and macd_signal is not None and macd < macd_signal and  # Bearish MACD crossover
            btc_dominance is not None and btc_dominance > 50 and  # BTC dominance rising
            fear_greed is not None and fear_greed >= 80  # Extreme greed
        ):
            return {
                "type": "exit_to_usdc",
                "coin": coin_name,
                "message": f"💵 Exit to USDC: {coin_name} shows overbought RSI ({rsi:.2f}), bearish MACD, and market greed ({fear_greed}/100)",
                "priority": "high",
                "action": "Convert {coin_name} to USDC to avoid potential market downturn"
            }

        return None

    def evaluate_all_alerts(self, coin_data: Dict[str, Any], market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate all alert conditions for all configured coins

        Args:
            coin_data: Dictionary with coin market data
            market_data: Market-wide metric data

        Returns:
            List of all triggered alerts
        """
        all_alerts = []

        # NOVA ANÁLISE PROFISSIONAL PRIORITÁRIA
        try:
            # Obter sentimento geral do mercado
            market_sentiment = self.professional_analyzer.get_market_sentiment(market_data)
            
            # Adicionar alerta de contexto de mercado se relevante
            if market_sentiment['confidence'] >= 70:
                phase = market_sentiment['phase']
                bias = market_sentiment['action_bias']
                risk = market_sentiment['risk_level']
                desc = market_sentiment['description']
                
                market_message = f"""<b>🌍 CONTEXTO DO MERCADO</b>

📊 <b>Fase:</b> {phase}
🎯 <b>Estratégia:</b> {bias}
⚠️ <b>Risco:</b> {risk}

<b>📝 Análise:</b>
{desc}

<b>🎯 RECOMENDAÇÃO GERAL:</b>"""
                
                if bias == 'COMPRA AGRESSIVA':
                    market_message += """
💰 Momento excelente para acumulação
🚀 Use 40-60% do capital em oportunidades
⏰ Janela de oportunidade limitada"""
                elif bias == 'VENDA PARCIAL':
                    market_message += """
⚠️ Realize 30-50% dos lucros
💵 Aumente posição em USDC
🛡️ Proteja capital acumulado"""
                elif bias == 'ROTAÇÃO ALTCOINS':
                    market_message += """
🔄 Mova capital de BTC para altcoins
🌟 Altseason em andamento
📈 Foque em projetos fundamentalmente sólidos"""
                else:
                    market_message += """
✋ Mantenha posições atuais
👀 Aguarde sinais mais definidos
📊 Mercado em consolidação"""
                
                market_alert = {
                    'type': 'market_context',
                    'coin': 'MERCADO',
                    'message': market_message,
                    'priority': 'high' if market_sentiment['confidence'] >= 85 else 'medium',
                    'market_phase': market_sentiment['phase'],
                    'confidence': market_sentiment['confidence']
                }
                all_alerts.append(market_alert)

            # Analisar cada moeda com contexto profissional
            for coin_config in self.config.get('coins', []):
                coin_id = coin_config.get('coingecko_id')
                coin_name = coin_config.get('name')

                if coin_id not in coin_data:
                    continue

                coin_market_data = coin_data[coin_id]
                
                # Calcular indicadores se disponível
                historical_df = coin_market_data.get('historical')
                if historical_df is not None and not historical_df.empty:
                    indicators_data = self.indicators.get_latest_indicator_values(
                        historical_df, 
                        self.config.get('indicators', {})
                    )
                    coin_market_data['indicators'] = indicators_data

                    # ANÁLISE PROFISSIONAL PRINCIPAL
                    coin_analysis = self.professional_analyzer.analyze_coin_signals(
                        coin_market_data, coin_config, market_sentiment
                    )
                    
                    # Gerar alerta profissional se significativo
                    professional_alert = self.professional_analyzer.generate_professional_alert(
                        coin_analysis, market_sentiment
                    )
                    
                    # Filtrar alertas baseado na configuração
                    if professional_alert:
                        prof_config = self.config.get('professional_alerts', {})
                        only_actionable = prof_config.get('only_actionable', True)
                        min_strength = prof_config.get('min_signal_strength', 35)
                        
                        # Aplicar filtros
                        if only_actionable and professional_alert.get('urgency') == 'BAIXA':
                            continue  # Pular alertas de baixa urgência
                        
                        if abs(professional_alert.get('signal_strength', 0)) < min_strength:
                            continue  # Pular sinais fracos
                        
                        all_alerts.append(professional_alert)

            # DETECÇÃO DE TOPO DE CICLO (executar uma vez por análise)
            try:
                self.logger.info("Iniciando análise de topo de ciclo...")
                self.logger.debug(f"Dados fornecidos para análise: coin_data={coin_data}, market_data={market_data}")

                # Usar o novo método analyze_cycle_top que inclui dashboard
                cycle_analysis = self.cycle_top_detector.analyze_cycle_top(
                    coin_data, market_data
                )

                self.logger.debug(f"Resultado da análise de topo de ciclo: {cycle_analysis}")
                
                # Verificar se deve enviar alerta (inclui dashboard diário)
                if cycle_analysis and cycle_analysis.get('should_alert', False):
                    # Usar o novo formato de dashboard
                    cycle_alert_message = self.cycle_top_detector.format_cycle_dashboard_alert(cycle_analysis)
                    
                    if cycle_alert_message:
                        # Determinar prioridade baseada no risk score
                        risk_score = cycle_analysis.get('risk_score', 0)
                        if risk_score >= 80:
                            priority = 'critical'
                        elif risk_score >= 50:
                            priority = 'high'
                        else:
                            priority = 'info'
                            
                        cycle_alert = {
                            'type': 'cycle_top_dashboard',
                            'priority': priority,
                            'message': cycle_alert_message,
                            'timestamp': datetime.now(),
                            'risk_score': risk_score,
                            'risk_level': cycle_analysis.get('risk_level', 'BAIXO'),
                            'dashboard': cycle_analysis.get('dashboard', {})
                        }
                        all_alerts.append(cycle_alert)
                        self.logger.info(f"Dashboard de topo de ciclo gerado - Risk Score: {risk_score}")
                        
            except Exception as e:
                self.logger.error(f"Error in cycle top detection: {e}")

                        # NOVO: ANÁLISE ESTRATÉGICA CONSOLIDADA (Goal: 1 BTC + 10 ETH)
            # Esta é agora a mensagem PRINCIPAL que substitui todas as outras
            try:
                self.logger.info("Iniciando análise estratégica consolidada...")
                
                # Verificar se deve enviar relatório estratégico
                strategic_config = self.config.get('strategic_alerts', {})
                if strategic_config.get('enabled', True):
                    strategic_report = self.strategic_advisor.generate_strategic_report()
                    
                    if strategic_report and "Erro" not in strategic_report:
                        strategic_alert = {
                            'type': 'strategic_consolidated',
                            'priority': 'high',
                            'message': strategic_report,
                            'timestamp': datetime.now(),
                            'category': 'STRATEGIC_OVERVIEW'
                        }
                        all_alerts.append(strategic_alert)
                        self.logger.info("Relatório estratégico consolidado gerado")
                        
                        # Se strategic_alerts.consolidate_alerts for True, retorne apenas esta mensagem
                        if strategic_config.get('consolidate_alerts', True):
                            self.logger.info("Modo consolidado ativo - enviando apenas análise estratégica")
                            return [strategic_alert]  # Retorna apenas a mensagem estratégica
                        
            except Exception as e:
                self.logger.error(f"Error in strategic analysis: {e}")

            # ANÁLISE PROFISSIONAL (só executa se não estiver em modo consolidado)
            strategic_config = self.config.get('strategic_alerts', {})
            if not strategic_config.get('consolidate_alerts', True):
                try:
                    # Obter sentimento geral do mercado
                    market_sentiment = self.professional_analyzer.get_market_sentiment(market_data)
                    
                    # Adicionar alerta de contexto de mercado se relevante
                    if market_sentiment['confidence'] >= 70:
                        # ... resto da análise profissional original
                        pass
                        
                except Exception as e:
                    self.logger.error(f"Erro na análise profissional: {e}")

        except Exception as e:
            self.logger.error(f"Erro geral na análise: {e}")

        # Alertas de mercado básicos como backup
        market_alerts = self.evaluate_market_metric_alerts(market_data)
        all_alerts.extend(market_alerts)

        # Ordenar por prioridade e força do sinal
        def alert_priority_score(alert):
            priority_scores = {'high': 0, 'medium': 1, 'low': 2}
            confidence_bonus = -alert.get('confidence', 0) / 100  # Maior confiança = menor score
            return priority_scores.get(alert.get('priority', 'low'), 2) + confidence_bonus

        all_alerts.sort(key=alert_priority_score)

        return all_alerts
    
    def get_market_summary(self, coin_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a market summary for reporting with structured format
        
        Args:
            coin_data: Dictionary with coin market data
            market_data: Market-wide metric data
            
        Returns:
            Market summary dictionary with structured format
        """
        # Calculate portfolio values
        altcoin_value = 0
        btc_amount = 0
        eth_amount = 0
        btc_price = 0
        eth_price = 0
        
        # Get BTC and ETH prices and amounts
        for coin_config in self.config.get('coins', []):
            coin_id = coin_config.get('coingecko_id')
            coin_name = coin_config.get('name')
            current_amount = coin_config.get('current_amount', 0)
            
            if coin_id in coin_data:
                coin_price = coin_data[coin_id].get('usd', 0)
                
                if coin_name == 'BTC':
                    btc_amount = current_amount
                    btc_price = coin_price
                elif coin_name == 'ETH':
                    eth_amount = current_amount
                    eth_price = coin_price
                elif coin_name not in ['BTC', 'ETH']:
                    # Calculate altcoin value (excluding BTC and ETH)
                    altcoin_value += current_amount * coin_price
        
        # Calculate goal value (1 BTC + 10 ETH)
        goal_btc = 1.0
        goal_eth = 10.0
        goal_value = (goal_btc * btc_price) + (goal_eth * eth_price)
        
        # Calculate current total portfolio value in BTC
        current_portfolio_btc = 0
        if btc_price > 0:
            current_portfolio_btc = (altcoin_value + (btc_amount * btc_price) + (eth_amount * eth_price)) / btc_price
        
        # Calculate progress towards goal
        progress_percentage = 0
        if goal_value > 0:
            current_total_value = altcoin_value + (btc_amount * btc_price) + (eth_amount * eth_price)
            progress_percentage = (current_total_value / goal_value) * 100
        
        # Get market metrics
        btc_dominance = market_data.get('btc_dominance', 0)
        fear_greed = market_data.get('fear_greed_index', {})
        fear_greed_value = fear_greed.get('value', 0) if isinstance(fear_greed, dict) else 0
        fear_greed_classification = fear_greed.get('value_classification', 'Neutral') if isinstance(fear_greed, dict) else 'Neutral'
        
        # Analyze market phase
        market_phase = self.analyze_market_phase(market_data)
        
        # Get ETH/BTC ratio
        eth_btc_ratio = market_data.get('eth_btc_ratio', 0.0320)
        
        # Analyze top altcoins performance
        top_altcoins = []
        for coin_config in self.config.get('coins', []):
            coin_id = coin_config.get('coingecko_id')
            coin_name = coin_config.get('name')
            
            if coin_id in coin_data and coin_name not in ['BTC', 'ETH']:
                change_24h = coin_data[coin_id].get('usd_24h_change', 0)
                if abs(change_24h) > 20:  # Only show significant moves
                    action = "VENDA IMEDIATA" if change_24h > 100 else "Monitore"
                    emoji = "🚀" if change_24h > 100 else "👁️"
                    score = min(100, max(0, int(50 + change_24h/2)))  # Simple score calculation
                    
                    top_altcoins.append({
                        'name': coin_name.lower(),
                        'change': change_24h,
                        'action': action,
                        'emoji': emoji,
                        'score': score
                    })
        
        # Sort by change percentage (descending)
        top_altcoins.sort(key=lambda x: x['change'], reverse=True)
        top_altcoins = top_altcoins[:3]  # Top 3
        
        # Generate structured report
        report_lines = [
            "🚨🎯 ESTRATÉGIA CRYPTO - Goal: 1 BTC + 10 ETH",
            "=========================================",
            "",
            "💰 ANÁLISE DO PORTFÓLIO:",
            f"   Valor das Altcoins: ${altcoin_value:,.0f}",
            f"   Meta (1 BTC + 10 ETH): ${goal_value:,.0f}",
            f"   Equivalente em BTC: {current_portfolio_btc:.2f} BTC",
            f"   Alcance da Meta: {progress_percentage:.1f}%",
            "",
            "📈 Contexto do Mercado:",
            f"   BTC Dominance: {btc_dominance:.2f}%",
            f"   Fear & Greed: {fear_greed_value}/100 ({fear_greed_classification})",
            "",
            "📊 FASE DO MERCADO:",
            f"   Status: {market_phase} - Aguardando sinais",
            "   ⏳ AÇÃO: Mantenha posições atuais",
            "",
            "🔺 ANÁLISE DE TOPO:",
            "   Risco: 5/100 (MÍNIMO)",
            "   💎 AÇÃO: Risco mínimo - Acumule agressivamente",
            "",
            "🌟 ALTSEASON METRIC:",
            "   Status: TRANSITION (Score: 0)",
            "   ⏳ AÇÃO: Aguarde sinais mais claros",
            "",
            "⚖️ BTC/ETH RATIO:",
            f"   Ratio Atual: {eth_btc_ratio:.4f}",
            "   ⏳ AÇÃO: Mantenha proporção atual BTC/ETH",
            "",
            "💎 TOP ALTCOIN AÇÕES:"
        ]
        
        # Add top altcoins
        for altcoin in top_altcoins:
            if altcoin['action'] == "VENDA IMEDIATA":
                report_lines.append(f"   {altcoin['emoji']} {altcoin['name']}: +{altcoin['change']:.1f}% - {altcoin['action']}")
            else:
                report_lines.append(f"   {altcoin['emoji']} {altcoin['name']}: +{altcoin['change']:.1f}% - Score {altcoin['score']} - {altcoin['action']}")
        
        report_lines.append("")
        report_lines.append("⏰...")
        
        # Create summary with both old format (for compatibility) and new structured format
        summary = {
            'timestamp': datetime.now(),
            'coins': {},
            'market_metrics': market_data,
            'alerts_count': 0,
            'structured_report': '\n'.join(report_lines),
            'portfolio_analysis': {
                'altcoin_value': altcoin_value,
                'goal_value': goal_value,
                'btc_equivalent': current_portfolio_btc,
                'progress_percentage': progress_percentage,
                'btc_amount': btc_amount,
                'eth_amount': eth_amount,
                'btc_price': btc_price,
                'eth_price': eth_price
            }
        }
        
        # Process coin data (keep for compatibility)
        for coin_config in self.config.get('coins', []):
            coin_id = coin_config.get('coingecko_id')
            coin_name = coin_config.get('name')
            
            if coin_id in coin_data:
                coin_market_data = coin_data[coin_id]
                coin_summary = {
                    'price': coin_market_data.get('usd'),
                    'change_24h': coin_market_data.get('usd_24h_change'),
                    'market_cap': coin_market_data.get('usd_market_cap'),
                    'volume_24h': coin_market_data.get('usd_24h_vol')
                }
                
                # Add technical indicators if available
                historical_df = coin_market_data.get('historical')
                if historical_df is not None and not historical_df.empty:
                    indicators_data = self.indicators.get_latest_indicator_values(
                        historical_df, 
                        self.config.get('indicators', {})
                    )
                    coin_summary['indicators'] = indicators_data
                
                summary['coins'][coin_name] = coin_summary
        
        return summary
    
    def analyze_market_phase(self, market_data: Dict[str, Any]) -> str:
        """
        Determine the current market phase for context
        """
        btc_dominance = market_data.get('btc_dominance', 50)
        fear_greed = market_data.get('fear_greed_index', {}).get('value', 50)
        eth_btc_ratio = market_data.get('eth_btc_ratio', 0.05)
        
        if fear_greed <= 25 and btc_dominance > 55:
            return "BEAR_MARKET"  # Medo extremo + BTC dominance alta
        elif fear_greed >= 75 and btc_dominance < 45:
            return "ALTCOIN_EUPHORIA"  # Ganância + BTC dominance baixa
        elif btc_dominance < 45 and eth_btc_ratio > 0.07:
            return "ALTSEASON"  # Alt season em andamento
        elif fear_greed <= 30:
            return "ACCUMULATION"  # Momento de acumulação
        elif fear_greed >= 70:
            return "DISTRIBUTION"  # Momento de distribuição
        else:
            return "NEUTRAL"

    def get_professional_action(self, alert_type: str, coin_name: str, market_phase: str, 
                              current_price: float = None, rsi: float = None) -> str:
        """
        Generate professional trading actions based on market context
        """
        actions = {
            # Ações de SAÍDA (proteção de capital)
            "exit_to_usdc": f"🔴 VENDA IMEDIATA: Converta {coin_name} para USDC. Sinais de topo de mercado detectados.",
            
            "market_top_warning": f"⚠️ TOPO PRÓXIMO: Reduza 50-70% da posição em {coin_name}. Mantenha stop-loss em 15%.",
            
            "distribution_phase": f"📉 FASE DISTRIBUIÇÃO: Venda 30-50% da posição em {coin_name}. Mercado sobrecomprado.",
            
            # Ações de ENTRADA (oportunidades)
            "accumulation_zone": f"💰 ZONA ACUMULAÇÃO: Compre {coin_name} em tranches. RSI oversold + mercado em medo.",
            
            "golden_cross_buy": f"📈 COMPRA FORTE: {coin_name} rompeu resistência. Entre com 25-40% da posição disponível.",
            
            "fear_opportunity": f"💎 OPORTUNIDADE: Mercado em pânico. Acumule {coin_name} gradualmente (DCA).",
            
            # Ações de ROTAÇÃO
            "btc_to_alts": f"🔄 ROTAÇÃO: Venda 40-60% do BTC e compre altcoins ({coin_name}). Altseason iniciando.",
            
            "alts_to_btc": f"🔄 ROTAÇÃO: Venda {coin_name} e compre BTC. BTC dominance subindo.",
            
            "eth_rotation": f"⚡ ETH FORTE: Rode posição de BTC para ETH. Ratio ETH/BTC favorável.",
            
            # Ações de MANUTENÇÃO
            "hold_position": f"✋ MANTENHA: Posição em {coin_name} estável. Aguarde sinais mais claros.",
            
            "partial_profit": f"💰 LUCRO PARCIAL: Venda 20-30% da posição em {coin_name}. Preserve ganhos.",
            
            "stop_loss": f"🛑 STOP LOSS: Defina stop em 10-15% abaixo do preço atual de {coin_name}."
        }
        
        return actions.get(alert_type, f"Monitore {coin_name} - sem ação específica no momento.")

    def evaluate_comprehensive_signals(self, coin_data: Dict[str, Any], market_data: Dict[str, Any], 
                                     coin_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Avalia sinais combinados para gerar alertas profissionais acionáveis
        """
        alerts = []
        coin_name = coin_config.get('name', 'Unknown')
        coin_id = coin_config.get('coingecko_id')
        current_price = coin_data.get('usd', 0)
        indicators = coin_data.get('indicators', {})
        
        rsi = indicators.get('rsi')
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        ma_short = indicators.get('ma_short')
        ma_long = indicators.get('ma_long')
        
        market_phase = self.analyze_market_phase(market_data)
        fear_greed = market_data.get('fear_greed_index', {}).get('value', 50)
        btc_dominance = market_data.get('btc_dominance', 50)
        
        cooldown = self.config.get('alert_cooldown', {}).get('comprehensive_alert', 60)
        
        # SINAL DE SAÍDA FORTE (Combinação de múltiplos fatores de risco)
        if (rsi and rsi > 75 and 
            macd and macd_signal and macd < macd_signal and
            fear_greed > 80 and 
            market_phase in ['DISTRIBUTION', 'ALTCOIN_EUPHORIA']):
            
            if self.cooldown_manager.can_send_alert('exit_signal', coin_name, cooldown):
                alerts.append({
                    'type': 'exit_to_usdc',
                    'coin': coin_name,
                    'message': f"🔴 SINAL DE SAÍDA: {coin_name} - RSI {rsi:.1f} + MACD bearish + Mercado ganância extrema",
                    'priority': 'high',
                    'action': self.get_professional_action('exit_to_usdc', coin_name, market_phase, current_price, rsi),
                    'confidence': 'ALTA',
                    'market_phase': market_phase
                })
        
        # SINAL DE ENTRADA FORTE (Oportunidade de compra)
        elif (rsi and rsi < 30 and 
              fear_greed < 30 and 
              market_phase in ['ACCUMULATION', 'BEAR_MARKET']):
            
            if self.cooldown_manager.can_send_alert('buy_signal', coin_name, cooldown):
                alerts.append({
                    'type': 'accumulation_zone',
                    'coin': coin_name,
                    'message': f"💰 ZONA DE COMPRA: {coin_name} - RSI {rsi:.1f} + Mercado em medo + Preço ${current_price:,.4f}",
                    'priority': 'high',
                    'action': self.get_professional_action('accumulation_zone', coin_name, market_phase, current_price, rsi),
                    'confidence': 'ALTA',
                    'market_phase': market_phase
                })
        
        # GOLDEN CROSS + Contexto favorável
        elif (ma_short and ma_long and ma_short > ma_long and 
              rsi and 45 < rsi < 65 and
              market_phase not in ['DISTRIBUTION']):
            
            if self.cooldown_manager.can_send_alert('golden_cross', coin_name, cooldown):
                alerts.append({
                    'type': 'golden_cross_buy',
                    'coin': coin_name,
                    'message': f"📈 GOLDEN CROSS: {coin_name} - MA50 > MA200 + RSI neutro {rsi:.1f}",
                    'priority': 'high',
                    'action': self.get_professional_action('golden_cross_buy', coin_name, market_phase, current_price, rsi),
                    'confidence': 'MÉDIA-ALTA',
                    'market_phase': market_phase
                })
        
        # ALTSEASON - Rotação BTC para ALTs
        if (market_phase == 'ALTSEASON' and 
            coin_name != 'BTC' and 
            btc_dominance < 45):
            
            if self.cooldown_manager.can_send_alert('altseason_rotation', coin_name, cooldown):
                alerts.append({
                    'type': 'btc_to_alts',
                    'coin': coin_name,
                    'message': f"🌟 ALTSEASON ATIVA: BTC Dominance {btc_dominance:.1f}% - Momento para {coin_name}",
                    'priority': 'medium',
                    'action': self.get_professional_action('btc_to_alts', coin_name, market_phase, current_price),
                    'confidence': 'MÉDIA',
                    'market_phase': market_phase
                })
        
        # TAKE PROFIT - Lucro parcial em ganância
        if (rsi and rsi > 70 and 
            fear_greed > 70 and 
            current_price > coin_config.get('alerts', {}).get('price_above', float('inf'))):
            
            if self.cooldown_manager.can_send_alert('profit_taking', coin_name, cooldown):
                alerts.append({
                    'type': 'partial_profit',
                    'coin': coin_name,
                    'message': f"💰 TOME LUCRO: {coin_name} em ${current_price:,.4f} - RSI {rsi:.1f} + Meta de preço atingida",
                    'priority': 'medium',
                    'action': self.get_professional_action('partial_profit', coin_name, market_phase, current_price, rsi),
                    'confidence': 'MÉDIA',
                    'market_phase': market_phase
                })
        
        return alerts
