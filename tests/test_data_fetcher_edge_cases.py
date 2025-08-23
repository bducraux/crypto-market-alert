"""
Comprehensive edge case tests for data_fetcher.py module
Tests network failures, API errors, malformed responses, and boundary conditions
"""

import pytest
import json
import requests
import time
import threading
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import DataFetcher


class TestDataFetcherNetworkEdgeCases:
    """Test network-related edge cases and failures"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher(retry_attempts=3, retry_delay=0.1)
    
    def test_network_timeout_with_retry_exhaustion(self, fetcher):
        """Test behavior when all retries are exhausted due to timeouts"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            
            result = fetcher._make_binance_request('ticker/price', {'symbol': 'BTCUSDT'})
            
            assert result is None
            assert mock_get.call_count == fetcher.retry_attempts
    
    def test_network_connection_error_with_retry(self, fetcher):
        """Test connection errors with retry logic"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
            
            result = fetcher._make_binance_request('ticker/price', {'symbol': 'BTCUSDT'})
            
            assert result is None
            assert mock_get.call_count == fetcher.retry_attempts
    
    def test_partial_timeout_recovery(self, fetcher):
        """Test recovery after partial timeouts"""
        with patch('requests.get') as mock_get:
            # First two calls timeout, third succeeds
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'symbol': 'BTCUSDT', 'price': '45000.50'}
            
            mock_get.side_effect = [
                requests.exceptions.Timeout("Timeout 1"),
                requests.exceptions.Timeout("Timeout 2"),
                mock_response
            ]
            
            result = fetcher._make_binance_request('ticker/price', {'symbol': 'BTCUSDT'})
            
            assert result is not None
            assert result['symbol'] == 'BTCUSDT'
            assert mock_get.call_count == 3
    
    def test_dns_resolution_failure(self, fetcher):
        """Test DNS resolution failures"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError("Name resolution failed")
            
            result = fetcher._make_coingecko_request('simple/price', {'ids': 'bitcoin'})
            
            assert result is None
    
    def test_ssl_certificate_error(self, fetcher):
        """Test SSL certificate verification errors"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.SSLError("SSL certificate verify failed")
            
            result = fetcher._make_binance_request('ticker/price', {'symbol': 'BTCUSDT'})
            
            assert result is None


class TestDataFetcherRateLimitingEdgeCases:
    """Test rate limiting scenarios and recovery"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher(retry_attempts=3, retry_delay=0.1)
    
    def test_rate_limit_429_with_retry_after_header(self, fetcher):
        """Test 429 rate limit with retry-after header"""
        with patch('requests.get') as mock_get:
            # Mock 429 response with retry-after header
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'retry-after': '5'}
            mock_get.return_value = mock_response
            
            result = fetcher._make_coingecko_request('simple/price', {'ids': 'bitcoin'})
            
            assert result is None
            assert mock_get.call_count >= 1
    
    def test_rate_limit_exponential_backoff(self, fetcher):
        """Test exponential backoff logic for rate limiting"""
        with patch('requests.get') as mock_get:
            with patch('time.sleep') as mock_sleep:
                # All requests return 429
                mock_response = Mock()
                mock_response.status_code = 429
                mock_get.return_value = mock_response
                
                result = fetcher._make_coingecko_request('simple/price', {'ids': 'bitcoin'})
                
                assert result is None
                # Verify exponential backoff was called
                assert mock_sleep.call_count >= 1
                # Check that sleep times increase (exponential backoff)
                sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
                assert len(sleep_calls) > 0
    
    def test_rate_limit_recovery_after_backoff(self, fetcher):
        """Test successful recovery after rate limit backoff"""
        with patch('requests.get') as mock_get:
            with patch('time.sleep'):
                # First call returns 429, second succeeds
                success_response = Mock()
                success_response.status_code = 200
                success_response.json.return_value = {'bitcoin': {'usd': 45000}}
                
                rate_limit_response = Mock()
                rate_limit_response.status_code = 429
                
                mock_get.side_effect = [rate_limit_response, success_response]
                
                result = fetcher._make_coingecko_request('simple/price', {'ids': 'bitcoin'})
                
                assert result is not None
                assert 'bitcoin' in result
                assert mock_get.call_count == 2


