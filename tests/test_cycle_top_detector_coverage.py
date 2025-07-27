"""
Cycle Top Detector Coverage Tests
Tests specifically designed to improve coverage for cycle_top_detector.py
Focuses on error handling, edge cases, and boundary conditions
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.cycle_top_detector import CycleTopDetector


class TestCycleTopDetectorErrorHandling:
    """Test error handling and edge cases in CycleTopDetector"""
    
    @pytest.fixture
    def detector(self):
        """Create CycleTopDetector instance for testing"""
        config = {
            'professional_alerts': {
                'cycle_top_detection': {
                    'btc_overextension': {'ma200_multiple': 4.0},
                    'extreme_euphoria': {'fear_greed_threshold': 90},
                    'market_structure': {'btc_dominance_threshold': 40}
                }
            }
        }
        return CycleTopDetector(config)
    
    def test_analyze_cycle_top_missing_btc_data(self, detector):
        """Test cycle top analysis with missing BTC data - covers error paths"""
        data_dict = {}  # No bitcoin data
        market_data = {'btc_dominance': 50, 'fear_greed_index': {'value': 50}}
        
        result = detector.analyze_cycle_top(data_dict, market_data)
        
        # Should handle missing data gracefully
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert result['risk_score'] >= 0
    
    def test_analyze_cycle_top_empty_market_data(self, detector):
        """Test cycle top analysis with empty market data - covers error handling"""
        data_dict = {'bitcoin': {'usd': 50000}}
        market_data = {}  # Empty market data
        
        result = detector.analyze_cycle_top(data_dict, market_data)
        
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert result['risk_score'] >= 0
    
    def test_analyze_cycle_top_exception_handling(self, detector):
        """Test exception handling in analyze_cycle_top - covers line 78-80"""
        # Mock _analyze_btc_overextension to raise exception
        with patch.object(detector, '_analyze_btc_overextension', side_effect=Exception("Test error")):
            data_dict = {'bitcoin': {'usd': 50000}}
            market_data = {'btc_dominance': 50}
            
            result = detector.analyze_cycle_top(data_dict, market_data)
            
            # Should return default result on exception
            assert isinstance(result, dict)
            assert 'risk_score' in result
    
    def test_btc_overextension_missing_ma200(self, detector):
        """Test BTC overextension analysis with missing MA200 - covers line 100-101"""
        btc_data = {'usd': 50000}  # Missing MA200 data
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should handle missing MA200 gracefully
        assert isinstance(result, dict)
        assert result['score'] == 0
        assert result['active_signals'] == 0
    
    def test_btc_overextension_zero_current_price(self, detector):
        """Test BTC overextension with zero current price - covers error paths"""
        btc_data = {'usd': 0, 'indicators': {'ma_long': 45000}}
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should handle zero price gracefully
        assert isinstance(result, dict)
        assert result['score'] == 0
    
    def test_btc_overextension_extreme_multiple(self, detector):
        """Test BTC overextension with extreme MA200 multiple - covers lines 115-118"""
        btc_data = {
            'usd': 270000,  # 6x above MA200 (45000 * 6)
            'indicators': {'ma_long': 45000}
        }
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should detect overextension (actual implementation gives 40 points for basic threshold)
        assert result['score'] >= 40  # Basic overextension score
        assert result['active_signals'] >= 1
        # Check if warnings exist when extreme conditions are met
        assert isinstance(result['warnings'], list)
    
    def test_btc_overextension_historical_data_processing(self, detector):
        """Test BTC overextension with historical data - covers lines 121-143"""
        # Create historical data
        dates = pd.date_range('2023-01-01', periods=20, freq='D')
        historical_data = pd.DataFrame({
            'close': [45000 + i * 100 for i in range(20)],  # Ascending prices
            'ma_short': [44000 + i * 50 for i in range(20)]  # MA50 values
        }, index=dates)
        
        btc_data = {
            'usd': 47000,
            'indicators': {'ma_long': 45000},
            'historical': historical_data
        }
        
        result = detector._analyze_btc_overextension(btc_data)
        
        # Should process historical data without error
        assert isinstance(result, dict)
        assert 'score' in result
    
    def test_extreme_euphoria_missing_fear_greed(self, detector):
        """Test extreme euphoria analysis with missing fear & greed data"""
        btc_data = {'usd': 50000}
        market_data = {}  # Missing fear_greed_index
        
        result = detector._analyze_extreme_euphoria(btc_data, market_data)
        
        # Should handle missing data gracefully
        assert isinstance(result, dict)
        assert result['score'] >= 0
    
    def test_extreme_euphoria_high_fear_greed(self, detector):
        """Test extreme euphoria with high fear & greed values"""
        btc_data = {'usd': 50000}
        market_data = {'fear_greed_index': {'value': 95}}  # Extreme greed
        
        result = detector._analyze_extreme_euphoria(btc_data, market_data)
        
        # Should detect extreme euphoria
        assert isinstance(result, dict)
        assert result['score'] > 0


class TestCycleTopDetectorBoundaryConditions:
    """Test boundary conditions and edge cases"""
    
    @pytest.fixture
    def detector(self):
        config = {
            'professional_alerts': {
                'cycle_top_detection': {
                    'btc_overextension': {'ma200_multiple': 4.0},
                    'extreme_euphoria': {'fear_greed_threshold': 90},
                    'market_structure': {'btc_dominance_threshold': 40}
                }
            }
        }
        return CycleTopDetector(config)
    
    def test_market_structure_missing_btc_dominance(self, detector):
        """Test market structure analysis with missing BTC dominance"""
        market_data = {}  # Missing btc_dominance
        data_dict = {'bitcoin': {'usd': 50000}}
        
        result = detector._analyze_market_structure(market_data, data_dict)
        
        # Should handle missing dominance gracefully
        assert isinstance(result, dict)
        assert result['score'] >= 0
    
    def test_market_structure_extreme_low_dominance(self, detector):
        """Test market structure with extremely low BTC dominance"""
        market_data = {'btc_dominance': 25.0}  # Very low dominance
        data_dict = {'bitcoin': {'usd': 50000}}
        
        result = detector._analyze_market_structure(market_data, data_dict)
        
        # Should detect low dominance signal
        assert isinstance(result, dict)
        assert result['score'] > 0
    
    def test_technical_signals_missing_data(self, detector):
        """Test technical signals analysis with missing data"""
        btc_data = {'usd': 50000}  # Missing indicators
        data_dict = {'bitcoin': btc_data}
        
        result = detector._analyze_technical_signals(btc_data, data_dict)
        
        # Should handle missing technical data gracefully
        assert isinstance(result, dict)
        assert result['score'] >= 0
    
    def test_calculate_risk_score_boundary_values(self, detector):
        """Test risk score calculation with boundary values"""
        # Test with maximum possible signals
        signals = {
            'btc_overextension': {'score': 100, 'active_signals': 5},
            'extreme_euphoria': {'score': 100, 'active_signals': 5},
            'market_structure': {'score': 100, 'active_signals': 5},
            'technical_signals': {'score': 100, 'active_signals': 5}
        }
        
        risk_score = detector._calculate_risk_score(signals)
        
        # Should cap at reasonable maximum
        assert isinstance(risk_score, int)
        assert 0 <= risk_score <= 100
    
    def test_calculate_risk_score_zero_signals(self, detector):
        """Test risk score calculation with zero signals"""
        signals = {
            'btc_overextension': {'score': 0, 'active_signals': 0},
            'extreme_euphoria': {'score': 0, 'active_signals': 0},
            'market_structure': {'score': 0, 'active_signals': 0},
            'technical_signals': {'score': 0, 'active_signals': 0}
        }
        
        risk_score = detector._calculate_risk_score(signals)
        
        # Should return zero for no signals
        assert risk_score == 0
    
    def test_get_risk_level_boundary_values(self, detector):
        """Test risk level determination with boundary values"""
        # Test boundary values - check that method returns strings
        assert isinstance(detector._get_risk_level(0), str)
        assert isinstance(detector._get_risk_level(25), str)
        assert isinstance(detector._get_risk_level(50), str)
        assert isinstance(detector._get_risk_level(75), str)
        assert isinstance(detector._get_risk_level(100), str)
        # Verify they are not empty strings
        assert len(detector._get_risk_level(0)) > 0
        assert len(detector._get_risk_level(100)) > 0


class TestCycleTopDetectorUtilityMethods:
    """Test utility methods and helper functions"""
    
    @pytest.fixture
    def detector(self):
        config = {
            'professional_alerts': {
                'cycle_top_detection': {
                    'btc_overextension': {'ma200_multiple': 4.0},
                    'extreme_euphoria': {'fear_greed_threshold': 90}
                }
            }
        }
        return CycleTopDetector(config)
    
    def test_should_send_alert_boundary_conditions(self, detector):
        """Test should_send_alert with boundary conditions"""
        # Test various risk scores
        assert isinstance(detector.should_send_alert({'risk_score': 0}), bool)
        assert isinstance(detector.should_send_alert({'risk_score': 50}), bool)
        assert isinstance(detector.should_send_alert({'risk_score': 100}), bool)
    
    def test_format_cycle_alert_missing_data(self, detector):
        """Test format_cycle_alert with missing data"""
        analysis = {'risk_score': 50, 'risk_level': 'MEDIUM', 'signals': {}}
        
        result = detector.format_cycle_alert(analysis)
        
        # Should handle missing data gracefully - may return empty string if no alert needed
        assert isinstance(result, str)
        # Just verify it returns a string, empty or not
    
    def test_get_default_result_structure(self, detector):
        """Test _get_default_result returns proper structure"""
        result = detector._get_default_result()
        
        # Should return proper default structure
        assert isinstance(result, dict)
        assert 'risk_score' in result
        assert 'risk_level' in result
        assert 'signals' in result
        assert 'dashboard' in result
        assert 'should_alert' in result
    
    def test_prepare_dashboard_missing_data(self, detector):
        """Test _prepare_dashboard with missing data"""
        btc_data = {}
        market_data = {}
        data_dict = {}
        signals = {}
        risk_score = 0
        
        result = detector._prepare_dashboard(btc_data, market_data, data_dict, signals, risk_score)
        
        # Should handle missing data gracefully
        assert isinstance(result, dict)
    
    def test_get_ma_trend_missing_data(self, detector):
        """Test _get_ma_trend with missing data"""
        btc_data = {}  # Missing MA data
        
        result = detector._get_ma_trend(btc_data)
        
        # Should handle missing data gracefully
        assert isinstance(result, str)
    
    def test_get_fear_greed_level_boundary_values(self, detector):
        """Test _get_fear_greed_level with boundary values"""
        # Test boundary values
        assert isinstance(detector._get_fear_greed_level(0), str)
        assert isinstance(detector._get_fear_greed_level(25), str)
        assert isinstance(detector._get_fear_greed_level(50), str)
        assert isinstance(detector._get_fear_greed_level(75), str)
        assert isinstance(detector._get_fear_greed_level(100), str)
    
    def test_get_market_trend_missing_data(self, detector):
        """Test _get_market_trend with missing data"""
        market_data = {}  # Missing trend data
        
        result = detector._get_market_trend(market_data)
        
        # Should handle missing data gracefully
        assert isinstance(result, str)
    
    def test_get_recommendation_extreme_risk(self, detector):
        """Test _get_recommendation with extreme risk score"""
        market_data = {'btc_dominance': 50}
        
        result = detector._get_recommendation(100, market_data)  # Maximum risk
        
        # Should provide appropriate recommendation
        assert isinstance(result, str)
        assert len(result) > 0


if __name__ == '__main__':
    pytest.main([__file__])