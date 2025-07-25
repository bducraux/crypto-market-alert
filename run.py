#!/usr/bin/env python3
"""
Run script for the crypto market alert system
Provides easy command-line interface for running the system
"""

import sys
import argparse
import asyncio
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import CryptoMarketAlertSystem


async def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Crypto Market Alert System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run continuous monitoring
  python run.py --once             # Run single check
  python run.py --config custom.yaml  # Use custom config file
  python run.py --test             # Test configuration and connections
        """
    )
    
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run a single market check instead of continuous monitoring'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test configuration and API connections without running alerts'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        # Create alert system
        alert_system = CryptoMarketAlertSystem(args.config)
        
        if args.test:
            print("🧪 Testing configuration and connections...")
            success = alert_system.initialize_components()
            if success:
                # Test API connections
                test_success = await test_connections(alert_system)
                if test_success:
                    print("✅ All tests passed! System ready to run.")
                    return 0
                else:
                    print("❌ Connection tests failed.")
                    return 1
            else:
                print("❌ Configuration test failed.")
                return 1
        
        elif args.once:
            print("📊 Running single market check...")
            alerts_count = await alert_system.run_once()
            print(f"✅ Completed. Generated {alerts_count} alerts.")
            return 0
        
        else:
            print("🚀 Starting continuous monitoring...")
            print("Press Ctrl+C to stop.")
            await alert_system.run_continuous()
            return 0
            
    except KeyboardInterrupt:
        print("\n👋 Shutdown requested by user")
        return 0
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1


async def test_connections(alert_system):
    """Test all system connections"""
    try:
        # Initialize components
        if not alert_system.initialize_components():
            return False
        
        # Test Telegram connection
        print("📱 Testing Telegram connection...")
        telegram_ok = await alert_system.alerts_orchestrator.telegram.test_connection()
        if telegram_ok:
            print("✅ Telegram connection successful")
        else:
            print("❌ Telegram connection failed")
            return False
        
        # Test CoinGecko API
        print("🌐 Testing CoinGecko API...")
        test_data = alert_system.data_fetcher.get_coin_market_data_batch(['bitcoin'])
        if test_data and 'bitcoin' in test_data:
            btc_price = test_data['bitcoin'].get('usd', 0)
            print(f"✅ CoinGecko API working (BTC: ${btc_price:,.2f})")
        else:
            print("❌ CoinGecko API failed")
            return False
        
        # Test Binance API
        print("🔶 Testing Binance API...")
        binance_btc = alert_system.data_fetcher.get_binance_price('BTCUSDT')
        if binance_btc and 'price' in binance_btc:
            binance_price = float(binance_btc['price'])
            print(f"✅ Binance API working (BTC: ${binance_price:,.2f})")
        else:
            print("❌ Binance API failed")
            return False
        
        # Test overall data fetcher functionality
        print("🔄 Testing hybrid data fetcher...")
        connection_status = alert_system.data_fetcher.test_connection()
        binance_ok = connection_status.get('binance', False)
        coingecko_ok = connection_status.get('coingecko', False)
        
        if binance_ok and coingecko_ok:
            print("✅ Hybrid data fetcher working (Both APIs)")
        elif coingecko_ok:
            print("⚠️ Hybrid data fetcher working (CoinGecko only)")
        elif binance_ok:
            print("⚠️ Hybrid data fetcher working (Binance only)")
        else:
            print("❌ Hybrid data fetcher failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
