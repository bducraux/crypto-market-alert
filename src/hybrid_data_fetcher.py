"""
Hybrid Data Fetcher - Combines Binance API (fast, reliable prices) with CoinGecko (market metrics)
Solves rate limiting issues by using Binance for high-frequency data and CoinGecko only for unique metrics
"""

import logging
import time
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class HybridDataFetcher:
    """
    Hybrid data fetcher that uses:
    - Binance API: For prices, volumes, historical data (fast, no rate limits)
    - CoinGecko API: Only for unique metrics (Fear & Greed, BTC Dominance)
    """
    
    def __init__(self, retry_attempts: int = 3, retry_delay: int = 2):
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        # Mapeamento de CoinGecko ID para símbolo Binance
        self.coin_mapping = {
            'bitcoin': 'BTCUSDT',
            'ethereum': 'ETHUSDT',
            'binancecoin': 'BNBUSDT',
            'chainlink': 'LINKUSDT',
            'ondo-finance': 'ONDOUSDT',
            'matic-network': 'MATICUSDT',
            'polygon': 'MATICUSDT',  # Alias para matic
            'cardano': 'ADAUSDT',
            'tron': 'TRXUSDT',
            'cosmos': 'ATOMUSDT',
            'lido-dao': 'LDOUSDT',
            'tether': None,  # USDT não precisa de par, valor fixo em ~$1
            'blockstack': 'STXUSDT',
            'render-token': 'RNDRUSDT',
            'pancakeswap-token': 'CAKEUSDT',
            'fetch-ai': 'FETUSDT',
            'pyth-network': 'PYTHUSDT'
        }
        
        logger.info("Hybrid Data Fetcher initialized (Binance + CoinGecko)")
    
    def _make_binance_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to Binance API with retry logic"""
        url = f"{self.binance_base_url}/{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Binance request failed (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"All retry attempts failed for Binance URL: {url}")
        
        return None
    
    def _make_coingecko_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make request to CoinGecko API with retry logic (only for essential metrics)"""
        url = f"{self.coingecko_base_url}/{endpoint}"
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, timeout=15)
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"CoinGecko request failed (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * 2)  # Longer delay for CoinGecko
                else:
                    logger.error(f"All retry attempts failed for CoinGecko URL: {url}")
        
        return None
    
    def get_binance_price(self, symbol: str) -> Optional[Dict]:
        """Get current price from Binance"""
        try:
            data = self._make_binance_request("ticker/24hr", {"symbol": symbol})
            if data:
                return {
                    'symbol': symbol,
                    'price': float(data['lastPrice']),
                    'change_24h': float(data['priceChangePercent']),
                    'volume_24h': float(data['volume']),
                    'high_24h': float(data['highPrice']),
                    'low_24h': float(data['lowPrice'])
                }
        except Exception as e:
            logger.error(f"Error getting Binance price for {symbol}: {e}")
        
        return None
    
    def get_binance_historical_data(self, symbol: str, interval: str = "1d", limit: int = 500) -> Optional[pd.DataFrame]:
        """Get historical data from Binance"""
        try:
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': min(limit, 1000)  # Binance limit
            }
            
            data = self._make_binance_request("klines", params)
            if not data:
                return None
            
            logger.debug(f"Retrieved {len(data)} klines for {symbol}")
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert types and timestamps
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # Set timestamp as index and keep close/volume columns for indicators
            df.set_index('timestamp', inplace=True)
            df = df[['close', 'volume']].copy()  # Keep close and volume
            
            logger.debug(f"Final DataFrame shape for {symbol}: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting Binance historical data for {symbol}: {e}")
            return None
    
    def get_coin_market_data_batch(self, coin_ids: List[str]) -> Dict[str, Dict]:
        """Get market data for multiple coins using Binance (fast)"""
        result = {}
        
        for coin_id in coin_ids:
            if coin_id not in self.coin_mapping:
                logger.warning(f"No Binance mapping for {coin_id}")
                continue
            
            binance_symbol = self.coin_mapping[coin_id]
            
            # Handle USDT specially (it's always ~$1)
            if coin_id == 'tether':
                result[coin_id] = {
                    'usd': 1.0,
                    'usd_24h_change': 0.0,
                    'usd_24h_vol': 0.0,
                    'last_updated': datetime.now().isoformat()
                }
                # Create dummy historical data for USDT with sufficient periods
                dates = pd.date_range(end=datetime.now(), periods=500, freq='D')
                dummy_df = pd.DataFrame({
                    'close': [1.0] * 500,
                    'volume': [1000000.0] * 500  # Add some volume data
                }, index=dates)
                result[coin_id]['historical'] = dummy_df
                continue
            
            # Get current price data
            price_data = self.get_binance_price(binance_symbol)
            if price_data:
                # Convert to expected format
                result[coin_id] = {
                    'usd': price_data['price'],
                    'usd_24h_change': price_data['change_24h'],
                    'usd_24h_vol': price_data['volume_24h'],
                    'last_updated': datetime.now().isoformat()
                }
                
                # Get historical data for technical analysis
                historical_df = self.get_binance_historical_data(binance_symbol, limit=500)
                if historical_df is not None:
                    result[coin_id]['historical'] = historical_df
                else:
                    logger.warning(f"Failed to get historical data for {coin_id}")
        
        logger.info(f"Retrieved data for {len(result)} coins from Binance")
        return result
    
    def get_btc_dominance(self) -> Optional[float]:
        """Get BTC dominance from CoinGecko (unique metric)"""
        try:
            data = self._make_coingecko_request("global")
            if data and 'data' in data:
                dominance = data['data'].get('market_cap_percentage', {}).get('btc')
                if dominance:
                    logger.debug(f"BTC Dominance: {dominance:.2f}%")
                    return float(dominance)
        except Exception as e:
            logger.error(f"Error getting BTC dominance: {e}")
        
        return None
    
    def get_eth_btc_ratio(self) -> Optional[float]:
        """Calculate ETH/BTC ratio using Binance prices"""
        try:
            # Get ETH and BTC prices from Binance
            eth_data = self.get_binance_price('ETHUSDT')
            btc_data = self.get_binance_price('BTCUSDT')
            
            if eth_data and btc_data:
                eth_price = eth_data['price']
                btc_price = btc_data['price']
                ratio = eth_price / btc_price
                logger.debug(f"ETH/BTC Ratio: {ratio:.6f}")
                return ratio
                
        except Exception as e:
            logger.error(f"Error calculating ETH/BTC ratio: {e}")
        
        return None
    
    def get_fear_greed_index(self) -> Optional[Dict]:
        """Get Fear & Greed Index from alternative API (since CoinGecko doesn't have it)"""
        try:
            # Using alternative.me API for Fear & Greed Index
            url = "https://api.alternative.me/fng/"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and 'data' in data and data['data']:
                fng_data = data['data'][0]
                return {
                    'value': int(fng_data['value']),
                    'value_classification': fng_data['value_classification'],
                    'timestamp': fng_data['timestamp'],
                    'time_until_update': data.get('metadata', {}).get('time_until_update')
                }
                
        except Exception as e:
            logger.error(f"Error getting Fear & Greed Index: {e}")
        
        return None
    
    def get_market_cap_data(self) -> Optional[Dict]:
        """Get basic market cap data from CoinGecko (minimal requests)"""
        try:
            # Only get essential data to minimize CoinGecko requests
            params = {
                'ids': 'bitcoin,ethereum',
                'vs_currencies': 'usd',
                'include_market_cap': 'true',
                'include_24hr_change': 'false'  # We get this from Binance
            }
            
            data = self._make_coingecko_request("simple/price", params)
            if data:
                return data
                
        except Exception as e:
            logger.error(f"Error getting market cap data: {e}")
        
        return None
    
    def validate_coin_id(self, coin_id: str) -> bool:
        """Check if we can fetch data for this coin"""
        return coin_id in self.coin_mapping
    
    def get_supported_coins(self) -> List[str]:
        """Get list of supported coin IDs"""
        return list(self.coin_mapping.keys())
    
    def test_connection(self) -> Dict[str, bool]:
        """Test connection to both APIs"""
        results = {}
        
        # Test Binance
        try:
            btc_data = self.get_binance_price('BTCUSDT')
            results['binance'] = btc_data is not None
        except:
            results['binance'] = False
        
        # Test CoinGecko (minimal request)
        try:
            dominance = self.get_btc_dominance()
            results['coingecko'] = dominance is not None
        except:
            results['coingecko'] = False
        
        # Test Fear & Greed
        try:
            fng = self.get_fear_greed_index()
            results['fear_greed'] = fng is not None
        except:
            results['fear_greed'] = False
        
        logger.info(f"API Connection Test: {results}")
        return results
