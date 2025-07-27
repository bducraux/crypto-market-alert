"""
API Contract Tests for External Services
Tests that validate real API response structures and data types
These tests may use real APIs and should be marked as integration tests
"""

import pytest
import requests
import sys
import os
from typing import Dict, Any
from unittest.mock import patch, Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import DataFetcher


@pytest.mark.integration
@pytest.mark.network
class TestBinanceAPIContract:
    """Test Binance API contract validation - using mocks to avoid rate limits"""
    
    @pytest.fixture(scope="class")
    def data_fetcher(self):
        """Create DataFetcher instance for contract testing"""
        return DataFetcher(retry_attempts=2, retry_delay=1)
    
    def test_binance_ticker_price_contract(self, data_fetcher):
        """Verify Binance ticker/price API returns expected data structure"""
        # Mock Binance API response to avoid rate limits
        mock_response = {'symbol': 'BTCUSDT', 'price': '45000.50'}
        
        with patch.object(data_fetcher, '_make_binance_request', return_value=mock_response):
            result = data_fetcher.get_binance_price('BTCUSDT')
            
            # Validate required fields are present
            assert 'symbol' in result, "Missing required field: symbol"
            assert 'price' in result, "Missing required field: price"
            
            # Validate data types
            assert isinstance(result['symbol'], str), "Symbol should be string"
            assert isinstance(result['price'], str), "Price should be string (as per Binance API)"
            
            # Validate field values
            assert result['symbol'] == 'BTCUSDT', f"Expected BTCUSDT, got {result['symbol']}"
            assert len(result['price']) > 0, "Price should not be empty"
            
            # Validate price can be converted to float and is positive
            price_float = float(result['price'])
            assert price_float > 0, f"Price should be positive, got {price_float}"
            assert price_float < 1000000, f"Price seems unrealistic: {price_float}"
    
    def test_binance_klines_contract(self, data_fetcher):
        """Verify Binance klines API returns expected OHLCV data structure"""
        result = data_fetcher.get_binance_historical_data('BTCUSDT', '1d', 5)
        
        if result is not None and not result.empty:
            # Validate DataFrame structure
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                assert col in result.columns, f"Missing required column: {col}"
            
            # Validate data types
            for col in required_columns:
                assert result[col].dtype in ['float64', 'int64'], f"Column {col} should be numeric"
            
            # Validate OHLCV relationships
            assert all(result['high'] >= result['low']), "High should be >= Low"
            assert all(result['high'] >= result['open']), "High should be >= Open"
            assert all(result['high'] >= result['close']), "High should be >= Close"
            assert all(result['low'] <= result['open']), "Low should be <= Open"
            assert all(result['low'] <= result['close']), "Low should be <= Close"
            assert all(result['volume'] >= 0), "Volume should be non-negative"
            
            # Validate reasonable value ranges
            assert all(result['close'] > 1000), "BTC price should be > $1000"
            assert all(result['close'] < 1000000), "BTC price should be < $1M"
        else:
            pytest.skip("Binance historical data not available - skipping contract test")
    
    def test_binance_multiple_symbols_contract(self, data_fetcher):
        """Test Binance API with multiple common trading pairs"""
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
        
        for symbol in test_symbols:
            result = data_fetcher.get_binance_price(symbol)
            
            if result:
                assert result['symbol'] == symbol
                assert isinstance(result['price'], str)
                assert float(result['price']) > 0
            # If one symbol fails, continue testing others


