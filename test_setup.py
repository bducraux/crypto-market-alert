#!/usr/bin/env python3
"""
Quick test script to verify the system configuration
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.utils import load_config, load_environment, get_env_variable
    from src.data_fetcher import DataFetcher
    from src.alerts import TelegramAlertsManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


async def test_system():
    """Test system configuration and connections"""
    print("🧪 Testing Crypto Market Alert System...")
    
    # Test 1: Load configuration
    print("\n1️⃣ Testing configuration...")
    try:
        config = load_config()
        print("✅ Configuration loaded successfully")
        
        # Validate required sections
        required_sections = ['coins', 'indicators', 'general']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required configuration section: {section}")
                return False
        
        print(f"✅ Found {len(config['coins'])} coins configured")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test 2: Load environment variables
    print("\n2️⃣ Testing environment variables...")
    try:
        load_environment()
        
        # Test Telegram configuration
        try:
            bot_token = get_env_variable('TELEGRAM_BOT_TOKEN')
            chat_id = get_env_variable('TELEGRAM_CHAT_ID')
            print("✅ Telegram configuration found")
        except ValueError as e:
            print(f"❌ Missing Telegram configuration: {e}")
            print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
            return False
        
        # Test optional CoinGecko API key
        try:
            api_key = get_env_variable('COINGECKO_API_KEY', None)
            if api_key:
                print("✅ CoinGecko API key found")
            else:
                print("ℹ️ No CoinGecko API key (using free tier)")
        except:
            print("ℹ️ No CoinGecko API key (using free tier)")
            
    except Exception as e:
        print(f"❌ Environment error: {e}")
        return False
    
    # Test 3: CoinGecko API connection
    print("\n3️⃣ Testing CoinGecko API...")
    try:
        api_key = get_env_variable('COINGECKO_API_KEY', None)
        data_fetcher = DataFetcher(api_key=api_key)
        
        # Test basic API call
        btc_price = data_fetcher.get_coin_price('bitcoin')
        if btc_price:
            print(f"✅ CoinGecko API working (BTC: ${btc_price:,.2f})")
        else:
            print("❌ CoinGecko API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ CoinGecko API error: {e}")
        return False
    
    # Test 4: Telegram bot connection
    print("\n4️⃣ Testing Telegram bot...")
    try:
        bot_token = get_env_variable('TELEGRAM_BOT_TOKEN')
        chat_id = get_env_variable('TELEGRAM_CHAT_ID')
        
        telegram_manager = TelegramAlertsManager(bot_token, chat_id)
        connection_ok = await telegram_manager.test_connection()
        
        if connection_ok:
            print("✅ Telegram bot connection successful")
            
            # Send test message
            test_sent = await telegram_manager.send_message(
                "🧪 <b>Test Message</b>\n\nCrypto Market Alert System test successful!"
            )
            if test_sent:
                print("✅ Test message sent to Telegram")
            else:
                print("⚠️ Telegram connection works but failed to send test message")
        else:
            print("❌ Telegram bot connection failed")
            print("Please check your bot token and chat ID")
            return False
            
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False
    
    # Test 5: Technical indicators
    print("\n5️⃣ Testing technical indicators...")
    try:
        from src.indicators import TechnicalIndicators
        import pandas as pd
        import numpy as np
        
        indicators = TechnicalIndicators()
        
        # Create test data
        test_data = pd.DataFrame({
            'close': np.random.uniform(40000, 50000, 100),
            'high': np.random.uniform(40000, 50000, 100),
            'low': np.random.uniform(40000, 50000, 100),
            'open': np.random.uniform(40000, 50000, 100),
        })
        
        # Test RSI calculation
        rsi = indicators.calculate_rsi(test_data)
        if rsi is not None and not rsi.empty:
            print("✅ RSI calculation working")
        else:
            print("❌ RSI calculation failed")
            return False
        
        # Test MACD calculation
        macd = indicators.calculate_macd(test_data)
        if macd and 'macd' in macd:
            print("✅ MACD calculation working")
        else:
            print("❌ MACD calculation failed")
            return False
            
        print("✅ Technical indicators working")
        
    except Exception as e:
        print(f"❌ Technical indicators error: {e}")
        return False
    
    print("\n🎉 All tests passed! System is ready to run.")
    print("\n🚀 To start monitoring:")
    print("   python run.py --once    # Single check")
    print("   python run.py           # Continuous monitoring")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_system())
    if not success:
        print("\n❌ Some tests failed. Please check your configuration.")
        sys.exit(1)
