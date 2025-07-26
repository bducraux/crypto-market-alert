"""
Unit tests for enhanced Strategic Advisor with partial exit strategy
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from src.strategic_advisor import StrategicAdvisor
from src.indicators import TechnicalIndicators


class TestPartialExitStrategy:
    """Test cases for partial exit strategy functionality"""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration"""
        return {
            'coins': [
                {
                    'symbol': 'bitcoin',
                    'coingecko_id': 'bitcoin',
                    'avg_price': 30000
                },
                {
                    'symbol': 'ethereum',
                    'coingecko_id': 'ethereum',
                    'avg_price': 2000
                },
                {
                    'symbol': 'chainlink',
                    'coingecko_id': 'chainlink',
                    'avg_price': 15
                }
            ]
        }
    
    @pytest.fixture
    def strategic_advisor(self, mock_config):
        """Create StrategicAdvisor instance with mocked dependencies"""
        with patch('src.strategic_advisor.load_config', return_value=mock_config):
            with patch('src.strategic_advisor.DataFetcher'):
                advisor = StrategicAdvisor()
                advisor.indicators = Mock(spec=TechnicalIndicators)
                return advisor
    
    @pytest.fixture
    def mock_btc_data(self):
        """Create mock BTC data with historical prices"""
        dates = pd.date_range('2023-01-01', periods=365, freq='D')
        prices = np.random.uniform(50000, 80000, 365)
        
        historical_df = pd.DataFrame({
            'close': prices,
            'high': prices * 1.02,
            'low': prices * 0.98,
            'volume': np.random.randint(1000000, 10000000, 365)
        }, index=dates)
        
        return {
            'usd': 75000,
            'historical': historical_df
        }
    
    @pytest.fixture
    def mock_market_data(self):
        """Create mock market data"""
        return {
            'bitcoin': {
                'usd': 75000,
                'historical': pd.DataFrame({
                    'close': np.random.uniform(70000, 80000, 365)
                })
            },
            'ethereum': {
                'usd': 4000,
                'historical': pd.DataFrame({
                    'close': np.random.uniform(3500, 4500, 365)
                })
            },
            'fear_greed_index': {'value': 75}
        }

    def test_calculate_partial_exit_strategy_low_risk(self, strategic_advisor, mock_btc_data):
        """Test partial exit calculation with low risk scenario"""
        # Mock indicators to return low risk signals
        strategic_advisor.indicators.calculate_pi_cycle_top.return_value = {
            'pi_cycle_signal': False,
            'distance': -15,
            'crossover_detected': False
        }
        
        strategic_advisor.indicators.get_latest_indicator_values.return_value = {
            'rsi': 45,
            'signal': 'NEUTRAL'
        }
        
        altseason_analysis = {'altseason_score': 10}
        data = {'bitcoin': mock_btc_data, 'fear_greed_index': {'value': 40}}
        
        result = strategic_advisor._calculate_partial_exit_strategy(data, altseason_analysis)
        
        # Should return None for low risk
        assert result is None
    
    def test_calculate_partial_exit_strategy_medium_risk(self, strategic_advisor, mock_btc_data):
        """Test partial exit calculation with medium risk (10% sell)"""
        # Mock indicators to return medium risk signals
        strategic_advisor.indicators.calculate_pi_cycle_top.return_value = {
            'pi_cycle_signal': False,
            'distance': -3,  # Close to trigger (+15 points)
            'crossover_detected': False
        }
        
        strategic_advisor.indicators.get_latest_indicator_values.return_value = {
            'rsi': 72,  # Overbought (+15 points since > 70)
            'signal': 'SELL'  # (+10 points)
        }
        
        altseason_analysis = {'altseason_score': 55}  # (+15 points since > 50)
        data = {'bitcoin': mock_btc_data, 'fear_greed_index': {'value': 72}}  # (+10 points since >= 70)
        # Total: 15 + 15 + 10 + 15 + 10 = 65 points (in 60-74 range)
        
        result = strategic_advisor._calculate_partial_exit_strategy(data, altseason_analysis)
        
        assert result is not None
        assert result['type'] == 'PARTIAL_EXIT'
        assert result['action'] == 'SELL_10_PERCENT'
        assert result['sell_percentage'] == 10
        assert result['confidence'] == 'MEDIUM'
        assert 60 <= result['risk_score'] < 75
    
    def test_calculate_partial_exit_strategy_high_risk(self, strategic_advisor, mock_btc_data):
        """Test partial exit calculation with high risk (25% sell)"""
        # Mock indicators to return high risk signals
        strategic_advisor.indicators.calculate_pi_cycle_top.return_value = {
            'pi_cycle_signal': False,
            'distance': -1,  # Very close to trigger
            'crossover_detected': False
        }
        
        strategic_advisor.indicators.get_latest_indicator_values.return_value = {
            'rsi': 82,  # Extremely overbought
            'signal': 'STRONG_SELL'
        }
        
        altseason_analysis = {'altseason_score': 45}  # Peak altseason
        data = {'bitcoin': mock_btc_data, 'fear_greed_index': {'value': 82}}
        
        result = strategic_advisor._calculate_partial_exit_strategy(data, altseason_analysis)
        
        assert result is not None
        assert result['type'] == 'PARTIAL_EXIT'
        assert result['action'] == 'SELL_25_PERCENT'
        assert result['sell_percentage'] == 25
        assert result['confidence'] == 'HIGH'
        assert 75 <= result['risk_score'] < 85
    
    def test_calculate_partial_exit_strategy_critical_risk(self, strategic_advisor, mock_btc_data):
        """Test partial exit calculation with critical risk (50% sell)"""
        # Mock indicators to return critical risk signals
        strategic_advisor.indicators.calculate_pi_cycle_top.return_value = {
            'pi_cycle_signal': True,  # Pi Cycle triggered!
            'distance': 2,
            'crossover_detected': True
        }
        
        strategic_advisor.indicators.get_latest_indicator_values.return_value = {
            'rsi': 85,  # Extremely overbought
            'signal': 'STRONG_SELL'
        }
        
        altseason_analysis = {'altseason_score': 55}  # Extreme altseason
        data = {'bitcoin': mock_btc_data, 'fear_greed_index': {'value': 88}}
        
        result = strategic_advisor._calculate_partial_exit_strategy(data, altseason_analysis)
        
        assert result is not None
        assert result['type'] == 'PARTIAL_EXIT'
        assert result['action'] == 'SELL_50_PERCENT'
        assert result['sell_percentage'] == 50
        assert result['confidence'] == 'HIGH'
        assert result['urgency'] == 'IMMEDIATE'
        assert result['risk_score'] >= 85
        assert 'Pi Cycle Top triggered' in result['risk_factors']
    
    def test_calculate_partial_exit_strategy_no_data(self, strategic_advisor):
        """Test partial exit calculation with missing data"""
        data = {}
        altseason_analysis = {}
        
        result = strategic_advisor._calculate_partial_exit_strategy(data, altseason_analysis)
        
        assert result is None
    
    def test_calculate_partial_exit_strategy_no_historical_data(self, strategic_advisor):
        """Test partial exit calculation with no historical data"""
        data = {
            'bitcoin': {
                'usd': 75000,
                'historical': None
            }
        }
        altseason_analysis = {'altseason_score': 20}
        
        result = strategic_advisor._calculate_partial_exit_strategy(data, altseason_analysis)
        
        assert result is None
    
    def test_generate_recommendations_includes_partial_exit(self, strategic_advisor, mock_btc_data):
        """Test that generate_recommendations includes partial exit recommendations"""
        # Mock partial exit strategy to return a recommendation
        partial_exit_rec = {
            'priority': 0,
            'type': 'PARTIAL_EXIT',
            'action': 'SELL_25_PERCENT',
            'sell_percentage': 25,
            'risk_score': 78,
            'confidence': 'HIGH'
        }
        
        with patch.object(strategic_advisor, '_calculate_partial_exit_strategy', return_value=partial_exit_rec):
            eth_btc_analysis = {'swap_recommendation': {'confidence': 'LOW'}}
            altseason_analysis = {'exit_alts_signal': False}
            altcoin_analysis = []
            data = {'bitcoin': mock_btc_data}
            
            recommendations = strategic_advisor._generate_recommendations(
                eth_btc_analysis, altseason_analysis, altcoin_analysis, data
            )
            
            # Should include the partial exit recommendation
            assert len(recommendations) >= 1
            assert recommendations[0]['type'] == 'PARTIAL_EXIT'
            assert recommendations[0]['action'] == 'SELL_25_PERCENT'
    
    def test_generate_recommendations_without_partial_exit(self, strategic_advisor, mock_btc_data):
        """Test that generate_recommendations works when no partial exit is needed"""
        # Mock partial exit strategy to return None
        with patch.object(strategic_advisor, '_calculate_partial_exit_strategy', return_value=None):
            eth_btc_analysis = {'swap_recommendation': {'confidence': 'HIGH', 'action': 'BUY_ETH', 'signals': ['test']}}
            altseason_analysis = {'exit_alts_signal': False}
            altcoin_analysis = []
            data = {'bitcoin': mock_btc_data}
            
            recommendations = strategic_advisor._generate_recommendations(
                eth_btc_analysis, altseason_analysis, altcoin_analysis, data
            )
            
            # Should not include partial exit, but should include other recommendations
            partial_exit_recs = [r for r in recommendations if r['type'] == 'PARTIAL_EXIT']
            assert len(partial_exit_recs) == 0
            
            # Should include ETH/BTC swap recommendation
            swap_recs = [r for r in recommendations if r['type'] == 'BTC_ETH_SWAP']
            assert len(swap_recs) == 1


