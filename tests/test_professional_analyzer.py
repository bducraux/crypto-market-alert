"""
Comprehensive tests for professional_analyzer module
Tests professional crypto analysis and signal generation
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.professional_analyzer import ProfessionalCryptoAnalyzer


class TestProfessionalCryptoAnalyzer:
    """Test ProfessionalCryptoAnalyzer functionality"""
    
    @pytest.fixture
    def config(self):
        """Default config for testing"""
        return {
            'professional_alerts': {
                'pnl_consideration': {
                    'min_profit_for_sell': 5.0,
                    'max_loss_for_sell': -15.0,
                    'hodl_on_loss': True,
                    'altseason_patience': True
                }
            }
        }
    
    @pytest.fixture
    def analyzer(self, config):
        """Create analyzer instance"""
        return ProfessionalCryptoAnalyzer(config)
    
    def test_init(self, config):
        """Test analyzer initialization"""
        analyzer = ProfessionalCryptoAnalyzer(config)
        assert analyzer.config == config
        assert analyzer.logger is not None
    
    def test_get_market_sentiment_capitulation(self, analyzer):
        """Test market sentiment during capitulation phase"""
        market_data = {
            'btc_dominance': 65.0,
            'fear_greed_index': {'value': 15},
            'eth_btc_ratio': 0.05
        }
        
        sentiment = analyzer.get_market_sentiment(market_data)
        
        assert sentiment['phase'] == 'CAPITULAÇÃO'
        assert sentiment['risk_level'] == 'BAIXO'
        assert sentiment['action_bias'] == 'COMPRA AGRESSIVA'
        assert sentiment['confidence'] == 85
        assert 'Pânico extremo' in sentiment['description']
    
    def test_get_market_sentiment_accumulation(self, analyzer):
        """Test market sentiment during accumulation phase"""
        market_data = {
            'btc_dominance': 58.0,
            'fear_greed_index': {'value': 25},
            'eth_btc_ratio': 0.055
        }
        
        sentiment = analyzer.get_market_sentiment(market_data)
        
        assert sentiment['phase'] == 'ACUMULAÇÃO'
        assert sentiment['risk_level'] == 'BAIXO-MÉDIO'
        assert sentiment['action_bias'] == 'COMPRA GRADUAL'
        assert sentiment['confidence'] == 75
        assert 'DCA' in sentiment['description']
    
    def test_get_market_sentiment_altcoin_euphoria(self, analyzer):
        """Test market sentiment during altcoin euphoria"""
        market_data = {
            'btc_dominance': 40.0,
            'fear_greed_index': {'value': 85},
            'eth_btc_ratio': 0.08
        }
        
        sentiment = analyzer.get_market_sentiment(market_data)
        
        assert sentiment['phase'] == 'EUFORIA ALTCOINS'
        assert sentiment['risk_level'] == 'MUITO ALTO'
        assert sentiment['action_bias'] == 'VENDA PARCIAL'
        assert sentiment['confidence'] == 90
        assert 'Risco de correção' in sentiment['description']
    
    def test_get_market_sentiment_distribution(self, analyzer):
        """Test market sentiment during distribution phase"""
        market_data = {
            'btc_dominance': 50.0,
            'fear_greed_index': {'value': 78},
            'eth_btc_ratio': 0.06
        }
        
        sentiment = analyzer.get_market_sentiment(market_data)
        
        assert sentiment['phase'] == 'DISTRIBUIÇÃO'
        assert sentiment['risk_level'] == 'ALTO'
        assert sentiment['action_bias'] == 'TOME LUCROS'
        assert sentiment['confidence'] == 80
        assert 'Realize lucros' in sentiment['description']
    
    def test_get_market_sentiment_altseason(self, analyzer):
        """Test market sentiment during altseason"""
        market_data = {
            'btc_dominance': 42.0,
            'fear_greed_index': {'value': 60},
            'eth_btc_ratio': 0.075
        }
        
        sentiment = analyzer.get_market_sentiment(market_data)
        
        assert sentiment['phase'] == 'ALTSEASON'
        assert sentiment['risk_level'] == 'MÉDIO'
        assert sentiment['action_bias'] == 'ROTAÇÃO ALTCOINS'
        assert sentiment['confidence'] == 70
        assert 'Altseason ativa' in sentiment['description']
    
    def test_get_market_sentiment_neutral(self, analyzer):
        """Test neutral market sentiment"""
        market_data = {
            'btc_dominance': 50.0,
            'fear_greed_index': {'value': 50},
            'eth_btc_ratio': 0.06
        }
        
        sentiment = analyzer.get_market_sentiment(market_data)
        
        assert sentiment['phase'] == 'NEUTRAL'
        assert sentiment['risk_level'] == 'MÉDIO'
        assert sentiment['action_bias'] == 'HOLD'
        assert sentiment['confidence'] == 50
    
    def test_get_market_sentiment_missing_data(self, analyzer):
        """Test sentiment with missing market data"""
        market_data = {}
        
        sentiment = analyzer.get_market_sentiment(market_data)
        
        # Should use defaults
        assert sentiment['phase'] == 'NEUTRAL'
        assert sentiment['confidence'] == 50
    
    def test_analyze_coin_signals_strong_buy(self, analyzer):
        """Test coin analysis with strong buy signals"""
        coin_data = {
            'usd': 45000.0,
            'indicators': {
                'rsi': 22.0,  # Extremely oversold
                'macd': 100.0,
                'macd_signal': 50.0,  # Strong bullish crossover
                'ma_short': 44000.0,
                'ma_long': 40000.0  # Golden cross
            }
        }
        
        coin_config = {
            'name': 'BTC',
            'avg_price': 50000.0  # In loss position
        }
        
        market_sentiment = {
            'phase': 'CAPITULAÇÃO',
            'action_bias': 'COMPRA AGRESSIVA',
            'risk_level': 'BAIXO'
        }
        
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, market_sentiment)
        
        assert analysis['coin'] == 'BTC'
        assert analysis['price'] == 45000.0
        assert analysis['signal_strength'] > 60
        assert analysis['action'] == 'COMPRA FORTE'
        assert analysis['urgency'] == 'ALTA'
        assert analysis['risk_reward'] == 'FAVORÁVEL'
        assert 'RSI extremamente oversold' in analysis['description']
    
    def test_analyze_coin_signals_gradual_buy(self, analyzer):
        """Test coin analysis with gradual buy signals"""
        coin_data = {
            'usd': 3000.0,
            'indicators': {
                'rsi': 32.0,  # Oversold
                'macd': 50.0,
                'macd_signal': 48.0,  # Mild bullish
                'ma_short': 3100.0,
                'ma_long': 3000.0  # Mild golden cross
            }
        }
        
        coin_config = {
            'name': 'ETH',
            'avg_price': 2800.0  # In profit
        }
        
        market_sentiment = {
            'phase': 'ACUMULAÇÃO',
            'action_bias': 'COMPRA GRADUAL',
            'risk_level': 'BAIXO-MÉDIO'
        }
        
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, market_sentiment)
        
        assert analysis['coin'] == 'ETH'
        assert analysis['signal_strength'] >= 40
        assert analysis['signal_strength'] < 60
        assert analysis['action'] == 'COMPRA GRADUAL'
        assert analysis['urgency'] == 'MÉDIA'
        assert analysis['pnl_percentage'] > 0  # Should be in profit
    
    def test_analyze_coin_signals_strong_sell(self, analyzer):
        """Test coin analysis with strong sell signals"""
        coin_data = {
            'usd': 60000.0,
            'indicators': {
                'rsi': 82.0,  # Extremely overbought
                'macd': 50.0,
                'macd_signal': 100.0,  # Strong bearish crossover
                'ma_short': 58000.0,
                'ma_long': 62000.0  # Death cross
            }
        }
        
        coin_config = {
            'name': 'BTC',
            'avg_price': 45000.0  # Good profit
        }
        
        market_sentiment = {
            'phase': 'EUFORIA ALTCOINS',
            'action_bias': 'VENDA PARCIAL',
            'risk_level': 'MUITO ALTO'
        }
        
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, market_sentiment)
        
        assert analysis['coin'] == 'BTC'
        assert analysis['signal_strength'] < -70
        assert analysis['action'] == 'VENDA IMEDIATA'
        assert analysis['urgency'] == 'ALTA'
        assert analysis['pnl_percentage'] > 5  # In good profit
    
    def test_analyze_coin_signals_hodl_on_loss(self, analyzer):
        """Test stop-loss decision when significant loss during altseason"""
        coin_data = {
            'usd': 100.0,
            'indicators': {
                'rsi': 78.0,  # Overbought
                'macd': 10.0,
                'macd_signal': 20.0,  # Bearish
                'ma_short': 95.0,
                'ma_long': 110.0  # Death cross
            }
        }
        
        coin_config = {
            'name': 'ALTCOIN',
            'avg_price': 150.0  # Significant loss (-33%)
        }
        
        market_sentiment = {
            'phase': 'ALTSEASON',
            'action_bias': 'ROTAÇÃO ALTCOINS',
            'risk_level': 'MÉDIO'
        }
        
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, market_sentiment)
        
        assert analysis['coin'] == 'ALTCOIN'
        assert analysis['signal_strength'] < -70
        # With significant loss (-33% > -15% threshold), system prioritizes capital protection
        assert analysis['action'] == 'VENDA IMEDIATA'  # Stop-loss kicks in
        assert analysis['pnl_percentage'] < -15  # Significant loss
        assert analysis['timeframe'] == 'IMEDIATO'  # Immediate action for capital protection
    
    def test_analyze_coin_signals_neutral_hold(self, analyzer):
        """Test neutral signals resulting in HOLD"""
        coin_data = {
            'usd': 45000.0,
            'indicators': {
                'rsi': 50.0,  # Neutral
                'macd': 100.0,
                'macd_signal': 98.0,  # Mild signals
                'ma_short': 45000.0,
                'ma_long': 44900.0  # Nearly flat
            }
        }
        
        coin_config = {
            'name': 'BTC',
            'avg_price': 44000.0
        }
        
        market_sentiment = {
            'phase': 'NEUTRAL',
            'action_bias': 'HOLD',
            'risk_level': 'MÉDIO'
        }
        
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, market_sentiment)
        
        assert analysis['coin'] == 'BTC'
        assert abs(analysis['signal_strength']) <= 30  # Should be weak signal
        assert analysis['action'] == 'HOLD/OBSERVE'
        assert analysis['urgency'] == 'BAIXA'
    
    def test_analyze_coin_signals_missing_indicators(self, analyzer):
        """Test analysis with missing technical indicators"""
        coin_data = {
            'usd': 45000.0,
            'indicators': {}  # No indicators
        }
        
        coin_config = {
            'name': 'BTC',
            'avg_price': 0  # No average price
        }
        
        market_sentiment = {
            'phase': 'NEUTRAL',
            'action_bias': 'HOLD',
            'risk_level': 'MÉDIO'
        }
        
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, market_sentiment)
        
        assert analysis['coin'] == 'BTC'
        assert analysis['signal_strength'] == 0
        assert analysis['pnl_percentage'] == 0
        assert analysis['action'] == 'HOLD/OBSERVE'
    
    def test_generate_professional_alert_strong_buy(self, analyzer):
        """Test generating alert for strong buy signal"""
        analysis = {
            'coin': 'BTC',
            'price': 45000.0,
            'signal_strength': 75,
            'action': 'COMPRA FORTE',
            'urgency': 'ALTA',
            'pnl_percentage': -10.0,
            'avg_price': 50000.0,
            'timeframe': 'CURTO PRAZO',
            'risk_reward': 'FAVORÁVEL',
            'description': 'RSI extremamente oversold | MACD bullish crossover',
            'specific_actions': ['COMPRE BTC imediatamente']
        }
        
        market_sentiment = {
            'phase': 'CAPITULAÇÃO',
            'action_bias': 'COMPRA AGRESSIVA'
        }
        
        alert = analyzer.generate_professional_alert(analysis, market_sentiment)
        
        assert alert is not None
        assert alert['type'] == 'professional_signal'
        assert alert['coin'] == 'BTC'
        assert alert['priority'] == 'high'
        assert 'COMPRA FORTE: BTC' in alert['message']
        assert '$45,000' in alert['message']
        assert '-10.0%' in alert['message']  # P&L
        assert 'Compre <b>BTC</b> AGORA' in alert['message']
        assert alert['signal_strength'] == 75
        assert alert['confidence'] == 75
    
    def test_generate_professional_alert_gradual_buy(self, analyzer):
        """Test generating alert for gradual buy signal"""
        analysis = {
            'coin': 'ETH',
            'price': 3000.0,
            'signal_strength': 45,
            'action': 'COMPRA GRADUAL',
            'urgency': 'MÉDIA',
            'pnl_percentage': 5.0,
            'avg_price': 2857.0,
            'timeframe': 'MÉDIO PRAZO',
            'risk_reward': 'POSITIVO',
            'description': 'RSI oversold',
            'specific_actions': ['Acumular ETH gradualmente']
        }
        
        market_sentiment = {
            'phase': 'ACUMULAÇÃO',
            'action_bias': 'COMPRA GRADUAL'
        }
        
        alert = analyzer.generate_professional_alert(analysis, market_sentiment)
        
        assert alert is not None
        assert alert['priority'] == 'medium'
        assert 'COMPRA GRADUAL: ETH' in alert['message']
        assert 'Acumule <b>ETH</b> gradualmente' in alert['message']
        assert 'DCA' in alert['message']
        assert '+5.0%' in alert['message']  # Positive P&L
    
    def test_generate_professional_alert_immediate_sell(self, analyzer):
        """Test generating alert for immediate sell signal"""
        analysis = {
            'coin': 'BTC',
            'price': 65000.0,
            'signal_strength': -85,
            'action': 'VENDA IMEDIATA',
            'urgency': 'ALTA',
            'pnl_percentage': 30.0,
            'avg_price': 50000.0,
            'timeframe': 'IMEDIATO',
            'risk_reward': 'PROTEÇÃO CAPITAL',
            'description': 'RSI extremely overbought | MACD bearish crossover',
            'specific_actions': ['VENDA BTC imediatamente']
        }
        
        market_sentiment = {
            'phase': 'EUFORIA ALTCOINS',
            'action_bias': 'VENDA PARCIAL'
        }
        
        alert = analyzer.generate_professional_alert(analysis, market_sentiment)
        
        assert alert is not None
        assert alert['priority'] == 'high'
        assert 'VENDA IMEDIATA: BTC' in alert['message']
        assert 'VENDA <b>BTC</b> IMEDIATAMENTE' in alert['message']
        assert 'Converta para USDC' in alert['message']
        assert '+30.0%' in alert['message']  # Good profit
    
    def test_generate_professional_alert_partial_sell(self, analyzer):
        """Test generating alert for partial sell signal"""
        analysis = {
            'coin': 'ETH',
            'price': 4000.0,
            'signal_strength': -55,
            'action': 'VENDA PARCIAL',
            'urgency': 'MÉDIA',
            'pnl_percentage': 15.0,
            'avg_price': 3478.0,
            'timeframe': 'CURTO PRAZO',
            'risk_reward': 'DEFENSIVO',
            'description': 'RSI overbought',
            'specific_actions': ['Vender parte da posição ETH']
        }
        
        market_sentiment = {
            'phase': 'DISTRIBUIÇÃO',
            'action_bias': 'TOME LUCROS'
        }
        
        alert = analyzer.generate_professional_alert(analysis, market_sentiment)
        
        assert alert is not None
        assert alert['priority'] == 'medium'
        assert 'VENDA PARCIAL: ETH' in alert['message']
        assert 'vender parte da posição' in alert['message']
        assert '(Lucro: +15.0%)' in alert['message']
    
    def test_generate_professional_alert_hodl_loss(self, analyzer):
        """Test generating alert for HODL during loss"""
        analysis = {
            'coin': 'ALTCOIN',
            'price': 80.0,
            'signal_strength': -75,
            'action': 'AGUARDAR ALTSEASON',
            'urgency': 'BAIXA',
            'pnl_percentage': -20.0,
            'avg_price': 100.0,
            'timeframe': 'LONGO PRAZO',
            'risk_reward': 'PACIÊNCIA ESTRATÉGICA',
            'description': 'Strong sell signals but in loss',
            'specific_actions': ['Wait for altseason recovery']
        }
        
        market_sentiment = {
            'phase': 'ALTSEASON',
            'action_bias': 'ROTAÇÃO ALTCOINS'
        }
        
        alert = analyzer.generate_professional_alert(analysis, market_sentiment)
        
        assert alert is not None
        assert alert['priority'] == 'low'
        assert 'AGUARDAR ALTSEASON' in alert['message']
        assert 'AGUARDE' in alert['message']
        assert '-20.0%' in alert['message']  # Loss percentage
        assert 'Altseason pode recuperar' in alert['message']
    
    def test_generate_professional_alert_weak_signal_filtered(self, analyzer):
        """Test that weak signals are filtered out"""
        analysis = {
            'coin': 'BTC',
            'price': 45000.0,
            'signal_strength': 25,  # Too weak
            'action': 'COMPRA GRADUAL',
            'urgency': 'BAIXA',
            'pnl_percentage': 0.0,
            'avg_price': 45000.0,
            'timeframe': 'MÉDIO PRAZO',
            'risk_reward': 'NEUTRO',
            'description': 'Weak signals',
            'specific_actions': []
        }
        
        market_sentiment = {
            'phase': 'NEUTRAL',
            'action_bias': 'HOLD'
        }
        
        alert = analyzer.generate_professional_alert(analysis, market_sentiment)
        
        assert alert is None  # Should be filtered out
    
    def test_generate_professional_alert_hold_filtered(self, analyzer):
        """Test that HOLD signals are filtered out"""
        analysis = {
            'coin': 'BTC',
            'price': 45000.0,
            'signal_strength': 35,  # Strong enough but...
            'action': 'HOLD/OBSERVE',  # This should be filtered
            'urgency': 'BAIXA',
            'pnl_percentage': 2.0,
            'avg_price': 44000.0,
            'timeframe': 'MÉDIO PRAZO',
            'risk_reward': 'NEUTRO',
            'description': 'Neutral signals',
            'specific_actions': []
        }
        
        market_sentiment = {
            'phase': 'NEUTRAL',
            'action_bias': 'HOLD'
        }
        
        alert = analyzer.generate_professional_alert(analysis, market_sentiment)
        
        assert alert is None  # HOLD/OBSERVE should be filtered out


class TestProfessionalAnalyzerIntegration:
    """Integration tests for the complete analysis flow"""
    
    @pytest.fixture
    def analyzer(self):
        config = {
            'professional_alerts': {
                'pnl_consideration': {
                    'min_profit_for_sell': 5.0,
                    'max_loss_for_sell': -15.0,
                    'hodl_on_loss': True,
                    'altseason_patience': True
                }
            }
        }
        return ProfessionalCryptoAnalyzer(config)
    
    def test_complete_analysis_flow_bull_market(self, analyzer):
        """Test complete analysis during accumulation phase with strong signals"""
        # Market in accumulation phase (better for buy signals)
        market_data = {
            'btc_dominance': 58.0,
            'fear_greed_index': {'value': 25},  # Fear phase, good for buying
            'eth_btc_ratio': 0.06
        }
        
        # Coin with very strong buy signals
        coin_data = {
            'usd': 50000.0,
            'indicators': {
                'rsi': 20.0,  # Very oversold
                'macd': 300.0,  # Strong bullish momentum
                'macd_signal': 100.0,
                'ma_short': 52000.0,
                'ma_long': 45000.0  # Strong golden cross
            }
        }
        
        coin_config = {
            'name': 'BTC',
            'avg_price': 45000.0  # In profit
        }
        
        # Step 1: Analyze market sentiment
        sentiment = analyzer.get_market_sentiment(market_data)
        assert sentiment['phase'] == 'ACUMULAÇÃO'
        assert sentiment['action_bias'] == 'COMPRA GRADUAL'
        
        # Step 2: Analyze coin signals
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, sentiment)
        assert analysis['coin'] == 'BTC'
        # In accumulation phase with very strong signals, should generate strong buy signal
        assert analysis['signal_strength'] > 60  # Strong buy signal
        assert analysis['action'] in ['COMPRA FORTE', 'COMPRA GRADUAL']
        
        # Step 3: Generate alert
        alert = analyzer.generate_professional_alert(analysis, sentiment)
        assert alert is not None
        assert alert['type'] == 'professional_signal'
        assert 'BTC' in alert['message']
    
    def test_complete_analysis_flow_bear_market(self, analyzer):
        """Test complete analysis during bear market"""
        # Bear market data
        market_data = {
            'btc_dominance': 65.0,
            'fear_greed_index': {'value': 15},
            'eth_btc_ratio': 0.05
        }
        
        # Coin with strong sell signals but in loss
        coin_data = {
            'usd': 30000.0,
            'indicators': {
                'rsi': 80.0,
                'macd': 50.0,
                'macd_signal': 150.0,
                'ma_short': 28000.0,
                'ma_long': 32000.0
            }
        }
        
        coin_config = {
            'name': 'BTC',
            'avg_price': 45000.0  # Significant loss
        }
        
        # Complete flow
        sentiment = analyzer.get_market_sentiment(market_data)
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, sentiment)
        alert = analyzer.generate_professional_alert(analysis, sentiment)
        
        # During capitulation, even strong sell signals might suggest HODL on loss
        assert sentiment['phase'] == 'CAPITULAÇÃO'
        assert analysis['pnl_percentage'] < -15  # Significant loss
        assert alert is not None  # Should generate some kind of alert
    
    def test_complete_analysis_flow_no_alert_generated(self, analyzer):
        """Test complete flow that results in no alert"""
        # Neutral market
        market_data = {
            'btc_dominance': 50.0,
            'fear_greed_index': {'value': 50},
            'eth_btc_ratio': 0.06
        }
        
        # Weak signals
        coin_data = {
            'usd': 45000.0,
            'indicators': {
                'rsi': 55.0,
                'macd': 100.0,
                'macd_signal': 95.0,
                'ma_short': 45100.0,
                'ma_long': 44900.0
            }
        }
        
        coin_config = {
            'name': 'BTC',
            'avg_price': 44000.0
        }
        
        # Complete flow
        sentiment = analyzer.get_market_sentiment(market_data)
        analysis = analyzer.analyze_coin_signals(coin_data, coin_config, sentiment)
        alert = analyzer.generate_professional_alert(analysis, sentiment)
        
        # Should not generate alert for weak signals
        assert sentiment['phase'] == 'NEUTRAL'
        assert abs(analysis['signal_strength']) <= 30  # Weak signals
        assert alert is None  # No alert for weak signals
