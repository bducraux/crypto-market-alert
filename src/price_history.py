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
    
    def get_last_stored_price(self, coin_id: str) -> Optional[float]:
        """
        Get the most recent stored price for a coin

        Args:
            coin_id: CoinGecko ID of the coin

        Returns:
            Most recent stored price, or None if not available
        """
        try:
            history_file = self._get_history_file(coin_id)

            if not history_file.exists():
                return None

            with open(history_file, 'r') as f:
                history = json.load(f)

            if not history:
                return None

            # Get the most recent entry (last in the list)
            last_entry = history[-1]
            return last_entry['price']

        except Exception as e:
            self.logger.error(f"Error getting last stored price for {coin_id}: {e}")
            return None

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
    
    def calculate_change_since_last(self, coin_id: str, current_price: float) -> Optional[float]:
        """
        Calculate price change percentage since last stored price

        Args:
            coin_id: CoinGecko ID of the coin
            current_price: Current price in USD

        Returns:
            Change percentage since last stored price, or None if not enough data
        """
        last_price = self.get_last_stored_price(coin_id)

        if last_price is None or last_price == 0:
            return None

        change_pct = ((current_price - last_price) / last_price) * 100
        return change_pct

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
    
    def enhance_coin_data_with_last_stored_change(self, coin_data: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Enhance coin data with change since last stored price

        Args:
            coin_data: Dictionary mapping coin_id to data dict

        Returns:
            Enhanced coin data with change since last stored price
        """
        for coin_id, data in coin_data.items():
            current_price = data.get('usd')

            if current_price:
                change_since_last = self.calculate_change_since_last(coin_id, current_price)
                if change_since_last is not None:
                    data['usd_change_since_last'] = change_since_last
                    data['change_source'] = 'last_stored'
                    self.logger.debug(f"{coin_id}: Change since last stored: {change_since_last:.2f}%")
                else:
                    # First read, no previous data
                    data['usd_change_since_last'] = 0
                    data['change_source'] = 'first_read'

        return coin_data

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

    def calculate_portfolio_value_history(self, portfolio_config: List[Dict], hours: int = 168) -> List[Dict]:
        """
        Calculate historical portfolio values based on coin holdings and price history

        Args:
            portfolio_config: List of coin configurations with coingecko_id and current_amount
            hours: Number of hours to look back (default: 168 = 7 days)

        Returns:
            List of dictionaries with timestamp and total_value
        """
        try:
            # Collect all timestamps across all coins
            all_timestamps = set()
            coin_histories = {}

            # Load history for each coin in portfolio
            for coin_config in portfolio_config:
                coin_id = coin_config.get('coingecko_id')
                amount = coin_config.get('current_amount', 0)

                if not coin_id or amount <= 0:
                    continue

                history = self.get_history(coin_id, hours)
                if history:
                    coin_histories[coin_id] = {
                        'amount': amount,
                        'history': {h['timestamp']: h['price'] for h in history}
                    }
                    all_timestamps.update(coin_histories[coin_id]['history'].keys())

            if not all_timestamps:
                return []

            # Sort timestamps
            sorted_timestamps = sorted(all_timestamps)

            # Calculate portfolio value at each timestamp
            portfolio_history = []

            for timestamp in sorted_timestamps:
                total_value = 0
                missing_data = False

                # Sum up value of all coins at this timestamp
                for coin_id, coin_data in coin_histories.items():
                    price = coin_data['history'].get(timestamp)
                    if price is not None:
                        total_value += price * coin_data['amount']
                    else:
                        # If we don't have price for this coin at this timestamp, skip this point
                        missing_data = True
                        break

                if not missing_data and total_value > 0:
                    portfolio_history.append({
                        'timestamp': timestamp,
                        'total_value': total_value
                    })

            self.logger.info(f"Calculated portfolio value history: {len(portfolio_history)} data points")
            return portfolio_history

        except Exception as e:
            self.logger.error(f"Error calculating portfolio value history: {e}")
            return []

    def generate_portfolio_table(self, portfolio_config: List[Dict], hours: int = 168) -> str:
        """
        Generate a clean table showing portfolio value evolution

        Args:
            portfolio_config: List of coin configurations
            hours: Number of hours to display (default: 168 = 7 days)

        Returns:
            Formatted table string for Telegram
        """
        try:
            history = self.calculate_portfolio_value_history(portfolio_config, hours)

            if not history or len(history) < 2:
                return "📊 Not enough historical data yet. Portfolio tracking available after 24h."

            values = [h['total_value'] for h in history]
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)

            # Calculate change
            first_val = values[0]
            last_val = values[-1]
            change_pct = ((last_val - first_val) / first_val) * 100
            change_usd = last_val - first_val
            change_emoji = "📈" if change_pct >= 0 else "📉"

            # Time range
            first_time = datetime.fromisoformat(history[0]['timestamp'])
            last_time = datetime.fromisoformat(history[-1]['timestamp'])

            # Determine period name
            if hours <= 24:
                period_name = "24 Hours"
            elif hours <= 72:
                period_name = "3 Days"
            elif hours <= 168:
                period_name = "7 Days"
            else:
                period_name = "30 Days"

            # Build output
            output = []
            output.append(f"{change_emoji} <b>Portfolio Value - Last {period_name}</b>\n")

            # Summary table
            output.append("<b>📊 Performance Summary:</b>")
            output.append(f"<b>Start Value</b>    ${first_val:>13,.2f}")
            output.append(f"<b>End Value</b>      ${last_val:>13,.2f}")
            output.append(f"<b>Change</b>         {change_pct:>+12.2f}%")
            output.append(f"<b>Change ($)</b>     ${change_usd:>+12,.2f}")
            output.append("───────────────────")
            output.append(f"<b>Highest</b>        ${max_val:>13,.2f}")
            output.append(f"<b>Lowest</b>         ${min_val:>13,.2f}")
            output.append(f"<b>Average</b>        ${avg_val:>13,.2f}")
            output.append(f"<b>Volatility</b>     ${max_val - min_val:>13,.2f}")

            # Sample key data points for detail table
            samples = []
            if hours <= 24:
                # Show every 4 hours for 24h view
                sample_count = min(7, len(history))
            elif hours <= 72:
                # Show every 12 hours for 3 day view
                sample_count = min(7, len(history))
            elif hours <= 168:
                # Show daily for 7 day view
                sample_count = min(8, len(history))
            else:
                # Show every 3-4 days for 30 day view
                sample_count = min(8, len(history))

            step = max(1, len(history) // sample_count)
            for i in range(0, len(history), step):
                samples.append(history[i])

            # Always include the last data point
            if samples[-1]['timestamp'] != history[-1]['timestamp']:
                samples.append(history[-1])

            # Detail table
            output.append(f"\n<b>📅 Key Data Points:</b>")
            output.append("<pre>")
            output.append("Date/Time        Value      Change")
            output.append("───────────────────────────────────")

            for i, sample in enumerate(samples):
                timestamp = datetime.fromisoformat(sample['timestamp'])
                value = sample['total_value']

                # Calculate change from previous sample
                if i > 0:
                    prev_value = samples[i-1]['total_value']
                    sample_change = ((value - prev_value) / prev_value) * 100
                    change_str = f"{sample_change:+6.2f}%"
                else:
                    change_str = "  ---  "

                date_str = timestamp.strftime("%m/%d %H:%M")
                output.append(f"{date_str}  ${value:>10,.0f}  {change_str}")

            output.append("</pre>")

            # Time range footer
            output.append(f"\n⏰ Period: {first_time.strftime('%Y-%m-%d %H:%M')} to {last_time.strftime('%Y-%m-%d %H:%M')}")
            output.append(f"📊 Total data points: {len(history)}")

            return "\n".join(output)

        except Exception as e:
            self.logger.error(f"Error generating portfolio table: {e}")
            return f"❌ Error generating portfolio summary: {str(e)}"

