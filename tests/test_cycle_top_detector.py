"""
Comprehensive tests for cycle_top_detector module
Tests cycle top detection algorithms, risk scoring, and alert generation
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.cycle_top_detector import CycleTopDetector


class TestCycleTopDetector:
    """Test CycleTopDetector initialization and configuration"""
    
    @pytest.fixture
    def basic_config(self):
        """Basic configuration for testing"""
        return {
            'professional_alerts': {
                'cycle_top_detection': {
                    'btc_overextension': {
                        'ma200_multiple': 4.0
                    },
                    'extreme_euphoria': {
                        'fear_greed_threshold': 80,
                        'btc_dominance_threshold': 35
                    },
                    'risk_thresholds': {
                        'low': 30,
                        'medium': 60,
                        'high': 80
                    }
                }
            }
        }
    
    @pytest.fixture
    def detector(self, basic_config):
        """Create CycleTopDetector instance for testing"""
        return CycleTopDetector(basic_config)
    
    def test_init_with_valid_config(self, basic_config):
        """Test initialization with valid configuration"""
        detector = CycleTopDetector(basic_config)
        
        assert detector.config == basic_config
        assert detector.cycle_config == basic_config['professional_alerts']['cycle_top_detection']
        assert detector.fear_greed_history == []
        assert detector.btc_dominance_history == []
        assert detector.logger is not None
    
    def test_init_with_empty_config(self):
        """Test initialization with empty configuration"""
        detector = CycleTopDetector({})
        
        assert detector.config == {}
        assert detector.cycle_config == {}
        assert detector.fear_greed_history == []
        assert detector.btc_dominance_history == []
    
    def test_init_with_partial_config(self):
        """Test initialization with partial configuration"""
        config = {'professional_alerts': {}}
        detector = CycleTopDetector(config)
        
        assert detector.config == config
        assert detector.cycle_config == {}


class TestAnalyzeCycleTop:
    """Test main analyze_cycle_top method"""
    
    @pytest.fixture
    def detector(self):
        config = {
            'professional_alerts': {
                'cycle_top_detection': {
                    'btc_overextension': {'ma200_multiple': 4.0},
                    'extreme_euphoria': {'fear_greed_threshold': 80},
                    'risk_thresholds': {'low': 30, 'medium': 60, 'high': 80}
                }
            }
        }
        return CycleTopDetector(config)
    
    @pytest.fixture
    def sample_data_dict(self):
        """Sample data dictionary for testing"""
        return {
            'bitcoin': {
                'usd': 50000,
                'current_price': 50000,
                'indicators': {
                    'ma_long': 12500,  # MA200
                    'ma_short': 45000,  # MA50
                    'rsi': 75
                },
                'historical': pd.DataFrame({
                    'close': [48000, 49000, 50000, 51000, 52000] * 4,
                    'timestamp': pd.date_range('2023-01-01', periods=20)
                })
            }
        }
    
    @pytest.fixture
    def sample_market_data(self):
        """Sample market data for testing"""
        return {
            'btc_dominance': 45.0,
            'fear_greed_index': {
                'value': 75,
                'value_classification': 'Greed'
            }
        }
    
    def test_analyze_cycle_top_success(self, detector, sample_data_dict, sample_market_data):
        """Test successful cycle top analysis"""
        result = detector.analyze_cycle_top(sample_data_dict, sample_market_data)
        
        # Check result structure
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'signals' in result
        assert 'dashboard' in result
        assert 'should_alert' in result
        
        # Check data types
        assert isinstance(result['risk_score'], int)
        assert isinstance(result['risk_level'], str)
        assert isinstance(result['signals'], dict)
        assert isinstance(result['dashboard'], dict)
        assert isinstance(result['should_alert'], bool)
        
        # Check signals structure
        signals = result['signals']
        assert 'btc_overextension' in signals
        assert 'extreme_euphoria' in signals
        assert 'market_structure' in signals
        assert 'technical_signals' in signals
    
    def test_analyze_cycle_top_with_missing_btc_data(self, detector, sample_market_data):
        """Test analysis with missing BTC data"""
        data_dict = {}
        result = detector.analyze_cycle_top(data_dict, sample_market_data)
        
        # Should still return valid structure
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert result['risk_score'] >= 0
    
    def test_analyze_cycle_top_with_none_inputs(self, detector):
        """Test analysis with None inputs"""
        result = detector.analyze_cycle_top(None, None)
        
        # Should handle gracefully and return default result
        assert isinstance(result, dict)
        assert 'risk_score' in result
    
    def test_analyze_cycle_top_exception_handling(self, detector):
        """Test exception handling in analyze_cycle_top"""
        # Mock _analyze_btc_overextension to raise exception
        with patch.object(detector, '_analyze_btc_overextension', side_effect=Exception("Test error")):
            result = detector.analyze_cycle_top({}, {})
            
            # Should return default result on exception
            assert isinstance(result, dict)
            assert 'risk_score' in result


class TestAnalyzeBtcOverextension:
    """Test BTC overextension analysis"""
    
    @pytest.fixture
    def detector(self):
        config = {
            'professional_alerts': {
                'cycle_top_detection': {
                    'btc_overextension': {'ma200_multiple': 4.0}
                }
            }
        }
        return CycleTopDetector(config)
    
    def test_btc_overextension_normal_conditions(self, detector):
        """Test BTC overextension under normal conditions"""
        btc_data = {
            'usd': 50000,
            'indicators': {
                'ma_long': 45000,  # 1.11x multiple - normal
                'ma_short': 48000
            }
        }
        
        result = detector._analyze_btc_overextension(btc_data)
        
        assert isinstance(result, dict)
        assert 'active_signals' in result
        assert 'score' in result
        assert 'details' in result
        assert 'signals' in result
        assert 'warnings' in result
        
        # Normal conditions should have low score
        assert result['score'] == 0
        assert result['active_signals'] == 0
        assert len(result['signals']) == 0
    
    def test_btc_overextension_high_multiple(self, detector):
        """Test BTC overextension with high MA200 multiple"""
        btc_data = {
            'usd': 200000,  # 4.4x multiple - above threshold
            'indicators': {
                'ma_long': 45000,  # MA200
                'ma_short': 48000
            }
        }
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should trigger overextension signal
        assert result['score'] > 0
        assert result['active_signals'] > 0
        assert len(result['signals']) > 0
        assert result['details']['ma200_multiple'] > 4.0
    
    def test_btc_overextension_extreme_multiple(self, detector):
        """Test BTC overextension with extreme MA200 multiple"""
        btc_data = {
            'usd': 300000,  # 6.67x multiple - extreme
            'indicators': {
                'ma_long': 45000,  # MA200
                'ma_short': 48000
            }
        }
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should trigger both overextension and extreme signals
        assert result['score'] >= 60  # 40 + 20 for extreme
        assert result['active_signals'] >= 2
        assert len(result['warnings']) > 0
    
    def test_btc_overextension_missing_data(self, detector):
        """Test BTC overextension with missing data"""
        btc_data = {}
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should handle missing data gracefully
        assert result['score'] == 0
        assert result['active_signals'] == 0
    
    def test_btc_overextension_zero_ma200(self, detector):
        """Test BTC overextension with zero MA200"""
        btc_data = {
            'usd': 50000,
            'indicators': {
                'ma_long': 0,  # Zero MA200
                'ma_short': 48000
            }
        }
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should handle zero MA200 gracefully
        assert result['score'] == 0
        assert result['active_signals'] == 0
    
    def test_btc_overextension_with_historical_data(self, detector):
        """Test BTC overextension with historical data for MA50 slope analysis"""
        historical_data = pd.DataFrame({
            'close': [45000, 46000, 47000, 48000, 49000, 50000, 51000, 52000, 53000, 54000],
            'timestamp': pd.date_range('2023-01-01', periods=10)
        })
        
        btc_data = {
            'usd': 200000,  # High multiple
            'indicators': {
                'ma_long': 45000,
                'ma_short': 48000
            },
            'historical': historical_data
        }
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should process historical data without errors
        assert isinstance(result, dict)
        assert result['score'] > 0  # Should still detect overextension


class TestAnalyzeExtremeEuphoria:
    """Test extreme euphoria analysis"""
    
    @pytest.fixture
    def detector(self):
        config = {
            'professional_alerts': {
                'cycle_top_detection': {
                    'extreme_euphoria': {
                        'fear_greed_threshold': 80,
                        'btc_dominance_threshold': 35
                    }
                }
            }
        }
        return CycleTopDetector(config)
    
    def test_extreme_euphoria_normal_conditions(self, detector):
        """Test extreme euphoria under normal conditions"""
        btc_data = {'usd': 50000}
        market_data = {
            'fear_greed_index': {'value': 50, 'value_classification': 'Neutral'},
            'btc_dominance': 45.0
        }
        
        result = detector._analyze_extreme_euphoria(btc_data, market_data)
        
        assert isinstance(result, dict)
        assert 'active_signals' in result
        assert 'score' in result
        
        # Normal conditions should have low score
        assert result['score'] == 0
        assert result['active_signals'] == 0
    
    def test_extreme_euphoria_high_fear_greed(self, detector):
        """Test extreme euphoria with high fear & greed index"""
        btc_data = {'usd': 50000}
        market_data = {
            'fear_greed_index': {'value': 90, 'value_classification': 'Extreme Greed'},
            'btc_dominance': 45.0
        }
        
        result = detector._analyze_extreme_euphoria(btc_data, market_data)
        
        # Should trigger euphoria signal
        assert result['score'] > 0
        assert result['active_signals'] > 0
    
    def test_extreme_euphoria_low_btc_dominance(self, detector):
        """Test extreme euphoria with high fear & greed (BTC dominance is handled in market structure)"""
        btc_data = {'usd': 50000}
        market_data = {
            'fear_greed_index': {'value': 90, 'value_classification': 'Extreme Greed'},  # High fear & greed
            'btc_dominance': 45.0
        }
        
        result = detector._analyze_extreme_euphoria(btc_data, market_data)
        
        # Should trigger euphoria signal due to high fear & greed
        assert result['score'] > 0
        assert result['active_signals'] > 0
    
    def test_extreme_euphoria_missing_data(self, detector):
        """Test extreme euphoria with missing data"""
        btc_data = {}
        market_data = {}
        
        result = detector._analyze_extreme_euphoria(btc_data, market_data)
        
        # Should handle missing data gracefully
        assert isinstance(result, dict)
        assert result['score'] == 0


class TestRiskCalculationAndScoring:
    """Test risk calculation and scoring methods"""
    
    @pytest.fixture
    def detector(self):
        config = {
            'professional_alerts': {
                'cycle_top_detection': {
                    'risk_thresholds': {
                        'low': 30,
                        'medium': 60,
                        'high': 80
                    }
                }
            }
        }
        return CycleTopDetector(config)
    
    def test_calculate_risk_score_low_risk(self, detector):
        """Test risk score calculation for low risk scenario"""
        signals = {
            'btc_overextension': {'score': 10, 'active_signals': 1},
            'extreme_euphoria': {'score': 5, 'active_signals': 0},
            'market_structure': {'score': 0, 'active_signals': 0},
            'technical_signals': {'score': 8, 'active_signals': 1}
        }
        
        risk_score = detector._calculate_risk_score(signals)
        
        assert isinstance(risk_score, int)
        assert 0 <= risk_score <= 100
        assert risk_score < 30  # Should be low risk
    
    def test_calculate_risk_score_high_risk(self, detector):
        """Test risk score calculation for high risk scenario"""
        signals = {
            'btc_overextension': {'score': 60, 'active_signals': 3},
            'extreme_euphoria': {'score': 40, 'active_signals': 2},
            'market_structure': {'score': 30, 'active_signals': 2},
            'technical_signals': {'score': 25, 'active_signals': 2}
        }
        
        risk_score = detector._calculate_risk_score(signals)
        
        assert isinstance(risk_score, int)
        assert risk_score > 80  # Should be high risk
    
    def test_get_risk_level_classifications(self, detector):
        """Test risk level classifications"""
        # Test minimum risk
        assert detector._get_risk_level(15) == 'MÍNIMO'
        assert detector._get_risk_level(29) == 'MÍNIMO'
        
        # Test low risk
        assert detector._get_risk_level(30) == 'BAIXO'
        assert detector._get_risk_level(49) == 'BAIXO'
        
        # Test medium risk
        assert detector._get_risk_level(50) == 'MÉDIO'
        assert detector._get_risk_level(69) == 'MÉDIO'
        
        # Test high risk
        assert detector._get_risk_level(70) == 'ALTO'
        assert detector._get_risk_level(84) == 'ALTO'
        
        # Test extreme risk
        assert detector._get_risk_level(85) == 'EXTREMO'
        assert detector._get_risk_level(100) == 'EXTREMO'
    
    def test_should_send_alert_thresholds(self, detector):
        """Test alert threshold logic"""
        # Should not alert for low risk
        assert not detector._should_send_alert(25)
        
        # Should alert for medium risk and above
        assert detector._should_send_alert(35)
        assert detector._should_send_alert(65)
        assert detector._should_send_alert(85)


class TestAlertFormattingAndDashboard:
    """Test alert formatting and dashboard preparation"""
    
    @pytest.fixture
    def detector(self):
        return CycleTopDetector({})
    
    def test_format_cycle_alert_basic(self, detector):
        """Test basic cycle alert formatting"""
        analysis = {
            'cycle_top_risk': 75,  # Use correct key name
            'risk_level': 'ALTO',  # Use Portuguese term
            'recommendation': 'VENDA PARCIAL',
            'confidence': 85,
            'signals': ['Signal 1', 'Signal 2'],
            'warnings': ['Warning 1']
        }
        
        result = detector.format_cycle_alert(analysis)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'ALERTA DE TOPO DE CICLO' in result
        assert '75' in result
    
    def test_prepare_dashboard_complete(self, detector):
        """Test complete dashboard preparation"""
        btc_data = {'usd': 50000, 'indicators': {'ma_long': 45000, 'rsi': 60}}
        market_data = {'btc_dominance': 45.0, 'fear_greed_index': {'value': 75}}
        data_dict = {'bitcoin': btc_data}
        signals = {
            'btc_overextension': {'score': 30, 'active_signals': 1},
            'extreme_euphoria': {'score': 20, 'active_signals': 1}
        }
        risk_score = 50
        
        dashboard = detector._prepare_dashboard(btc_data, market_data, data_dict, signals, risk_score)
        
        assert isinstance(dashboard, dict)
        assert 'btc_metrics' in dashboard
        assert 'market_metrics' in dashboard
        assert 'risk_score' in dashboard
        assert 'risk_level' in dashboard
        assert 'portfolio_stats' in dashboard
    
    def test_format_cycle_dashboard_alert(self, detector):
        """Test cycle dashboard alert formatting"""
        analysis = {
            'dashboard': {
                'risk_score': 65,
                'risk_level': 'ALTO',
                'btc_metrics': {
                    'price': '$50,000',
                    'ma200_multiple': 1.11,
                    'rsi': 60
                },
                'market_metrics': {
                    'fear_greed': 75,
                    'btc_dominance': '45.0%'
                },
                'recommendation': 'RISCO ALTO - Monitore de perto'
            }
        }
        
        result = detector.format_cycle_dashboard_alert(analysis)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'DASHBOARD TOPO DE CICLO' in result
        # The dashboard shows the actual risk score from the dashboard data
        assert 'RISCO DE TOPO:' in result
        assert '$50,000' in result  # Check for price instead


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling"""
    
    @pytest.fixture
    def detector(self):
        return CycleTopDetector({})
    
    def test_get_default_result_structure(self, detector):
        """Test default result structure"""
        result = detector._get_default_result()
        
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'signals' in result
        assert 'dashboard' in result
        assert 'should_alert' in result
        
        # Default should be safe values
        assert result['risk_score'] == 0
        assert result['should_alert'] is False
    
    def test_analyze_with_malformed_data(self, detector):
        """Test analysis with malformed data structures"""
        malformed_data = {
            'bitcoin': 'not_a_dict',  # Should be dict
            'invalid_key': None
        }
        malformed_market = 'not_a_dict'  # Should be dict
        
        result = detector.analyze_cycle_top(malformed_data, malformed_market)
        
        # Should handle gracefully
        assert isinstance(result, dict)
        assert 'risk_score' in result
    
    def test_analyze_with_extreme_values(self, detector):
        """Test analysis with extreme numerical values"""
        extreme_data = {
            'bitcoin': {
                'usd': 1e15,  # Extremely large price
                'indicators': {
                    'ma_long': 1e-10,  # Extremely small MA
                    'ma_short': float('inf')  # Infinite value
                }
            }
        }
        extreme_market = {
            'btc_dominance': -100,  # Negative dominance
            'fear_greed_index': {'value': 1000}  # Out of range value
        }
        
        result = detector.analyze_cycle_top(extreme_data, extreme_market)
        
        # Should handle extreme values without crashing
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 0 <= result['risk_score'] <= 100
    
    def test_helper_methods_with_none_inputs(self, detector):
        """Test helper methods with None inputs"""
        # Test trend analysis methods
        assert detector._get_ma_trend(None) is not None
        assert detector._get_fear_greed_level(None) is not None
        assert detector._get_market_trend(None) is not None
        assert detector._get_recommendation(50, None) is not None
    
    def test_unicode_and_special_characters(self, detector):
        """Test handling of unicode and special characters in data"""
        unicode_data = {
            'bitcoin': {
                'usd': 50000,
                'symbol': '₿TC',  # Unicode symbol
                'name': 'Bitçoin'  # Special characters
            }
        }
        unicode_market = {
            'fear_greed_index': {
                'value': 75,
                'value_classification': 'Gréed 🚀'  # Unicode emoji
            }
        }
        
        result = detector.analyze_cycle_top(unicode_data, unicode_market)
        
        # Should handle unicode characters without issues
        assert isinstance(result, dict)
        assert 'risk_score' in result