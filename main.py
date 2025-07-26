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
        Initialize all system components
        
        Returns:
            True if initialization successful
        """
        try:
            # Initialize data fetcher
            # API key is no longer needed for Binance, but keep for CoinGecko metrics
            api_key = get_env_variable('COINGECKO_API_KEY', None)
            general_config = self.config.get('general', {})
            
            # Use data fetcher for better reliability and performance
            self.data_fetcher = DataFetcher(
                retry_attempts=general_config.get('retry_attempts', 3),
                retry_delay=general_config.get('retry_delay', 2)
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
            eth_btc_ratio = self.data_fetcher.get_eth_btc_ratio()
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
        Collect data for all configured coins
        
        Returns:
            Dictionary containing coin data
        """
        coin_ids = [coin['coingecko_id'] for coin in self.config.get('coins', [])]
        
        if not coin_ids:
            self.logger.warning("No coins configured for monitoring")
            return {}
        
        try:
            # Get market data for all coins
            coin_data = self.data_fetcher.get_coin_market_data_batch(coin_ids)
            
            self.logger.info(f"Collected data for {len(coin_data)} coins")
            
            # Log current prices
            for coin_id, data in coin_data.items():
                price = data.get('usd')
                change_24h = data.get('usd_24h_change')
                if price:
                    change_text = f" ({change_24h:+.2f}%)" if change_24h else ""
                    self.logger.debug(f"{coin_id}: ${price:,.2f}{change_text}")
            
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


async def main():
    """Main entry point"""
    # Check command line arguments
    run_once = '--once' in sys.argv
    config_path = "config/config.yaml"
    
    # Check for custom config path
    for i, arg in enumerate(sys.argv):
        if arg == '--config' and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 1]
    
    try:
        # Create and run the alert system
        alert_system = CryptoMarketAlertSystem(config_path)
        
        if run_once:
            print("Running single market check...")
            alerts_count = await alert_system.run_once()
            print(f"Generated {alerts_count} alerts")
        else:
            print("Starting continuous monitoring...")
            await alert_system.run_continuous()
            
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
