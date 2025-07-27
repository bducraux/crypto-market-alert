#!/usr/bin/env python3
"""
Debug script to simulate the exact production flow that generates alerts
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config, load_environment, get_env_variable
from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy
from src.alerts import TelegramAlertsManager, AlertsOrchestrator

async def debug_production_flow():
    """Debug the exact production flow that generates alerts"""
    print("Debugging production alert flow...")
    
    try:
        # Load environment and configuration (exactly like main.py)
        load_environment()
        config = load_config("config/config.yaml")
        print("✓ Configuration and environment loaded")
        
        # Initialize components exactly like main.py
        data_fetcher = DataFetcher(
            retry_attempts=config.get('general', {}).get('retry_attempts', 3),
            retry_delay=config.get('general', {}).get('retry_delay', 2)
        )
        strategy = AlertStrategy(config)
        
        # Initialize Telegram (but don't send)
        bot_token = get_env_variable('TELEGRAM_BOT_TOKEN')
        chat_id = get_env_variable('TELEGRAM_CHAT_ID')
        telegram_manager = TelegramAlertsManager(bot_token, chat_id)
        alerts_orchestrator = AlertsOrchestrator(telegram_manager)
        
        print("✓ Components initialized exactly like main.py")
        
        # Simulate collect_market_data method from main.py
        print("\n" + "="*60)
        print("COLLECTING MARKET DATA (like main.py):")
        print("="*60)
        
        market_data = {}
        
        try:
            # Get BTC dominance
            btc_dominance = data_fetcher.get_btc_dominance()
            if btc_dominance:
                market_data['btc_dominance'] = btc_dominance
                print(f"BTC Dominance: {btc_dominance:.2f}%")
            
            # Get ETH/BTC ratio
            eth_btc_ratio = data_fetcher.get_eth_btc_ratio()
            if eth_btc_ratio:
                market_data['eth_btc_ratio'] = eth_btc_ratio
                print(f"ETH/BTC Ratio: {eth_btc_ratio:.6f}")
            
            # Get Fear & Greed Index
            fear_greed = data_fetcher.get_fear_greed_index()
            if fear_greed:
                market_data['fear_greed_index'] = fear_greed
                print(f"Fear & Greed Index: {fear_greed}")
            
        except Exception as e:
            print(f"Error collecting market data: {e}")
        
        # Simulate collect_coin_data method from main.py
        print("\n" + "="*60)
        print("COLLECTING COIN DATA (like main.py):")
        print("="*60)
        
        coin_ids = [coin['coingecko_id'] for coin in config.get('coins', [])]
        
        if not coin_ids:
            print("No coins configured for monitoring")
            return False
        
        try:
            # Get market data for all coins (exactly like main.py)
            coin_data = data_fetcher.get_coin_market_data_batch(coin_ids)
            print(f"Collected data for {len(coin_data)} coins")
            
            # Log current prices (like main.py does)
            for coin_id, data in coin_data.items():
                price = data.get('usd')
                change_24h = data.get('usd_24h_change')
                if price:
                    change_text = f" ({change_24h:+.2f}%)" if change_24h else ""
                    print(f"{coin_id}: ${price:,.2f}{change_text}")
            
        except Exception as e:
            print(f"Error collecting coin data: {e}")
            return False
        
        if not coin_data:
            print("No coin data available")
            return False
        
        # Generate market summary (exactly like main.py)
        print("\n" + "="*60)
        print("GENERATING MARKET SUMMARY (like main.py):")
        print("="*60)
        
        summary = strategy.get_market_summary(coin_data, market_data)
        
        # Print portfolio analysis
        portfolio = summary.get('portfolio_analysis', {})
        print(f"Portfolio Analysis from strategy.get_market_summary:")
        print(f"  Altcoin Value: ${portfolio.get('altcoin_value', 0):,.2f}")
        print(f"  Goal Value: ${portfolio.get('goal_value', 0):,.2f}")
        print(f"  BTC Equivalent: {portfolio.get('btc_equivalent', 0):.4f} BTC")
        print(f"  Progress: {portfolio.get('progress_percentage', 0):.2f}%")
        print(f"  BTC Amount: {portfolio.get('btc_amount', 0)}")
        print(f"  ETH Amount: {portfolio.get('eth_amount', 0)}")
        print(f"  BTC Price: ${portfolio.get('btc_price', 0):,.2f}")
        print(f"  ETH Price: ${portfolio.get('eth_price', 0):,.2f}")
        
        # Show the structured report that would be sent
        print("\n" + "="*60)
        print("STRUCTURED REPORT (what would be sent):")
        print("="*60)
        structured_report = summary.get('structured_report', 'No structured report found')
        print(structured_report)
        
        # Format the message exactly like it would be sent
        print("\n" + "="*60)
        print("TELEGRAM MESSAGE FORMAT:")
        print("="*60)
        
        formatted_message = telegram_manager.format_summary_message(summary, 0)
        print("Formatted message that would be sent:")
        print("-" * 40)
        print(formatted_message)
        print("-" * 40)
        
        # Let's also check if there are any alerts that might interfere
        print("\n" + "="*60)
        print("CHECKING FOR ALERTS:")
        print("="*60)
        
        alerts = strategy.evaluate_all_alerts(coin_data, market_data)
        print(f"Generated {len(alerts)} alerts")
        
        if alerts:
            for i, alert in enumerate(alerts):
                print(f"Alert {i+1}: {alert.get('message', 'No message')}")
        
        # Now let's check if there's any difference in the data when we call it again
        print("\n" + "="*60)
        print("SECOND DATA FETCH (checking for consistency):")
        print("="*60)
        
        coin_data_2 = data_fetcher.get_coin_market_data_batch(coin_ids)
        summary_2 = strategy.get_market_summary(coin_data_2, market_data)
        portfolio_2 = summary_2.get('portfolio_analysis', {})
        
        print(f"Second fetch results:")
        print(f"  Progress: {portfolio_2.get('progress_percentage', 0):.2f}%")
        print(f"  BTC Equivalent: {portfolio_2.get('btc_equivalent', 0):.4f} BTC")
        print(f"  Altcoin Value: ${portfolio_2.get('altcoin_value', 0):,.2f}")
        
        # Check for differences
        if abs(portfolio.get('progress_percentage', 0) - portfolio_2.get('progress_percentage', 0)) > 0.1:
            print("⚠️ INCONSISTENCY DETECTED between first and second fetch!")
        else:
            print("✓ Data is consistent between fetches")
        
        print("\n✓ Production flow debug completed!")
        return True
        
    except Exception as e:
        print(f"✗ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_production_flow())
    sys.exit(0 if success else 1)