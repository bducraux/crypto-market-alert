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
  python run.py --dry-run          # Generate sample Telegram message
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
        '--dry-run',
        action='store_true',
        help='Generate and display sample Telegram message without sending'
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
                
                # Show portfolio valuation
                if test_success:
                    print("\n💰 Portfolio Valuation Report:")
                    from src.portfolio_utils import PortfolioAnalyzer
                    coin_data = alert_system.collect_coin_data()
                    analyzer = PortfolioAnalyzer(alert_system)
                    portfolio_data = analyzer.generate_portfolio_report(coin_data, "detailed")
                    portfolio_text = analyzer.format_for_test(portfolio_data)
                    print(portfolio_text)
                    
                if test_success:
                    print("\n✅ All tests passed! System ready to run.")
                    return 0
                else:
                    print("\n❌ Connection tests failed.")
                    return 1
            else:
                print("❌ Configuration test failed.")
                return 1
        
        elif args.dry_run:
            print("🧪 Generating sample Telegram message...")
            success = alert_system.initialize_components()
            if success:
                test_success = await test_connections(alert_system)
                if test_success:
                    print("\n📱 Sample Telegram Message:")
                    print("=" * 60)
                    
                    # Generate sample message
                    coin_data = alert_system.collect_coin_data()
                    market_data = alert_system.collect_market_data()
                    
                    # Generate strategic report message
                    strategic_report = alert_system.strategy.strategic_advisor.generate_strategic_report()
                    
                    print(strategic_report)
                    print("=" * 60)
                    print("✅ Sample message generated successfully!")
                    return 0
                else:
                    print("\n❌ Connection tests failed.")
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
    """Test all system connections with enhanced validation"""
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
        
        # Test Binance API first (primary source)
        print("🔶 Testing Binance API...")
        binance_btc = alert_system.data_fetcher.get_binance_price('BTCUSDT')
        if binance_btc and 'price' in binance_btc:
            binance_price = float(binance_btc['price']) if isinstance(binance_btc['price'], str) else binance_btc['price']
            print(f"✅ Binance API working (BTC: ${binance_price:,.2f})")
            binance_working = True
        else:
            print("❌ Binance API failed")
            binance_working = False
        
        # Test historical data from Binance
        print("📈 Testing Binance historical data...")
        try:
            historical_data = alert_system.data_fetcher.get_historical_data('BTCUSDT', limit=100)
            if historical_data is not None and len(historical_data) > 50:
                print(f"✅ Binance historical data working ({len(historical_data)} periods)")
                historical_working = True
            else:
                print("⚠️ Binance historical data limited")
                historical_working = False
        except Exception as e:
            print(f"❌ Binance historical data failed: {e}")
            historical_working = False
        
        # Test CoinGecko API (fallback and market metrics)
        print("🌐 Testing CoinGecko API...")
        test_data = alert_system.data_fetcher.get_coin_market_data_batch(['bitcoin'])
        if test_data and 'bitcoin' in test_data:
            btc_price = test_data['bitcoin'].get('usd', 0)
            print(f"✅ CoinGecko API working (BTC: ${btc_price:,.2f})")
            coingecko_working = True
        else:
            print("❌ CoinGecko API failed")
            coingecko_working = False
        
        # Test CoinMarketCap API (backup for market metrics)
        print("🪙 Testing CoinMarketCap API...")
        try:
            if hasattr(alert_system.data_fetcher, 'coinmarketcap') and alert_system.data_fetcher.coinmarketcap:
                cmc_data = alert_system.data_fetcher._make_coinmarketcap_request("global-metrics/quotes/latest")
                if cmc_data and 'data' in cmc_data:
                    btc_dominance = cmc_data['data'].get('btc_dominance', 0)
                    print(f"✅ CoinMarketCap API working (BTC Dominance: {btc_dominance:.2f}%)")
                    cmc_working = True
                else:
                    print("❌ CoinMarketCap API failed")
                    cmc_working = False
            else:
                print("⚠️ CoinMarketCap API not configured")
                cmc_working = False
        except Exception as e:
            print(f"❌ CoinMarketCap API error: {e}")
            cmc_working = False
        
        # Test overall data fetcher functionality
        print("🔄 Testing hybrid data fetcher...")
        connection_status = alert_system.data_fetcher.test_connection()
        print(f"📊 Connection status: {connection_status}")
        
        # Evaluate overall system readiness
        critical_systems = binance_working and telegram_ok and historical_working
        fallback_available = coingecko_working or cmc_working
        
        if critical_systems and fallback_available:
            print("✅ System fully operational (Primary + Fallback APIs)")
            return True
        elif critical_systems:
            print("⚠️ System operational (Primary APIs only - limited market metrics)")
            return True
        elif binance_working and telegram_ok:
            print("⚠️ System degraded (Basic price alerts only)")
            return True
        else:
            print("❌ System not ready (Critical components failed)")
            return False
        
    except Exception as e:
        print(f"❌ Connection test error: {e}")
        return False


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
