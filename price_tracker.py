#!/usr/bin/env python3
"""
Price Tracker Service
Runs in background and records coin prices every hour for historical tracking
"""

import sys
import time
import logging
import schedule
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from main import CryptoMarketAlertSystem
from src.price_history import PriceHistoryTracker
from src.utils import load_environment


class PriceTrackerService:
    """Service that tracks coin prices hourly"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the price tracker service"""
        # Load environment
        load_environment()
        
        # Initialize alert system (for data fetching)
        self.alert_system = CryptoMarketAlertSystem(config_path)
        self.alert_system.initialize_components()
        
        # Initialize price tracker
        self.price_tracker = PriceHistoryTracker()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("Price Tracker Service initialized")
    
    def track_prices(self):
        """Track current prices for all configured coins"""
        try:
            self.logger.info("Starting price tracking cycle...")
            
            # Fetch current coin data
            coin_data = self.alert_system.collect_coin_data()
            
            if not coin_data:
                self.logger.warning("Failed to fetch coin data")
                return
            
            # Record prices
            count = self.price_tracker.bulk_record_prices(coin_data)
            
            self.logger.info(f"✅ Tracked {count} coin prices at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Log some stats
            stats = self.price_tracker.get_stats()
            self.logger.info(f"Total coins tracked: {stats['total_coins']}, Total data points: {stats['total_data_points']}")
            
        except Exception as e:
            self.logger.error(f"Error tracking prices: {e}")
    
    def run(self):
        """Run the price tracker service"""
        self.logger.info("🚀 Starting Price Tracker Service")
        self.logger.info("📊 Will track prices every hour")
        
        # Track prices immediately on startup
        self.logger.info("Running initial price tracking...")
        self.track_prices()
        
        # Schedule hourly tracking
        schedule.every().hour.at(":00").do(self.track_prices)
        
        self.logger.info("⏰ Scheduler started. Prices will be tracked every hour.")
        self.logger.info("Press Ctrl+C to stop.")
        
        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("\n👋 Price Tracker Service stopped by user")


def main():
    """Main entry point"""
    try:
        service = PriceTrackerService()
        service.run()
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
        return 0
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