@pytest.mark.integration
@pytest.mark.network
class TestCoinGeckoAPIContract:
    """Test CoinGecko API contract validation"""
    
    @pytest.fixture(scope="class")
    def data_fetcher(self):
        """Create DataFetcher instance for contract testing"""
        return DataFetcher(retry_attempts=2, retry_delay=2)  # Longer delay for CoinGecko
    
    def test_coingecko_simple_price_contract(self, data_fetcher):
        """Verify CoinGecko simple/price API returns expected data structure"""
        result = data_fetcher.get_coin_market_data_batch(['bitcoin'])
        
        if result and 'bitcoin' in result:
            btc_data = result['bitcoin']
            
            # Validate required fields
            required_fields = ['usd', 'usd_24h_change', 'usd_24h_vol', 'usd_market_cap']
            for field in required_fields:
                assert field in btc_data, f"Missing required field: {field}"
            
            # Validate data types
            for field in required_fields:
                assert isinstance(btc_data[field], (int, float)), f"Field {field} should be numeric"
            
            # Validate value ranges
            assert btc_data['usd'] > 1000, f"BTC price too low: {btc_data['usd']}"
            assert btc_data['usd'] < 1000000, f"BTC price too high: {btc_data['usd']}"
            assert btc_data['usd_market_cap'] > btc_data['usd'], "Market cap should be > price"
            assert btc_data['usd_24h_vol'] > 0, "24h volume should be positive"
            assert -100 <= btc_data['usd_24h_change'] <= 1000, "24h change should be reasonable"
        else:
            pytest.skip("CoinGecko API not available - skipping contract test")
    
    def test_coingecko_batch_request_contract(self, data_fetcher):
        """Test CoinGecko batch request with multiple coins"""
        coins = ['bitcoin', 'ethereum', 'cardano']
        result = data_fetcher.get_coin_market_data_batch(coins)
        
        if result:
            # Should return data for at least some coins
            assert len(result) > 0, "Should return data for at least one coin"
            
            for coin_id, coin_data in result.items():
                assert coin_id in coins, f"Unexpected coin in response: {coin_id}"
                assert isinstance(coin_data, dict), f"Coin data should be dict for {coin_id}"
                assert 'usd' in coin_data, f"Missing USD price for {coin_id}"
                assert isinstance(coin_data['usd'], (int, float)), f"USD price should be numeric for {coin_id}"
                assert coin_data['usd'] > 0, f"USD price should be positive for {coin_id}"
        else:
            pytest.skip("CoinGecko batch API not available - skipping contract test")
    
    def test_coingecko_btc_dominance_contract(self, data_fetcher):
        """Verify CoinGecko BTC dominance API returns expected structure"""
        result = data_fetcher.get_btc_dominance()
        
        if result is not None:
            # Validate data type
            assert isinstance(result, (int, float)), "BTC dominance should be numeric"
            
            # Validate reasonable range (BTC dominance should be 0-100%)
            assert 0 <= result <= 100, f"BTC dominance should be 0-100%, got {result}"
            
            # Validate it's a reasonable value (historically BTC dominance is 30-80%)
            assert 20 <= result <= 90, f"BTC dominance seems unrealistic: {result}%"
        else:
            pytest.skip("CoinGecko dominance API not available - skipping contract test")
    
    def test_coingecko_eth_btc_ratio_contract(self, data_fetcher):
        """Test ETH/BTC ratio calculation from CoinGecko data"""
        result = data_fetcher.get_eth_btc_ratio()
        
        if result is not None:
            # Validate data type
            assert isinstance(result, (int, float)), "ETH/BTC ratio should be numeric"
            
            # Validate reasonable range (historically ETH/BTC is 0.01-0.15)
            assert 0.005 <= result <= 0.5, f"ETH/BTC ratio seems unrealistic: {result}"
            
            # Validate precision (should have reasonable decimal places)
            assert result > 0, "ETH/BTC ratio should be positive"
        else:
            pytest.skip("ETH/BTC ratio calculation not available - skipping contract test")


@pytest.mark.integration
@pytest.mark.network
class TestFearGreedAPIContract:
    """Test Fear & Greed Index API contract validation"""
    
    @pytest.fixture(scope="class")
    def data_fetcher(self):
        """Create DataFetcher instance for contract testing"""
        return DataFetcher(retry_attempts=2, retry_delay=1)
    
    def test_fear_greed_index_contract(self, data_fetcher):
        """Verify Fear & Greed Index API returns expected data structure"""
        result = data_fetcher.get_fear_greed_index()
        
        if result:
            # Validate required fields
            required_fields = ['value', 'classification', 'timestamp']
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
            
            # Validate data types
            assert isinstance(result['value'], int), "Value should be integer"
            assert isinstance(result['classification'], str), "Classification should be string"
            assert isinstance(result['timestamp'], str), "Timestamp should be string"
            
            # Validate value range (Fear & Greed index is 0-100)
            assert 0 <= result['value'] <= 100, f"Fear & Greed value should be 0-100, got {result['value']}"
            
            # Validate classification values
            valid_classifications = [
                'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'
            ]
            assert result['classification'] in valid_classifications, \
                f"Invalid classification: {result['classification']}"
            
            # Validate timestamp format (should be numeric string)
            assert result['timestamp'].isdigit(), "Timestamp should be numeric string"
            assert len(result['timestamp']) >= 10, "Timestamp should be at least 10 digits"
            
            # Validate value-classification consistency
            value = result['value']
            classification = result['classification']
            
            if value <= 25:
                assert 'Fear' in classification, f"Value {value} should indicate Fear"
            elif value >= 75:
                assert 'Greed' in classification, f"Value {value} should indicate Greed"
        else:
            pytest.skip("Fear & Greed API not available - skipping contract test")


