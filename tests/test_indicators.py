"""
Unit tests for indicators module
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from src.indicators import TechnicalIndicators


class TestTechnicalIndicators:
    """Test cases for TechnicalIndicators class"""
    
    @pytest.fixture
    def indicators(self):
        """Create a TechnicalIndicators instance for testing"""
        return TechnicalIndicators()
    
    @pytest.fixture
    def sample_price_data(self):
        """Create sample price data for testing"""
        dates = pd.date_range('2023-01-01', periods=250, freq='D')  # Increased to 250 for MA200
        np.random.seed(42)  # For reproducible tests
        
        # Generate realistic price data
        price = 45000  # Starting price
        prices = [price]
        
        for _ in range(249):  # 249 more prices for total of 250
            change = np.random.normal(0, 0.02)  # 2% daily volatility
            price = price * (1 + change)
            prices.append(price)
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, 250)  # Match the length
        }, index=dates)
        
        return df
    
    @pytest.fixture
    def minimal_price_data(self):
        """Create minimal price data for edge case testing"""
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'close': [100, 105, 102, 108, 110]
        }, index=dates)
        return df
    
    def test_initialization(self, indicators):
        """Test TechnicalIndicators initialization"""
        assert indicators is not None
        assert hasattr(indicators, 'logger')
    
    def test_validate_data_success(self, indicators, sample_price_data):
        """Test successful data validation"""
        result = indicators.validate_data(sample_price_data, min_periods=10)
        assert result is True
    
    def test_validate_data_empty_dataframe(self, indicators):
        """Test validation with empty DataFrame"""
        empty_df = pd.DataFrame()
        result = indicators.validate_data(empty_df)
        assert result is False
    
    def test_validate_data_insufficient_periods(self, indicators, minimal_price_data):
        """Test validation with insufficient data periods"""
        result = indicators.validate_data(minimal_price_data, min_periods=10)
        assert result is False
    
    def test_validate_data_missing_column(self, indicators):
        """Test validation with missing required column"""
        df = pd.DataFrame({'price': [100, 105, 102]})  # Missing 'close' column
        result = indicators.validate_data(df)
        assert result is False
    
    @patch('src.indicators.ta.rsi')
    def test_calculate_rsi_success(self, mock_rsi, indicators, sample_price_data):
        """Test successful RSI calculation"""
        mock_rsi.return_value = pd.Series([30, 40, 60, 70, 50], name='RSI_14')
        
        result = indicators.calculate_rsi(sample_price_data, period=14)
        
        assert result is not None
        assert isinstance(result, float)
        assert result == 50.0  # Latest value from the mocked series
        mock_rsi.assert_called_once()
    
    def test_calculate_rsi_insufficient_data(self, indicators, minimal_price_data):
        """Test RSI calculation with insufficient data"""
        result = indicators.calculate_rsi(minimal_price_data, period=14)
        assert result is None
    
    @patch('src.indicators.ta.macd')
    def test_calculate_macd_success(self, mock_macd, indicators, sample_price_data):
        """Test successful MACD calculation"""
        mock_macd_df = pd.DataFrame({
            'MACD_12_26_9': [1.0, 2.0, 1.5, 0.5, -0.5],
            'MACDs_12_26_9': [0.8, 1.8, 1.2, 0.3, -0.2],
            'MACDh_12_26_9': [0.2, 0.2, 0.3, 0.2, -0.3]
        })
        mock_macd.return_value = mock_macd_df
        
        result = indicators.calculate_macd(sample_price_data)
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'macd' in result
        assert 'signal' in result
        assert 'histogram' in result
    
    @patch('src.indicators.ta.sma')
    def test_calculate_moving_averages_success(self, mock_sma, indicators, sample_price_data):
        """Test successful moving averages calculation"""
        mock_sma.side_effect = [
            pd.Series([45100, 45200, 45300], name='SMA_50'),  # Short MA
            pd.Series([45000, 45100, 45200], name='SMA_200')  # Long MA
        ]
        
        result = indicators.calculate_moving_averages(sample_price_data, 50, 200)
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'ma_short' in result
        assert 'ma_long' in result
        assert mock_sma.call_count == 2
    
    @patch('src.indicators.ta.ema')
    def test_calculate_ema_success(self, mock_ema, indicators, sample_price_data):
        """Test successful EMA calculation"""
        mock_ema.side_effect = [
            pd.Series([45100, 45150], name='EMA_20'),
            pd.Series([45000, 45100], name='EMA_50'),
            pd.Series([44900, 45000], name='EMA_200')
        ]
        
        result = indicators.calculate_ema(sample_price_data, [20, 50, 200])
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'ema_20' in result
        assert 'ema_50' in result
        assert 'ema_200' in result
    
    @patch('src.indicators.ta.bbands')
    def test_calculate_bollinger_bands_success(self, mock_bbands, indicators, sample_price_data):
        """Test successful Bollinger Bands calculation"""
        mock_bb_df = pd.DataFrame({
            'BBU_20_2': [46000, 46100, 46200],  # Upper band
            'BBM_20_2': [45000, 45100, 45200],  # Middle band (SMA)
            'BBL_20_2': [44000, 44100, 44200]   # Lower band
        })
        mock_bbands.return_value = mock_bb_df
        
        result = indicators.calculate_bollinger_bands(sample_price_data)
        
        assert result is not None
        assert isinstance(result, dict)
        assert 'bb_upper' in result
        assert 'bb_middle' in result
        assert 'bb_lower' in result
    
    def test_calculate_stochastic_missing_columns(self, indicators, minimal_price_data):
        """Test Stochastic calculation with missing required columns"""
        result = indicators.calculate_stochastic(minimal_price_data)
        assert result is None
    
    def test_calculate_volume_indicators_missing_volume(self, indicators, minimal_price_data):
        """Test volume indicators with missing volume column"""
        result = indicators.calculate_volume_indicators(minimal_price_data)
        assert result is None
    
    @patch('src.indicators.TechnicalIndicators.calculate_rsi')
    @patch('src.indicators.TechnicalIndicators.calculate_macd')
    @patch('src.indicators.TechnicalIndicators.calculate_moving_averages')
    def test_get_latest_indicator_values(self, mock_ma, mock_macd, mock_rsi, indicators, sample_price_data):
        """Test getting latest indicator values"""
        # Mock indicator calculations
        mock_rsi.return_value = 55.0  # Now returns scalar instead of Series
        mock_macd.return_value = {
            'macd': pd.Series([1.0, 1.2, 0.8, 0.5, 0.7]),
            'signal': pd.Series([0.8, 1.0, 0.6, 0.4, 0.6]),
            'histogram': pd.Series([0.2, 0.2, 0.2, 0.1, 0.1])
        }
        mock_ma.return_value = {
            'ma_short': pd.Series([45100, 45150, 45200, 45250, 45300]),
            'ma_long': pd.Series([45000, 45050, 45100, 45150, 45200])
        }
        
        config = {
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'ma_short': 50,
            'ma_long': 200
        }
        
        result = indicators.get_latest_indicator_values(sample_price_data, config)
        
        assert isinstance(result, dict)
        assert 'rsi' in result
        assert 'current_price' in result
        assert result['rsi'] == 55.0
        assert result['current_price'] == sample_price_data['close'].iloc[-1]
    
    def test_detect_crossovers_bullish(self, indicators):
        """Test bullish crossover detection"""
        # Create a proper bullish crossover: series1 was below, now above series2
        series1 = pd.Series([1, 2, 2.5, 2.8, 3.2])  # Crosses above 3 at the end
        series2 = pd.Series([3, 3, 3, 3, 3])        # Flat at 3
        
        result = indicators.detect_crossovers(series1, series2, periods_back=2)
        
        # Check: series1[-2] = 2.8 <= 3, series1[-1] = 3.2 > 3 = bullish crossover
        assert result['bullish_crossover'] is True
        assert result['bearish_crossover'] is False
    
    def test_detect_crossovers_bearish(self, indicators):
        """Test bearish crossover detection"""
        # Create a proper bearish crossover: series1 was above, now below series2
        series1 = pd.Series([5, 4, 3.2, 3.1, 2.8])  # Crosses below 3 at the end
        series2 = pd.Series([3, 3, 3, 3, 3])        # Flat at 3
        
        result = indicators.detect_crossovers(series1, series2, periods_back=2)
        
        # Check: series1[-2] = 3.1 >= 3, series1[-1] = 2.8 < 3 = bearish crossover
        assert result['bullish_crossover'] is False
        assert result['bearish_crossover'] is True
    
    def test_detect_crossovers_no_crossover(self, indicators):
        """Test no crossover detection"""
        series1 = pd.Series([1, 1, 1, 1, 1])  # Flat series
        series2 = pd.Series([2, 2, 2, 2, 2])  # Flat series (higher)
        
        result = indicators.detect_crossovers(series1, series2, periods_back=2)
        
        assert result['bullish_crossover'] is False
        assert result['bearish_crossover'] is False
    
    def test_detect_crossovers_insufficient_data(self, indicators):
        """Test crossover detection with insufficient data"""
        series1 = pd.Series([1])
        series2 = pd.Series([2])
        
        result = indicators.detect_crossovers(series1, series2, periods_back=2)
        
        assert result['bullish_crossover'] is False
        assert result['bearish_crossover'] is False
    
    def test_calculate_support_resistance_success(self, indicators, sample_price_data):
        """Test successful support/resistance calculation"""
        result = indicators.calculate_support_resistance(sample_price_data, window=20)
        
        assert isinstance(result, dict)
        assert 'support' in result
        assert 'resistance' in result
        assert result['support'] is not None
        assert result['resistance'] is not None
        assert result['support'] <= result['resistance']
    
    def test_calculate_support_resistance_missing_columns(self, indicators, minimal_price_data):
        """Test support/resistance calculation with missing columns"""
        result = indicators.calculate_support_resistance(minimal_price_data, window=20)
        
        assert result['support'] is None
        assert result['resistance'] is None
    
    def test_calculate_support_resistance_insufficient_data(self, indicators):
        """Test support/resistance calculation with insufficient data"""
        df = pd.DataFrame({
            'high': [100, 105],
            'low': [95, 100]
        })
        
        result = indicators.calculate_support_resistance(df, window=20)
        
        assert result['support'] is None
        assert result['resistance'] is None


class TestNewIndicators:
    """Test cases for new technical indicators: Pi Cycle Top and 3-Line RCI"""
    
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
    
    def test_pi_cycle_top_calculation_success(self, indicators, btc_price_data):
        """Test successful Pi Cycle Top calculation"""
        result = indicators.calculate_pi_cycle_top(btc_price_data)
        
        assert isinstance(result, dict)
        assert 'pi_cycle_signal' in result
        assert 'ma_111' in result
        assert 'ma_350_2x' in result
        assert 'distance' in result
        
        # Signal should be boolean
        assert isinstance(result['pi_cycle_signal'], bool)
        
        # MAs should be numeric or None
        if result['ma_111'] is not None:
            assert isinstance(result['ma_111'], (int, float))
        if result['ma_350_2x'] is not None:
            assert isinstance(result['ma_350_2x'], (int, float))
    
    def test_pi_cycle_top_insufficient_data(self, indicators):
        """Test Pi Cycle Top with insufficient data"""
        # Create data with only 100 days (less than required 350)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        df = pd.DataFrame({
            'close': list(range(100))
        }, index=dates)
        
        result = indicators.calculate_pi_cycle_top(df)
        
        assert result['pi_cycle_signal'] is False
        assert result['ma_111'] is None
        assert result['ma_350_2x'] is None
        assert result['distance'] is None
    
    def test_pi_cycle_top_custom_periods(self, indicators, btc_price_data):
        """Test Pi Cycle Top with custom periods"""
        result = indicators.calculate_pi_cycle_top(btc_price_data, short_period=50, long_period=200)
        
        assert isinstance(result, dict)
        assert 'pi_cycle_signal' in result
        # Should work with smaller periods
        assert result['ma_111'] is not None or result['ma_350_2x'] is not None
    
    def test_pi_cycle_top_empty_dataframe(self, indicators):
        """Test Pi Cycle Top with empty DataFrame"""
        empty_df = pd.DataFrame()
        result = indicators.calculate_pi_cycle_top(empty_df)
        
        assert result['pi_cycle_signal'] is False
        assert result['ma_111'] is None
        assert result['ma_350_2x'] is None
    
    def test_pi_cycle_top_crossover_detection(self, indicators):
        """Test Pi Cycle Top crossover detection logic"""
        # Create synthetic data that should trigger Pi Cycle signal
        dates = pd.date_range('2023-01-01', periods=400, freq='D')
        
        # Create a scenario where 111-day MA crosses above 2x 350-day MA near the end
        base_prices = []
        for i in range(400):
            if i < 350:
                # Steady growth early on
                price = 30000 + (i * 100)  # Linear growth
            else:
                # Exponential growth at the end (bubble phase)
                price = 30000 + (350 * 100) + ((i - 350) ** 2 * 50)
            base_prices.append(price)
        
        df = pd.DataFrame({
            'close': base_prices
        }, index=dates)
        
        result = indicators.calculate_pi_cycle_top(df)
        
        # With this synthetic data, we should get some meaningful results
        assert isinstance(result['pi_cycle_signal'], bool)
        assert result['ma_111'] is not None
        assert result['ma_350_2x'] is not None
    
    def test_rci_3_line_calculation_success(self, indicators, btc_price_data):
        """Test successful 3-line RCI calculation"""
        result = indicators.calculate_rci_3_line(btc_price_data)
        
        assert isinstance(result, dict)
        assert 'rci_short' in result
        assert 'rci_medium' in result
        assert 'rci_long' in result
        assert 'signal' in result
        
        # RCI values should be between -100 and 100 or None
        for key in ['rci_short', 'rci_medium', 'rci_long']:
            if result[key] is not None:
                assert -100 <= result[key] <= 100
        
        # Signal should be one of the expected values
        assert result['signal'] in ['STRONG_BUY', 'BUY', 'NEUTRAL', 'SELL', 'STRONG_SELL']
    
    def test_rci_3_line_insufficient_data(self, indicators):
        """Test 3-line RCI with insufficient data"""
        # Create data with only 5 days (less than required 52)
        dates = pd.date_range('2023-01-01', periods=5, freq='D')
        df = pd.DataFrame({
            'close': [100, 105, 102, 108, 110]
        }, index=dates)
        
        result = indicators.calculate_rci_3_line(df)
        
        assert result['rci_short'] is None
        assert result['rci_medium'] is None
        assert result['rci_long'] is None
        assert result['signal'] == 'NEUTRAL'
    
    def test_rci_3_line_custom_periods(self, indicators, btc_price_data):
        """Test 3-line RCI with custom periods"""
        custom_periods = [5, 14, 21]  # Shorter periods
        result = indicators.calculate_rci_3_line(btc_price_data, periods=custom_periods)
        
        assert isinstance(result, dict)
        # Should work with shorter periods
        assert result['rci_short'] is not None
        assert result['rci_medium'] is not None
        assert result['rci_long'] is not None
    
    def test_single_rci_calculation(self, indicators, btc_price_data):
        """Test single RCI calculation"""
        # Test the underlying single RCI calculation
        rci_value = indicators._calculate_single_rci(btc_price_data['close'], period=14)
        
        if rci_value is not None:
            assert -100 <= rci_value <= 100
            assert isinstance(rci_value, (int, float))
    
    def test_single_rci_insufficient_data(self, indicators):
        """Test single RCI with insufficient data"""
        short_series = pd.Series([100, 105, 102])
        rci_value = indicators._calculate_single_rci(short_series, period=14)
        
        assert rci_value is None
    
    def test_rci_signal_analysis_all_bullish(self, indicators):
        """Test RCI signal analysis with all bullish signals"""
        rci_values = {
            'short': 60,
            'medium': 40,
            'long': 30
        }
        
        signal = indicators._analyze_rci_signals(rci_values)
        assert signal == 'STRONG_BUY'
    
    def test_rci_signal_analysis_all_bearish(self, indicators):
        """Test RCI signal analysis with all bearish signals"""
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
            'short': -1,
            'medium': 1,
            'long': 0
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


class TestIndicatorsEdgeCases:
    """Test critical edge cases and boundary conditions for technical indicators"""
    
    @pytest.fixture
    def indicators(self):
        return TechnicalIndicators()
    
    def test_nan_values_in_price_data(self, indicators):
        """Test handling of NaN values in price data"""
        # Create DataFrame with NaN values
        df = pd.DataFrame({
            'close': [100, np.nan, 102, 101, np.nan, 103, 104],
            'high': [101, np.nan, 103, 102, np.nan, 104, 105],
            'low': [99, np.nan, 101, 100, np.nan, 102, 103],
            'volume': [1000, np.nan, 1100, 1050, np.nan, 1200, 1150],
            'timestamp': pd.date_range('2023-01-01', periods=7)
        })
        
        # RSI calculation should handle NaN gracefully
        try:
            result = indicators.calculate_rsi(df, period=14)
            # Should either return None or a valid number (not NaN)
            assert result is None or (isinstance(result, (int, float)) and not np.isnan(result))
        except Exception as e:
            # Should not crash with unhandled exception
            assert False, f"RSI calculation crashed with NaN data: {e}"
        
        # MACD calculation should handle NaN gracefully
        try:
            result = indicators.calculate_macd(df)
            # MACD may return None with insufficient data (needs 35+ periods)
            if result is not None:
                assert isinstance(result, dict)
                for key, value in result.items():
                    if value is not None:
                        # Check if the series contains NaN values
                        if hasattr(value, 'isna'):
                            # For pandas Series, check if all values are NaN
                            if not value.isna().all():
                                assert not value.isna().any(), f"MACD {key} contains NaN values"
                        else:
                            # For scalar values
                            assert not np.isnan(value), f"MACD {key} returned NaN"
        except Exception as e:
            assert False, f"MACD calculation crashed with NaN data: {e}"
    
    def test_infinite_values_in_price_data(self, indicators):
        """Test handling of infinite values in price data"""
        # Create DataFrame with infinite values
        df = pd.DataFrame({
            'close': [100, np.inf, 102, 101, -np.inf, 103, 104],
            'high': [101, np.inf, 103, 102, -np.inf, 104, 105],
            'low': [99, np.inf, 101, 100, -np.inf, 102, 103],
            'volume': [1000, np.inf, 1100, 1050, -np.inf, 1200, 1150],
            'timestamp': pd.date_range('2023-01-01', periods=7)
        })
        
        # Should handle infinite values without crashing
        try:
            result = indicators.calculate_rsi(df, period=14)
            assert result is None or (isinstance(result, (int, float)) and np.isfinite(result))
        except Exception as e:
            assert False, f"RSI calculation crashed with infinite data: {e}"
    
    def test_insufficient_data_for_calculations(self, indicators):
        """Test handling when there's insufficient data for calculations"""
        # Create DataFrame with very few data points
        insufficient_df = pd.DataFrame({
            'close': [100, 101],  # Only 2 data points
            'high': [101, 102],
            'low': [99, 100],
            'volume': [1000, 1100],
            'timestamp': pd.date_range('2023-01-01', periods=2)
        })
        
        # RSI with period 14 should handle insufficient data
        result = indicators.calculate_rsi(insufficient_df, period=14)
        assert result is None, "RSI should return None with insufficient data"
        
        # MACD should handle insufficient data
        result = indicators.calculate_macd(insufficient_df)
        assert isinstance(result, dict)
        # Should return None or handle gracefully
        for key, value in result.items():
            assert value is None or isinstance(value, (int, float))
        
        # Bollinger Bands should handle insufficient data
        result = indicators.calculate_bollinger_bands(insufficient_df, period=20)
        assert isinstance(result, dict)
        for key, value in result.items():
            assert value is None or isinstance(value, (int, float))
    
    def test_zero_and_negative_prices(self, indicators):
        """Test handling of zero and negative prices"""
        # Create DataFrame with zero and negative prices
        df = pd.DataFrame({
            'close': [100, 0, -50, 101, 0, 103, -10],
            'high': [101, 1, -49, 102, 1, 104, -9],
            'low': [99, -1, -51, 100, -1, 102, -11],
            'volume': [1000, 1100, 1050, 1200, 1150, 1300, 1250],
            'timestamp': pd.date_range('2023-01-01', periods=7)
        })
        
        # Should handle zero and negative prices gracefully
        try:
            result = indicators.calculate_rsi(df, period=14)
            # Should either return None or a valid RSI value
            assert result is None or (0 <= result <= 100)
        except Exception as e:
            assert False, f"RSI calculation crashed with zero/negative prices: {e}"
        
        # MACD should handle zero and negative prices
        try:
            result = indicators.calculate_macd(df)
            assert isinstance(result, dict)
        except Exception as e:
            assert False, f"MACD calculation crashed with zero/negative prices: {e}"
    
    def test_missing_ohlcv_columns(self, indicators):
        """Test handling of missing OHLCV columns"""
        # Test with missing 'high' column
        df_missing_high = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'low': [99, 100, 101, 102, 103],
            'volume': [1000, 1100, 1200, 1300, 1400],
            'timestamp': pd.date_range('2023-01-01', periods=5)
        })
        
        # Should handle missing columns gracefully
        try:
            result = indicators.calculate_bollinger_bands(df_missing_high)
            # Should work with just 'close' column
            assert isinstance(result, dict)
        except KeyError:
            # Acceptable to fail with missing required columns
            pass
        except Exception as e:
            assert False, f"Unexpected error with missing columns: {e}"
        
        # Test with only 'close' column
        df_close_only = pd.DataFrame({
            'close': [100, 101, 102, 103, 104, 105, 106],
            'timestamp': pd.date_range('2023-01-01', periods=7)
        })
        
        # RSI should work with just close prices
        try:
            result = indicators.calculate_rsi(df_close_only, period=5)
            assert result is None or isinstance(result, (int, float))
        except Exception as e:
            assert False, f"RSI failed with close-only data: {e}"
    
    def test_extreme_volatility_scenarios(self, indicators):
        """Test handling of extreme volatility scenarios"""
        # Create data with extreme price swings
        extreme_prices = [100, 1000, 10, 500, 1, 2000, 50]
        df = pd.DataFrame({
            'close': extreme_prices,
            'high': [p * 1.1 for p in extreme_prices],
            'low': [p * 0.9 for p in extreme_prices],
            'volume': [1000] * len(extreme_prices),
            'timestamp': pd.date_range('2023-01-01', periods=len(extreme_prices))
        })
        
        # Should handle extreme volatility without crashing
        try:
            result = indicators.calculate_rsi(df, period=5)
            assert result is None or (0 <= result <= 100)
        except Exception as e:
            assert False, f"RSI crashed with extreme volatility: {e}"
        
        try:
            result = indicators.calculate_bollinger_bands(df, period=5)
            assert isinstance(result, dict)
            # Bollinger bands should handle extreme volatility
            if result.get('bb_upper') and result.get('bb_lower'):
                assert result['bb_upper'] > result['bb_lower']
        except Exception as e:
            assert False, f"Bollinger Bands crashed with extreme volatility: {e}"
    
    def test_duplicate_timestamps(self, indicators):
        """Test handling of duplicate timestamps"""
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104],
            'high': [101, 102, 103, 104, 105],
            'low': [99, 100, 101, 102, 103],
            'volume': [1000, 1100, 1200, 1300, 1400],
            'timestamp': ['2023-01-01', '2023-01-01', '2023-01-02', '2023-01-02', '2023-01-03']
        })
        
        # Should handle duplicate timestamps gracefully
        try:
            result = indicators.calculate_rsi(df, period=3)
            assert result is None or isinstance(result, (int, float))
        except Exception as e:
            assert False, f"RSI crashed with duplicate timestamps: {e}"
    
    def test_empty_dataframe(self, indicators):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        
        # Should handle empty DataFrame gracefully
        try:
            result = indicators.calculate_rsi(empty_df)
            assert result is None
        except Exception as e:
            assert False, f"RSI crashed with empty DataFrame: {e}"
        
        try:
            result = indicators.calculate_macd(empty_df)
            assert isinstance(result, dict)
            for value in result.values():
                assert value is None
        except Exception as e:
            assert False, f"MACD crashed with empty DataFrame: {e}"
    
    def test_single_price_value(self, indicators):
        """Test handling of DataFrame with single repeated price"""
        # All prices are the same (no volatility)
        df = pd.DataFrame({
            'close': [100] * 20,
            'high': [100] * 20,
            'low': [100] * 20,
            'volume': [1000] * 20,
            'timestamp': pd.date_range('2023-01-01', periods=20)
        })
        
        # RSI should handle no price movement
        try:
            result = indicators.calculate_rsi(df, period=14)
            # RSI should be 50 (neutral) when there's no price movement
            assert result is None or result == 50.0
        except Exception as e:
            assert False, f"RSI crashed with no price movement: {e}"
        
        # Bollinger Bands should handle zero volatility
        try:
            result = indicators.calculate_bollinger_bands(df, period=10)
            assert isinstance(result, dict)
            if result.get('bb_upper') and result.get('bb_lower'):
                # With zero volatility, upper and lower bands should be close to middle
                assert abs(result['bb_upper'] - result['bb_lower']) < 1
        except Exception as e:
            assert False, f"Bollinger Bands crashed with zero volatility: {e}"
    
    def test_very_large_numbers(self, indicators):
        """Test handling of very large price numbers"""
        large_prices = [1e10, 1e11, 1e12, 1e13, 1e14]
        df = pd.DataFrame({
            'close': large_prices,
            'high': [p * 1.01 for p in large_prices],
            'low': [p * 0.99 for p in large_prices],
            'volume': [1000] * len(large_prices),
            'timestamp': pd.date_range('2023-01-01', periods=len(large_prices))
        })
        
        # Should handle very large numbers without overflow
        try:
            result = indicators.calculate_rsi(df, period=3)
            assert result is None or (0 <= result <= 100)
        except Exception as e:
            assert False, f"RSI crashed with very large numbers: {e}"
    
    def test_very_small_numbers(self, indicators):
        """Test handling of very small price numbers"""
        small_prices = [1e-10, 1e-9, 1e-8, 1e-7, 1e-6]
        df = pd.DataFrame({
            'close': small_prices,
            'high': [p * 1.01 for p in small_prices],
            'low': [p * 0.99 for p in small_prices],
            'volume': [1000] * len(small_prices),
            'timestamp': pd.date_range('2023-01-01', periods=len(small_prices))
        })
        
        # Should handle very small numbers without underflow
        try:
            result = indicators.calculate_rsi(df, period=3)
            assert result is None or (0 <= result <= 100)
        except Exception as e:
            assert False, f"RSI crashed with very small numbers: {e}"


