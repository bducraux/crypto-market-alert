#!/usr/bin/env python3
"""
Test script to verify the new structured report format
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config
from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy

async def test_new_format():
    """Test the new structured report format"""
    print("Testing new structured report format...")
    
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
        
        # Fetch market data
        print("Fetching market data...")
        coin_data = data_fetcher.get_coin_market_data_batch(coin_ids)
        
        # Create mock market data for testing
        market_data = {
            'btc_dominance': 59.33,
            'fear_greed_index': {
                'value': 72,
                'value_classification': 'Greed'
            },
            'eth_btc_ratio': 0.0320
        }
        
        if coin_data:
            print(f"✓ Fetched data for {len(coin_data)} coins")
            
            # Generate market summary with new format
            summary = strategy.get_market_summary(coin_data, market_data)
            
            # Print the structured report
            print("\n" + "="*50)
            print("STRUCTURED REPORT:")
            print("="*50)
            print(summary.get('structured_report', 'No structured report found'))
            
            # Print portfolio analysis details
            portfolio = summary.get('portfolio_analysis', {})
            print("\n" + "="*50)
            print("PORTFOLIO ANALYSIS DETAILS:")
            print("="*50)
            print(f"Altcoin Value: ${portfolio.get('altcoin_value', 0):,.2f}")
            print(f"Goal Value: ${portfolio.get('goal_value', 0):,.2f}")
            print(f"BTC Equivalent: {portfolio.get('btc_equivalent', 0):.4f} BTC")
            print(f"Progress: {portfolio.get('progress_percentage', 0):.2f}%")
            print(f"Current BTC: {portfolio.get('btc_amount', 0):.8f}")
            print(f"Current ETH: {portfolio.get('eth_amount', 0):.8f}")
            print(f"BTC Price: ${portfolio.get('btc_price', 0):,.2f}")
            print(f"ETH Price: ${portfolio.get('eth_price', 0):,.2f}")
            
            print("\n✓ Test completed successfully!")
            
        else:
            print("✗ Failed to fetch coin data")
            return False
            
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_new_format())
    sys.exit(0 if success else 1)