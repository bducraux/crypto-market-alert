#!/usr/bin/env python3
"""
Debug script to simulate the exact alert sending process
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import load_config, load_environment
from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy
from src.alerts import TelegramAlertsManager, AlertsOrchestrator

async def debug_alert_sending():
    """Debug the exact alert sending process"""
    print("Debugging alert sending process...")
    
    try:
        # Load environment and configuration (like main.py does)
        load_environment()
        config = load_config("config/config.yaml")
        print("✓ Configuration and environment loaded")
        
        # Initialize components exactly like main.py
        data_fetcher = DataFetcher()
        strategy = AlertStrategy(config)
        print("✓ Components initialized")
        
        # Simulate the collect_market_data method from main.py
        print("\nCollecting market data (like main.py)...")
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
                print(f"Fear & Greed Index: {fear_greed['value']}/100")
            
        except Exception as e:
            print(f"Error collecting market data: {e}")
        
        # Simulate the collect_coin_data method from main.py
        print("\nCollecting coin data (like main.py)...")
        coin_ids = [coin['coingecko_id'] for coin in config.get('coins', [])]
        
        if not coin_ids:
            print("No coins configured for monitoring")
            return False
        
        try:
            # Get market data for all coins
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
        
        # Generate market summary (like main.py does)
        print("\nGenerating market summary...")
        summary = strategy.get_market_summary(coin_data, market_data)
        
        # Print portfolio analysis
        portfolio = summary.get('portfolio_analysis', {})
        print("\nPortfolio Analysis:")
        print(f"Altcoin Value: ${portfolio.get('altcoin_value', 0):,.2f}")
        print(f"Goal Value: ${portfolio.get('goal_value', 0):,.2f}")
        print(f"BTC Equivalent: {portfolio.get('btc_equivalent', 0):.4f} BTC")
        print(f"Progress: {portfolio.get('progress_percentage', 0):.2f}%")
        print(f"Current BTC: {portfolio.get('btc_amount', 0):.8f}")
        print(f"Current ETH: {portfolio.get('eth_amount', 0):.8f}")
        print(f"BTC Price: ${portfolio.get('btc_price', 0):,.2f}")
        print(f"ETH Price: ${portfolio.get('eth_price', 0):,.2f}")
        
        # Show the structured report
        print("\n" + "="*60)
        print("STRUCTURED REPORT:")
        print("="*60)
        print(summary.get('structured_report', 'No structured report found'))
        
        # Now simulate the alert sending process
        print("\n" + "="*60)
        print("SIMULATING ALERT SENDING PROCESS:")
        print("="*60)
        
        # Initialize Telegram manager (but don't actually send)
        try:
            from src.utils import get_env_variable
            bot_token = get_env_variable('TELEGRAM_BOT_TOKEN')
            chat_id = get_env_variable('TELEGRAM_CHAT_ID')
            
            telegram_manager = TelegramAlertsManager(bot_token, chat_id)
            alerts_orchestrator = AlertsOrchestrator(telegram_manager)
            
            # Format the message that would be sent
            formatted_message = telegram_manager.format_summary_message(summary, 0)
            
            print("Message that would be sent:")
            print("-" * 40)
            print(formatted_message)
            print("-" * 40)
            
        except Exception as e:
            print(f"Error simulating alert sending: {e}")
            
            # Try to format the message manually
            structured_report = summary.get('structured_report')
            if structured_report:
                from datetime import datetime
                timestamp = summary.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
                message = f"📊 Market Summary - {timestamp}\n\n"
                message += f"{structured_report}\n\n"
                message += f"🚨 Active Alerts: 0\n"
                
                print("Manual formatted message:")
                print("-" * 40)
                print(message)
                print("-" * 40)
        
        print("\n✓ Debug completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(debug_alert_sending())
    sys.exit(0 if success else 1)