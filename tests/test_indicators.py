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
        assert isinstance(result, pd.Series)
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
        assert 'upper' in result
        assert 'middle' in result
        assert 'lower' in result
    
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
        mock_rsi.return_value = pd.Series([30, 40, 50, 60, 55])
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
        assert result['rsi'] == 55
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
