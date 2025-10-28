"""
Price History Tracker
Tracks coin prices hourly for historical comparison and 24h change calculation
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PriceHistoryTracker:
    """Simple price history tracker using JSON files"""
    
    def __init__(self, storage_dir: str = "data/price_history"):
        """
        Initialize price history tracker
        
        Args:
            storage_dir: Directory to store price history files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def _get_history_file(self, coin_id: str) -> Path:
        """Get the history file path for a coin"""
        return self.storage_dir / f"{coin_id}.json"
    
    def record_price(self, coin_id: str, price: float, timestamp: Optional[datetime] = None):
        """
        Record a price for a coin
        
        Args:
            coin_id: CoinGecko ID of the coin
            price: Current price in USD
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        try:
            history_file = self._get_history_file(coin_id)
            
            # Load existing history
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []
            
            # Add new price entry
            entry = {
                'timestamp': timestamp.isoformat(),
                'price': price
            }
            history.append(entry)
            
            # Keep only last 30 days of data (720 hours)
            cutoff_time = timestamp - timedelta(days=30)
            history = [
                h for h in history 
                if datetime.fromisoformat(h['timestamp']) > cutoff_time
            ]
            
            # Save updated history
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            self.logger.debug(f"Recorded price for {coin_id}: ${price:.6f}")
            
        except Exception as e:
            self.logger.error(f"Error recording price for {coin_id}: {e}")
    
    def get_price_24h_ago(self, coin_id: str) -> Optional[float]:
        """
        Get the price from approximately 24 hours ago
        
        Args:
            coin_id: CoinGecko ID of the coin
            
        Returns:
            Price from 24h ago, or None if not available
        """
        try:
            history_file = self._get_history_file(coin_id)
            
            if not history_file.exists():
                return None
            
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                return None
            
            # Find price closest to 24 hours ago
            target_time = datetime.now() - timedelta(hours=24)
            
            # Find closest entry
            closest_entry = None
            min_diff = timedelta.max
            
            for entry in history:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                diff = abs(entry_time - target_time)
                
                if diff < min_diff:
                    min_diff = diff
                    closest_entry = entry
            
            if closest_entry and min_diff < timedelta(hours=2):  # Within 2 hours tolerance
                return closest_entry['price']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting 24h price for {coin_id}: {e}")
            return None
    
    def calculate_24h_change(self, coin_id: str, current_price: float) -> Optional[float]:
        """
        Calculate 24h price change percentage
        
        Args:
            coin_id: CoinGecko ID of the coin
            current_price: Current price in USD
            
        Returns:
            24h change percentage, or None if not enough data
        """
        price_24h_ago = self.get_price_24h_ago(coin_id)
        
        if price_24h_ago is None or price_24h_ago == 0:
            return None
        
        change_pct = ((current_price - price_24h_ago) / price_24h_ago) * 100
        return change_pct
    
    def get_history(self, coin_id: str, hours: int = 24) -> List[Dict]:
        """
        Get price history for a coin
        
        Args:
            coin_id: CoinGecko ID of the coin
            hours: Number of hours of history to retrieve
            
        Returns:
            List of price entries with timestamp and price
        """
        try:
            history_file = self._get_history_file(coin_id)
            
            if not history_file.exists():
                return []
            
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter by time range
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_history = [
                h for h in history
                if datetime.fromisoformat(h['timestamp']) > cutoff_time
            ]
            
            return filtered_history
            
        except Exception as e:
            self.logger.error(f"Error getting history for {coin_id}: {e}")
            return []
    
    def bulk_record_prices(self, coin_data: Dict[str, Dict]) -> int:
        """
        Record prices for multiple coins at once
        
        Args:
            coin_data: Dictionary mapping coin_id to data dict with 'usd' price
            
        Returns:
            Number of prices recorded
        """
        count = 0
        timestamp = datetime.now()
        
        for coin_id, data in coin_data.items():
            price = data.get('usd')
            if price and price > 0:
                self.record_price(coin_id, price, timestamp)
                count += 1
        
        self.logger.info(f"Recorded prices for {count} coins")
        return count
    
    def enhance_coin_data_with_history(self, coin_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Enhance coin data with historical 24h change if API data is missing
        
        Args:
            coin_data: Dictionary mapping coin_id to data dict
            
        Returns:
            Enhanced coin data with 24h change from history if needed
        """
        for coin_id, data in coin_data.items():
            current_price = data.get('usd')
            api_change = data.get('usd_24h_change')
            
            # If API didn't provide 24h change, calculate from our history
            if current_price and (api_change is None or api_change == 0):
                historical_change = self.calculate_24h_change(coin_id, current_price)
                if historical_change is not None:
                    data['usd_24h_change'] = historical_change
                    data['24h_change_source'] = 'history'
                    self.logger.debug(f"{coin_id}: Using historical 24h change: {historical_change:.2f}%")
        
        return coin_data
    
    def get_stats(self) -> Dict:
        """Get statistics about tracked price history"""
        stats = {
            'total_coins': 0,
            'coins_with_data': [],
            'oldest_data': None,
            'total_data_points': 0
        }
        
        try:
            for history_file in self.storage_dir.glob("*.json"):
                coin_id = history_file.stem
                stats['coins_with_data'].append(coin_id)
                stats['total_coins'] += 1
                
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    stats['total_data_points'] += len(history)
                    
                    if history:
                        oldest = min(h['timestamp'] for h in history)
                        if stats['oldest_data'] is None or oldest < stats['oldest_data']:
                            stats['oldest_data'] = oldest
        
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
        
        return stats