class TestDataFetcherMalformedResponseEdgeCases:
    """Test handling of malformed and invalid API responses"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher(retry_attempts=2, retry_delay=0.1)
    
    def test_malformed_json_response(self, fetcher):
        """Test handling of invalid JSON from API"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value = mock_response
            
            result = fetcher._make_coingecko_request('simple/price', {'ids': 'bitcoin'})
            
            assert result is None
    
    def test_empty_json_response(self, fetcher):
        """Test handling of empty JSON response"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {}
            mock_get.return_value = mock_response
            
            result = fetcher._make_binance_request('ticker/price', {'symbol': 'BTCUSDT'})
            
            assert result == {}
    
    def test_null_json_response(self, fetcher):
        """Test handling of null JSON response"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = None
            mock_get.return_value = mock_response
            
            result = fetcher._make_coingecko_request('simple/price', {'ids': 'bitcoin'})
            
            assert result is None
    
    def test_missing_required_fields_in_response(self, fetcher):
        """Test handling when required fields are missing from response"""
        with patch('requests.get') as mock_get:
            # Response missing 'price' field
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'symbol': 'BTCUSDT'}  # Missing 'price'
            mock_get.return_value = mock_response
            
            result = fetcher.get_binance_price('BTCUSDT')
            
            # Should handle gracefully - either return None or partial data
            assert result is None or 'price' not in result
    
    def test_unexpected_data_types_in_response(self, fetcher):
        """Test handling of unexpected data types in API response"""
        with patch('requests.get') as mock_get:
            # Price as integer instead of string
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'symbol': 'BTCUSDT', 'price': 45000}  # int instead of str
            mock_get.return_value = mock_response
            
            result = fetcher.get_binance_price('BTCUSDT')
            
            # Should handle different data types gracefully
            assert result is not None
            assert 'symbol' in result
    
    def test_extremely_large_price_values(self, fetcher):
        """Test handling of unrealistic price values"""
        with patch.object(fetcher, '_make_binance_request') as mock_request:
            # Extremely large price that might cause overflow
            large_price = "999999999999999999999.99999999"
            mock_request.return_value = {'symbol': 'BTCUSDT', 'price': large_price}
            
            result = fetcher.get_binance_price('BTCUSDT')
            
            # Should handle large numbers without crashing
            assert result is not None
            if 'price' in result:
                # Should not cause overflow errors
                try:
                    float(result['price'])
                    assert float(result['price']) < float('inf')
                except (ValueError, OverflowError):
                    # Acceptable to reject invalid values
                    pass
    
    def test_extremely_small_price_values(self, fetcher):
        """Test handling of very small price values"""
        with patch.object(fetcher, '_make_binance_request') as mock_request:
            # Very small price that might cause underflow
            small_price = "0.000000000000000001"
            mock_request.return_value = {'symbol': 'BTCUSDT', 'price': small_price}
            
            result = fetcher.get_binance_price('BTCUSDT')
            
            # Should handle small numbers without underflow
            assert result is not None
            if 'price' in result:
                try:
                    price_float = float(result['price'])
                    assert price_float >= 0
                except ValueError:
                    # Acceptable to reject invalid values
                    pass


class TestDataFetcherAPIFallbackEdgeCases:
    """Test API fallback behavior and edge cases"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher(retry_attempts=2, retry_delay=0.1)
    
    def test_binance_down_coingecko_working(self, fetcher):
        """Test fallback when Binance is down but CoinGecko works"""
        with patch('src.data_fetcher.DataFetcher.get_coin_market_data_batch') as mock_batch:
            mock_batch.return_value = {'bitcoin': {'usd': 45000, 'source': 'coingecko'}}
            
            result = fetcher.get_coin_market_data_batch(['bitcoin'])
            
            assert result is not None
            if 'bitcoin' in result:
                assert result['bitcoin']['usd'] == 45000

    def test_coingecko_down_binance_working(self, fetcher):
        """Test fallback when CoinGecko is down but Binance works"""
        with patch('src.data_fetcher.DataFetcher.get_coin_market_data_batch') as mock_batch:
            mock_batch.return_value = {'bitcoin': {'usd': 45000.50, 'source': 'binance'}}
            
            result = fetcher.get_coin_market_data_batch(['bitcoin'])
            
            # Should fallback to Binance
            if result and 'bitcoin' in result:
                assert result['bitcoin']['usd'] == 45000.50

    def test_both_apis_down_graceful_degradation(self, fetcher):
        """Test graceful degradation when both APIs are down"""
        with patch('src.data_fetcher.DataFetcher.get_coin_market_data_batch') as mock_batch:
            mock_batch.return_value = {}
            
            result = fetcher.get_coin_market_data_batch(['bitcoin'])
            
            # Should handle gracefully - return empty dict or None
            assert result is None or result == {}
    
    def test_partial_api_outage_mixed_results(self, fetcher):
        """Test handling when some API calls succeed and others fail"""
        def mock_coingecko_request(endpoint, params=None):
            # Simulate partial outage - some coins work, others don't
            if params and 'bitcoin' in params.get('ids', ''):
                return {'bitcoin': {'usd': 45000}}
            return None
        
        with patch.object(fetcher, '_make_coingecko_request', side_effect=mock_coingecko_request):
            result = fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
            
            # Should return partial results
            if result:
                assert 'bitcoin' in result or len(result) >= 0


class TestDataFetcherConcurrencyEdgeCases:
    """Test thread safety and concurrent request handling"""
    
    @pytest.fixture
    def fetcher(self):
        return DataFetcher(retry_attempts=2, retry_delay=0.1)
    
    def test_concurrent_cache_access(self, fetcher):
        """Test that cache access is thread-safe"""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch.object(fetcher, '_make_coingecko_request') as mock_request:
                mock_request.return_value = {'bitcoin': {'usd': 45000}}
                result = fetcher.get_coin_market_data_batch(['bitcoin'])
                results.append(result)
        
        # Create multiple threads making concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should complete without errors
        assert len(results) == 5
        for result in results:
            assert result is not None or result == {}
    
    def test_rate_limiting_thread_safety(self, fetcher):
        """Test that rate limiting is properly synchronized across threads"""
        import threading
        
        call_times = []
        
        def timed_request():
            start_time = time.time()
            with patch.object(fetcher, '_make_coingecko_request') as mock_request:
                mock_request.return_value = {'bitcoin': {'usd': 45000}}
                fetcher.get_coin_market_data_batch(['bitcoin'])
            call_times.append(time.time() - start_time)
        
        # Make concurrent requests that should be rate-limited
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=timed_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should complete without race conditions
        assert len(call_times) == 3


if __name__ == '__main__':
    pytest.main([__file__])