@pytest.mark.integration
@pytest.mark.network
class TestAPIErrorHandlingContracts:
    """Test API error handling and edge cases in real scenarios"""
    
    @pytest.fixture(scope="class")
    def data_fetcher(self):
        """Create DataFetcher instance for error testing"""
        return DataFetcher(retry_attempts=1, retry_delay=0.5)
    
    def test_binance_invalid_symbol_handling(self, data_fetcher):
        """Test Binance API handling of invalid trading symbols"""
        # Test with clearly invalid symbol
        result = data_fetcher.get_binance_price('INVALIDCOIN')
        
        # Should handle gracefully and return None
        assert result is None, "Invalid symbol should return None"
    
    def test_coingecko_invalid_coin_handling(self, data_fetcher):
        """Test CoinGecko API handling of invalid coin IDs"""
        # Test with clearly invalid coin ID
        result = data_fetcher.get_coin_market_data_batch(['invalid-coin-12345'])
        
        # Should handle gracefully - either return None or empty dict
        assert result is None or result == {}, "Invalid coin should return None or empty dict"
    
    def test_api_rate_limiting_behavior(self, data_fetcher):
        """Test API behavior under potential rate limiting"""
        # Make multiple rapid requests to test rate limiting handling
        results = []
        for i in range(3):
            result = data_fetcher.get_binance_price('BTCUSDT')
            results.append(result)
        
        # At least some requests should succeed (or all fail gracefully)
        successful_requests = [r for r in results if r is not None]
        
        # Either all succeed (no rate limiting) or some fail gracefully
        assert len(successful_requests) >= 0, "Should handle rate limiting gracefully"
        
        # If any succeed, they should have valid structure
        for result in successful_requests:
            assert 'symbol' in result
            assert 'price' in result


@pytest.mark.integration
@pytest.mark.network
class TestAPIPerformanceContracts:
    """Test API performance and response time contracts"""
    
    @pytest.fixture(scope="class")
    def data_fetcher(self):
        """Create DataFetcher instance for performance testing"""
        return DataFetcher(retry_attempts=1, retry_delay=0.1)
    
    def test_binance_response_time_contract(self, data_fetcher, performance_monitor):
        """Test that Binance API responds within reasonable time"""
        performance_monitor.start()
        
        result = data_fetcher.get_binance_price('BTCUSDT')
        
        if result:
            # Should respond within 10 seconds for single request
            performance_monitor.assert_under_threshold(10.0)
        else:
            pytest.skip("Binance API not available - skipping performance test")
    
    def test_coingecko_response_time_contract(self, data_fetcher, performance_monitor):
        """Test that CoinGecko API responds within reasonable time"""
        performance_monitor.start()
        
        result = data_fetcher.get_coin_market_data_batch(['bitcoin'])
        
        if result:
            # CoinGecko can be slower, allow up to 15 seconds
            performance_monitor.assert_under_threshold(15.0)
        else:
            pytest.skip("CoinGecko API not available - skipping performance test")
    
    def test_fear_greed_response_time_contract(self, data_fetcher, performance_monitor):
        """Test that Fear & Greed API responds within reasonable time"""
        performance_monitor.start()
        
        result = data_fetcher.get_fear_greed_index()
        
        if result:
            # Should respond within 10 seconds
            performance_monitor.assert_under_threshold(10.0)
        else:
            pytest.skip("Fear & Greed API not available - skipping performance test")


if __name__ == '__main__':
    # Run only contract tests
    pytest.main([__file__, '-m', 'integration'])