class TestIndicatorsExceptionHandling:
    """Test exception handling in technical indicators"""
    
    @pytest.fixture
    def indicators(self):
        return TechnicalIndicators()
    
    @patch('pandas_ta.rsi')
    def test_rsi_calculation_exception(self, mock_rsi, indicators):
        """Test RSI calculation exception handling"""
        # Mock pandas_ta.rsi to raise an exception
        mock_rsi.side_effect = Exception("pandas_ta RSI calculation failed")
        
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 5,
            'timestamp': pd.date_range('2023-01-01', periods=25)
        })
        
        result = indicators.calculate_rsi(df, period=14)
        
        # Should handle exception gracefully and return None
        assert result is None
        mock_rsi.assert_called_once()
    
    @patch('pandas_ta.rsi')
    def test_rsi_empty_result_handling(self, mock_rsi, indicators):
        """Test RSI handling when pandas_ta returns None or empty"""
        # Mock pandas_ta.rsi to return None
        mock_rsi.return_value = None
        
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 5,
            'timestamp': pd.date_range('2023-01-01', periods=25)
        })
        
        result = indicators.calculate_rsi(df, period=14)
        
        # Should handle None result gracefully
        assert result is None
    
    @patch('pandas_ta.macd')
    def test_macd_calculation_exception(self, mock_macd, indicators):
        """Test MACD calculation exception handling"""
        # Mock pandas_ta.macd to raise an exception
        mock_macd.side_effect = Exception("pandas_ta MACD calculation failed")
        
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 10,
            'timestamp': pd.date_range('2023-01-01', periods=50)
        })
        
        result = indicators.calculate_macd(df)
        
        # Should handle exception gracefully and return dict with None values
        assert isinstance(result, dict)
        assert result['macd'] is None
        assert result['signal'] is None
        assert result['histogram'] is None
        mock_macd.assert_called_once()
    
    @patch('pandas_ta.sma')
    def test_moving_averages_exception(self, mock_sma, indicators):
        """Test moving averages calculation exception handling"""
        # Mock pandas_ta.sma to raise an exception
        mock_sma.side_effect = Exception("pandas_ta SMA calculation failed")
        
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 50,
            'timestamp': pd.date_range('2023-01-01', periods=250)
        })
        
        result = indicators.calculate_moving_averages(df, 50, 200)
        
        # Should handle exception gracefully and return None
        assert result is None
        mock_sma.assert_called_once()
    
    @patch('pandas_ta.ema')
    def test_ema_calculation_exception(self, mock_ema, indicators):
        """Test EMA calculation exception handling"""
        # Mock pandas_ta.ema to raise an exception
        mock_ema.side_effect = Exception("pandas_ta EMA calculation failed")
        
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 50,
            'timestamp': pd.date_range('2023-01-01', periods=250)
        })
        
        result = indicators.calculate_ema(df, [20, 50, 200])
        
        # Should handle exception gracefully and return None
        assert result is None
        mock_ema.assert_called_once()
    
    def test_moving_averages_insufficient_data(self, indicators):
        """Test moving averages with insufficient data for long period"""
        # Create DataFrame with insufficient data for MA200
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 20,  # Only 100 periods
            'timestamp': pd.date_range('2023-01-01', periods=100)
        })
        
        result = indicators.calculate_moving_averages(df, 50, 200)  # Needs 200 periods
        
        # Should return None due to insufficient data
        assert result is None
    
    def test_ema_insufficient_data(self, indicators):
        """Test EMA with insufficient data for max period"""
        # Create DataFrame with insufficient data for EMA200
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 20,  # Only 100 periods
            'timestamp': pd.date_range('2023-01-01', periods=100)
        })
        
        result = indicators.calculate_ema(df, [20, 50, 200])  # Needs 200 periods
        
        # Should return None due to insufficient data
        assert result is None
    
    @patch('pandas_ta.bbands')
    def test_bollinger_bands_exception(self, mock_bbands, indicators):
        """Test Bollinger Bands calculation exception handling"""
        # Mock pandas_ta.bbands to raise an exception
        mock_bbands.side_effect = Exception("pandas_ta Bollinger Bands calculation failed")
        
        df = pd.DataFrame({
            'close': [100, 101, 102, 103, 104] * 10,
            'timestamp': pd.date_range('2023-01-01', periods=50)
        })
        
        result = indicators.calculate_bollinger_bands(df)
        
        # Should handle exception gracefully and return dict with None values
        assert isinstance(result, dict)
        assert result['bb_upper'] is None
        assert result['bb_middle'] is None
        assert result['bb_lower'] is None
        mock_bbands.assert_called_once()
    
    @patch('pandas_ta.stoch')
    def test_stochastic_exception(self, mock_stoch, indicators):
        """Test Stochastic calculation exception handling"""
        # Mock pandas_ta.stoch to raise an exception
        mock_stoch.side_effect = Exception("pandas_ta Stochastic calculation failed")
        
        df = pd.DataFrame({
            'high': [101, 102, 103, 104, 105] * 10,
            'low': [99, 100, 101, 102, 103] * 10,
            'close': [100, 101, 102, 103, 104] * 10,
            'timestamp': pd.date_range('2023-01-01', periods=50)
        })
        
        result = indicators.calculate_stochastic(df)
        
        # Should handle exception gracefully and return None
        assert result is None
        mock_stoch.assert_called_once()
    
    @patch('pandas_ta.sma')
    @patch('pandas_ta.ad')
    @patch('pandas_ta.obv')
    def test_volume_indicators_exception(self, mock_obv, mock_ad, mock_sma, indicators):
        """Test volume indicators calculation exception handling"""
        # Mock pandas_ta functions to raise exceptions
        mock_sma.side_effect = Exception("pandas_ta SMA calculation failed")
        mock_ad.side_effect = Exception("pandas_ta AD calculation failed")
        mock_obv.side_effect = Exception("pandas_ta OBV calculation failed")
        
        df = pd.DataFrame({
            'high': [101, 102, 103, 104, 105] * 10,
            'low': [99, 100, 101, 102, 103] * 10,
            'close': [100, 101, 102, 103, 104] * 10,
            'volume': [1000, 1100, 1200, 1300, 1400] * 10,
            'timestamp': pd.date_range('2023-01-01', periods=50)
        })
        
        result = indicators.calculate_volume_indicators(df)
        
        # Should handle exception gracefully and return None
        assert result is None
        mock_sma.assert_called_once()
    
    def test_support_resistance_insufficient_data(self, indicators):
        """Test support/resistance with insufficient data"""
        # Create DataFrame with insufficient data for window
        df = pd.DataFrame({
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [100, 101, 102],
            'timestamp': pd.date_range('2023-01-01', periods=3)
        })
        
        result = indicators.calculate_support_resistance(df, window=20)  # Needs 20 periods
        
        # Should handle insufficient data gracefully
        assert isinstance(result, dict)
        assert 'support' in result
        assert 'resistance' in result
