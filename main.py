"""
Main execution script for the crypto market alert system
Coordinates data fetching, analysis, and alert generation
"""

import asyncio
import logging
import sys
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.utils import load_config, setup_logging, load_environment, get_env_variable, validate_config
from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy
from src.alerts import TelegramAlertsManager, AlertsOrchestrator


class CryptoMarketAlertSystem:
    """Main coordinator for the crypto market alert system"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the crypto market alert system
        
        Args:
            config_path: Path to configuration file
        """
        # Load environment variables
        load_environment()
        
        # Load and validate configuration
        self.config = load_config(config_path)
        validate_config(self.config)
        
        # Set up logging
        self.logger = setup_logging(self.config)
        
        # Initialize components
        self.data_fetcher = None
        self.strategy = None
        self.alerts_orchestrator = None
        
        # Runtime state
        self.last_check_time = None
        self.error_count = 0
        self.max_errors = 5
        
        self.logger.info("Crypto Market Alert System initialized")
    
    def initialize_components(self) -> bool:
        """
        Initialize all system components with enhanced configuration
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize data fetcher with configuration
            # API key is no longer needed for Binance, but keep for CoinGecko metrics
            api_key = get_env_variable('COINGECKO_API_KEY', None)
            general_config = self.config.get('general', {})
            
            # Use data fetcher for better reliability and performance
            self.data_fetcher = DataFetcher(
                retry_attempts=general_config.get('retry_attempts', 3),
                retry_delay=general_config.get('retry_delay', 2),
                config=self.config  # Pass full config for enhanced settings
            )
            
            # Initialize strategy
            self.strategy = AlertStrategy(self.config)
            
            # Initialize Telegram alerts
            bot_token = get_env_variable('TELEGRAM_BOT_TOKEN')
            chat_id = get_env_variable('TELEGRAM_CHAT_ID')
            
            telegram_manager = TelegramAlertsManager(bot_token, chat_id)
            self.alerts_orchestrator = AlertsOrchestrator(telegram_manager)
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            return False
    
    def collect_market_data(self) -> Dict[str, Any]:
        """
        Collect all required market data
        
        Returns:
            Dictionary containing market data
        """
        market_data = {}
        
        try:
            # Get BTC dominance
            btc_dominance = self.data_fetcher.get_btc_dominance()
            if btc_dominance:
                market_data['btc_dominance'] = btc_dominance
                self.logger.debug(f"BTC Dominance: {btc_dominance:.2f}%")
            
            # Get ETH/BTC ratio
            eth_btc_ratio = self.data_fetcher.get_eth_btc_ratio(self.config.get('coins', []))
            if eth_btc_ratio:
                market_data['eth_btc_ratio'] = eth_btc_ratio
                self.logger.debug(f"ETH/BTC Ratio: {eth_btc_ratio:.6f}")
            
            # Get Fear & Greed Index
            fear_greed = self.data_fetcher.get_fear_greed_index()
            if fear_greed:
                market_data['fear_greed_index'] = fear_greed
                self.logger.debug(f"Fear & Greed Index: {fear_greed['value']}/100")
            
        except Exception as e:
            self.logger.error(f"Error collecting market data: {e}")
        
        return market_data
    
    def collect_coin_data(self) -> Dict[str, Any]:
        """
        Collect data for all configured coins with enhanced validation
        
        Returns:
            Dictionary containing coin data with quality checks
        """
        coin_ids = [coin['coingecko_id'] for coin in self.config.get('coins', [])]
        
        if not coin_ids:
            self.logger.warning("No coins configured for monitoring")
            return {}
        
        try:
            # Get market data for all coins using optimized Binance-first approach
            coin_data = self.data_fetcher.get_coin_market_data_batch(coin_ids, self.config.get('coins', []))
            
            # Validate data quality
            valid_coins = 0
            for coin_id, data in coin_data.items():
                price = data.get('usd')
                if price and price > 0:
                    valid_coins += 1
                    # Log current prices with data source info
                    change_24h = data.get('usd_24h_change')
                    source = data.get('source', 'unknown')
                    change_text = f" ({change_24h:+.2f}%)" if change_24h else ""
                    self.logger.debug(f"{coin_id}: ${price:,.4f}{change_text} [{source}]")
                else:
                    self.logger.warning(f"Invalid price data for {coin_id}: {price}")
            
            success_rate = (valid_coins / len(coin_ids)) * 100 if coin_ids else 0
            self.logger.info(f"Collected valid data for {valid_coins}/{len(coin_ids)} coins ({success_rate:.1f}% success)")
            
            # Alert if success rate is too low
            if success_rate < 80:
                self.logger.warning(f"Low data success rate: {success_rate:.1f}% - API issues detected")
            
            return coin_data
            
        except Exception as e:
            self.logger.error(f"Error collecting coin data: {e}")
            return {}
    
    async def run_single_check(self) -> int:
        """
        Run a single market check cycle
        
        Returns:
            Number of alerts generated
        """
        self.logger.info("Starting market check cycle")
        start_time = time.time()
        
        try:
            # Collect market data
            market_data = self.collect_market_data()
            coin_data = self.collect_coin_data()
            
            if not coin_data:
                self.logger.warning("No coin data available, skipping alert evaluation")
                return 0
            
            # Evaluate alerts
            alerts = self.strategy.evaluate_all_alerts(coin_data, market_data)
            
            # Send alerts if any
            if alerts:
                self.logger.info(f"Generated {len(alerts)} alerts")
                results = await self.alerts_orchestrator.send_alerts(alerts)
                self.logger.info(f"Sent {results['telegram_sent']} Telegram alerts")
            else:
                self.logger.info("No alerts triggered")
            
            # Generate market summary
            summary = self.strategy.get_market_summary(coin_data, market_data)
            
            # Reset error count on successful run
            self.error_count = 0
            self.last_check_time = datetime.now()
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Market check completed in {elapsed_time:.2f} seconds")
            
            return len(alerts)
            
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Error in market check cycle: {e}")
            
            # Send error notification if too many errors
            if self.error_count >= self.max_errors:
                try:
                    await self.alerts_orchestrator.telegram.send_error_message(
                        "Repeated Errors",
                        f"Market check failed {self.error_count} times. Last error: {str(e)}"
                    )
                except:
                    pass  # Don't fail if error notification fails
            
            return 0
    
    async def send_daily_summary(self) -> None:
        """Send daily market summary"""
        try:
            market_data = self.collect_market_data()
            coin_data = self.collect_coin_data()
            
            if coin_data:
                summary = self.strategy.get_market_summary(coin_data, market_data)
                await self.alerts_orchestrator.send_periodic_summary(summary, [])
                self.logger.info("Daily summary sent")
        except Exception as e:
            self.logger.error(f"Failed to send daily summary: {e}")
    
    async def run_continuous(self) -> None:
        """
        Run the alert system continuously
        """
        # Initialize components
        if not self.initialize_components():
            self.logger.error("Failed to initialize components, exiting")
            return
        
        # Initialize alert system
        if not await self.alerts_orchestrator.initialize():
            self.logger.error("Failed to initialize alert system, exiting")
            return
        
        check_interval = self.config.get('general', {}).get('check_interval', 300)
        self.logger.info(f"Starting continuous monitoring (check interval: {check_interval}s)")
        
        last_daily_summary = datetime.now().date()
        
        while True:
            try:
                # Run market check
                alerts_count = await self.run_single_check()
                
                # Send daily summary if it's a new day
                current_date = datetime.now().date()
                if current_date > last_daily_summary:
                    await self.send_daily_summary()
                    last_daily_summary = current_date
                
                # Wait for next check
                self.logger.debug(f"Waiting {check_interval} seconds until next check")
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def run_once(self) -> int:
        """
        Run the alert system once (for testing)
        
        Returns:
            Number of alerts generated
        """
        # Initialize components
        if not self.initialize_components():
            self.logger.error("Failed to initialize components")
            return 0
        
        # Run single check
        alerts_count = await self.run_single_check()
        
        return alerts_count


async def test_data_quality(alert_system):
    """Test data quality and provide detailed reporting"""
    try:
        # Test market data collection
        market_data = alert_system.collect_market_data()
        print(f"📈 Market data: {len(market_data)} metrics collected")
        
        # Test coin data collection with detailed analysis
        print("🪙 Testing coin data collection...")
        coin_data = alert_system.collect_coin_data()
        
        # Analyze data quality by coin
        insufficient_data_coins = []
        sufficient_data_coins = []
        
        for coin_config in alert_system.config.get('coins', []):
            coin_id = coin_config.get('coingecko_id')
            coin_name = coin_config.get('name', coin_id)
            
            if coin_id in coin_data:
                coin_info = coin_data[coin_id]
                historical = coin_info.get('historical')
                
                if historical is not None:
                    periods = len(historical)
                    if periods < 350:
                        insufficient_data_coins.append({
                            'name': coin_name,
                            'id': coin_id,
                            'periods': periods,
                            'binance_symbol': coin_config.get('binance_id', 'N/A')
                        })
                    else:
                        sufficient_data_coins.append({
                            'name': coin_name,
                            'periods': periods
                        })
                else:
                    insufficient_data_coins.append({
                        'name': coin_name,
                        'id': coin_id,
                        'periods': 0,
                        'binance_symbol': coin_config.get('binance_id', 'N/A')
                    })
        
        # Report results
        print(f"\n📊 Data Quality Report:")
        print(f"✅ Coins with sufficient data (350+ periods): {len(sufficient_data_coins)}")
        for coin in sufficient_data_coins:
            print(f"   • {coin['name']}: {coin['periods']} periods")
        
        if insufficient_data_coins:
            print(f"\n⚠️ Coins with insufficient data: {len(insufficient_data_coins)}")
            for coin in insufficient_data_coins:
                periods = coin['periods']
                symbol = coin.get('binance_symbol', 'N/A')
                print(f"   • {coin['name']} ({symbol}): {periods} periods (need 350)")
                
            print(f"\n💡 Recommendations for coins with insufficient data:")
            print(f"   • These are likely newer tokens with limited trading history")
            print(f"   • Basic indicators (RSI, MACD) will work with fewer periods")
            print(f"   • Advanced indicators (Pi Cycle Top) require more data")
            print(f"   • Consider using 4h or 1h intervals for more data points")
        
        # Test a single check to ensure everything works
        print(f"\n🔄 Running single market check to test full pipeline...")
        alerts_count = await alert_system.run_single_check()
        print(f"✅ Market check completed. Generated {alerts_count} alerts")
        
        # Portfolio Valuation Report
        print(f"\n💰 Portfolio Valuation Report:")
        from src.portfolio_utils import PortfolioAnalyzer
        analyzer = PortfolioAnalyzer(alert_system)
        portfolio_data = analyzer.generate_portfolio_report(coin_data, "detailed")
        portfolio_text = analyzer.format_for_test(portfolio_data)
        print(portfolio_text)
        
        print(f"\n🎯 System Status: Ready for operation")
        print(f"   • Total coins monitored: {len(coin_data)}")
        print(f"   • Coins with full indicator support: {len(sufficient_data_coins)}")
        print(f"   • Coins with basic indicator support: {len(insufficient_data_coins)}")
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Enhanced main entry point with basic CLI support
    import argparse
    
    parser = argparse.ArgumentParser(description="Crypto Market Alert System")
    parser.add_argument('--test', action='store_true', help='Test system components')
    parser.add_argument('--once', action='store_true', help='Run single check')
    parser.add_argument('--config', default='config/config.yaml', help='Config file path')
    
    args = parser.parse_args()
    
    if '--test' in sys.argv or args.test:
        print("🧪 Testing Crypto Market Alert System...")
        alert_system = CryptoMarketAlertSystem(args.config)
        
        # Test initialization
        print("📋 Testing component initialization...")
        success = alert_system.initialize_components()
        if success:
            print("✅ Components initialized successfully")
        else:
            print("❌ Component initialization failed")
            sys.exit(1)
        
        # Test data fetching with validation
        print("📊 Testing data fetching and validation...")
        asyncio.run(test_data_quality(alert_system))
        
    elif '--once' in sys.argv or args.once:
        # Single run
        alert_system = CryptoMarketAlertSystem(args.config)
        alerts_count = asyncio.run(alert_system.run_once())
        print(f"Generated {alerts_count} alerts")
        
    else:
        # This file should be run via run.py for better CLI interface
        print("⚠️ Please use 'python run.py' for the complete CLI interface")
        print("   This provides better argument parsing and testing capabilities")
        
        # Basic fallback execution
        alert_system = CryptoMarketAlertSystem(args.config)
        asyncio.run(alert_system.run_once())
