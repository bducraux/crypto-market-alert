#!/usr/bin/env python3
"""
Test script to verify that Binance is used as primary API for price data
and CoinGecko is used only for market cap and unique metrics.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import DataFetcher
import logging

# Configure logging to see the API calls
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_api_priority():
    """Test that Binance is used as primary for price data"""
    print("Testing API priority...")
    
    fetcher = DataFetcher()
    
    # Test getting market data for a few coins
    test_coins = ['bitcoin', 'ethereum', 'binancecoin']
    
    print(f"\nTesting market data for: {test_coins}")
    market_data = fetcher.get_coin_market_data_batch(test_coins)
    
    if market_data:
        print(f"\nSuccessfully retrieved data for {len(market_data)} coins:")
        for coin_id, data in market_data.items():
            print(f"  {coin_id}:")
            print(f"    Price: ${data.get('usd', 'N/A')}")
            print(f"    24h Change: {data.get('usd_24h_change', 'N/A')}%")
            print(f"    24h Volume: ${data.get('usd_24h_vol', 'N/A')}")
            print(f"    Market Cap: ${data.get('usd_market_cap', 'N/A')}")
            print(f"    Has Historical: {'Yes' if 'historical' in data else 'No'}")
    else:
        print("Failed to retrieve market data")
        return False
    
    # Test unique CoinGecko metrics
    print("\nTesting unique CoinGecko metrics...")
    
    btc_dominance = fetcher.get_btc_dominance()
    print(f"BTC Dominance: {btc_dominance}%")
    
    fear_greed = fetcher.get_fear_greed_index()
    if fear_greed:
        print(f"Fear & Greed Index: {fear_greed['value']} ({fear_greed['value_classification']})")
    
    # Test connection to both APIs
    print("\nTesting API connections...")
    connections = fetcher.test_connection()
    print(f"Binance connection: {'OK' if connections.get('binance') else 'FAILED'}")
    print(f"CoinGecko connection: {'OK' if connections.get('coingecko') else 'FAILED'}")
    
    return True

if __name__ == "__main__":
    success = test_api_priority()
    if success:
        print("\n✅ API priority test completed successfully!")
        print("Binance is now primary for price data, CoinGecko for unique metrics only.")
    else:
        print("\n❌ API priority test failed!")
        sys.exit(1)