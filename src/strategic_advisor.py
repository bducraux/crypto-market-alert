"""
Strategic Advisor - Goal: 1 BTC + 10 ETH
Focuses on maximizing BTC and ETH holdings through strategic trading decisions
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass
from src.data_fetcher import DataFetcher
from src.indicators import TechnicalIndicators
from src.utils import load_config

logger = logging.getLogger(__name__)

@dataclass
class StrategicSignal:
    action: str  # 'BUY_BTC', 'BUY_ETH', 'SWAP_BTC_TO_ETH', 'SWAP_ETH_TO_BTC', 'SELL_ALT', 'HOLD'
    coin: str
    confidence: str  # 'HIGH', 'MEDIUM', 'LOW'
    reason: str
    target_price: Optional[float] = None
    expected_return: Optional[float] = None

class StrategicAdvisor:
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.data_fetcher = DataFetcher()
        self.indicators = TechnicalIndicators()
        
        # Strategic goals
        self.target_btc = 1.0
        self.target_eth = 10.0
        
        # Get user's current portfolio from config
        self.portfolio_coins = {coin['symbol']: coin for coin in self.config['coins']}
        
    def analyze_strategic_position(self) -> Dict:
        """Main strategic analysis for achieving 1 BTC + 10 ETH goal"""
        try:
            # Get coin IDs from config
            coin_ids = [coin['coingecko_id'] for coin in self.config.get('coins', [])]
            
            # Get current market data
            all_data = self.data_fetcher.get_coin_market_data_batch(coin_ids)
            
            # Get market metrics (usando sistema híbrido)
            market_metrics = {
                'btc_dominance': self.data_fetcher.get_btc_dominance(),
                'eth_btc_ratio': self.data_fetcher.get_eth_btc_ratio(),
                'fear_greed_index': self.data_fetcher.get_fear_greed_index()
            }
            
            # Calculate current ETH/BTC ratio and trends
            eth_btc_analysis = self._analyze_eth_btc_ratio(all_data)
            
            # Check altseason status for timing altcoin exits
            altseason_analysis = self._analyze_altseason(all_data, market_metrics)
            
            # Analyze each altcoin for exit opportunities
            altcoin_analysis = self._analyze_altcoins(all_data)
            
            # Generate strategic recommendations
            recommendations = self._generate_recommendations(
                eth_btc_analysis, altseason_analysis, altcoin_analysis, all_data
            )
            
            # Calculate portfolio progress toward goals
            progress = self._calculate_goal_progress(all_data)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'strategic_goal': f"Target: {self.target_btc} BTC + {self.target_eth} ETH",
                'current_progress': progress,
                'eth_btc_analysis': eth_btc_analysis,
                'altseason_status': altseason_analysis,
                'altcoin_opportunities': altcoin_analysis,
                'recommendations': recommendations,
                'market_phase': self._determine_market_phase(all_data, market_metrics)
            }
            
        except Exception as e:
            logger.error(f"Strategic analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_eth_btc_ratio(self, data: Dict) -> Dict:
        """Analyze ETH/BTC ratio for optimal swap timing"""
        try:
            btc_data = data.get('bitcoin', {})
            eth_data = data.get('ethereum', {})
            
            if not btc_data or not eth_data:
                return {'error': 'Missing BTC or ETH data'}
            
            btc_price = btc_data.get('usd', 0)
            eth_price = eth_data.get('usd', 0)
            
            if btc_price == 0 or eth_price == 0:
                return {'error': 'Invalid price data'}
            
            current_ratio = eth_price / btc_price
            
            # Calculate technical indicators from historical data if available
            btc_historical = btc_data.get('historical')
            eth_historical = eth_data.get('historical')
            
            btc_rsi = 50  # Default values
            eth_rsi = 50
            btc_ma_200 = btc_price
            eth_ma_200 = eth_price
            
            if btc_historical is not None and not btc_historical.empty:
                try:
                    btc_indicators = self.indicators.get_latest_indicator_values(
                        btc_historical, {'rsi_period': 14, 'ma_long': 200}
                    )
                    btc_rsi = btc_indicators.get('rsi', 50)
                    btc_ma_200 = btc_indicators.get('ma_long', btc_price)
                except Exception as e:
                    logger.debug(f"Failed to calculate BTC indicators: {e}")
            
            if eth_historical is not None and not eth_historical.empty:
                try:
                    eth_indicators = self.indicators.get_latest_indicator_values(
                        eth_historical, {'rsi_period': 14, 'ma_long': 200}
                    )
                    eth_rsi = eth_indicators.get('rsi', 50)
                    eth_ma_200 = eth_indicators.get('ma_long', eth_price)
                except Exception as e:
                    logger.debug(f"Failed to calculate ETH indicators: {e}")
            
            # Calculate price positions relative to MA200
            btc_vs_ma200 = ((btc_price / btc_ma_200) - 1) * 100
            eth_vs_ma200 = ((eth_price / eth_ma_200) - 1) * 100
            
            # Determine optimal strategy
            swap_signal = self._calculate_swap_signal(
                current_ratio, btc_rsi, eth_rsi, btc_vs_ma200, eth_vs_ma200
            )
            
            return {
                'current_ratio': round(current_ratio, 4),
                'btc_price': btc_price,
                'eth_price': eth_price,
                'btc_rsi': btc_rsi,
                'eth_rsi': eth_rsi,
                'btc_vs_ma200': round(btc_vs_ma200, 1),
                'eth_vs_ma200': round(eth_vs_ma200, 1),
                'swap_recommendation': swap_signal,
                'ratio_analysis': self._analyze_ratio_trend(current_ratio)
            }
            
        except Exception as e:
            logger.error(f"ETH/BTC analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_swap_signal(self, ratio: float, btc_rsi: float, eth_rsi: float, 
                              btc_vs_ma200: float, eth_vs_ma200: float) -> Dict:
        """Calculate optimal BTC/ETH swap timing"""
        
        # Historical ratio ranges (approximate)
        ratio_low = 0.04   # ETH cheap vs BTC
        ratio_high = 0.08  # ETH expensive vs BTC
        ratio_extreme_high = 0.10
        
        signals = []
        confidence = "LOW"
        action = "HOLD"
        
        # ETH oversold vs BTC (good time to buy ETH)
        if ratio < ratio_low:
            if btc_rsi > 60 and eth_rsi < 40:
                signals.append("ETH heavily oversold vs BTC")
                action = "SWAP_BTC_TO_ETH"
                confidence = "HIGH"
            elif btc_vs_ma200 > 20 and eth_vs_ma200 < 0:
                signals.append("BTC overextended, ETH lagging")
                action = "SWAP_BTC_TO_ETH"
                confidence = "MEDIUM"
        
        # ETH overbought vs BTC (good time to buy BTC)
        elif ratio > ratio_high:
            if eth_rsi > 70 and btc_rsi < 50:
                signals.append("ETH overbought vs BTC")
                action = "SWAP_ETH_TO_BTC"
                confidence = "HIGH"
            elif ratio > ratio_extreme_high:
                signals.append("ETH extremely expensive vs BTC")
                action = "SWAP_ETH_TO_BTC"
                confidence = "HIGH"
        
        # Momentum considerations
        if btc_rsi > 80 and eth_rsi < 40:
            signals.append("Strong BTC momentum, ETH lagging - consider ETH")
            if action == "HOLD":
                action = "FAVOR_ETH"
                confidence = "MEDIUM"
        elif eth_rsi > 80 and btc_rsi < 40:
            signals.append("Strong ETH momentum, BTC lagging - consider BTC")
            if action == "HOLD":
                action = "FAVOR_BTC"
                confidence = "MEDIUM"
        
        return {
            'action': action,
            'confidence': confidence,
            'signals': signals,
            'ratio_position': 'LOW' if ratio < ratio_low else 'HIGH' if ratio > ratio_high else 'NORMAL'
        }
    
    def _analyze_altseason(self, data: Dict, market_metrics: Dict) -> Dict:
        """Analyze if we're in altseason with enhanced detection"""
        try:
            btc_dominance = market_metrics.get('btc_dominance', 50)
            eth_btc_ratio = market_metrics.get('eth_btc_ratio', 0.035)
            
            # Get BTC and ETH data for trend analysis
            btc_data = data.get('bitcoin', {})
            eth_data = data.get('ethereum', {})
            btc_price = btc_data.get('usd', 0)
            eth_price = eth_data.get('usd', 0)
            
            # Calculate technical indicators for both BTC and ETH
            btc_rsi = 50
            eth_rsi = 50
            btc_ma_50 = btc_price
            eth_ma_50 = eth_price
            
            # BTC indicators
            btc_historical = btc_data.get('historical')
            if btc_historical is not None and not btc_historical.empty:
                try:
                    btc_indicators = self.indicators.get_latest_indicator_values(
                        btc_historical, {'rsi_period': 14, 'ma_short': 50}
                    )
                    btc_rsi = btc_indicators.get('rsi', 50)
                    btc_ma_50 = btc_indicators.get('ma_short', btc_price)
                except Exception as e:
                    logger.debug(f"Failed to calculate BTC indicators for altseason: {e}")
            
            # ETH indicators
            eth_historical = eth_data.get('historical')
            if eth_historical is not None and not eth_historical.empty:
                try:
                    eth_indicators = self.indicators.get_latest_indicator_values(
                        eth_historical, {'rsi_period': 14, 'ma_short': 50}
                    )
                    eth_rsi = eth_indicators.get('rsi', 50)
                    eth_ma_50 = eth_indicators.get('ma_short', eth_price)
                except Exception as e:
                    logger.debug(f"Failed to calculate ETH indicators for altseason: {e}")
            
            altseason_indicators = []
            altseason_score = 0
            phase = "ACCUMULATION"
            
            # Enhanced BTC dominance analysis with trend
            if btc_dominance:
                if btc_dominance < 40:
                    altseason_indicators.append(f"BTC dominance very low ({btc_dominance:.1f}%) - Peak altseason")
                    altseason_score += 40
                    phase = "PEAK_ALTSEASON"
                elif btc_dominance < 45:
                    altseason_indicators.append(f"BTC dominance low ({btc_dominance:.1f}%) - Altseason active")
                    altseason_score += 30
                    phase = "ALTSEASON"
                elif btc_dominance > 60:
                    altseason_indicators.append(f"BTC dominance high ({btc_dominance:.1f}%) - BTC season")
                    altseason_score -= 20
                    phase = "BTC_SEASON"
                elif btc_dominance > 55:
                    altseason_indicators.append(f"BTC dominance elevated ({btc_dominance:.1f}%) - BTC favored")
                    altseason_score -= 10
            
            # ETH/BTC ratio analysis (key altseason indicator)
            if eth_btc_ratio:
                if eth_btc_ratio > 0.08:  # Very strong ETH
                    altseason_indicators.append(f"ETH/BTC ratio very high ({eth_btc_ratio:.4f}) - Strong altseason")
                    altseason_score += 25
                elif eth_btc_ratio > 0.06:  # Strong ETH
                    altseason_indicators.append(f"ETH/BTC ratio elevated ({eth_btc_ratio:.4f}) - Moderate altseason")
                    altseason_score += 15
                elif eth_btc_ratio < 0.03:  # Weak ETH
                    altseason_indicators.append(f"ETH/BTC ratio low ({eth_btc_ratio:.4f}) - ETH weakness")
                    altseason_score -= 15
            
            # Cross-asset momentum analysis
            if btc_rsi > 70 and eth_rsi > 70:
                altseason_indicators.append("Both BTC and ETH overbought - Potential altcoin rotation")
                altseason_score += 20
            elif btc_rsi > 75:
                altseason_indicators.append(f"BTC extremely overbought (RSI {btc_rsi:.1f}) - Alts may benefit")
                altseason_score += 25
            elif btc_rsi < 30:
                altseason_indicators.append(f"BTC oversold (RSI {btc_rsi:.1f}) - Money flowing to BTC")
                altseason_score -= 15
            
            # ETH leadership analysis
            if eth_price > eth_ma_50 * 1.15 and btc_price < btc_ma_50 * 1.05:
                altseason_indicators.append("ETH outperforming BTC - Altseason leadership")
                altseason_score += 20
            elif eth_price < eth_ma_50 * 0.95:
                altseason_indicators.append("ETH underperforming - Weak altseason setup")
                altseason_score -= 10
            
            # Combined trend analysis
            if btc_price > btc_ma_50 * 1.1 and eth_price > eth_ma_50 * 1.1:
                if btc_dominance and btc_dominance < 50:
                    altseason_indicators.append("Both BTC/ETH up + Low dominance = Strong altseason")
                    altseason_score += 20
                else:
                    altseason_indicators.append("BTC/ETH up but high dominance = Mixed signals")
                    altseason_score += 5
            
            # Final phase determination with more granular levels
            if altseason_score > 50:
                phase = "EXTREME_ALTSEASON"
                recommendation = "Strong profit taking on alts - Consider 25-50% exits"
                exit_signal = True
            elif altseason_score > 35:
                phase = "PEAK_ALTSEASON" 
                recommendation = "Major profit taking - Consider 10-25% exits"
                exit_signal = True
            elif altseason_score > 20:
                phase = "ALTSEASON"
                recommendation = "Monitor closely, light profit taking on pumped alts"
                exit_signal = False
            elif altseason_score > 0:
                phase = "EARLY_ALTSEASON"
                recommendation = "Building altseason momentum - Hold positions"
                exit_signal = False
            elif altseason_score < -15:
                phase = "BTC_SEASON"
                recommendation = "Focus on BTC/ETH accumulation"
                exit_signal = False
            else:
                phase = "TRANSITION"
                recommendation = "Wait for clearer directional signals"
                exit_signal = False
            
            return {
                'phase': phase,
                'score': altseason_score,
                'btc_dominance': btc_dominance,
                'eth_btc_ratio': eth_btc_ratio,
                'indicators': altseason_indicators,
                'recommendation': recommendation,
                'exit_alts_signal': exit_signal,
                'btc_rsi': btc_rsi,
                'eth_rsi': eth_rsi
            }
            
        except Exception as e:
            logger.error(f"Enhanced altseason analysis failed: {e}")
            return {'error': str(e)}
    
    def _analyze_altcoins(self, data: Dict) -> List[Dict]:
        """Analyze each altcoin for exit/hold signals"""
        altcoin_analysis = []
        
        # Exclude BTC and ETH from altcoin analysis
        altcoins = [coin for coin in self.config['coins'] 
                   if coin['symbol'] not in ['bitcoin', 'ethereum']]
        
        for coin_config in altcoins:
            coin_id = coin_config['coingecko_id']
            coin_data = data.get(coin_id, {})
            
            if not coin_data:
                continue
            
            analysis = self._analyze_single_altcoin(coin_config, coin_data)
            if analysis:
                altcoin_analysis.append(analysis)
        
        # Sort by opportunity score (highest first)
        altcoin_analysis.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
        
        return altcoin_analysis
    
    def _analyze_single_altcoin(self, coin_config: Dict, coin_data: Dict) -> Optional[Dict]:
        """Analyze individual altcoin for trading opportunities"""
        try:
            symbol = coin_config['symbol']
            avg_price = coin_config.get('avg_price', 0)
            current_price = coin_data.get('usd', 0)
            
            if current_price == 0 or avg_price == 0:
                return None
            
            # Calculate P&L
            pnl_percent = ((current_price / avg_price) - 1) * 100
            
            # Technical indicators from historical data if available
            rsi = 50
            ma_50 = current_price
            ma_200 = current_price
            
            historical_df = coin_data.get('historical')
            if historical_df is not None and not historical_df.empty:
                try:
                    indicators = self.indicators.get_latest_indicator_values(
                        historical_df, {'rsi_period': 14, 'ma_short': 50, 'ma_long': 200}
                    )
                    rsi = indicators.get('rsi', 50)
                    ma_50 = indicators.get('ma_short', current_price)
                    ma_200 = indicators.get('ma_long', current_price)
                except Exception as e:
                    logger.debug(f"Failed to calculate indicators for {symbol}: {e}")
            
            # Position analysis (handle None values safely)
            if ma_50 is not None and ma_200 is not None:
                above_ma_50 = current_price > ma_50
                above_ma_200 = current_price > ma_200
            else:
                # Use current price as fallback for missing MA values
                ma_50 = current_price
                ma_200 = current_price
                above_ma_50 = True  # Neutral position when MA data unavailable
                above_ma_200 = True
            
            # Calculate opportunity score
            opportunity_score = self._calculate_altcoin_opportunity_score(
                pnl_percent, rsi, above_ma_50, above_ma_200
            )
            
            # Generate recommendation
            recommendation = self._get_altcoin_recommendation(
                pnl_percent, rsi, opportunity_score
            )
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'avg_price': avg_price,
                'pnl_percent': round(pnl_percent, 1),
                'rsi': rsi,
                'above_ma_50': above_ma_50,
                'above_ma_200': above_ma_200,
                'opportunity_score': opportunity_score,
                'recommendation': recommendation
            }
            
        except Exception as e:
            logger.error(f"Altcoin analysis failed for {symbol}: {e}")
            return None
    
    def _calculate_altcoin_opportunity_score(self, pnl_percent: float, rsi: float, 
                                           above_ma_50: bool, above_ma_200: bool) -> int:
        """Calculate opportunity score for altcoin (0-100)"""
        score = 0
        
        # Handle None values safely
        pnl_percent = pnl_percent if pnl_percent is not None else 0
        rsi = rsi if rsi is not None else 50
        
        # Profit level (higher profit = higher exit opportunity)
        if pnl_percent > 50:
            score += 40
        elif pnl_percent > 20:
            score += 25
        elif pnl_percent > 0:
            score += 10
        else:
            score -= 20  # In loss, lower priority for exit
        
        # RSI overbought (higher RSI = better exit opportunity)
        if rsi > 80:
            score += 30
        elif rsi > 70:
            score += 20
        elif rsi > 60:
            score += 10
        elif rsi < 30:
            score -= 15  # Oversold, might bounce
        
        # Technical position
        if above_ma_50 and above_ma_200:
            score += 15  # Strong position
        elif above_ma_200:
            score += 5   # Decent position
        else:
            score -= 10  # Weak position
        
        return max(0, min(100, score))
    
    def _get_altcoin_recommendation(self, pnl_percent: float, rsi: float, 
                                  opportunity_score: int) -> Dict:
        """Generate specific recommendation for altcoin"""
        
        # Handle None values safely
        pnl_percent = pnl_percent if pnl_percent is not None else 0
        rsi = rsi if rsi is not None else 50
        opportunity_score = opportunity_score if opportunity_score is not None else 0
        
        if opportunity_score > 70:
            if pnl_percent > 30 and rsi > 75:
                return {
                    'action': 'STRONG_SELL',
                    'reason': f'High profit ({pnl_percent:.1f}%) + overbought (RSI {rsi:.0f})',
                    'confidence': 'HIGH'
                }
            else:
                return {
                    'action': 'PARTIAL_SELL',
                    'reason': f'Good exit opportunity (score {opportunity_score})',
                    'confidence': 'MEDIUM'
                }
        
        elif opportunity_score > 40:
            return {
                'action': 'MONITOR_CLOSELY',
                'reason': f'Moderate opportunity (score {opportunity_score})',
                'confidence': 'MEDIUM'
            }
        
        elif pnl_percent < -10 and rsi < 40:
            return {
                'action': 'HODL',
                'reason': f'In loss ({pnl_percent:.1f}%), oversold - wait for recovery',
                'confidence': 'MEDIUM'
            }
        
        else:
            return {
                'action': 'HOLD',
                'reason': 'No clear signal',
                'confidence': 'LOW'
            }
    
    def _generate_recommendations(self, eth_btc_analysis: Dict, altseason_analysis: Dict,
                                altcoin_analysis: List[Dict], data: Dict) -> List[Dict]:
        """Generate prioritized strategic recommendations"""
        recommendations = []
        
        # Calculate cycle top risk and partial exit recommendations
        partial_exit_rec = self._calculate_partial_exit_strategy(data, altseason_analysis)
        if partial_exit_rec:
            recommendations.append(partial_exit_rec)
        
        # ETH/BTC swap recommendations
        swap_rec = eth_btc_analysis.get('swap_recommendation', {})
        if swap_rec.get('confidence') in ['HIGH', 'MEDIUM']:
            recommendations.append({
                'priority': 1,
                'type': 'BTC_ETH_SWAP',
                'action': swap_rec.get('action'),
                'reason': ', '.join(swap_rec.get('signals', [])),
                'confidence': swap_rec.get('confidence')
            })
        
        # Altcoin exit recommendations (during altseason peak)
        if altseason_analysis.get('exit_alts_signal', False):
            strong_sell_alts = [alt for alt in altcoin_analysis 
                              if alt.get('recommendation', {}).get('action') == 'STRONG_SELL']
            
            if strong_sell_alts:
                recommendations.append({
                    'priority': 1,
                    'type': 'ALTCOIN_EXIT',
                    'action': 'SELL_ALTS',
                    'coins': [alt['symbol'] for alt in strong_sell_alts[:3]],  # Top 3
                    'reason': f"Altseason peak detected - take profits on {len(strong_sell_alts)} coins",
                    'confidence': 'HIGH'
                })
        
        # Individual altcoin opportunities
        for alt in altcoin_analysis[:5]:  # Top 5 opportunities
            if alt.get('opportunity_score', 0) > 60:
                recommendations.append({
                    'priority': 2,
                    'type': 'ALTCOIN_INDIVIDUAL',
                    'action': alt['recommendation']['action'],
                    'coin': alt['symbol'],
                    'reason': alt['recommendation']['reason'],
                    'confidence': alt['recommendation']['confidence'],
                    'pnl': alt['pnl_percent']
                })
        
        return recommendations

    def _calculate_partial_exit_strategy(self, data: Dict, altseason_analysis: Dict) -> Optional[Dict]:
        """
        Calculate partial exit recommendations based on cycle top risk
        
        Returns partial sell recommendations when risk score exceeds thresholds:
        - Risk 60-74: Sell 10%
        - Risk 75-84: Sell 25% 
        - Risk 85+: Sell 50%
        """
        try:
            # Get BTC data for cycle analysis
            btc_data = data.get('bitcoin', {})
            if not btc_data:
                return None
            
            btc_price = btc_data.get('usd', 0)
            btc_historical = btc_data.get('historical')
            
            if btc_historical is None or btc_historical.empty:
                return None
            
            # Calculate cycle risk indicators
            risk_score = 0
            risk_factors = []
            
            # 1. Pi Cycle Top Indicator
            pi_cycle_data = self.indicators.calculate_pi_cycle_top(btc_historical)
            if pi_cycle_data.get('pi_cycle_signal', False):
                risk_score += 30
                risk_factors.append("Pi Cycle Top triggered")
            elif pi_cycle_data.get('distance', 0) > -5:  # Close to trigger
                risk_score += 15
                risk_factors.append("Approaching Pi Cycle Top")
            
            # 2. RSI Analysis
            btc_indicators = self.indicators.get_latest_indicator_values(
                btc_historical, {'rsi_period': 14, 'enable_rci': True}
            )
            btc_rsi = btc_indicators.get('rsi', 50)
            
            if btc_rsi > 80:
                risk_score += 25
                risk_factors.append(f"BTC RSI extremely overbought ({btc_rsi:.1f})")
            elif btc_rsi > 70:
                risk_score += 15
                risk_factors.append(f"BTC RSI overbought ({btc_rsi:.1f})")
            
            # 3. RCI 3-Line analysis for trend exhaustion
            rci_signal = btc_indicators.get('signal', 'NEUTRAL')
            if rci_signal == 'STRONG_SELL':
                risk_score += 20
                risk_factors.append("RCI signals trend exhaustion")
            elif rci_signal == 'SELL':
                risk_score += 10
                risk_factors.append("RCI shows weakening trend")
            
            # 4. Altseason analysis contribution
            altseason_score = altseason_analysis.get('altseason_score', 0)
            if altseason_score > 50:  # Peak altseason
                risk_score += 15
                risk_factors.append("Altseason at peak levels")
            
            # 5. Fear & Greed extreme levels
            fear_greed_data = data.get('fear_greed_index', {})
            fear_greed_value = fear_greed_data.get('value', 50) if fear_greed_data else 50
            
            if fear_greed_value >= 80:
                risk_score += 20
                risk_factors.append(f"Extreme Greed ({fear_greed_value})")
            elif fear_greed_value >= 70:
                risk_score += 10
                risk_factors.append(f"High Greed ({fear_greed_value})")
            
            # Determine partial exit recommendation
            if risk_score >= 85:
                return {
                    'priority': 0,  # Highest priority
                    'type': 'PARTIAL_EXIT',
                    'action': 'SELL_50_PERCENT',
                    'sell_percentage': 50,
                    'risk_score': risk_score,
                    'reason': f"Critical risk level ({risk_score}/100) - Major profit taking recommended",
                    'risk_factors': risk_factors,
                    'confidence': 'HIGH',
                    'urgency': 'IMMEDIATE'
                }
            elif risk_score >= 75:
                return {
                    'priority': 1,
                    'type': 'PARTIAL_EXIT',
                    'action': 'SELL_25_PERCENT',
                    'sell_percentage': 25,
                    'risk_score': risk_score,
                    'reason': f"High risk level ({risk_score}/100) - Partial profit taking",
                    'risk_factors': risk_factors,
                    'confidence': 'HIGH',
                    'urgency': 'HIGH'
                }
            elif risk_score >= 60:
                return {
                    'priority': 2,
                    'type': 'PARTIAL_EXIT',
                    'action': 'SELL_10_PERCENT',
                    'sell_percentage': 10,
                    'risk_score': risk_score,
                    'reason': f"Moderate risk level ({risk_score}/100) - Light profit taking",
                    'risk_factors': risk_factors,
                    'confidence': 'MEDIUM',
                    'urgency': 'MEDIUM'
                }
            
            return None  # No partial exit needed
            
        except Exception as e:
            logger.error(f"Partial exit strategy calculation failed: {e}")
            return None
    
    def _calculate_goal_progress(self, data: Dict) -> Dict:
        """Calculate progress toward 1 BTC + 10 ETH goal"""
        # This is simplified - in reality you'd need actual portfolio quantities
        # For now, we'll show the goal and current prices
        
        btc_price = data.get('bitcoin', {}).get('usd', 0)
        eth_price = data.get('ethereum', {}).get('usd', 0)
        
        goal_value_usd = (self.target_btc * btc_price) + (self.target_eth * eth_price)
        
        return {
            'target_btc': self.target_btc,
            'target_eth': self.target_eth,
            'goal_value_usd': round(goal_value_usd, 2),
            'btc_price': btc_price,
            'eth_price': eth_price,
            'note': 'Add actual portfolio quantities for precise tracking'
        }
    
    def _determine_market_phase(self, data: Dict, market_metrics: Dict) -> str:
        """Determine overall market phase"""
        btc_data = data.get('bitcoin', {})
        btc_price = btc_data.get('usd', 0)
        
        # Calculate BTC RSI if historical data available
        btc_rsi = 50
        btc_historical = btc_data.get('historical')
        if btc_historical is not None and not btc_historical.empty:
            try:
                btc_indicators = self.indicators.get_latest_indicator_values(
                    btc_historical, {'rsi_period': 14}
                )
                btc_rsi = btc_indicators.get('rsi', 50)
            except Exception as e:
                logger.debug(f"Failed to calculate BTC RSI for market phase: {e}")
        
        btc_dominance = market_metrics.get('btc_dominance', 50)
        fear_greed_data = market_metrics.get('fear_greed_index', {})
        fear_greed = fear_greed_data.get('value', 50) if isinstance(fear_greed_data, dict) else 50
        
        if fear_greed > 80 and btc_rsi > 70:
            return "EUPHORIA - Consider reducing risk"
        elif fear_greed < 20 and btc_rsi < 30:
            return "EXTREME_FEAR - Accumulation opportunity"
        elif btc_dominance and btc_dominance > 60:
            return "BTC_SEASON - Focus on BTC"
        elif btc_dominance and btc_dominance < 45:
            return "ALTSEASON - Monitor alt exits"
        else:
            return "NEUTRAL - Wait for clearer signals"
    
    def _analyze_ratio_trend(self, current_ratio: float) -> str:
        """Analyze ETH/BTC ratio trend"""
        # Simplified trend analysis
        if current_ratio < 0.05:
            return "ETH very cheap vs BTC - consider accumulating ETH"
        elif current_ratio > 0.08:
            return "ETH expensive vs BTC - consider BTC"
        else:
            return "ETH/BTC ratio in normal range"
    
    def generate_strategic_report(self) -> str:
        """Generate formatted strategic report with clear analysis and actions"""
        analysis = self.analyze_strategic_position()
        
        if 'error' in analysis:
            return f"❌ Análise Estratégica - Erro: {analysis['error']}"
        
        # Get current progress and calculate portfolio metrics
        progress = analysis.get('current_progress', {})
        altcoin_opportunities = analysis.get('altcoin_opportunities', [])
        eth_btc_analysis = analysis.get('eth_btc_analysis', {})
        altseason_status = analysis.get('altseason_status', {})
        market_phase = analysis.get('market_phase', 'UNKNOWN')
        
        # Calculate portfolio value and goal achievement potential
        portfolio_analysis = self._calculate_portfolio_achievement(altcoin_opportunities, progress)
        
        report = []
        report.append("🎯 ESTRATÉGIA CRYPTO - Goal: 1 BTC + 10 ETH")
        report.append("=" * 50)
        
        # Portfolio Achievement Analysis
        if portfolio_analysis:
            report.append("💰 ANÁLISE DO PORTFÓLIO:")
            total_alt_value = portfolio_analysis.get('total_altcoin_value_usd', 0)
            goal_value = portfolio_analysis.get('goal_value_usd', 0)
            btc_equivalent = portfolio_analysis.get('total_altcoin_value_btc', 0)
            achievement_percent = portfolio_analysis.get('achievement_percentage', 0)
            
            report.append(f"   Valor das Altcoins: ${total_alt_value:,.0f}")
            report.append(f"   Meta (1 BTC + 10 ETH): ${goal_value:,.0f}")
            report.append(f"   Equivalente em BTC: {btc_equivalent:.3f} BTC")
            report.append(f"   Alcance da Meta: {achievement_percent:.1f}%")
            
            if achievement_percent >= 100:
                report.append("   🎉 AÇÃO: Você pode alcançar a meta vendendo altcoins!")
            elif achievement_percent >= 80:
                report.append("   ⚠️ AÇÃO: Muito próximo da meta - considere vendas parciais")
            else:
                report.append("   📈 AÇÃO: Continue acumulando - ainda distante da meta")
        
        report.append("")
        
        # Market Phase Analysis
        report.append("📊 FASE DO MERCADO:")
        if "EUPHORIA" in market_phase:
            report.append("   Status: EUFORIA - Zona de perigo")
            report.append("   🚨 AÇÃO: Venda parcial imediatamente")
        elif "FEAR" in market_phase:
            report.append("   Status: MEDO EXTREMO - Oportunidade")
            report.append("   💎 AÇÃO: Acumule agressivamente")
        elif "BTC_SEASON" in market_phase:
            report.append("   Status: BTC SEASON - Dominância alta")
            report.append("   ₿ AÇÃO: Foque em acumular BTC")
        elif "ALTSEASON" in market_phase:
            report.append("   Status: ALTSEASON - Altcoins em alta")
            report.append("   🌟 AÇÃO: Monitore saídas de altcoins")
        else:
            report.append("   Status: NEUTRO - Aguardando sinais")
            report.append("   ⏳ AÇÃO: Mantenha posições atuais")
        
        report.append("")
        
        # Cycle Top Analysis
        cycle_risk = self._calculate_enhanced_cycle_risk(analysis)
        report.append("🔺 ANÁLISE DE TOPO:")
        report.append(f"   Risco: {cycle_risk['score']}/100 ({cycle_risk['level']})")
        if cycle_risk['score'] >= 80:
            report.append("   🔴 AÇÃO: TOPO PRÓXIMO - Venda 50-70% do portfólio")
        elif cycle_risk['score'] >= 60:
            report.append("   🟠 AÇÃO: Alto risco - Venda 20-30% dos lucros")
        elif cycle_risk['score'] >= 40:
            report.append("   🟡 AÇÃO: Risco moderado - Prepare vendas parciais")
        elif cycle_risk['score'] >= 20:
            report.append("   � AÇÃO: Baixo risco - Continue acumulando")
        else:
            report.append("   💎 AÇÃO: Risco mínimo - Acumule agressivamente")
        
        report.append("")
        
        # Altseason Metric
        altseason = altseason_status
        if 'error' not in altseason:
            phase = altseason.get('phase', 'UNKNOWN')
            score = altseason.get('score', 0)
            
            report.append("🌟 ALTSEASON METRIC:")
            report.append(f"   Status: {phase} (Score: {score})")
            
            if phase == "PEAK_ALTSEASON":
                report.append("   🎯 AÇÃO: VENDA ALTCOINS AGORA - Pico detectado")
            elif phase == "ALTSEASON":
                report.append("   📈 AÇÃO: Monitore altcoins para vendas parciais")
            elif phase == "BTC_SEASON":
                report.append("   ₿ AÇÃO: Mova capital para BTC")
            else:
                report.append("   ⏳ AÇÃO: Aguarde sinais mais claros")
        
        report.append("")
        
        # BTC/ETH Ratio Analysis
        eth_btc = eth_btc_analysis
        if 'error' not in eth_btc:
            ratio = eth_btc.get('current_ratio', 0)
            swap_rec = eth_btc.get('swap_recommendation', {})
            
            report.append("⚖️ BTC/ETH RATIO:")
            report.append(f"   Ratio Atual: {ratio:.4f}")
            
            action = swap_rec.get('action', 'HOLD')
            confidence = swap_rec.get('confidence', 'LOW')
            
            if action == 'SWAP_BTC_TO_ETH' and confidence == 'HIGH':
                report.append("   🔄 AÇÃO: TROQUE BTC por ETH - Alta confiança")
            elif action == 'SWAP_ETH_TO_BTC' and confidence == 'HIGH':
                report.append("   🔄 AÇÃO: TROQUE ETH por BTC - Alta confiança")
            elif action == 'FAVOR_ETH':
                report.append("   📈 AÇÃO: Prefira ETH nas próximas compras")
            elif action == 'FAVOR_BTC':
                report.append("   📈 AÇÃO: Prefira BTC nas próximas compras")
            else:
                report.append("   ⏳ AÇÃO: Mantenha proporção atual BTC/ETH")
        
        report.append("")
        
        # Top Altcoin Actions
        if altcoin_opportunities:
            report.append("💎 TOP ALTCOIN AÇÕES:")
            strong_sells = [alt for alt in altcoin_opportunities 
                          if alt.get('recommendation', {}).get('action') == 'STRONG_SELL']
            
            if strong_sells:
                for alt in strong_sells[:3]:  # Top 3
                    symbol = alt.get('symbol', 'UNKNOWN')
                    pnl = alt.get('pnl_percent', 0)
                    report.append(f"   � {symbol}: +{pnl:.1f}% - VENDA IMEDIATA")
            
            monitor_coins = [alt for alt in altcoin_opportunities 
                           if alt.get('recommendation', {}).get('action') == 'MONITOR_CLOSELY']
            
            if monitor_coins:
                for alt in monitor_coins[:2]:  # Top 2
                    symbol = alt.get('symbol', 'UNKNOWN')
                    pnl = alt.get('pnl_percent', 0)
                    score = alt.get('opportunity_score', 0)
                    report.append(f"   👁️ {symbol}: +{pnl:.1f}% - Score {score} - Monitore")
        
        report.append("")
        report.append(f"⏰ Atualizado: {datetime.now().strftime('%H:%M:%S')}")
        
        return "\n".join(report)
    
    def _calculate_portfolio_achievement(self, altcoins: List[Dict], progress: Dict) -> Dict:
        """Calculate if selling altcoins can achieve the 1 BTC + 10 ETH goal"""
        try:
            btc_price = progress.get('btc_price', 0)
            eth_price = progress.get('eth_price', 0)
            
            if btc_price == 0 or eth_price == 0:
                return {}
            
            # Calculate total altcoin value using a more realistic approach
            # Instead of fixed quantities, use a percentage-based approach
            total_altcoin_value_usd = 0
            
            # Get config to check avg_price vs current_price for each altcoin
            altcoin_configs = [coin for coin in self.config['coins'] 
                             if coin['coingecko_id'] not in ['bitcoin', 'ethereum']]
            
            # Use realistic portfolio allocation instead of fixed 1000 units
            # Assume total altcoin investment based on performance data
            estimated_total_altcoin_investment = 0
            
            for alt in altcoins:
                symbol = alt.get('symbol', '')
                current_price = alt.get('current_price', 0)
                pnl_percent = alt.get('pnl_percent', 0)
                
                # Find the config for this altcoin
                config_coin = next((c for c in altcoin_configs if c.get('symbol') == symbol), None)
                if config_coin:
                    avg_price = config_coin.get('avg_price', current_price)
                    
                    # Estimate initial investment (this should be replaced with actual holdings)
                    # For now, use a conservative estimate based on typical DCA amounts
                    estimated_investment_per_coin = 1000  # $1000 per altcoin (adjust this!)
                    
                    # Calculate current value based on performance
                    if pnl_percent != 0:
                        current_value = estimated_investment_per_coin * (1 + pnl_percent / 100)
                    else:
                        current_value = estimated_investment_per_coin
                    
                    total_altcoin_value_usd += current_value
            
            # Goal value: 1 BTC + 10 ETH
            goal_value_usd = (self.target_btc * btc_price) + (self.target_eth * eth_price)
            
            # BTC equivalent of altcoins
            total_altcoin_value_btc = total_altcoin_value_usd / btc_price
            
            # Achievement percentage
            achievement_percentage = (total_altcoin_value_usd / goal_value_usd) * 100
            
            return {
                'total_altcoin_value_usd': total_altcoin_value_usd,
                'total_altcoin_value_btc': total_altcoin_value_btc,
                'goal_value_usd': goal_value_usd,
                'achievement_percentage': achievement_percentage
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate portfolio achievement: {e}")
            return {}
    
    def _calculate_cycle_top_risk(self, analysis: Dict) -> Dict:
        """Calculate cycle top risk score and level"""
        try:
            # This is a simplified risk calculation
            # You can integrate with your existing cycle_top_detector
            
            eth_btc = analysis.get('eth_btc_analysis', {})
            altseason = analysis.get('altseason_status', {})
            
            risk_score = 0
            
            # ETH/BTC ratio risk
            ratio = eth_btc.get('current_ratio', 0.05)
            if ratio > 0.08:
                risk_score += 20
            elif ratio < 0.04:
                risk_score += 10
            
            # Altseason risk
            altseason_score = altseason.get('score', 0)
            if altseason_score > 40:
                risk_score += 30
            elif altseason_score > 20:
                risk_score += 15
            
            # Market phase risk
            market_phase = analysis.get('market_phase', '')
            if 'EUPHORIA' in market_phase:
                risk_score += 40
            elif 'FEAR' in market_phase:
                risk_score -= 20
            
            # Ensure score is between 0-100
            risk_score = max(0, min(100, risk_score))
            
            # Determine level
            if risk_score >= 80:
                level = "CRÍTICO"
            elif risk_score >= 60:
                level = "ALTO"
            elif risk_score >= 40:
                level = "MODERADO"
            elif risk_score >= 20:
                level = "BAIXO"
            else:
                level = "MÍNIMO"
            
            return {
                'score': risk_score,
                'level': level
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate cycle top risk: {e}")
            return {'score': 0, 'level': 'UNKNOWN'}

    def _calculate_enhanced_cycle_risk(self, analysis: Dict) -> Dict:
        """
        Calculate enhanced cycle top risk using new indicators (Pi Cycle + RCI)
        """
        try:
            # Get BTC data for enhanced analysis
            data = {}  # This should be passed from analyze_strategic_position
            btc_data = data.get('bitcoin', {})
            btc_historical = btc_data.get('historical')
            
            risk_score = 0
            pi_cycle_info = {}
            rci_info = {}
            
            # If we have BTC historical data, calculate new indicators
            if btc_historical is not None and not btc_historical.empty:
                try:
                    # Pi Cycle Top Indicator
                    pi_cycle_data = self.indicators.calculate_pi_cycle_top(btc_historical)
                    pi_cycle_info = pi_cycle_data
                    
                    if pi_cycle_data.get('pi_cycle_signal', False):
                        risk_score += 30  # Major risk if Pi Cycle triggered
                    elif pi_cycle_data.get('distance', -100) > -5:
                        risk_score += 15  # Moderate risk if approaching
                    
                    # RCI 3-Line Analysis
                    rci_data = self.indicators.calculate_rci_3_line(btc_historical)
                    rci_info = rci_data
                    
                    rci_signal = rci_data.get('signal', 'NEUTRAL')
                    if rci_signal == 'STRONG_SELL':
                        risk_score += 20
                    elif rci_signal == 'SELL':
                        risk_score += 10
                    
                    # RSI contribution
                    btc_indicators = self.indicators.get_latest_indicator_values(
                        btc_historical, {'rsi_period': 14}
                    )
                    btc_rsi = btc_indicators.get('rsi', 50)
                    
                    if btc_rsi > 80:
                        risk_score += 25
                    elif btc_rsi > 70:
                        risk_score += 15
                    
                except Exception as e:
                    logger.debug(f"Enhanced indicators calculation failed: {e}")
            
            # Add traditional risk factors
            traditional_risk = self._calculate_cycle_top_risk(analysis)
            risk_score += traditional_risk.get('score', 0) * 0.5  # Weight traditional score at 50%
            
            # Ensure score is between 0-100
            risk_score = max(0, min(100, int(risk_score)))
            
            # Determine level
            if risk_score >= 85:
                level = "EXTREMO"
            elif risk_score >= 75:
                level = "CRÍTICO"
            elif risk_score >= 60:
                level = "ALTO"
            elif risk_score >= 40:
                level = "MODERADO"
            elif risk_score >= 20:
                level = "BAIXO"
            else:
                level = "MÍNIMO"
            
            return {
                'score': risk_score,
                'level': level,
                'pi_cycle': pi_cycle_info,
                'rci': rci_info
            }
            
        except Exception as e:
            logger.error(f"Enhanced cycle risk calculation failed: {e}")
            # Fallback to traditional calculation
            return self._calculate_cycle_top_risk(analysis)
