#!/usr/bin/env python3
"""
Debug script to compare real market data vs test data
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config
from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy

async def debug_market_data():
    """Debug market data collection and calculations"""
    print("Debugging market data collection...")
    
    try:
        # Load configuration
        config = load_config("config/config.yaml")
        print("✓ Configuration loaded")
        
        # Initialize components
        data_fetcher = DataFetcher()
        strategy = AlertStrategy(config)
        print("✓ Components initialized")
        
        # Get coin IDs from config
        coin_ids = [coin.get('coingecko_id') for coin in config.get('coins', [])]
        print(f"✓ Found {len(coin_ids)} coins in config")
        
        # Fetch coin data (same as test)
        print("\nFetching coin data...")
        coin_data = data_fetcher.get_coin_market_data_batch(coin_ids)
        
        if coin_data:
            print(f"✓ Fetched data for {len(coin_data)} coins")
            
            # Show BTC and ETH prices from coin data
            btc_price = coin_data.get('bitcoin', {}).get('usd', 0)
            eth_price = coin_data.get('ethereum', {}).get('usd', 0)
            print(f"BTC Price from coin_data: ${btc_price:,.2f}")
            print(f"ETH Price from coin_data: ${eth_price:,.2f}")
            
            # Fetch REAL market data (like main.py does)
            print("\nFetching REAL market data...")
            real_market_data = {}
            
            try:
                # Get BTC dominance
                btc_dominance = data_fetcher.get_btc_dominance()
                if btc_dominance:
                    real_market_data['btc_dominance'] = btc_dominance
                    print(f"Real BTC Dominance: {btc_dominance:.2f}%")
                
                # Get ETH/BTC ratio
                eth_btc_ratio = data_fetcher.get_eth_btc_ratio()
                if eth_btc_ratio:
                    real_market_data['eth_btc_ratio'] = eth_btc_ratio
                    print(f"Real ETH/BTC Ratio: {eth_btc_ratio:.6f}")
                
                # Get Fear & Greed Index
                fear_greed = data_fetcher.get_fear_greed_index()
                if fear_greed:
                    real_market_data['fear_greed_index'] = fear_greed
                    print(f"Real Fear & Greed Index: {fear_greed}")
                
            except Exception as e:
                print(f"Error fetching real market data: {e}")
            
            # Create mock market data (like test does)
            mock_market_data = {
                'btc_dominance': 59.33,
                'fear_greed_index': {
                    'value': 72,
                    'value_classification': 'Greed'
                },
                'eth_btc_ratio': 0.0320
            }
            
            print(f"\nMock BTC Dominance: {mock_market_data['btc_dominance']:.2f}%")
            print(f"Mock ETH/BTC Ratio: {mock_market_data['eth_btc_ratio']:.6f}")
            print(f"Mock Fear & Greed Index: {mock_market_data['fear_greed_index']}")
            
            # Generate summary with REAL market data
            print("\n" + "="*60)
            print("SUMMARY WITH REAL MARKET DATA:")
            print("="*60)
            real_summary = strategy.get_market_summary(coin_data, real_market_data)
            real_portfolio = real_summary.get('portfolio_analysis', {})
            
            print(f"Altcoin Value: ${real_portfolio.get('altcoin_value', 0):,.2f}")
            print(f"Goal Value: ${real_portfolio.get('goal_value', 0):,.2f}")
            print(f"BTC Equivalent: {real_portfolio.get('btc_equivalent', 0):.4f} BTC")
            print(f"Progress: {real_portfolio.get('progress_percentage', 0):.2f}%")
            print(f"Current BTC: {real_portfolio.get('btc_amount', 0):.8f}")
            print(f"Current ETH: {real_portfolio.get('eth_amount', 0):.8f}")
            
            # Generate summary with MOCK market data
            print("\n" + "="*60)
            print("SUMMARY WITH MOCK MARKET DATA:")
            print("="*60)
            mock_summary = strategy.get_market_summary(coin_data, mock_market_data)
            mock_portfolio = mock_summary.get('portfolio_analysis', {})
            
            print(f"Altcoin Value: ${mock_portfolio.get('altcoin_value', 0):,.2f}")
            print(f"Goal Value: ${mock_portfolio.get('goal_value', 0):,.2f}")
            print(f"BTC Equivalent: {mock_portfolio.get('btc_equivalent', 0):.4f} BTC")
            print(f"Progress: {mock_portfolio.get('progress_percentage', 0):.2f}%")
            print(f"Current BTC: {mock_portfolio.get('btc_amount', 0):.8f}")
            print(f"Current ETH: {mock_portfolio.get('eth_amount', 0):.8f}")
            
            # Show the structured reports
            print("\n" + "="*60)
            print("REAL MARKET DATA STRUCTURED REPORT:")
            print("="*60)
            print(real_summary.get('structured_report', 'No structured report found'))
            
            print("\n" + "="*60)
            print("MOCK MARKET DATA STRUCTURED REPORT:")
            print("="*60)
            print(mock_summary.get('structured_report', 'No structured report found'))
            
            print("\n✓ Debug completed successfully!")
            
        else:
            print("✗ Failed to fetch coin data")
            return False
            
    except Exception as e:
        print(f"✗ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(debug_market_data())
    sys.exit(0 if success else 1)