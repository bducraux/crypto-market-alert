"""
Data fetcher module for cryptocurrency market data
Handles API calls to CoinGecko and other data sources
"""

import requests
import pandas as pd
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataFetcher:
    """Handles fetching cryptocurrency data from various APIs"""
    
    def __init__(self, api_key: Optional[str] = None, retry_attempts: int = 3, retry_delay: int = 5):
        """
        Initialize the data fetcher
        
        Args:
            api_key: CoinGecko API key (optional for free tier)
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Delay between retry attempts in seconds
        """
        self.api_key = api_key
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.base_url = "https://api.coingecko.com/api/v3"
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting for free tier (50 calls/minute)
        self.last_request_time = 0
        self.min_request_interval = 1.2  # seconds between requests
    
    def _make_request(self, url: str, params: Dict[str, Any] = None) -> Optional[Dict]:
        """
        Make HTTP request with retry logic and rate limiting
        
        Args:
            url: API endpoint URL
            params: Request parameters
            
        Returns:
            JSON response data or None if failed
        """
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        headers = {}
        if self.api_key:
            headers['x-cg-demo-api-key'] = self.api_key
        
        for attempt in range(self.retry_attempts):
            try:
                self.last_request_time = time.time()
                response = requests.get(url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"All retry attempts failed for URL: {url}")
                    return None
        
        return None
    
    def get_coin_price(self, coin_id: str, vs_currency: str = "usd") -> Optional[float]:
        """
        Get current price for a specific coin
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin')
            vs_currency: Currency to price against (default: 'usd')
            
        Returns:
            Current price or None if failed
        """
        url = f"{self.base_url}/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': vs_currency,
            'include_24hr_change': 'true'
        }
        
        data = self._make_request(url, params)
        if data and coin_id in data:
            return data[coin_id].get(vs_currency)
        
        return None
    
    def get_multiple_coin_prices(self, coin_ids: List[str], vs_currency: str = "usd") -> Dict[str, Dict]:
        """
        Get current prices for multiple coins
        
        Args:
            coin_ids: List of CoinGecko coin IDs
            vs_currency: Currency to price against
            
        Returns:
            Dictionary with coin data
        """
        url = f"{self.base_url}/simple/price"
        params = {
            'ids': ','.join(coin_ids),
            'vs_currencies': vs_currency,
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        data = self._make_request(url, params)
        return data if data else {}
    
    def get_historical_prices(self, coin_id: str, days: int = 30, vs_currency: str = "usd") -> Optional[pd.DataFrame]:
        """
        Get historical price data for technical analysis
        
        Args:
            coin_id: CoinGecko coin ID
            days: Number of days of historical data
            vs_currency: Currency to price against
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        # Use market_chart endpoint for more reliable data
        # For technical analysis, we need sufficient data points
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        
        # Ensure we get enough data points for technical analysis
        # Use hourly data for shorter periods, daily for longer
        if days <= 30:
            interval = 'hourly'
            api_days = max(days, 30)  # Minimum 30 days for hourly data
        else:
            interval = 'daily' if days > 90 else 'hourly'
            api_days = max(days, 200)  # Ensure we get enough data for MA200
        
        params = {
            'vs_currency': vs_currency,
            'days': api_days,
            'interval': interval
        }
        
        data = self._make_request(url, params)
        if not data:
            return None
        
        # Extract prices and volume data to create proper OHLCV
        prices = data.get('prices', [])
        volumes = data.get('total_volumes', [])
        
        if not prices:
            return None
        
        # Create volume lookup for timestamps
        volume_dict = {timestamp: volume for timestamp, volume in volumes} if volumes else {}
        
        # Convert to DataFrame with proper OHLCV structure
        df_data = []
        
        # For hourly data, we can create better OHLC approximations
        if interval == 'hourly' and len(prices) > 24:
            # Group hourly data into daily OHLCV candles
            daily_groups = {}
            for timestamp, price in prices:
                date_key = pd.to_datetime(timestamp, unit='ms').date()
                if date_key not in daily_groups:
                    daily_groups[date_key] = []
                daily_groups[date_key].append((timestamp, price))
            
            # Create daily OHLCV from hourly data
            for date_key in sorted(daily_groups.keys()):
                day_prices = daily_groups[date_key]
                if len(day_prices) >= 4:  # Need at least 4 hours of data
                    timestamps, prices_list = zip(*day_prices)
                    day_volume = sum(volume_dict.get(ts, 0) for ts in timestamps)
                    
                    df_data.append({
                        'timestamp': timestamps[0],  # Use first timestamp of the day
                        'open': prices_list[0],
                        'high': max(prices_list),
                        'low': min(prices_list),
                        'close': prices_list[-1],
                        'volume': day_volume
                    })
        else:
            # For daily data or insufficient hourly data, use price as approximation
            for timestamp, price in prices:
                volume = volume_dict.get(timestamp, 0)
                df_data.append({
                    'timestamp': timestamp,
                    'open': price,
                    'high': price,
                    'low': price,
                    'close': price,
                    'volume': volume
                })
        
        if not df_data:
            return None
        
        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df = df.astype(float)
        
        # Sort by timestamp to ensure proper order
        df = df.sort_index()
        
        # Limit to requested number of days if we fetched more
        if len(df) > days:
            df = df.tail(days)
        
        return df
    
    def get_market_data(self, coin_id: str) -> Optional[Dict]:
        """
        Get comprehensive market data for a coin
        
        Args:
            coin_id: CoinGecko coin ID
            
        Returns:
            Market data dictionary or None if failed
        """
        url = f"{self.base_url}/coins/{coin_id}"
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'true',
            'community_data': 'false',
            'developer_data': 'false',
            'sparkline': 'false'
        }
        
        return self._make_request(url, params)
    
    def get_btc_dominance(self) -> Optional[float]:
        """
        Get Bitcoin dominance percentage
        
        Returns:
            BTC dominance percentage or None if failed
        """
        url = f"{self.base_url}/global"
        data = self._make_request(url)
        
        if data and 'data' in data:
            return data['data'].get('market_cap_percentage', {}).get('btc')
        
        return None
    
    def get_eth_btc_ratio(self) -> Optional[float]:
        """
        Get ETH/BTC price ratio
        
        Returns:
            ETH/BTC ratio or None if failed
        """
        prices = self.get_multiple_coin_prices(['ethereum', 'bitcoin'])
        
        if 'ethereum' in prices and 'bitcoin' in prices:
            eth_price = prices['ethereum']['usd']
            btc_price = prices['bitcoin']['usd']
            if btc_price and btc_price > 0:
                return eth_price / btc_price
        
        return None
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """
        Get Fear & Greed Index from alternative.me API
        
        Returns:
            Fear & Greed Index data or None if failed
        """
        url = "https://api.alternative.me/fng/"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                return {
                    'value': int(data['data'][0]['value']),
                    'value_classification': data['data'][0]['value_classification'],
                    'timestamp': data['data'][0]['timestamp']
                }
        except Exception as e:
            self.logger.warning(f"Failed to fetch Fear & Greed Index: {e}")
        
        return None
    
    def get_coin_market_data_batch(self, coin_ids: List[str]) -> Dict[str, Dict]:
        """
        Get market data for multiple coins efficiently
        
        Args:
            coin_ids: List of CoinGecko coin IDs
            
        Returns:
            Dictionary mapping coin IDs to their market data
        """
        result = {}
        
        # Get basic price data for all coins
        price_data = self.get_multiple_coin_prices(coin_ids)
        
        # Get additional market data for each coin
        for coin_id in coin_ids:
            if coin_id in price_data:
                result[coin_id] = price_data[coin_id]
                
                # Add historical data for technical analysis (200+ days for MA200)
                # Tentar com 250 dias, se falhar tentar com menos
                historical_df = self.get_historical_prices(coin_id, days=250)
                if historical_df is None:
                    self.logger.warning(f"Failed to get 250 days for {coin_id}, trying 180 days")
                    historical_df = self.get_historical_prices(coin_id, days=180)
                    if historical_df is None:
                        self.logger.warning(f"Failed to get 180 days for {coin_id}, trying 100 days")
                        historical_df = self.get_historical_prices(coin_id, days=100)
                        
                if historical_df is not None:
                    result[coin_id]['historical'] = historical_df
                else:
                    self.logger.error(f"Failed to get any historical data for {coin_id}")
        
        return result
    
    def validate_coin_id(self, coin_id: str) -> bool:
        """
        Validate if a coin ID exists on CoinGecko
        
        Args:
            coin_id: CoinGecko coin ID to validate
            
        Returns:
            True if coin exists, False otherwise
        """
        price = self.get_coin_price(coin_id)
        return price is not None
    
    def get_trending_coins(self, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get trending/popular coins
        
        Args:
            limit: Number of trending coins to return
            
        Returns:
            List of trending coin data or None if failed
        """
        url = f"{self.base_url}/search/trending"
        data = self._make_request(url)
        
        if data and 'coins' in data:
            return data['coins'][:limit]
        
        return None