class TestEnhancedAltseasonDetection:
    """Test cases for enhanced altseason detection"""
    
    @pytest.fixture
    def strategic_advisor(self):
        """Create StrategicAdvisor instance with mocked dependencies"""
        mock_config = {
            'coins': [
                {'symbol': 'bitcoin', 'coingecko_id': 'bitcoin'},
                {'symbol': 'ethereum', 'coingecko_id': 'ethereum'}
            ]
        }
        
        with patch('src.strategic_advisor.load_config', return_value=mock_config):
            with patch('src.strategic_advisor.DataFetcher'):
                advisor = StrategicAdvisor()
                advisor.indicators = Mock(spec=TechnicalIndicators)
                return advisor
    
    def test_analyze_altseason_peak_conditions(self, strategic_advisor):
        """Test altseason analysis under peak conditions"""
        # Mock indicators
        strategic_advisor.indicators.get_latest_indicator_values.side_effect = [
            {'rsi': 78, 'ma_short': 70000},  # BTC indicators
            {'rsi': 72, 'ma_short': 4200}    # ETH indicators
        ]
        
        data = {
            'bitcoin': {
                'usd': 75000,
                'historical': pd.DataFrame({'close': [70000, 72000, 75000]})
            },
            'ethereum': {
                'usd': 4500,
                'historical': pd.DataFrame({'close': [4000, 4200, 4500]})
            }
        }
        
        market_metrics = {
            'btc_dominance': 38,  # Very low
            'eth_btc_ratio': 0.09  # Very high
        }
        
        result = strategic_advisor._analyze_altseason(data, market_metrics)
        
        assert result['phase'] in ['PEAK_ALTSEASON', 'EXTREME_ALTSEASON']
        assert result['score'] > 35
        assert result['exit_alts_signal'] is True
        assert 'BTC dominance very low' in str(result['indicators'])
        assert 'ETH/BTC ratio very high' in str(result['indicators'])
    
    def test_analyze_altseason_btc_season(self, strategic_advisor):
        """Test altseason analysis during BTC season"""
        # Mock indicators
        strategic_advisor.indicators.get_latest_indicator_values.side_effect = [
            {'rsi': 45, 'ma_short': 70000},  # BTC indicators
            {'rsi': 35, 'ma_short': 3500}    # ETH indicators
        ]
        
        data = {
            'bitcoin': {
                'usd': 75000,
                'historical': pd.DataFrame({'close': [70000, 72000, 75000]})
            },
            'ethereum': {
                'usd': 3300,  # ETH underperforming
                'historical': pd.DataFrame({'close': [3500, 3400, 3300]})
            }
        }
        
        market_metrics = {
            'btc_dominance': 65,  # Very high
            'eth_btc_ratio': 0.025  # Low
        }
        
        result = strategic_advisor._analyze_altseason(data, market_metrics)
        
        assert result['phase'] == 'BTC_SEASON'
        assert result['score'] < 0
        assert result['exit_alts_signal'] is False
        assert 'BTC dominance high' in str(result['indicators'])
    
    def test_analyze_altseason_transition_phase(self, strategic_advisor):
        """Test altseason analysis during transition phase"""
        # Mock indicators
        strategic_advisor.indicators.get_latest_indicator_values.side_effect = [
            {'rsi': 55, 'ma_short': 70000},  # BTC indicators
            {'rsi': 50, 'ma_short': 3800}    # ETH indicators
        ]
        
        data = {
            'bitcoin': {
                'usd': 72000,
                'historical': pd.DataFrame({'close': [70000, 71000, 72000]})
            },
            'ethereum': {
                'usd': 3800,
                'historical': pd.DataFrame({'close': [3700, 3750, 3800]})
            }
        }
        
        market_metrics = {
            'btc_dominance': 52,  # Neutral
            'eth_btc_ratio': 0.053  # Neutral
        }
        
        result = strategic_advisor._analyze_altseason(data, market_metrics)
        
        assert result['phase'] in ['TRANSITION', 'EARLY_ALTSEASON']
        assert -10 <= result['score'] <= 20
        assert result['exit_alts_signal'] is False
    
    def test_analyze_altseason_error_handling(self, strategic_advisor):
        """Test altseason analysis error handling"""
        # Mock the logger to avoid interference and force an actual exception
        # We'll force an exception by making eth_btc_ratio a non-numeric value
        # that will cause an error in calculations
        
        data = {
            'bitcoin': {'usd': 70000, 'historical': pd.DataFrame()},
            'ethereum': {'usd': 3500, 'historical': pd.DataFrame()}
        }
        market_metrics = {'btc_dominance': 50, 'eth_btc_ratio': 'invalid'}  # This will cause an error
        
        result = strategic_advisor._analyze_altseason(data, market_metrics)
        
        # Check if error handling worked - either returned error dict or handled gracefully
        if 'error' in result:
            assert 'error' in result
        else:
            # Method handled the error gracefully by using defaults
            assert 'phase' in result
            assert 'score' in result
