"""
Comprehensive test suite for data_fetcher.py module
Tests Binance and CoinGecko API integration with mocking
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import requests

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import DataFetcher


class TestDataFetcher:
    """Test suite for DataFetcher class"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher(retry_attempts=2, retry_delay=1)
    
    def test_initialization(self, fetcher):
        """Test DataFetcher initialization"""
        assert fetcher.retry_attempts == 2
        assert fetcher.retry_delay == 1
        assert fetcher.binance_base_url == "https://api.binance.com/api/v3"
        assert fetcher.coingecko_base_url == "https://api.coingecko.com/api/v3"
    
    @patch('requests.get')
    def test_make_binance_request_success(self, mock_get, fetcher):
        """Test successful Binance API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'symbol': 'BTCUSDT', 'price': '50000'}
        mock_get.return_value = mock_response
        
        result = fetcher._make_binance_request('/ticker/price', {'symbol': 'BTCUSDT'})
        
        assert result == {'symbol': 'BTCUSDT', 'price': '50000'}
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_make_binance_request_failure(self, mock_get, fetcher):
        """Test failed Binance API request"""
        mock_response = Mock()
        mock_response.status_code = 429  # Rate limit
        mock_get.return_value = mock_response
        
        result = fetcher._make_binance_request('/ticker/price', {'symbol': 'BTCUSDT'})
        
        assert result is None
    
    @patch('requests.get')
    def test_make_binance_request_exception(self, mock_get, fetcher):
        """Test Binance API request with exception"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        result = fetcher._make_binance_request('/ticker/price', {'symbol': 'BTCUSDT'})
        
        assert result is None
    
    @patch('requests.get')
    def test_make_coingecko_request_success(self, mock_get, fetcher):
        """Test successful CoinGecko API request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'bitcoin': {'usd': 50000}}
        mock_get.return_value = mock_response
        
        result = fetcher._make_coingecko_request('/simple/price', {
            'ids': 'bitcoin',
            'vs_currencies': 'usd'
        })
        
        assert result == {'bitcoin': {'usd': 50000}}
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_make_coingecko_request_rate_limit(self, mock_get, fetcher):
        """Test CoinGecko API request with rate limiting"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        result = fetcher._make_coingecko_request('/simple/price', {
            'ids': 'bitcoin',
            'vs_currencies': 'usd'
        })
        
        assert result is None
    
    @patch.object(DataFetcher, '_make_binance_request')
    def test_get_binance_price_success(self, mock_request, fetcher):
        """Test successful Binance price retrieval"""
        mock_request.return_value = {'symbol': 'BTCUSDT', 'price': '50000.00'}
        
        result = fetcher.get_binance_price('BTCUSDT')
        
        assert result == {'symbol': 'BTCUSDT', 'price': '50000.00'}
        mock_request.assert_called_once_with('ticker/price', {'symbol': 'BTCUSDT'})
    
    @patch.object(DataFetcher, '_make_binance_request')
    def test_get_binance_price_failure(self, mock_request, fetcher):
        """Test failed Binance price retrieval"""
        mock_request.return_value = None
        
        result = fetcher.get_binance_price('INVALID')
        
        assert result is None
    
    @patch.object(DataFetcher, '_make_binance_request')
    def test_get_binance_historical_data_success(self, mock_request, fetcher):
        """Test successful Binance historical data retrieval"""
        mock_klines = [
            [1609459200000, "29000", "30000", "28000", "29500", "1000", 1609462800000, "29250000", 100, "500", "14625000", "0"],
            [1609462800000, "29500", "31000", "29000", "30000", "1200", 1609466400000, "36000000", 120, "600", "18000000", "0"]
        ]
        mock_request.return_value = mock_klines
        
        result = fetcher.get_binance_historical_data('BTCUSDT', '1d', 2)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'open' in result.columns
        assert 'close' in result.columns
        assert 'high' in result.columns
        assert 'low' in result.columns
        assert 'volume' in result.columns
    
    @patch.object(DataFetcher, '_make_binance_request')
    def test_get_binance_historical_data_failure(self, mock_request, fetcher):
        """Test failed Binance historical data retrieval"""
        mock_request.return_value = None
        
        result = fetcher.get_binance_historical_data('INVALID', '1d', 100)
        
        assert result is None
    
    @patch.object(DataFetcher, '_make_coingecko_request')
    def test_get_coin_market_data_batch_success(self, mock_request, fetcher):
        """Test successful CoinGecko batch data retrieval"""
        mock_response = {
            'bitcoin': {
                'usd': 50000,
                'usd_market_cap': 1000000000,
                'usd_24h_vol': 50000000,
                'usd_24h_change': 5.5
            },
            'ethereum': {
                'usd': 3000,
                'usd_market_cap': 400000000,
                'usd_24h_vol': 20000000,
                'usd_24h_change': -2.1
            }
        }
        mock_request.return_value = mock_response
        
        result = fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
        
        assert 'bitcoin' in result
        assert 'ethereum' in result
        assert result['bitcoin']['usd'] == 50000
        assert result['ethereum']['usd'] == 3000
    
    @patch.object(DataFetcher, '_make_coingecko_request')
    def test_get_coin_market_data_batch_with_binance_fallback(self, mock_cg_request, fetcher):
        """Test CoinGecko batch data with Binance fallback"""
        # CoinGecko fails
        mock_cg_request.return_value = None
        
        with patch.object(fetcher, 'get_binance_price') as mock_binance:
            mock_binance.return_value = {'price': '50000.00'}
            
            result = fetcher.get_coin_market_data_batch(['bitcoin'])
            
            # Should get data from Binance fallback
            assert 'bitcoin' in result
            assert result['bitcoin']['usd'] == 50000.00
            mock_binance.assert_called()
    
    @patch.object(DataFetcher, '_make_coingecko_request')
    def test_get_btc_dominance_success(self, mock_request, fetcher):
        """Test successful BTC dominance retrieval"""
        mock_response = {
            'data': {
                'market_cap_percentage': {
                    'btc': 65.5
                }
            }
        }
        mock_request.return_value = mock_response
        
        result = fetcher.get_btc_dominance()
        
        assert result == 65.5
    
    @patch.object(DataFetcher, '_make_coingecko_request')
    def test_get_btc_dominance_failure(self, mock_request, fetcher):
        """Test failed BTC dominance retrieval"""
        mock_request.return_value = None
        
        result = fetcher.get_btc_dominance()
        
        assert result is None
    
    @patch.object(DataFetcher, 'get_coin_market_data_batch')
    def test_get_eth_btc_ratio_success(self, mock_batch, fetcher):
        """Test successful ETH/BTC ratio calculation"""
        mock_batch.return_value = {
            'ethereum': {'usd': 3000},
            'bitcoin': {'usd': 60000}
        }
        
        result = fetcher.get_eth_btc_ratio()
        
        assert result == 0.05  # 3000 / 60000
    
    @patch.object(DataFetcher, 'get_coin_market_data_batch')
    def test_get_eth_btc_ratio_failure(self, mock_batch, fetcher):
        """Test failed ETH/BTC ratio calculation"""
        mock_batch.return_value = None
        
        result = fetcher.get_eth_btc_ratio()
        
        assert result is None
    
    @patch('requests.get')
    def test_get_fear_greed_index_success(self, mock_get, fetcher):
        """Test successful Fear & Greed index retrieval"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{
                'value': '75',
                'value_classification': 'Greed',
                'timestamp': '1609459200'
            }]
        }
        mock_get.return_value = mock_response
        
        result = fetcher.get_fear_greed_index()
        
        assert result['value'] == 75
        assert result['classification'] == 'Greed'
        assert 'timestamp' in result
    
    @patch('requests.get')
    def test_get_fear_greed_index_failure(self, mock_get, fetcher):
        """Test failed Fear & Greed index retrieval"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = fetcher.get_fear_greed_index()
        
        assert result is None
    
    @patch.object(DataFetcher, 'get_btc_dominance')
    @patch.object(DataFetcher, 'get_coin_market_data_batch')
    def test_get_market_cap_data_success(self, mock_batch, mock_dominance, fetcher):
        """Test successful market cap data retrieval"""
        mock_dominance.return_value = 65.5
        mock_batch.return_value = {
            'bitcoin': {'usd_market_cap': 1000000000},
            'ethereum': {'usd_market_cap': 400000000}
        }
        
        result = fetcher.get_market_cap_data()
        
        assert result['btc_dominance'] == 65.5
        assert result['btc_market_cap'] == 1000000000
        assert result['eth_market_cap'] == 400000000
        assert result['total_market_cap'] > 0
    
    def test_validate_coin_id_valid(self, fetcher):
        """Test coin ID validation for valid coins"""
        assert fetcher.validate_coin_id('bitcoin') is True
        assert fetcher.validate_coin_id('ethereum') is True
        assert fetcher.validate_coin_id('binancecoin') is True
    
    def test_validate_coin_id_invalid(self, fetcher):
        """Test coin ID validation for invalid coins"""
        assert fetcher.validate_coin_id('') is False
        assert fetcher.validate_coin_id(None) is False
        assert fetcher.validate_coin_id('invalid_coin_12345') is False
    
    def test_get_supported_coins(self, fetcher):
        """Test getting list of supported coins"""
        coins = fetcher.get_supported_coins()
        
        assert isinstance(coins, list)
        assert 'bitcoin' in coins
        assert 'ethereum' in coins
        assert len(coins) > 0
    
    @patch.object(DataFetcher, 'get_binance_price')
    @patch.object(DataFetcher, 'get_coin_market_data_batch')
    def test_connection_test_success(self, mock_cg_batch, mock_binance, fetcher):
        """Test successful connection test"""
        mock_binance.return_value = {'price': '50000'}
        mock_cg_batch.return_value = {'bitcoin': {'usd': 50000}}
        
        with patch.object(fetcher, 'get_fear_greed_index', return_value={'value': 50}):
            result = fetcher.test_connection()
            
            assert result['binance'] is True
            assert result['coingecko'] is True
            assert result['fear_greed'] is True
    
    @patch.object(DataFetcher, 'get_binance_price')
    @patch.object(DataFetcher, 'get_coin_market_data_batch')
    def test_connection_test_partial_failure(self, mock_cg_batch, mock_binance, fetcher):
        """Test connection test with partial failures"""
        mock_binance.return_value = None  # Binance fails
        mock_cg_batch.return_value = {'bitcoin': {'usd': 50000}}  # CoinGecko works
        
        with patch.object(fetcher, 'get_fear_greed_index', return_value=None):  # Fear & Greed fails
            result = fetcher.test_connection()
            
            assert result['binance'] is False
            assert result['coingecko'] is True
            assert result['fear_greed'] is False


