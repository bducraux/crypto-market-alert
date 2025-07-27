#!/usr/bin/env python3
"""
Debug script to trace portfolio calculation values step by step
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config, load_environment
from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy

async def debug_portfolio_calculation():
    """Debug portfolio calculation step by step"""
    print("Debugging portfolio calculation...")
    
    try:
        # Load environment and configuration
        load_environment()
        config = load_config("config/config.yaml")
        print("✓ Configuration loaded")
        
        # Print config BTC and ETH amounts
        print("\n" + "="*60)
        print("CONFIG ANALYSIS:")
        print("="*60)
        
        btc_config = None
        eth_config = None
        
        for coin_config in config.get('coins', []):
            coin_name = coin_config.get('name')
            current_amount = coin_config.get('current_amount', 0)
            coingecko_id = coin_config.get('coingecko_id')
            
            if coin_name == 'BTC':
                btc_config = coin_config
                print(f"BTC Config - Amount: {current_amount}, ID: {coingecko_id}")
            elif coin_name == 'ETH':
                eth_config = coin_config
                print(f"ETH Config - Amount: {current_amount}, ID: {coingecko_id}")
        
        if not btc_config or not eth_config:
            print("❌ Missing BTC or ETH config!")
            return False
        
        # Initialize components
        data_fetcher = DataFetcher()
        strategy = AlertStrategy(config)
        print("✓ Components initialized")
        
        # Get coin IDs and fetch data
        coin_ids = [coin.get('coingecko_id') for coin in config.get('coins', [])]
        print(f"✓ Coin IDs: {coin_ids}")
        
        # Fetch coin data
        print("\nFetching coin data...")
        coin_data = data_fetcher.get_coin_market_data_batch(coin_ids)
        
        if not coin_data:
            print("❌ Failed to fetch coin data")
            return False
        
        print(f"✓ Fetched data for {len(coin_data)} coins")
        
        # Analyze coin_data content
        print("\n" + "="*60)
        print("COIN DATA ANALYSIS:")
        print("="*60)
        
        for coin_id, data in coin_data.items():
            print(f"\n{coin_id}:")
            print(f"  usd: {data.get('usd', 'MISSING')}")
            print(f"  usd_24h_change: {data.get('usd_24h_change', 'MISSING')}")
            print(f"  keys: {list(data.keys())}")
        
        # Now manually trace the portfolio calculation
        print("\n" + "="*60)
        print("MANUAL PORTFOLIO CALCULATION:")
        print("="*60)
        
        altcoin_value = 0
        btc_amount = 0
        eth_amount = 0
        btc_price = 0
        eth_price = 0
        
        print("\nStep 1: Processing each coin from config...")
        
        for coin_config in config.get('coins', []):
            coin_id = coin_config.get('coingecko_id')
            coin_name = coin_config.get('name')
            current_amount = coin_config.get('current_amount', 0)
            
            print(f"\nProcessing {coin_name} ({coin_id}):")
            print(f"  Current amount from config: {current_amount}")
            
            if coin_id in coin_data:
                coin_price = coin_data[coin_id].get('usd', 0)
                print(f"  Price from coin_data: ${coin_price}")
                
                if coin_name == 'BTC':
                    btc_amount = current_amount
                    btc_price = coin_price
                    print(f"  → Set BTC: amount={btc_amount}, price=${btc_price}")
                elif coin_name == 'ETH':
                    eth_amount = current_amount
                    eth_price = coin_price
                    print(f"  → Set ETH: amount={eth_amount}, price=${eth_price}")
                elif coin_name not in ['BTC', 'ETH']:
                    altcoin_contribution = current_amount * coin_price
                    altcoin_value += altcoin_contribution
                    print(f"  → Altcoin contribution: ${altcoin_contribution:,.2f}")
            else:
                print(f"  ❌ {coin_id} NOT FOUND in coin_data!")
        
        print(f"\nStep 2: Final values:")
        print(f"  BTC Amount: {btc_amount}")
        print(f"  BTC Price: ${btc_price:,.2f}")
        print(f"  ETH Amount: {eth_amount}")
        print(f"  ETH Price: ${eth_price:,.2f}")
        print(f"  Altcoin Value: ${altcoin_value:,.2f}")
        
        # Calculate goal value
        goal_btc = 1.0
        goal_eth = 10.0
        goal_value = (goal_btc * btc_price) + (goal_eth * eth_price)
        
        print(f"\nStep 3: Goal calculation:")
        print(f"  Goal: {goal_btc} BTC + {goal_eth} ETH")
        print(f"  Goal Value: (1 * ${btc_price:,.2f}) + (10 * ${eth_price:,.2f}) = ${goal_value:,.2f}")
        
        # Calculate current total value
        btc_value = btc_amount * btc_price
        eth_value = eth_amount * eth_price
        current_total_value = altcoin_value + btc_value + eth_value
        
        print(f"\nStep 4: Current portfolio calculation:")
        print(f"  BTC Value: {btc_amount} * ${btc_price:,.2f} = ${btc_value:,.2f}")
        print(f"  ETH Value: {eth_amount} * ${eth_price:,.2f} = ${eth_value:,.2f}")
        print(f"  Altcoin Value: ${altcoin_value:,.2f}")
        print(f"  Total Current Value: ${current_total_value:,.2f}")
        
        # Calculate progress
        progress_percentage = 0
        if goal_value > 0:
            progress_percentage = (current_total_value / goal_value) * 100
        
        print(f"\nStep 5: Progress calculation:")
        print(f"  Progress: (${current_total_value:,.2f} / ${goal_value:,.2f}) * 100 = {progress_percentage:.2f}%")
        
        # Calculate BTC equivalent
        current_portfolio_btc = 0
        if btc_price > 0:
            current_portfolio_btc = current_total_value / btc_price
        
        print(f"  BTC Equivalent: ${current_total_value:,.2f} / ${btc_price:,.2f} = {current_portfolio_btc:.4f} BTC")
        
        # Now compare with strategy.get_market_summary
        print("\n" + "="*60)
        print("STRATEGY.GET_MARKET_SUMMARY COMPARISON:")
        print("="*60)
        
        # Create mock market data
        market_data = {
            'btc_dominance': 59.33,
            'fear_greed_index': {
                'value': 72,
                'value_classification': 'Greed'
            },
            'eth_btc_ratio': 0.0320
        }
        
        summary = strategy.get_market_summary(coin_data, market_data)
        portfolio = summary.get('portfolio_analysis', {})
        
        print(f"Strategy Result:")
        print(f"  Altcoin Value: ${portfolio.get('altcoin_value', 0):,.2f}")
        print(f"  Goal Value: ${portfolio.get('goal_value', 0):,.2f}")
        print(f"  BTC Equivalent: {portfolio.get('btc_equivalent', 0):.4f} BTC")
        print(f"  Progress: {portfolio.get('progress_percentage', 0):.2f}%")
        print(f"  BTC Amount: {portfolio.get('btc_amount', 0)}")
        print(f"  ETH Amount: {portfolio.get('eth_amount', 0)}")
        print(f"  BTC Price: ${portfolio.get('btc_price', 0):,.2f}")
        print(f"  ETH Price: ${portfolio.get('eth_price', 0):,.2f}")
        
        # Check for discrepancies
        print(f"\nDiscrepancy Check:")
        print(f"  Manual vs Strategy Altcoin Value: ${altcoin_value:,.2f} vs ${portfolio.get('altcoin_value', 0):,.2f}")
        print(f"  Manual vs Strategy Progress: {progress_percentage:.2f}% vs {portfolio.get('progress_percentage', 0):.2f}%")
        print(f"  Manual vs Strategy BTC Equivalent: {current_portfolio_btc:.4f} vs {portfolio.get('btc_equivalent', 0):.4f}")
        
        print("\n✓ Debug completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_portfolio_calculation())
    sys.exit(0 if success else 1)