"""
Unit tests for data_fetcher module
"""

import pytest
import pandas as pd
import requests
from unittest.mock import Mock, patch, MagicMock
from src.data_fetcher import DataFetcher


class TestDataFetcher:
    """Test cases for DataFetcher class"""
    
    @pytest.fixture
    def data_fetcher(self):
        """Create a DataFetcher instance for testing"""
        return DataFetcher(api_key="test_key", retry_attempts=2, retry_delay=1)
    
    @pytest.fixture
    def mock_response_data(self):
        """Mock response data for API calls"""
        return {
            'bitcoin': {
                'usd': 45000.0,
                'usd_24h_change': 2.5,
                'usd_market_cap': 850000000000,
                'usd_24h_vol': 25000000000
            },
            'ethereum': {
                'usd': 3000.0,
                'usd_24h_change': -1.2,
                'usd_market_cap': 360000000000,
                'usd_24h_vol': 15000000000
            }
        }
    
    @pytest.fixture
    def mock_ohlc_data(self):
        """Mock OHLC data for historical prices"""
        return [
            [1640995200000, 46000, 47000, 45500, 46500],  # timestamp, open, high, low, close
            [1641081600000, 46500, 46800, 45800, 46200],
            [1641168000000, 46200, 46900, 45900, 46700],
        ]
    
    def test_initialization(self):
        """Test DataFetcher initialization"""
        fetcher = DataFetcher(api_key="test", retry_attempts=3, retry_delay=5)
        
        assert fetcher.api_key == "test"
        assert fetcher.retry_attempts == 3
        assert fetcher.retry_delay == 5
        assert fetcher.base_url == "https://api.coingecko.com/api/v3"
        assert fetcher.min_request_interval == 1.2
    
    @patch('src.data_fetcher.requests.get')
    def test_make_request_success(self, mock_get, data_fetcher, mock_response_data):
        """Test successful API request"""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = data_fetcher._make_request("https://api.test.com/endpoint")
        
        assert result == mock_response_data
        mock_get.assert_called_once()
    
    @patch('src.data_fetcher.time.sleep')  # Mock sleep to speed up tests
    @patch('src.data_fetcher.requests.get')
    def test_make_request_failure(self, mock_get, mock_sleep, data_fetcher):
        """Test failed API request with retries"""
        # Mock failed response
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        result = data_fetcher._make_request("https://api.test.com/endpoint")
        
        assert result is None
        assert mock_get.call_count == data_fetcher.retry_attempts
        # Verify sleep was called for retries (retry_attempts - 1 times)
        assert mock_sleep.call_count == data_fetcher.retry_attempts - 1
    
    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_get_coin_price_success(self, mock_request, data_fetcher):
        """Test successful coin price retrieval"""
        mock_request.return_value = {
            'bitcoin': {'usd': 45000.0}
        }
        
        price = data_fetcher.get_coin_price('bitcoin')
        
        assert price == 45000.0
        mock_request.assert_called_once()
    
    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_get_coin_price_failure(self, mock_request, data_fetcher):
        """Test failed coin price retrieval"""
        mock_request.return_value = None
        
        price = data_fetcher.get_coin_price('bitcoin')
        
        assert price is None
    
    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_get_multiple_coin_prices(self, mock_request, data_fetcher, mock_response_data):
        """Test multiple coin price retrieval"""
        mock_request.return_value = mock_response_data
        
        prices = data_fetcher.get_multiple_coin_prices(['bitcoin', 'ethereum'])
        
        assert prices == mock_response_data
        assert 'bitcoin' in prices
        assert 'ethereum' in prices
    
    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_get_historical_prices_success(self, mock_request, data_fetcher, mock_ohlc_data):
        """Test successful historical price retrieval"""
        mock_request.return_value = mock_ohlc_data
        
        df = data_fetcher.get_historical_prices('bitcoin', days=30)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['open', 'high', 'low', 'close']
        assert df.index.name == 'timestamp'
    
    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_get_historical_prices_failure(self, mock_request, data_fetcher):
        """Test failed historical price retrieval"""
        mock_request.return_value = None
        
        df = data_fetcher.get_historical_prices('bitcoin', days=30)
        
        assert df is None
    
    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_get_btc_dominance_success(self, mock_request, data_fetcher):
        """Test successful BTC dominance retrieval"""
        mock_request.return_value = {
            'data': {
                'market_cap_percentage': {
                    'btc': 42.5
                }
            }
        }
        
        dominance = data_fetcher.get_btc_dominance()
        
        assert dominance == 42.5
    
    @patch('src.data_fetcher.DataFetcher._make_request')
    def test_get_btc_dominance_failure(self, mock_request, data_fetcher):
        """Test failed BTC dominance retrieval"""
        mock_request.return_value = None
        
        dominance = data_fetcher.get_btc_dominance()
        
        assert dominance is None
    
    @patch('src.data_fetcher.DataFetcher.get_multiple_coin_prices')
    def test_get_eth_btc_ratio_success(self, mock_prices, data_fetcher):
        """Test successful ETH/BTC ratio calculation"""
        mock_prices.return_value = {
            'ethereum': {'usd': 3000.0},
            'bitcoin': {'usd': 45000.0}
        }
        
        ratio = data_fetcher.get_eth_btc_ratio()
        
        assert ratio == 3000.0 / 45000.0
    
    @patch('src.data_fetcher.DataFetcher.get_multiple_coin_prices')
    def test_get_eth_btc_ratio_failure(self, mock_prices, data_fetcher):
        """Test failed ETH/BTC ratio calculation"""
        mock_prices.return_value = {}
        
        ratio = data_fetcher.get_eth_btc_ratio()
        
        assert ratio is None
    
    @patch('src.data_fetcher.requests.get')
    def test_get_fear_greed_index_success(self, mock_get, data_fetcher):
        """Test successful Fear & Greed Index retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [{
                'value': '25',
                'value_classification': 'Fear',
                'timestamp': '1641024000'
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        fear_greed = data_fetcher.get_fear_greed_index()
        
        assert fear_greed['value'] == 25
        assert fear_greed['value_classification'] == 'Fear'
    
    @patch('src.data_fetcher.requests.get')
    def test_get_fear_greed_index_failure(self, mock_get, data_fetcher):
        """Test failed Fear & Greed Index retrieval"""
        mock_get.side_effect = Exception("API error")
        
        fear_greed = data_fetcher.get_fear_greed_index()
        
        assert fear_greed is None
    
    @patch('src.data_fetcher.DataFetcher.get_multiple_coin_prices')
    @patch('src.data_fetcher.DataFetcher.get_historical_prices')
    def test_get_coin_market_data_batch(self, mock_historical, mock_prices, data_fetcher, mock_response_data):
        """Test batch coin market data retrieval"""
        mock_prices.return_value = mock_response_data
        mock_historical.return_value = pd.DataFrame({
            'open': [46000, 46500],
            'high': [47000, 46800],
            'low': [45500, 45800],
            'close': [46500, 46200]
        })
        
        result = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
        
        assert 'bitcoin' in result
        assert 'ethereum' in result
        assert 'historical' in result['bitcoin']
        assert isinstance(result['bitcoin']['historical'], pd.DataFrame)
    
    @patch('src.data_fetcher.DataFetcher.get_coin_price')
    def test_validate_coin_id_success(self, mock_price, data_fetcher):
        """Test successful coin ID validation"""
        mock_price.return_value = 45000.0
        
        is_valid = data_fetcher.validate_coin_id('bitcoin')
        
        assert is_valid is True
    
    @patch('src.data_fetcher.DataFetcher.get_coin_price')
    def test_validate_coin_id_failure(self, mock_price, data_fetcher):
        """Test failed coin ID validation"""
        mock_price.return_value = None
        
        is_valid = data_fetcher.validate_coin_id('invalid_coin')
        
        assert is_valid is False
