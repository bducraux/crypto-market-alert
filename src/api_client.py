"""
Generic API Client with caching, rate limiting and retry logic
Follows DRY principle by providing a common base for all API interactions
"""

import logging
import time
import requests
import threading
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class APIClient(ABC):
    """
    Abstract base class for API clients with common functionality:
    - Rate limiting
    - Caching
    - Retry logic
    - Error handling
    """
    
    def __init__(self, 
                 base_url: str,
                 retry_attempts: int = 3,
                 retry_delay: int = 2,
                 cache_ttl: int = 60,
                 min_interval: float = 1.0):
        self.base_url = base_url
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.cache_ttl = cache_ttl
        self.min_interval = min_interval
        
        # Caching and rate limiting
        self._cache = {}
        self._last_request = 0
        self._lock = threading.Lock()
    
    def _create_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Create a unique cache key from URL and parameters"""
        url = f"{self.base_url}/{endpoint}"
        if params:
            params_str = requests.compat.urlencode(params)
            return f"{url}?{params_str}"
        return url
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        """Check if we have valid cached data"""
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                logger.debug(f"Using cached data for {cache_key}")
                return cached_data
        return None
    
    def _cache_data(self, cache_key: str, data: Dict) -> None:
        """Store data in cache"""
        with self._lock:
            self._cache[cache_key] = (data, time.time())
    
    def _apply_rate_limiting(self) -> None:
        """Apply rate limiting between requests"""
        with self._lock:
            current_time = time.time()
            time_since_last = current_time - self._last_request
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
                time.sleep(sleep_time)
            self._last_request = time.time()
    
    @abstractmethod
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers specific to this API"""
        pass
    
    @abstractmethod
    def _handle_rate_limit_response(self, response: requests.Response, attempt: int) -> bool:
        """Handle rate limit responses (return True to retry)"""
        pass
    
    def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Make API request with caching, rate limiting and retry logic
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data or None if failed
        """
        cache_key = self._create_cache_key(endpoint, params)
        
        # Check cache first
        cached_data = self._get_cached_data(cache_key)
        if cached_data is not None:
            return cached_data
        
        # Apply rate limiting
        self._apply_rate_limiting()
        
        url = f"{self.base_url}/{endpoint}"
        headers = self._prepare_headers()
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=15)
                
                # Handle rate limiting
                if response.status_code == 429:
                    if self._handle_rate_limit_response(response, attempt):
                        continue
                    else:
                        logger.error(f"Rate limit exceeded, giving up after {attempt + 1} attempts")
                        return None
                
                # Handle other error status codes
                if response.status_code != 200:
                    logger.warning(f"Request failed with status {response.status_code}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                        continue
                    else:
                        return None
                
                response.raise_for_status()
                
                # Parse JSON response
                try:
                    data = response.json()
                    self._cache_data(cache_key, data)
                    return data
                except ValueError as e:
                    logger.error(f"Invalid JSON response: {e}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return None
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.retry_attempts}): {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"All retry attempts failed for {url}")
        
        return None


class BinanceClient(APIClient):
    """Binance API client - fast, reliable for prices and historical data"""
    
    def __init__(self, retry_attempts: int = 3, retry_delay: int = 1):
        super().__init__(
            base_url="https://api.binance.com/api/v3",
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
            cache_ttl=30,  # Shorter cache for price data
            min_interval=0.1  # Binance has no strict rate limits
        )
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Binance doesn't require special headers"""
        return {}
    
    def _handle_rate_limit_response(self, response: requests.Response, attempt: int) -> bool:
        """Handle Binance rate limit (unlikely but possible)"""
        backoff_time = (2 ** attempt) * 2
        logger.warning(f"Binance rate limit, backing off for {backoff_time}s")
        time.sleep(backoff_time)
        return True


class CoinGeckoClient(APIClient):
    """CoinGecko API client - for unique market metrics"""
    
    def __init__(self, retry_attempts: int = 3, retry_delay: int = 2):
        super().__init__(
            base_url="https://api.coingecko.com/api/v3",
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
            cache_ttl=60,  # Longer cache for market metrics
            min_interval=1.2  # Respect CoinGecko rate limits
        )
    
    def _prepare_headers(self) -> Dict[str, str]:
        """CoinGecko doesn't require special headers for free tier"""
        return {}
    
    def _handle_rate_limit_response(self, response: requests.Response, attempt: int) -> bool:
        """Handle CoinGecko rate limit with exponential backoff"""
        backoff_time = (2 ** attempt) * 5
        logger.warning(f"CoinGecko rate limit, backing off for {backoff_time}s")
        time.sleep(backoff_time)
        return True


class CoinMarketCapClient(APIClient):
    """CoinMarketCap API client - for fallback data"""
    
    def __init__(self, api_key: str, retry_attempts: int = 3, retry_delay: int = 3):
        super().__init__(
            base_url="https://pro-api.coinmarketcap.com/v1",
            retry_attempts=retry_attempts,
            retry_delay=retry_delay,
            cache_ttl=300,  # Longer cache to preserve monthly limits
            min_interval=2.0  # Conservative rate limiting
        )
        self.api_key = api_key
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare CoinMarketCap headers with API key"""
        return {
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accept': 'application/json'
        }
    
    def _handle_rate_limit_response(self, response: requests.Response, attempt: int) -> bool:
        """Handle CoinMarketCap rate limit with longer backoff"""
        backoff_time = (2 ** attempt) * 10
        logger.warning(f"CoinMarketCap rate limit, backing off for {backoff_time}s")
        time.sleep(backoff_time)
        return True
