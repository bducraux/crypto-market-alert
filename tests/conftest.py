"""
Shared pytest fixtures for optimized test performance
Provides common mock setups and reusable test data to reduce execution time
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import DataFetcher
from src.alerts import TelegramAlertsManager, AlertsOrchestrator
from src.strategy import AlertStrategy
from src.indicators import TechnicalIndicators


# ============================================================================
# PERFORMANCE OPTIMIZED FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def shared_data_fetcher():
    """Share DataFetcher instance across test session for performance"""
    return DataFetcher(retry_attempts=1, retry_delay=0.1)


@pytest.fixture(scope="session")
def shared_telegram_manager():
    """Share TelegramAlertsManager instance across test session"""
    return TelegramAlertsManager(
        bot_token="test_token_session",
        chat_id="test_chat_id_session"
    )


@pytest.fixture(scope="session")
def shared_indicators():
    """Share TechnicalIndicators instance across test session"""
    return TechnicalIndicators()


# ============================================================================
# MOCK RESPONSE FACTORIES
# ============================================================================

@pytest.fixture
def mock_successful_api_response():
    """Reusable mock for successful API responses"""
    def _mock_response(data, status_code=200):
        mock = Mock()
        mock.status_code = status_code
        mock.json.return_value = data
        mock.raise_for_status.return_value = None
        return mock
    return _mock_response


@pytest.fixture
def mock_failed_api_response():
    """Reusable mock for failed API responses"""
    def _mock_response(status_code=500, exception=None):
        mock = Mock()
        mock.status_code = status_code
        if exception:
            mock.json.side_effect = exception
            mock.raise_for_status.side_effect = exception
        else:
            mock.json.return_value = {}
            mock.raise_for_status.return_value = None
        return mock
    return _mock_response


@pytest.fixture
def mock_binance_price_response():
    """Factory for Binance price response mocks"""
    def _create_response(symbol="BTCUSDT", price="45000.50"):
        return {
            'symbol': symbol,
            'price': price
        }
    return _create_response


@pytest.fixture
def mock_coingecko_market_response():
    """Factory for CoinGecko market data response mocks"""
    def _create_response(coin_id="bitcoin", price=45000.50, change_24h=5.5):
        return {
            coin_id: {
                'usd': price,
                'usd_market_cap': price * 19500000,
                'usd_24h_vol': price * 1000,
                'usd_24h_change': change_24h
            }
        }
    return _create_response


@pytest.fixture
def mock_fear_greed_response():
    """Factory for Fear & Greed index response mocks"""
    def _create_response(value=50, classification="Neutral"):
        return {
            'data': [{
                'value': str(value),
                'value_classification': classification,
                'timestamp': '1609459200'
            }]
        }
    return _create_response


# ============================================================================
# REALISTIC TEST DATA GENERATORS
# ============================================================================

@pytest.fixture(scope="session")
def realistic_price_data():
    """Generate realistic cryptocurrency price data for testing"""
    np.random.seed(42)  # For reproducible tests
    dates = pd.date_range('2023-01-01', periods=250, freq='D')
    
    # Generate realistic BTC price movement
    base_price = 45000
    prices = [base_price]
    
    for _ in range(249):
        # Realistic daily volatility (2-3%)
        change = np.random.normal(0, 0.025)
        new_price = prices[-1] * (1 + change)
        # Ensure price stays within reasonable bounds
        new_price = max(10000, min(150000, new_price))
        prices.append(new_price)
    
    return pd.DataFrame({
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 50000000, 250)
    }, index=dates)


@pytest.fixture
def realistic_market_scenarios():
    """Provide realistic market scenario data for testing"""
    return {
        'bull_market': {
            'btc_change': 15.5,
            'eth_change': 18.2,
            'fear_greed': 85,
            'btc_dominance': 42.5
        },
        'bear_market': {
            'btc_change': -25.0,
            'eth_change': -30.1,
            'fear_greed': 8,
            'btc_dominance': 68.3
        },
        'sideways_market': {
            'btc_change': 2.1,
            'eth_change': -1.5,
            'fear_greed': 45,
            'btc_dominance': 55.2
        },
        'altseason': {
            'btc_change': -5.2,
            'eth_change': 25.8,
            'fear_greed': 75,
            'btc_dominance': 38.5
        }
    }


@pytest.fixture
def sample_coin_configs():
    """Provide sample coin configurations for testing"""
    return {
        'bitcoin': {
            'symbol': 'BTC',
            'coingecko_id': 'bitcoin',
            'price_above': 50000,
            'price_below': 40000,
            'rsi_overbought': 70,
            'rsi_oversold': 30
        },
        'ethereum': {
            'symbol': 'ETH',
            'coingecko_id': 'ethereum',
            'price_above': 3500,
            'price_below': 2500,
            'rsi_overbought': 70,
            'rsi_oversold': 30
        }
    }


# ============================================================================
# ALERT AND STRATEGY FIXTURES
# ============================================================================

@pytest.fixture
def sample_alerts():
    """Generate sample alert data for testing"""
    return [
        {
            'message': 'BTC price alert',
            'type': 'price_above',
            'coin': 'BTC',
            'priority': 'high',
            'current_price': 55000.0,
            'threshold': 50000
        },
        {
            'message': 'ETH RSI overbought',
            'type': 'rsi_overbought',
            'coin': 'ETH',
            'priority': 'medium',
            'rsi_value': 75.5,
            'threshold': 70
        },
        {
            'message': 'Market fear detected',
            'type': 'extreme_fear',
            'coin': 'Market',
            'priority': 'high',
            'value': 15,
            'classification': 'Extreme Fear'
        }
    ]


@pytest.fixture
def mock_strategy_config():
    """Provide mock strategy configuration for testing"""
    return {
        'coins': [
            {
                'symbol': 'BTC',
                'coingecko_id': 'bitcoin',
                'price_above': 50000,
                'price_below': 40000
            }
        ],
        'indicators': {
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30
        },
        'alerts': {
            'telegram_enabled': True,
            'batch_size': 5
        }
    }


# ============================================================================
# ASYNC FIXTURES FOR TELEGRAM TESTING
# ============================================================================

@pytest.fixture
def mock_telegram_bot():
    """Mock Telegram bot for async testing"""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=True)
    return bot


@pytest.fixture
def mock_alerts_orchestrator():
    """Mock AlertsOrchestrator for testing"""
    telegram_manager = Mock()
    telegram_manager.send_message = AsyncMock(return_value=True)
    return AlertsOrchestrator(telegram_manager, batch_size=5)


# ============================================================================
# PERFORMANCE MONITORING FIXTURES
# ============================================================================

@pytest.fixture
def performance_monitor():
    """Monitor test execution time for performance optimization"""
    import time
    
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
            return self.end_time - self.start_time if self.start_time else 0
        
        def assert_under_threshold(self, threshold_seconds=1.0):
            duration = self.stop()
            assert duration < threshold_seconds, f"Test took {duration:.2f}s, expected < {threshold_seconds}s"
    
    return PerformanceMonitor()


# ============================================================================
# EDGE CASE DATA FIXTURES
# ============================================================================

@pytest.fixture
def edge_case_price_data():
    """Provide edge case price data for boundary testing"""
    return {
        'extremely_large': "999999999999.99999999",
        'extremely_small': "0.000000000001",
        'zero': "0.0",
        'negative': "-100.50",
        'invalid_format': "not_a_number",
        'empty_string': "",
        'null_value': None,
        'scientific_notation': "1.23e-8"
    }


@pytest.fixture
def malicious_html_content():
    """Provide malicious HTML content for injection testing"""
    return {
        'script_tag': "<script>alert('xss')</script>",
        'img_tag': '<img src="x" onerror="alert(1)">',
        'iframe_tag': '<iframe src="javascript:alert(1)"></iframe>',
        'link_tag': '<a href="javascript:alert(1)">Click me</a>',
        'style_tag': '<style>body{background:url("javascript:alert(1)")}</style>',
        'mixed_content': '''
            <script>alert('xss1')</script>
            <img src="x" onerror="alert('xss2')">
            Normal text here
            <a href="javascript:alert('xss3')">Link</a>
        '''
    }


# ============================================================================
# CLEANUP FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatic cleanup after each test for performance"""
    yield
    # Cleanup any global state, clear caches, etc.
    # This runs after each test automatically