class TestDataFetcherIntegration:
    """Integration tests for DataFetcher with realistic scenarios"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher()
    
    @patch.object(DataFetcher, '_make_binance_request')
    @patch.object(DataFetcher, '_make_coingecko_request')
    def test_crypto_market_crash_scenario(self, mock_cg, mock_binance, fetcher):
        """Test data fetching during market crash scenario"""
        # Simulate extreme market conditions
        crash_data = {
            'bitcoin': {'usd': 20000, 'usd_24h_change': -15.5},
            'ethereum': {'usd': 1200, 'usd_24h_change': -18.2}
        }
        mock_cg.return_value = crash_data
        mock_binance.return_value = {'price': '20000.00'}
        
        result = fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
        
        assert result['bitcoin']['usd'] == 20000
        assert result['bitcoin']['usd_24h_change'] == -15.5
        assert result['ethereum']['usd_24h_change'] == -18.2
    
    @patch.object(DataFetcher, '_make_coingecko_request')
    def test_altseason_scenario(self, mock_cg, fetcher):
        """Test data fetching during altseason scenario"""
        # Simulate altseason with low BTC dominance
        altseason_data = {
            'data': {
                'market_cap_percentage': {
                    'btc': 38.5,  # Very low BTC dominance
                    'eth': 18.2
                }
            }
        }
        mock_cg.return_value = altseason_data
        
        btc_dominance = fetcher.get_btc_dominance()
        
        assert btc_dominance == 38.5
        # This should trigger altseason alerts in the main system
    
    @patch.object(DataFetcher, '_make_binance_request')
    def test_high_volatility_scenario(self, mock_binance, fetcher):
        """Test historical data during high volatility"""
        # Simulate high volatility klines data
        volatile_klines = [
            [1609459200000, "50000", "55000", "45000", "52000", "2000", 1609462800000, "100000000", 200, "1000", "50000000", "0"],
            [1609462800000, "52000", "48000", "44000", "46000", "2500", 1609466400000, "115000000", 250, "1250", "57500000", "0"],
            [1609466400000, "46000", "51000", "42000", "49000", "3000", 1609470000000, "140000000", 300, "1500", "70000000", "0"]
        ]
        mock_binance.return_value = volatile_klines
        
        result = fetcher.get_binance_historical_data('BTCUSDT', '1h', 3)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        # Check for high volatility indicators
        price_range = result['high'].max() - result['low'].min()
        assert price_range > 10000  # High volatility
    
    @patch('requests.get')
    def test_extreme_fear_scenario(self, mock_get, fetcher):
        """Test Fear & Greed index during extreme fear"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{
                'value': '8',  # Extreme Fear
                'value_classification': 'Extreme Fear',
                'timestamp': '1609459200'
            }]
        }
        mock_get.return_value = mock_response
        
        result = fetcher.get_fear_greed_index()
        
        assert result['value'] == 8
        assert result['classification'] == 'Extreme Fear'
        # This should trigger buying opportunity alerts
    
    @patch('requests.get')
    def test_extreme_greed_scenario(self, mock_get, fetcher):
        """Test Fear & Greed index during extreme greed"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{
                'value': '92',  # Extreme Greed
                'value_classification': 'Extreme Greed',
                'timestamp': '1609459200'
            }]
        }
        mock_get.return_value = mock_response
        
        result = fetcher.get_fear_greed_index()
        
        assert result['value'] == 92
        assert result['classification'] == 'Extreme Greed'
        # This should trigger selling/caution alerts
    
    @patch.object(DataFetcher, 'get_coin_market_data_batch')
    def test_eth_btc_ratio_bull_market(self, mock_batch, fetcher):
        """Test ETH/BTC ratio during ETH bull run"""
        # ETH outperforming BTC
        mock_batch.return_value = {
            'ethereum': {'usd': 4500},
            'bitcoin': {'usd': 50000}
        }
        
        ratio = fetcher.get_eth_btc_ratio()
        
        assert ratio == 0.09  # High ratio indicates ETH strength
        # This should contribute to altseason detection


class TestDataFetcherErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher(retry_attempts=1, retry_delay=0.1)
    
    @patch('requests.get')
    def test_network_timeout_handling(self, mock_get, fetcher):
        """Test handling of network timeouts"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
        
        result = fetcher._make_binance_request('/ticker/price', {'symbol': 'BTCUSDT'})
        
        assert result is None
    
    @patch('requests.get')
    def test_json_decode_error_handling(self, mock_get, fetcher):
        """Test handling of JSON decode errors"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        result = fetcher._make_coingecko_request('/simple/price', {})
        
        assert result is None
    
    @patch.object(DataFetcher, '_make_binance_request')
    def test_malformed_klines_data_handling(self, mock_request, fetcher):
        """Test handling of malformed klines data"""
        # Missing fields in klines data
        malformed_klines = [
            [1609459200000, "50000", "55000"],  # Missing fields
            ["invalid", "50000", "55000", "45000", "52000", "2000"]  # Invalid timestamp
        ]
        mock_request.return_value = malformed_klines
        
        result = fetcher.get_binance_historical_data('BTCUSDT', '1d', 2)
        
        # Should handle gracefully and return None or empty DataFrame
        assert result is None or result.empty
    
    def test_empty_coin_list_handling(self, fetcher):
        """Test handling of empty coin list"""
        result = fetcher.get_coin_market_data_batch([])
        
        assert result == {}
    
    @patch.object(DataFetcher, '_make_coingecko_request')
    def test_partial_data_handling(self, mock_request, fetcher):
        """Test handling of partial data responses"""
        # Some coins missing from response
        mock_request.return_value = {
            'bitcoin': {'usd': 50000}
            # ethereum missing
        }
        
        result = fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
        
        assert 'bitcoin' in result
        # Should handle missing ethereum gracefully


if __name__ == '__main__':
    pytest.main([__file__])
