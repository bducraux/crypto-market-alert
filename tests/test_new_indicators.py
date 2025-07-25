"""
Unit tests for new technical indicators: Pi Cycle Top and 3-Line RCI
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from src.indicators import TechnicalIndicators


class TestNewIndicators:
    """Test cases for new technical indicators"""
    
    @pytest.fixture
    def indicators(self):
        """Create a TechnicalIndicators instance for testing"""
        return TechnicalIndicators()
    
    @pytest.fixture
    def btc_price_data(self):
        """Create realistic BTC price data for Pi Cycle testing"""
        dates = pd.date_range('2023-01-01', periods=400, freq='D')  # 400 days for 350-day MA
        np.random.seed(42)
        
        # Simulate BTC bull run price action
        base_price = 20000
        prices = []
        current_price = base_price
        
        for i in range(400):
            # Simulate bull market with some volatility
            if i < 200:
                # Early bull market - steady growth
                growth = np.random.normal(0.003, 0.025)  # 0.3% daily growth avg
            else:
                # Late bull market - more volatile, potential top
                growth = np.random.normal(0.002, 0.035)  # Slower growth, more volatile
            
            current_price = current_price * (1 + growth)
            prices.append(current_price)
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000000, 50000000, 400)
        }, index=dates)
        
        return df
    
    @pytest.fixture
    def minimal_price_data(self):
        """Create minimal price data for edge case testing"""
        dates = pd.date_range('2023-01-01', periods=50, freq='D')
        df = pd.DataFrame({
            'close': np.random.uniform(40000, 50000, 50)
        }, index=dates)
        return df

    # Pi Cycle Top Indicator Tests
    def test_pi_cycle_top_calculation_success(self, indicators, btc_price_data):
        """Test successful Pi Cycle Top calculation"""
        result = indicators.calculate_pi_cycle_top(btc_price_data)
        
        assert isinstance(result, dict)
        assert 'pi_cycle_signal' in result
        assert 'ma_111' in result
        assert 'ma_350_2x' in result
        assert 'distance' in result
        assert 'crossover_detected' in result
        assert 'risk_level' in result
        
        # Check that we get numeric values
        if result['ma_111'] is not None:
            assert isinstance(result['ma_111'], float)
        if result['ma_350_2x'] is not None:
            assert isinstance(result['ma_350_2x'], float)
        
        # Risk level should be HIGH or LOW
        assert result['risk_level'] in ['HIGH', 'LOW']
    
    def test_pi_cycle_top_insufficient_data(self, indicators, minimal_price_data):
        """Test Pi Cycle calculation with insufficient data"""
        result = indicators.calculate_pi_cycle_top(minimal_price_data)
        
        assert result['pi_cycle_signal'] is False
        assert result['ma_111'] is None
        assert result['ma_350_2x'] is None
        assert result['distance'] is None
    
    def test_pi_cycle_top_custom_periods(self, indicators, btc_price_data):
        """Test Pi Cycle with custom periods"""
        result = indicators.calculate_pi_cycle_top(btc_price_data, short_period=50, long_period=200)
        
        assert isinstance(result, dict)
        # Should work with shorter periods
        assert 'pi_cycle_signal' in result
    
    def test_pi_cycle_top_empty_dataframe(self, indicators):
        """Test Pi Cycle with empty DataFrame"""
        empty_df = pd.DataFrame()
        result = indicators.calculate_pi_cycle_top(empty_df)
        
        assert result['pi_cycle_signal'] is False
        assert result['ma_111'] is None
        assert result['ma_350_2x'] is None
    
    def test_pi_cycle_top_crossover_detection(self, indicators):
        """Test Pi Cycle crossover detection logic"""
        # Create data where MA111 crosses above 2x MA350
        dates = pd.date_range('2023-01-01', periods=400, freq='D')
        
        # Create a scenario where crossover occurs
        prices = []
        for i in range(400):
            if i < 390:
                # Before crossover - MA111 below 2x MA350
                price = 50000 + i * 10
            else:
                # Crossover period - sharp price increase
                price = 50000 + i * 50
            prices.append(price)
        
        df = pd.DataFrame({'close': prices}, index=dates)
        result = indicators.calculate_pi_cycle_top(df)
        
        # Should detect the signal when MA111 is above 2x MA350
        assert isinstance(result['pi_cycle_signal'], bool)
        assert isinstance(result['distance'], (int, float)) or result['distance'] is None

    # 3-Line RCI Tests
    def test_rci_3_line_calculation_success(self, indicators, btc_price_data):
        """Test successful 3-Line RCI calculation"""
        result = indicators.calculate_rci_3_line(btc_price_data)
        
        assert isinstance(result, dict)
        assert 'rci_short' in result
        assert 'rci_medium' in result
        assert 'rci_long' in result
        assert 'signal' in result
        assert 'overbought_level' in result
        assert 'oversold_level' in result
        
        # Check RCI values are in expected range (-100 to 100)
        for key in ['rci_short', 'rci_medium', 'rci_long']:
            rci_value = result[key]
            if rci_value is not None:
                assert -100 <= rci_value <= 100
        
        # Signal should be one of the expected values
        assert result['signal'] in ['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']
        
        # Levels should be correct
        assert result['overbought_level'] == 80
        assert result['oversold_level'] == -80
    
    def test_rci_3_line_insufficient_data(self, indicators):
        """Test RCI calculation with insufficient data"""
        short_df = pd.DataFrame({
            'close': [100, 105, 102, 108, 110]  # Only 5 periods
        })
        
        result = indicators.calculate_rci_3_line(short_df, periods=[9, 26, 52])
        
        assert result['rci_short'] is None
        assert result['rci_medium'] is None
        assert result['rci_long'] is None
        assert result['signal'] == 'NEUTRAL'
    
    def test_rci_3_line_custom_periods(self, indicators, btc_price_data):
        """Test RCI with custom periods"""
        custom_periods = [5, 14, 21]
        result = indicators.calculate_rci_3_line(btc_price_data, periods=custom_periods)
        
        assert isinstance(result, dict)
        assert 'rci_short' in result
        assert 'rci_medium' in result
        assert 'rci_long' in result
    
    def test_single_rci_calculation(self, indicators, btc_price_data):
        """Test single RCI calculation method"""
        rci_value = indicators._calculate_single_rci(btc_price_data, period=14)
        
        if rci_value is not None:
            assert isinstance(rci_value, float)
            assert -100 <= rci_value <= 100
    
    def test_single_rci_insufficient_data(self, indicators):
        """Test single RCI with insufficient data"""
        short_df = pd.DataFrame({'close': [100, 105]})  # Only 2 periods
        rci_value = indicators._calculate_single_rci(short_df, period=14)
        
        assert rci_value is None
    
    def test_rci_signal_analysis_all_bullish(self, indicators):
        """Test RCI signal analysis with all bullish indicators"""
        rci_values = {
            'short': 60,
            'medium': 40,
            'long': 30
        }
        
        signal = indicators._analyze_rci_signals(rci_values)
        assert signal == 'STRONG_BUY'
    
    def test_rci_signal_analysis_all_bearish(self, indicators):
        """Test RCI signal analysis with all bearish indicators"""
        rci_values = {
            'short': -60,
            'medium': -40,
            'long': -30
        }
        
        signal = indicators._analyze_rci_signals(rci_values)
        assert signal == 'STRONG_SELL'
    
    def test_rci_signal_analysis_majority_bullish(self, indicators):
        """Test RCI signal analysis with majority bullish"""
        rci_values = {
            'short': 30,
            'medium': 20,
            'long': -10
        }
        
        signal = indicators._analyze_rci_signals(rci_values)
        assert signal == 'BUY'
    
    def test_rci_signal_analysis_majority_bearish(self, indicators):
        """Test RCI signal analysis with majority bearish"""
        rci_values = {
            'short': -30,
            'medium': -20,
            'long': 10
        }
        
        signal = indicators._analyze_rci_signals(rci_values)
        assert signal == 'SELL'
    
    def test_rci_signal_analysis_neutral(self, indicators):
        """Test RCI signal analysis with neutral/mixed signals"""
        rci_values = {
            'short': 5,
            'medium': -5,
            'long': 2
        }
        
        signal = indicators._analyze_rci_signals(rci_values)
        assert signal == 'NEUTRAL'
    
    def test_rci_signal_analysis_with_none_values(self, indicators):
        """Test RCI signal analysis with None values"""
        rci_values = {
            'short': None,
            'medium': 20,
            'long': 30
        }
        
        signal = indicators._analyze_rci_signals(rci_values)
        assert signal == 'NEUTRAL'

    # Integration tests
    def test_get_latest_indicator_values_with_new_indicators(self, indicators, btc_price_data):
        """Test integration of new indicators in get_latest_indicator_values"""
        config = {
            'rsi_period': 14,
            'enable_pi_cycle': True,
            'enable_rci': True,
            'rci_periods': [9, 26, 52]
        }
        
        result = indicators.get_latest_indicator_values(btc_price_data, config)
        
        # Should include new indicators
        assert 'pi_cycle_signal' in result
        assert 'rci_short' in result
        assert 'rci_medium' in result
        assert 'rci_long' in result
        assert 'signal' in result
        
        # Should still include standard indicators
        assert 'current_price' in result
        if 'rsi' in result:
            assert isinstance(result['rsi'], (float, type(None)))
    
    def test_get_latest_indicator_values_without_new_indicators(self, indicators, btc_price_data):
        """Test that new indicators are not included when disabled"""
        config = {
            'rsi_period': 14,
            'enable_pi_cycle': False,
            'enable_rci': False
        }
        
        result = indicators.get_latest_indicator_values(btc_price_data, config)
        
        # Should not include new indicators
        assert 'pi_cycle_signal' not in result
        assert 'rci_short' not in result
        assert 'rci_medium' not in result
        assert 'rci_long' not in result
        
        # Should still include standard indicators
        assert 'current_price' in result
    
    def test_error_handling_pi_cycle(self, indicators):
        """Test error handling in Pi Cycle calculation"""
        # Test with invalid data
        invalid_df = pd.DataFrame({'invalid_column': [1, 2, 3]})
        result = indicators.calculate_pi_cycle_top(invalid_df)
        
        assert result['pi_cycle_signal'] is False
        assert result['ma_111'] is None
        assert result['ma_350_2x'] is None
    
    def test_error_handling_rci(self, indicators):
        """Test error handling in RCI calculation"""
        # Test with invalid data
        invalid_df = pd.DataFrame({'invalid_column': [1, 2, 3]})
        result = indicators.calculate_rci_3_line(invalid_df)
        
        assert result['rci_short'] is None
        assert result['rci_medium'] is None
        assert result['rci_long'] is None
        assert result['signal'] == 'NEUTRAL'
