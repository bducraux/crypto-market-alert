"""
Unit tests for strategy module
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from src.strategy import AlertStrategy


class TestAlertStrategy:
    """Test cases for AlertStrategy class"""
    
    @pytest.fixture
    def sample_config(self):
        """Create sample configuration for testing"""
        return {
            'coins': [
                {
                    'symbol': 'bitcoin',
                    'name': 'BTC',
                    'coingecko_id': 'bitcoin',
                    'alerts': {
                        'price_above': 50000,
                        'price_below': 40000,
                        'rsi_oversold': 30,
                        'rsi_overbought': 70
                    }
                },
                {
                    'symbol': 'ethereum',
                    'name': 'ETH',
                    'coingecko_id': 'ethereum',
                    'alerts': {
                        'price_above': 3500,
                        'price_below': 2500,
                        'rsi_oversold': 25,
                        'rsi_overbought': 75
                    }
                }
            ],
            'indicators': {
                'rsi_period': 14,
                'ma_short': 50,
                'ma_long': 200,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9
            },
            'market_metrics': {
                'btc_dominance': {
                    'above': 60.0,
                    'below': 40.0
                },
                'eth_btc_ratio': {
                    'above': 0.08,
                    'below': 0.04
                },
                'fear_greed_index': {
                    'extreme_fear': 20,
                    'extreme_greed': 80
                }
            },
            'alert_cooldown': {
                'price_alert': 60,
                'indicator_alert': 30,
                'market_metric_alert': 120
            }
        }
    
    @pytest.fixture
    def strategy(self, sample_config):
        """Create an AlertStrategy instance for testing"""
        return AlertStrategy(sample_config)
    
    @pytest.fixture
    def sample_coin_data(self):
        """Create sample coin market data"""
        return {
            'usd': 45000.0,
            'usd_24h_change': 2.5,
            'usd_market_cap': 850000000000,
            'usd_24h_vol': 25000000000
        }
    
    @pytest.fixture
    def sample_coin_config(self):
        """Create sample coin configuration"""
        return {
            'name': 'BTC',
            'symbol': 'bitcoin',
            'coingecko_id': 'bitcoin',
            'alerts': {
                'price_above': 50000,
                'price_below': 40000,
                'rsi_oversold': 30,
                'rsi_overbought': 70
            }
        }
    
    @pytest.fixture
    def sample_price_df(self):
        """Create sample price DataFrame for technical analysis"""
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        np.random.seed(42)
        
        prices = []
        price = 45000
        for _ in range(100):
            change = np.random.normal(0, 0.02)
            price = price * (1 + change)
            prices.append(price)
        
        return pd.DataFrame({
            'open': prices,
            'high': [p * 1.02 for p in prices],
            'low': [p * 0.98 for p in prices],
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 100)
        }, index=dates)
    
    def test_initialization(self, strategy, sample_config):
        """Test AlertStrategy initialization"""
        assert strategy.config == sample_config
        assert strategy.indicators is not None
        assert strategy.cooldown_manager is not None
        assert hasattr(strategy, 'logger')
    
    def test_evaluate_price_alerts_above_threshold(self, strategy, sample_coin_config):
        """Test price alert when price is above threshold"""
        coin_data = {'usd': 55000.0}  # Above 50000 threshold
        
        alerts = strategy.evaluate_price_alerts(coin_data, sample_coin_config)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'price_above'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['priority'] == 'high'
        assert alerts[0]['current_price'] == 55000.0
        assert alerts[0]['threshold'] == 50000
    
    def test_evaluate_price_alerts_below_threshold(self, strategy, sample_coin_config):
        """Test price alert when price is below threshold"""
        coin_data = {'usd': 35000.0}  # Below 40000 threshold
        
        alerts = strategy.evaluate_price_alerts(coin_data, sample_coin_config)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'price_below'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['priority'] == 'high'
        assert alerts[0]['current_price'] == 35000.0
        assert alerts[0]['threshold'] == 40000
    
    def test_evaluate_price_alerts_within_range(self, strategy, sample_coin_config):
        """Test no price alerts when price is within normal range"""
        coin_data = {'usd': 45000.0}  # Between 40000 and 50000
        
        alerts = strategy.evaluate_price_alerts(coin_data, sample_coin_config)
        
        assert len(alerts) == 0
    
    def test_evaluate_price_alerts_no_price_data(self, strategy, sample_coin_config):
        """Test price alerts with missing price data"""
        coin_data = {}  # No price data
        
        alerts = strategy.evaluate_price_alerts(coin_data, sample_coin_config)
        
        assert len(alerts) == 0
    
    def test_evaluate_rsi_alerts_oversold(self, strategy, sample_coin_config):
        """Test RSI oversold alert"""
        indicators_data = {'rsi': 25.0}  # Below 30 threshold
        
        alerts = strategy.evaluate_rsi_alerts(indicators_data, sample_coin_config)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'rsi_oversold'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['priority'] == 'medium'
        assert alerts[0]['rsi_value'] == 25.0
        assert alerts[0]['threshold'] == 30
    
    def test_evaluate_rsi_alerts_overbought(self, strategy, sample_coin_config):
        """Test RSI overbought alert"""
        indicators_data = {'rsi': 75.0}  # Above 70 threshold
        
        alerts = strategy.evaluate_rsi_alerts(indicators_data, sample_coin_config)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'rsi_overbought'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['priority'] == 'medium'
        assert alerts[0]['rsi_value'] == 75.0
        assert alerts[0]['threshold'] == 70
    
    def test_evaluate_rsi_alerts_normal_range(self, strategy, sample_coin_config):
        """Test no RSI alerts when in normal range"""
        indicators_data = {'rsi': 50.0}  # Between 30 and 70
        
        alerts = strategy.evaluate_rsi_alerts(indicators_data, sample_coin_config)
        
        assert len(alerts) == 0
    
    def test_evaluate_rsi_alerts_no_rsi_data(self, strategy, sample_coin_config):
        """Test RSI alerts with missing RSI data"""
        indicators_data = {}  # No RSI data
        
        alerts = strategy.evaluate_rsi_alerts(indicators_data, sample_coin_config)
        
        assert len(alerts) == 0
    
    @patch('src.strategy.TechnicalIndicators.calculate_macd')
    @patch('src.strategy.TechnicalIndicators.detect_crossovers')
    def test_evaluate_macd_alerts_bullish_crossover(self, mock_crossovers, mock_macd, strategy, sample_coin_config, sample_price_df):
        """Test MACD bullish crossover alert"""
        # Mock MACD calculation
        mock_macd.return_value = {
            'macd': pd.Series([1, 2, 3]),
            'signal': pd.Series([2, 2, 2]),
            'histogram': pd.Series([-1, 0, 1])
        }
        
        # Mock crossover detection
        mock_crossovers.return_value = {
            'bullish_crossover': True,
            'bearish_crossover': False
        }
        
        alerts = strategy.evaluate_macd_alerts(sample_price_df, sample_coin_config)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'macd_bullish'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['signal'] == 'bullish'
    
    @patch('src.strategy.TechnicalIndicators.calculate_macd')
    @patch('src.strategy.TechnicalIndicators.detect_crossovers')
    def test_evaluate_macd_alerts_bearish_crossover(self, mock_crossovers, mock_macd, strategy, sample_coin_config, sample_price_df):
        """Test MACD bearish crossover alert"""
        # Mock MACD calculation
        mock_macd.return_value = {
            'macd': pd.Series([3, 2, 1]),
            'signal': pd.Series([2, 2, 2]),
            'histogram': pd.Series([1, 0, -1])
        }
        
        # Mock crossover detection
        mock_crossovers.return_value = {
            'bullish_crossover': False,
            'bearish_crossover': True
        }
        
        alerts = strategy.evaluate_macd_alerts(sample_price_df, sample_coin_config)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'macd_bearish'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['signal'] == 'bearish'
    
    @patch('src.strategy.TechnicalIndicators.calculate_moving_averages')
    @patch('src.strategy.TechnicalIndicators.detect_crossovers')
    def test_evaluate_ma_crossover_alerts_golden_cross(self, mock_crossovers, mock_ma, strategy, sample_coin_config, sample_price_df):
        """Test Golden Cross (MA bullish crossover) alert"""
        # Mock MA calculation
        mock_ma.return_value = {
            'ma_short': pd.Series([45000, 45100, 45200]),
            'ma_long': pd.Series([45100, 45100, 45100])
        }
        
        # Mock crossover detection
        mock_crossovers.return_value = {
            'bullish_crossover': True,
            'bearish_crossover': False
        }
        
        alerts = strategy.evaluate_ma_crossover_alerts(sample_price_df, sample_coin_config)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'golden_cross'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['priority'] == 'high'
        assert alerts[0]['signal'] == 'bullish'
    
    def test_evaluate_market_metric_alerts_btc_dominance_high(self, strategy):
        """Test BTC dominance high alert"""
        market_data = {'btc_dominance': 65.0}  # Above 60% threshold
        
        alerts = strategy.evaluate_market_metric_alerts(market_data)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'btc_dominance_high'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['priority'] == 'medium'
        assert alerts[0]['value'] == 65.0
        assert alerts[0]['threshold'] == 60.0
    
    def test_evaluate_market_metric_alerts_btc_dominance_low(self, strategy):
        """Test BTC dominance low alert"""
        market_data = {'btc_dominance': 35.0}  # Below 40% threshold
        
        alerts = strategy.evaluate_market_metric_alerts(market_data)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'btc_dominance_low'
        assert alerts[0]['coin'] == 'BTC'
        assert alerts[0]['priority'] == 'medium'
        assert alerts[0]['value'] == 35.0
        assert alerts[0]['threshold'] == 40.0
    
    def test_evaluate_market_metric_alerts_eth_btc_ratio_high(self, strategy):
        """Test ETH/BTC ratio high alert"""
        market_data = {'eth_btc_ratio': 0.09}  # Above 0.08 threshold
        
        alerts = strategy.evaluate_market_metric_alerts(market_data)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'eth_btc_ratio_high'
        assert alerts[0]['coin'] == 'ETH'
        assert alerts[0]['value'] == 0.09
        assert alerts[0]['threshold'] == 0.08
    
    def test_evaluate_market_metric_alerts_extreme_fear(self, strategy):
        """Test extreme fear alert"""
        market_data = {
            'fear_greed_index': {
                'value': 15,
                'value_classification': 'Extreme Fear'
            }
        }
        
        alerts = strategy.evaluate_market_metric_alerts(market_data)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'extreme_fear'
        assert alerts[0]['coin'] == 'Market'
        assert alerts[0]['priority'] == 'high'
        assert alerts[0]['value'] == 15
        assert alerts[0]['classification'] == 'Extreme Fear'
    
    def test_evaluate_market_metric_alerts_extreme_greed(self, strategy):
        """Test extreme greed alert"""
        market_data = {
            'fear_greed_index': {
                'value': 85,
                'value_classification': 'Extreme Greed'
            }
        }
        
        alerts = strategy.evaluate_market_metric_alerts(market_data)
        
        assert len(alerts) == 1
        assert alerts[0]['type'] == 'extreme_greed'
        assert alerts[0]['coin'] == 'Market'
        assert alerts[0]['priority'] == 'high'
        assert alerts[0]['value'] == 85
        assert alerts[0]['classification'] == 'Extreme Greed'
    
    def test_cooldown_manager_prevents_duplicate_alerts(self, strategy, sample_coin_config):
        """Test that cooldown manager prevents duplicate alerts"""
        coin_data = {'usd': 55000.0}  # Above threshold
        
        # First alert should be sent
        alerts1 = strategy.evaluate_price_alerts(coin_data, sample_coin_config)
        assert len(alerts1) == 1
        
        # Second alert (immediate) should be blocked by cooldown
        alerts2 = strategy.evaluate_price_alerts(coin_data, sample_coin_config)
        assert len(alerts2) == 0
    
    @patch('src.strategy.TechnicalIndicators.get_latest_indicator_values')
    def test_get_market_summary(self, mock_indicators, strategy):
        """Test market summary generation"""
        coin_data = {
            'bitcoin': {
                'usd': 45000.0,
                'usd_24h_change': 2.5,
                'usd_market_cap': 850000000000,
                'usd_24h_vol': 25000000000,
                'historical': pd.DataFrame({
                    'close': [44000, 44500, 45000]
                })
            }
        }
        
        market_data = {
            'btc_dominance': 42.5,
            'eth_btc_ratio': 0.067,
            'fear_greed_index': {
                'value': 50,
                'value_classification': 'Neutral'
            }
        }
        
        mock_indicators.return_value = {'rsi': 55.0, 'current_price': 45000.0}
        
        summary = strategy.get_market_summary(coin_data, market_data)
        
        assert 'timestamp' in summary
        assert 'coins' in summary
        assert 'market_metrics' in summary
        assert 'BTC' in summary['coins']
        assert summary['coins']['BTC']['price'] == 45000.0
        assert summary['market_metrics'] == market_data
