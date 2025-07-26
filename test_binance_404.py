#!/usr/bin/env python3
"""
Test script to reproduce Binance API 404 errors
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import DataFetcher
import logging
import requests

# Configure logging to see detailed errors
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

def test_binance_endpoints():
    """Test individual Binance endpoints to identify 404 errors"""
    print("Testing Binance API endpoints...")
    
    fetcher = DataFetcher()
    base_url = "https://api.binance.com/api/v3"
    
    # Test the problematic endpoints directly
    test_endpoints = [
        ("/ticker/price", {"symbol": "BTCUSDT"}),
        ("ticker/price", {"symbol": "BTCUSDT"}),
        ("ticker/24hr", {"symbol": "BTCUSDT"}),
        ("/ticker/24hr", {"symbol": "BTCUSDT"}),
        ("klines", {"symbol": "BTCUSDT", "interval": "1d", "limit": 10}),
        ("/klines", {"symbol": "BTCUSDT", "interval": "1d", "limit": 10})
    ]
    
    for endpoint, params in test_endpoints:
        url = base_url + "/" + endpoint
        print("\nTesting: " + url)
        print("Params: " + str(params))
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print("Status Code: " + str(response.status_code))
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    print("Success! Response keys: " + str(list(data.keys())))
                else:
                    print("Success! List response")
            else:
                print("Failed! Response: " + response.text[:200])
                
        except Exception as e:
            print("Exception: " + str(e))
    
    print("\n" + "="*50)
    print("Testing through DataFetcher methods...")
    
    # Test through the DataFetcher methods
    print("\nTesting get_binance_price('BTCUSDT')...")
    price_data = fetcher.get_binance_price('BTCUSDT')
    print("Result: " + str(price_data))
    
    print("\nTesting get_binance_historical_data('BTCUSDT')...")
    hist_data = fetcher.get_binance_historical_data('BTCUSDT', limit=5)
    if hist_data is not None:
        print("Result: " + str(hist_data.shape))
    else:
        print("Result: None")

if __name__ == "__main__":
    test_binance_endpoints()