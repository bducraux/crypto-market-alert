"""
Comprehensive Market Cycle Top Analysis
Advanced multi-indicator analysis for detecting market cycle peaks and optimal exit timing
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from src.indicators import TechnicalIndicators

logger = logging.getLogger(__name__)


class CycleTopAnalyzer:
    """
    Comprehensive cycle top analysis using multiple professional indicators
    
    Analyzes market cycle position using:
    - Pi Cycle Top (Bitcoin-specific cycle indicator)
    - RSI (Relative Strength Index) across multiple timeframes
    - MVRV Z-Score (Market Value to Realized Value)
    - Moving Average Ribbons (50, 100, 200 day analysis)
    - Fear & Greed Index (Market sentiment)
    - Network Activity (On-chain metrics when available)
    - Altcoin Performance Divergence
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.indicators = TechnicalIndicators()
        self.logger = logging.getLogger(__name__)
        
        # Indicator thresholds from config
        self.thresholds = {
            'pi_cycle_approach': 0.95,  # When 111-day MA approaches 350-day MA * 2
            'pi_cycle_danger': 1.02,    # When 111-day MA crosses above
            'rsi_warning': 70,          # RSI warning level
            'rsi_danger': 80,           # RSI extreme level
            'fear_greed_warning': 75,   # Market greed warning
            'fear_greed_danger': 85,    # Extreme greed
            'ma_overextension': 3.0,    # Price > 3x MA200
            'volume_spike': 2.5,        # Volume > 2.5x average
        }
    
    def analyze_market_cycle_top(self, coin_data: Dict, market_data: Dict) -> Dict:
        """
        Comprehensive market cycle top analysis
        
        Returns detailed analysis with individual indicator status and recommendations
        """
        try:
            btc_data = coin_data.get('bitcoin', {})
            if not btc_data:
                return {'error': 'Bitcoin data not available'}
            
            # Get Bitcoin historical data for technical analysis
            btc_historical = btc_data.get('historical')
            if btc_historical is None or len(btc_historical) < 350:
                return {'error': 'Insufficient Bitcoin historical data for cycle analysis'}
            
            analysis_result = {
                'timestamp': datetime.now().isoformat(),
                'overall_risk_score': 0,
                'risk_level': 'LOW',
                'recommendation': '',
                'indicators': {}
            }
            
            # 1. Pi Cycle Top Analysis (Bitcoin-specific market cycle indicator)
            pi_cycle_analysis = self._analyze_pi_cycle_top(btc_historical, btc_data)
            analysis_result['indicators']['pi_cycle'] = pi_cycle_analysis
            
            # 2. RSI Analysis (Multiple timeframes)
            rsi_analysis = self._analyze_rsi_conditions(btc_data, btc_historical, coin_data)
            analysis_result['indicators']['rsi'] = rsi_analysis
            
            # 3. Moving Average Analysis
            ma_analysis = self._analyze_moving_averages(btc_data, btc_historical)
            analysis_result['indicators']['moving_averages'] = ma_analysis
            
            # 4. Market Sentiment Analysis
            sentiment_analysis = self._analyze_market_sentiment(market_data)
            analysis_result['indicators']['market_sentiment'] = sentiment_analysis
            
            # 5. Altcoin Performance Divergence
            altcoin_analysis = self._analyze_altcoin_divergence(coin_data, btc_data)
            analysis_result['indicators']['altcoin_divergence'] = altcoin_analysis
            
            # 6. Volume Analysis
            volume_analysis = self._analyze_volume_patterns(btc_data, btc_historical)
            analysis_result['indicators']['volume'] = volume_analysis
            
            # Calculate overall risk score and recommendation
            self._calculate_overall_assessment(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Cycle top analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_pi_cycle_top(self, historical_data, btc_data: Dict) -> Dict:
        \"\"\"Analyze Pi Cycle Top indicator - Bitcoin's most reliable cycle top signal\"\"\"
        try:
            if len(historical_data) < 350:
                return {
                    'status': 'INSUFFICIENT_DATA',
                    'signal': 'NEUTRAL',
                    'value': None,
                    'recommendation': 'Need more historical data',
                    'explanation': 'Pi Cycle requires 350+ days of data'
                }
            
            # Calculate Pi Cycle Top using TechnicalIndicators
            pi_cycle_data = self.indicators.calculate_pi_cycle_top(historical_data)
            
            if not pi_cycle_data or 'pi_cycle_signal' not in pi_cycle_data:
                return {
                    'status': 'ERROR',
                    'signal': 'NEUTRAL',
                    'value': None,
                    'recommendation': 'Unable to calculate Pi Cycle',
                    'explanation': 'Calculation error'
                }
            
            ma_111 = pi_cycle_data.get('ma_111')
            ma_350_2x = pi_cycle_data.get('ma_350_2x')
            distance = pi_cycle_data.get('distance', 0)
            signal_triggered = pi_cycle_data.get('pi_cycle_signal', False)
            
            # Determine status and recommendation
            if signal_triggered:
                status = 'SIGNAL_TRIGGERED'
                signal = 'SELL'
                recommendation = 'IMMEDIATE EXIT - Pi Cycle Top triggered'
                explanation = 'Historical data shows this is typically the cycle peak'
            elif distance > 0.95:
                status = 'APPROACHING_SIGNAL'
                signal = 'CAUTION'
                recommendation = 'PREPARE FOR EXIT - Signal approaching'
                explanation = 'Pi Cycle lines are converging, top may be near'
            elif distance > 0.8:
                status = 'ELEVATED_RISK'
                signal = 'MONITOR'
                recommendation = 'MONITOR CLOSELY - Risk increasing'
                explanation = 'Price extension increasing, watch for reversal signs'
            else:
                status = 'SAFE_ZONE'
                signal = 'HOLD'
                recommendation = 'CONTINUE ACCUMULATING'
                explanation = 'Cycle top indicators not yet active'
            
            return {
                'status': status,
                'signal': signal,
                'value': distance,
                'ma_111': ma_111,
                'ma_350_2x': ma_350_2x,
                'signal_triggered': signal_triggered,
                'recommendation': recommendation,
                'explanation': explanation,
                'risk_score': min(100, max(0, int(distance * 100))) if distance else 0
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'signal': 'NEUTRAL',
                'value': None,
                'recommendation': f'Analysis failed: {str(e)}',
                'explanation': 'Technical calculation error'
            }
    
    def _analyze_rsi_conditions(self, btc_data: Dict, btc_historical, coin_data: Dict) -> Dict:
        \"\"\"Analyze RSI across Bitcoin and major altcoins for overbought conditions\"\"\"
        try:
            # Calculate Bitcoin RSI
            btc_indicators = self.indicators.get_latest_indicator_values(
                btc_historical, 
                {'rsi_period': 14}, 
                'bitcoin'
            )
            btc_rsi = btc_indicators.get('rsi', 50)
            
            # Count overbought altcoins
            overbought_count = 0
            total_analyzed = 0
            
            for coin_config in self.config.get('coins', []):
                coin_id = coin_config.get('coingecko_id')
                if coin_id in coin_data and coin_id != 'bitcoin':
                    coin_historical = coin_data[coin_id].get('historical')
                    if coin_historical is not None and len(coin_historical) >= 14:
                        coin_indicators = self.indicators.get_latest_indicator_values(
                            coin_historical, 
                            {'rsi_period': 14},
                            coin_id
                        )
                        coin_rsi = coin_indicators.get('rsi')
                        if coin_rsi and coin_rsi > 75:
                            overbought_count += 1
                        total_analyzed += 1
            
            # Determine status
            if btc_rsi >= 80:
                status = 'EXTREME_OVERBOUGHT'
                signal = 'STRONG_SELL'
                recommendation = 'SELL IMMEDIATELY - BTC extremely overbought'
            elif btc_rsi >= 70:
                status = 'OVERBOUGHT'
                signal = 'SELL'
                recommendation = 'CONSIDER SELLING - BTC overbought'
            elif btc_rsi >= 60:
                status = 'ELEVATED'
                signal = 'CAUTION'
                recommendation = 'MONITOR - BTC showing strength'
            else:
                status = 'NORMAL'
                signal = 'HOLD'
                recommendation = 'SAFE TO HOLD - RSI not extreme'
            
            # Enhance recommendation based on altcoin RSI
            if overbought_count >= 5:
                signal = 'STRONG_SELL' if signal != 'STRONG_SELL' else signal
                recommendation += f' + {overbought_count} altcoins overbought'
            
            explanation = f'RSI measures momentum. >70 = overbought, >80 = extremely overbought. Currently {btc_rsi:.1f}'
            
            return {
                'status': status,
                'signal': signal,
                'btc_rsi': btc_rsi,
                'overbought_altcoins': overbought_count,
                'total_analyzed': total_analyzed,
                'recommendation': recommendation,
                'explanation': explanation,
                'risk_score': min(100, max(0, int((btc_rsi - 30) * 2.5))) if btc_rsi else 0
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'signal': 'NEUTRAL',
                'recommendation': f'RSI analysis failed: {str(e)}',
                'explanation': 'Unable to calculate RSI'
            }
    
    def _analyze_moving_averages(self, btc_data: Dict, btc_historical) -> Dict:
        \"\"\"Analyze Bitcoin's position relative to key moving averages\"\"\"
        try:
            btc_price = btc_data.get('usd', 0)
            
            # Calculate moving averages
            ma_data = self.indicators.calculate_moving_averages(btc_historical, 50, 200)
            if not ma_data:
                return {'status': 'ERROR', 'recommendation': 'Unable to calculate MAs'}
            
            ma_50 = ma_data.get('ma_short')
            ma_200 = ma_data.get('ma_long')
            
            if ma_50 is None or ma_200 is None or ma_50.empty or ma_200.empty:
                return {'status': 'ERROR', 'recommendation': 'MA calculation failed'}
            
            current_ma_50 = float(ma_50.iloc[-1])
            current_ma_200 = float(ma_200.iloc[-1])
            
            # Calculate overextension ratios
            price_vs_ma50 = btc_price / current_ma_50 if current_ma_50 > 0 else 1
            price_vs_ma200 = btc_price / current_ma_200 if current_ma_200 > 0 else 1
            
            # Determine status
            if price_vs_ma200 > 4.0:
                status = 'EXTREME_OVEREXTENSION'
                signal = 'STRONG_SELL'
                recommendation = 'MAJOR EXIT SIGNAL - Extreme overextension'
            elif price_vs_ma200 > 3.0:
                status = 'HIGH_OVEREXTENSION'
                signal = 'SELL'
                recommendation = 'CONSIDER MAJOR SELLS - High overextension'
            elif price_vs_ma200 > 2.0:
                status = 'MODERATE_OVEREXTENSION'
                signal = 'CAUTION'
                recommendation = 'TAKE SOME PROFITS - Above normal levels'
            else:
                status = 'NORMAL_RANGE'
                signal = 'HOLD'
                recommendation = 'SAFE TO HOLD - Normal price levels'
            
            explanation = f'Price is {price_vs_ma200:.1f}x above 200-day MA. >3x typically signals tops'
            
            return {
                'status': status,
                'signal': signal,
                'btc_price': btc_price,
                'ma_50': current_ma_50,
                'ma_200': current_ma_200,
                'price_vs_ma50': price_vs_ma50,
                'price_vs_ma200': price_vs_ma200,
                'recommendation': recommendation,
                'explanation': explanation,
                'risk_score': min(100, max(0, int((price_vs_ma200 - 1) * 33)))
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'signal': 'NEUTRAL',
                'recommendation': f'MA analysis failed: {str(e)}',
                'explanation': 'Unable to analyze moving averages'
            }
    
    def _analyze_market_sentiment(self, market_data: Dict) -> Dict:
        \"\"\"Analyze Fear & Greed Index and market sentiment indicators\"\"\"
        try:
            fear_greed = market_data.get('fear_greed_index', {})
            if isinstance(fear_greed, dict):
                fg_value = fear_greed.get('value', 50)
                fg_classification = fear_greed.get('value_classification', 'Neutral')
            else:
                fg_value = 50
                fg_classification = 'Neutral'
            
            btc_dominance = market_data.get('btc_dominance', 50)
            
            # Analyze Fear & Greed
            if fg_value >= 85:
                fg_status = 'EXTREME_GREED'
                fg_signal = 'STRONG_SELL'
                fg_recommendation = 'SELL IMMEDIATELY - Extreme greed often marks tops'
            elif fg_value >= 75:
                fg_status = 'GREED'
                fg_signal = 'SELL'
                fg_recommendation = 'CONSIDER SELLING - Market becoming greedy'
            elif fg_value >= 60:
                fg_status = 'MODERATE_GREED'
                fg_signal = 'CAUTION'
                fg_recommendation = 'BE CAUTIOUS - Sentiment improving'
            else:
                fg_status = 'NEUTRAL_TO_FEAR'
                fg_signal = 'HOLD'
                fg_recommendation = 'SAFE TO HOLD - Sentiment not extreme'
            
            # Analyze BTC Dominance context
            if btc_dominance > 65:
                dominance_context = 'Very high BTC dominance - potential alt rotation coming'
            elif btc_dominance < 40:
                dominance_context = 'Low BTC dominance - alt season risk'
            else:
                dominance_context = 'Normal BTC dominance levels'
            
            explanation = f'Fear & Greed at {fg_value}/100. Extreme greed (>85) often signals market tops'
            
            return {
                'status': fg_status,
                'signal': fg_signal,
                'fear_greed_value': fg_value,
                'fear_greed_classification': fg_classification,
                'btc_dominance': btc_dominance,
                'dominance_context': dominance_context,
                'recommendation': fg_recommendation,
                'explanation': explanation,
                'risk_score': min(100, max(0, int((fg_value - 50) * 2))) if fg_value >= 50 else 0
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'signal': 'NEUTRAL',
                'recommendation': f'Sentiment analysis failed: {str(e)}',
                'explanation': 'Unable to analyze market sentiment'
            }
    
    def _analyze_altcoin_divergence(self, coin_data: Dict, btc_data: Dict) -> Dict:
        \"\"\"Analyze altcoin performance vs Bitcoin for divergence signals\"\"\"
        try:
            btc_change = btc_data.get('usd_24h_change', 0)
            
            strong_performers = 0
            weak_performers = 0
            total_alts = 0
            
            for coin_config in self.config.get('coins', []):
                coin_id = coin_config.get('coingecko_id')
                coin_name = coin_config.get('name', '')
                
                if coin_id in coin_data and coin_name not in ['BTC', 'ETH']:
                    alt_change = coin_data[coin_id].get('usd_24h_change', 0)
                    
                    if alt_change > btc_change + 10:  # Significantly outperforming
                        strong_performers += 1
                    elif alt_change < btc_change - 10:  # Underperforming
                        weak_performers += 1
                    
                    total_alts += 1
            
            # Calculate divergence ratio
            if total_alts > 0:
                strong_ratio = strong_performers / total_alts
                weak_ratio = weak_performers / total_alts
            else:
                strong_ratio = weak_ratio = 0
            
            # Determine status
            if strong_ratio > 0.6:
                status = 'STRONG_ALT_OUTPERFORMANCE'
                signal = 'CAUTION'
                recommendation = 'WATCH FOR ROTATION - Alts very strong vs BTC'
            elif weak_ratio > 0.6:
                status = 'ALT_WEAKNESS'
                signal = 'BTC_STRENGTH'
                recommendation = 'BTC DOMINANCE - Alts showing weakness'
            else:
                status = 'BALANCED_PERFORMANCE'
                signal = 'NEUTRAL'
                recommendation = 'NORMAL CORRELATION - No major divergence'
            
            explanation = f'{strong_performers}/{total_alts} alts outperforming BTC significantly'
            
            return {
                'status': status,
                'signal': signal,
                'strong_performers': strong_performers,
                'weak_performers': weak_performers,
                'total_analyzed': total_alts,
                'btc_change_24h': btc_change,
                'recommendation': recommendation,
                'explanation': explanation,
                'risk_score': min(100, max(0, int(strong_ratio * 60)))
            }
            
        except Exception as e:
            return {
                'status': 'ERROR',
                'signal': 'NEUTRAL',
                'recommendation': f'Divergence analysis failed: {str(e)}',
                'explanation': 'Unable to analyze altcoin divergence'
            }
    
    def _analyze_volume_patterns(self, btc_data: Dict, btc_historical) -> Dict:
        \"\"\"Analyze volume patterns for distribution signals\"\"\"
        try:
            current_volume = btc_data.get('usd_24h_vol', 0)
            
            if btc_historical is None or len(btc_historical) < 30:
                return {
                    'status': 'INSUFFICIENT_DATA',
                    'signal': 'NEUTRAL',
                    'recommendation': 'Need more volume data',
                    'explanation': 'Not enough historical volume data'
                }
            
            # Calculate average volume over last 30 days
            if 'volume' in btc_historical.columns:
                recent_volumes = btc_historical['volume'].tail(30)
                avg_volume = recent_volumes.mean()
                
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                
                if volume_ratio > 3.0:
                    status = 'VOLUME_SPIKE'
                    signal = 'CAUTION'
                    recommendation = 'HIGH VOLUME - Possible distribution'
                elif volume_ratio > 2.0:
                    status = 'ELEVATED_VOLUME'
                    signal = 'MONITOR'
                    recommendation = 'ABOVE AVERAGE VOLUME - Watch for continuation'
                elif volume_ratio < 0.5:
                    status = 'LOW_VOLUME'
                    signal = 'NEUTRAL'
                    recommendation = 'LOW VOLUME - Limited conviction'
                else:
                    status = 'NORMAL_VOLUME'
                    signal = 'NEUTRAL'
                    recommendation = 'NORMAL VOLUME LEVELS'
                
                explanation = f'Current volume is {volume_ratio:.1f}x the 30-day average'
                
                return {
                    'status': status,
                    'signal': signal,
                    'current_volume': current_volume,
                    'average_volume': avg_volume,
                    'volume_ratio': volume_ratio,
                    'recommendation': recommendation,
                    'explanation': explanation,
                    'risk_score': min(100, max(0, int((volume_ratio - 1) * 50))) if volume_ratio > 1 else 0
                }
            else:
                return {
                    'status': 'NO_VOLUME_DATA',
                    'signal': 'NEUTRAL',
                    'recommendation': 'Volume data not available',
                    'explanation': 'Historical volume data missing'
                }
                
        except Exception as e:
            return {
                'status': 'ERROR',
                'signal': 'NEUTRAL',
                'recommendation': f'Volume analysis failed: {str(e)}',
                'explanation': 'Unable to analyze volume patterns'
            }
    
    def _calculate_overall_assessment(self, analysis_result: Dict) -> None:
        \"\"\"Calculate overall risk score and provide consolidated recommendation\"\"\"
        indicators = analysis_result['indicators']
        total_score = 0
        valid_indicators = 0
        
        # Weight each indicator based on reliability
        weights = {
            'pi_cycle': 0.35,          # Highest weight - most reliable for BTC tops
            'rsi': 0.20,               # Strong momentum indicator
            'moving_averages': 0.20,   # Price structure analysis
            'market_sentiment': 0.15,  # Sentiment contrarian indicator
            'altcoin_divergence': 0.05, # Market structure
            'volume': 0.05             # Confirmation indicator
        }
        
        for indicator_name, weight in weights.items():
            if indicator_name in indicators:
                indicator_data = indicators[indicator_name]
                risk_score = indicator_data.get('risk_score', 0)
                if risk_score is not None:
                    total_score += risk_score * weight
                    valid_indicators += 1
        
        # Normalize score
        if valid_indicators > 0:
            analysis_result['overall_risk_score'] = min(100, max(0, int(total_score)))
        else:
            analysis_result['overall_risk_score'] = 0
        
        # Determine risk level and recommendation
        score = analysis_result['overall_risk_score']
        
        if score >= 80:
            analysis_result['risk_level'] = 'CRITICAL'
            analysis_result['recommendation'] = 'IMMEDIATE EXIT - Multiple top signals active'
        elif score >= 65:
            analysis_result['risk_level'] = 'HIGH'
            analysis_result['recommendation'] = 'MAJOR SELLING - Significant risk detected'
        elif score >= 45:
            analysis_result['risk_level'] = 'MODERATE'
            analysis_result['recommendation'] = 'PARTIAL SELLING - Take some profits'
        elif score >= 25:
            analysis_result['risk_level'] = 'LOW'
            analysis_result['recommendation'] = 'MONITOR CLOSELY - Some risk signals'
        else:
            analysis_result['risk_level'] = 'MINIMAL'
            analysis_result['recommendation'] = 'CONTINUE ACCUMULATING - Low risk environment'
    
    def format_analysis_for_telegram(self, analysis: Dict) -> str:
        \"\"\"Format the comprehensive analysis for Telegram messages\"\"\"
        if 'error' in analysis:
            return f\"🔺 CYCLE TOP ANALYSIS:\\n   ❌ Error: {analysis['error']}\"
        
        output = []
        output.append(\"🔺 CYCLE TOP ANALYSIS:\")
        output.append(f\"   Overall Risk: {analysis['overall_risk_score']}/100 ({analysis['risk_level']})\")
        output.append(f\"   💎 ACTION: {analysis['recommendation']}\")
        output.append(\"\")
        
        indicators = analysis.get('indicators', {})
        
        # Pi Cycle Top (most important)\n        if 'pi_cycle' in indicators:\n            pi = indicators['pi_cycle']\n            if pi.get('signal_triggered'):\n                output.append(\"   🚨 Pi Cycle: SIGNAL TRIGGERED\")\n            elif pi.get('value', 0) > 0.8:\n                output.append(f\"   ⚠️ Pi Cycle: {pi.get('value', 0):.2f} (Approaching)\")\n            else:\n                output.append(f\"   ✅ Pi Cycle: {pi.get('value', 0):.2f} (Safe)\")
        
        # RSI Analysis
        if 'rsi' in indicators:
            rsi = indicators['rsi']
            btc_rsi = rsi.get('btc_rsi', 0)
            overbought_alts = rsi.get('overbought_altcoins', 0)
            if btc_rsi >= 80:
                output.append(f\"   🔴 BTC RSI: {btc_rsi:.0f} (EXTREME)\")
            elif btc_rsi >= 70:
                output.append(f\"   🟡 BTC RSI: {btc_rsi:.0f} (Overbought)\")
            else:
                output.append(f\"   ✅ BTC RSI: {btc_rsi:.0f} (Normal)\")
            
            if overbought_alts >= 5:
                output.append(f\"   📊 {overbought_alts} altcoins overbought\")
        
        # Market Sentiment
        if 'market_sentiment' in indicators:
            sentiment = indicators['market_sentiment']
            fg_value = sentiment.get('fear_greed_value', 50)
            if fg_value >= 85:
                output.append(f\"   😱 Fear & Greed: {fg_value} (EXTREME GREED)\")
            elif fg_value >= 75:
                output.append(f\"   😊 Fear & Greed: {fg_value} (Greed)\")
            else:
                output.append(f\"   😐 Fear & Greed: {fg_value} (Normal)\")
        
        return \"\\n\".join(output)
