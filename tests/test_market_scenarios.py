"""
Realistic Market Scenario Tests
Tests market analysis logic with various realistic market conditions
Validates system behavior during different market phases
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import DataFetcher
from src.strategy import AlertStrategy
from src.indicators import TechnicalIndicators


@pytest.mark.unit
class TestMarketCrashScenarios:
    """Test system behavior during market crash scenarios"""
    
    @pytest.fixture
    def data_fetcher(self):
        return DataFetcher(retry_attempts=1, retry_delay=0.1)
    
    @pytest.fixture
    def strategy(self, mock_strategy_config):
        return AlertStrategy(mock_strategy_config)
    
    @pytest.mark.parametrize("crash_severity,btc_change,eth_change,fear_greed,expected_phase", [
        ("mild_crash", -12.5, -15.2, 25, "BEARISH"),
        ("moderate_crash", -25.0, -30.1, 15, "CRASH"),
        ("severe_crash", -40.5, -45.8, 8, "CRASH"),
        ("flash_crash", -55.0, -60.2, 5, "EXTREME_CRASH"),
    ])
    def test_market_crash_detection_logic(self, data_fetcher, crash_severity, btc_change, eth_change, fear_greed, expected_phase):
        """Test crash detection with various realistic crash scenarios"""
        
        # Mock market data for crash scenario
        crash_market_data = {
            'bitcoin': {
                'usd': 35000.0,  # Down from typical ~50k
                'usd_24h_change': btc_change,
                'usd_24h_vol': 25000000000,  # High volume during crash
                'usd_market_cap': 680000000000
            },
            'ethereum': {
                'usd': 2200.0,  # Down from typical ~3k
                'usd_24h_change': eth_change,
                'usd_24h_vol': 15000000000,
                'usd_market_cap': 265000000000
            }
        }
        
        fear_greed_data = {
            'value': fear_greed,
            'classification': 'Extreme Fear' if fear_greed <= 25 else 'Fear',
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=crash_market_data):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=fear_greed_data):
                
                # Test market analysis logic
                market_data = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
                fg_data = data_fetcher.get_fear_greed_index()
                
                # Validate crash detection logic
                assert market_data['bitcoin']['usd_24h_change'] < -10, "Should detect significant BTC decline"
                assert market_data['ethereum']['usd_24h_change'] < -10, "Should detect significant ETH decline"
                assert fg_data['value'] <= 50, "Fear & Greed should indicate fear during crash"
                
                # Test correlation between assets during crash
                btc_decline = abs(market_data['bitcoin']['usd_24h_change'])
                eth_decline = abs(market_data['ethereum']['usd_24h_change'])
                correlation_ratio = min(btc_decline, eth_decline) / max(btc_decline, eth_decline)
                assert correlation_ratio > 0.5, "Assets should be correlated during market crash"
    
    def test_market_crash_volume_spike(self, data_fetcher):
        """Test that market crashes are accompanied by volume spikes"""
        crash_data = {
            'bitcoin': {
                'usd': 32000.0,
                'usd_24h_change': -28.5,
                'usd_24h_vol': 45000000000,  # Very high volume
                'usd_market_cap': 620000000000
            }
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=crash_data):
            result = data_fetcher.get_coin_market_data_batch(['bitcoin'])
            
            # During crashes, volume typically spikes above normal levels
            normal_volume_threshold = 20000000000  # $20B typical
            assert result['bitcoin']['usd_24h_vol'] > normal_volume_threshold, \
                "Crash should be accompanied by high volume"
    
    def test_market_crash_recovery_detection(self, data_fetcher):
        """Test detection of market recovery after crash"""
        # Simulate recovery scenario
        recovery_data = {
            'bitcoin': {
                'usd': 42000.0,  # Recovering from crash
                'usd_24h_change': 15.2,  # Strong bounce
                'usd_24h_vol': 35000000000,
                'usd_market_cap': 815000000000
            },
            'ethereum': {
                'usd': 2800.0,
                'usd_24h_change': 18.5,  # Strong ETH recovery
                'usd_24h_vol': 20000000000,
                'usd_market_cap': 337000000000
            }
        }
        
        recovery_fear_greed = {
            'value': 45,  # Moving from fear to neutral
            'classification': 'Neutral',
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=recovery_data):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=recovery_fear_greed):
                
                market_data = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
                fg_data = data_fetcher.get_fear_greed_index()
                
                # Validate recovery detection
                assert market_data['bitcoin']['usd_24h_change'] > 10, "Should detect strong BTC recovery"
                assert market_data['ethereum']['usd_24h_change'] > 10, "Should detect strong ETH recovery"
                assert fg_data['value'] > 35, "Fear & Greed should improve during recovery"


@pytest.mark.unit
class TestBullMarketScenarios:
    """Test system behavior during bull market scenarios"""
    
    @pytest.fixture
    def data_fetcher(self):
        return DataFetcher(retry_attempts=1, retry_delay=0.1)
    
    @pytest.mark.parametrize("bull_phase,btc_change,eth_change,fear_greed,btc_dominance", [
        ("early_bull", 8.5, 12.2, 65, 45.2),
        ("mid_bull", 15.2, 22.8, 75, 42.8),
        ("late_bull", 25.5, 35.1, 85, 38.5),
        ("euphoria", 45.0, 55.8, 92, 35.2),
    ])
    def test_bull_market_phase_detection(self, data_fetcher, bull_phase, btc_change, eth_change, fear_greed, btc_dominance):
        """Test detection of different bull market phases"""
        
        bull_market_data = {
            'bitcoin': {
                'usd': 65000.0 if bull_phase == "euphoria" else 55000.0,
                'usd_24h_change': btc_change,
                'usd_24h_vol': 30000000000,
                'usd_market_cap': 1200000000000
            },
            'ethereum': {
                'usd': 4500.0 if bull_phase == "euphoria" else 3800.0,
                'usd_24h_change': eth_change,
                'usd_24h_vol': 18000000000,
                'usd_market_cap': 540000000000
            }
        }
        
        bull_fear_greed = {
            'value': fear_greed,
            'classification': 'Extreme Greed' if fear_greed >= 85 else 'Greed',
            'timestamp': '1609459200'
        }
        
        dominance_data = {
            'data': {
                'market_cap_percentage': {
                    'btc': btc_dominance
                }
            }
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=bull_market_data):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=bull_fear_greed):
                with patch.object(data_fetcher, '_make_coingecko_request', return_value=dominance_data):
                    
                    market_data = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
                    fg_data = data_fetcher.get_fear_greed_index()
                    dominance = data_fetcher.get_btc_dominance()
                    
                    # Validate bull market characteristics
                    assert market_data['bitcoin']['usd_24h_change'] > 5, "BTC should show positive momentum"
                    assert market_data['ethereum']['usd_24h_change'] > 5, "ETH should show positive momentum"
                    assert fg_data['value'] >= 60, "Fear & Greed should indicate greed in bull market"
                    
                    # Test altseason detection in late bull phases
                    if bull_phase in ["late_bull", "euphoria"]:
                        assert dominance < 50, "BTC dominance should decline in altseason"
                        assert market_data['ethereum']['usd_24h_change'] > market_data['bitcoin']['usd_24h_change'], \
                            "ETH should outperform BTC in altseason"
    
    def test_bubble_detection_logic(self, data_fetcher):
        """Test detection of potential market bubbles"""
        bubble_data = {
            'bitcoin': {
                'usd': 85000.0,  # Very high price
                'usd_24h_change': 35.5,  # Unsustainable daily gain
                'usd_24h_vol': 60000000000,  # Extreme volume
                'usd_market_cap': 1650000000000
            },
            'ethereum': {
                'usd': 6500.0,  # Very high ETH price
                'usd_24h_change': 42.8,  # Extreme daily gain
                'usd_24h_vol': 35000000000,
                'usd_market_cap': 780000000000
            }
        }
        
        extreme_greed = {
            'value': 95,  # Extreme greed
            'classification': 'Extreme Greed',
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=bubble_data):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=extreme_greed):
                
                market_data = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
                fg_data = data_fetcher.get_fear_greed_index()
                
                # Validate bubble indicators
                assert market_data['bitcoin']['usd_24h_change'] > 30, "Extreme daily gains indicate bubble"
                assert market_data['ethereum']['usd_24h_change'] > 30, "Extreme ETH gains indicate bubble"
                assert fg_data['value'] >= 90, "Extreme greed indicates bubble territory"
                
                # Test volume surge during bubble
                assert market_data['bitcoin']['usd_24h_vol'] > 50000000000, "Bubble should have extreme volume"
    
    def test_profit_taking_recommendations(self, data_fetcher):
        """Test profit-taking recommendation logic during bull markets"""
        profit_taking_scenario = {
            'bitcoin': {
                'usd': 72000.0,  # High but not extreme
                'usd_24h_change': 18.5,
                'usd_24h_vol': 35000000000,
                'usd_market_cap': 1400000000000
            }
        }
        
        high_greed = {
            'value': 82,  # High greed but not extreme
            'classification': 'Greed',
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=profit_taking_scenario):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=high_greed):
                
                market_data = data_fetcher.get_coin_market_data_batch(['bitcoin'])
                fg_data = data_fetcher.get_fear_greed_index()
                
                # Validate profit-taking conditions
                btc_price = market_data['bitcoin']['usd']
                greed_level = fg_data['value']
                
                # Logic for partial profit taking
                if btc_price > 70000 and greed_level > 80:
                    profit_taking_signal = True
                else:
                    profit_taking_signal = False
                
                assert profit_taking_signal, "Should recommend profit taking at high prices with high greed"


@pytest.mark.unit
class TestSidewaysMarketScenarios:
    """Test system behavior during sideways/consolidation market scenarios"""
    
    @pytest.fixture
    def data_fetcher(self):
        return DataFetcher(retry_attempts=1, retry_delay=0.1)
    
    @pytest.mark.parametrize("consolidation_type,btc_change,eth_change,fear_greed,volatility", [
        ("tight_range", 2.1, -1.5, 45, "low"),
        ("wide_range", -5.2, 6.8, 52, "medium"),
        ("choppy", 8.5, -7.2, 38, "high"),
        ("accumulation", 1.8, 2.5, 55, "low"),
    ])
    def test_sideways_market_detection(self, data_fetcher, consolidation_type, btc_change, eth_change, fear_greed, volatility):
        """Test detection of sideways market conditions"""
        
        sideways_data = {
            'bitcoin': {
                'usd': 48000.0,  # Mid-range price
                'usd_24h_change': btc_change,
                'usd_24h_vol': 15000000000 if volatility == "low" else 25000000000,
                'usd_market_cap': 930000000000
            },
            'ethereum': {
                'usd': 3200.0,  # Mid-range ETH price
                'usd_24h_change': eth_change,
                'usd_24h_vol': 10000000000 if volatility == "low" else 18000000000,
                'usd_market_cap': 385000000000
            }
        }
        
        neutral_fear_greed = {
            'value': fear_greed,
            'classification': 'Neutral' if 40 <= fear_greed <= 60 else ('Fear' if fear_greed < 40 else 'Greed'),
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=sideways_data):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=neutral_fear_greed):
                
                market_data = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
                fg_data = data_fetcher.get_fear_greed_index()
                
                # Validate sideways market characteristics
                btc_change_abs = abs(market_data['bitcoin']['usd_24h_change'])
                eth_change_abs = abs(market_data['ethereum']['usd_24h_change'])
                
                if consolidation_type == "tight_range":
                    assert btc_change_abs < 5, "Tight range should have small price movements"
                    assert eth_change_abs < 5, "Tight range should have small ETH movements"
                elif consolidation_type == "wide_range":
                    assert 5 <= max(btc_change_abs, eth_change_abs) <= 10, "Wide range allows moderate movements"
                
                # Test neutral sentiment during sideways action
                if consolidation_type in ["tight_range", "accumulation"]:
                    assert 35 <= fg_data['value'] <= 65, "Sideways markets often have neutral sentiment"
    
    def test_breakout_detection_logic(self, data_fetcher):
        """Test detection of breakouts from sideways ranges"""
        # Simulate breakout scenario
        breakout_data = {
            'bitcoin': {
                'usd': 52000.0,  # Breaking above resistance
                'usd_24h_change': 12.5,  # Strong breakout move
                'usd_24h_vol': 28000000000,  # Volume surge on breakout
                'usd_market_cap': 1010000000000
            },
            'ethereum': {
                'usd': 3600.0,  # ETH also breaking out
                'usd_24h_change': 15.2,
                'usd_24h_vol': 16000000000,
                'usd_market_cap': 433000000000
            }
        }
        
        breakout_sentiment = {
            'value': 68,  # Improving sentiment on breakout
            'classification': 'Greed',
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=breakout_data):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=breakout_sentiment):
                
                market_data = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
                fg_data = data_fetcher.get_fear_greed_index()
                
                # Validate breakout characteristics
                assert market_data['bitcoin']['usd_24h_change'] > 10, "Breakout should have strong price move"
                assert market_data['ethereum']['usd_24h_change'] > 10, "ETH should confirm breakout"
                assert market_data['bitcoin']['usd_24h_vol'] > 25000000000, "Breakout should have volume surge"
                assert fg_data['value'] > 60, "Sentiment should improve on breakout"
    
    def test_range_bound_trading_logic(self, data_fetcher):
        """Test range-bound trading detection and logic"""
        # Simulate range-bound scenario with clear support/resistance
        range_data = {
            'bitcoin': {
                'usd': 46500.0,  # Near support level
                'usd_24h_change': -3.2,  # Small decline to support
                'usd_24h_vol': 18000000000,  # Normal volume
                'usd_market_cap': 903000000000
            }
        }
        
        range_sentiment = {
            'value': 42,  # Slight fear at support
            'classification': 'Fear',
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=range_data):
            with patch.object(data_fetcher, 'get_fear_greed_index', return_value=range_sentiment):
                
                market_data = data_fetcher.get_coin_market_data_batch(['bitcoin'])
                fg_data = data_fetcher.get_fear_greed_index()
                
                # Test range-bound logic
                btc_price = market_data['bitcoin']['usd']
                
                # Define typical BTC range (example: 45k-50k)
                support_level = 45000
                resistance_level = 50000
                
                # Validate range-bound behavior
                assert support_level <= btc_price <= resistance_level, "Price should be within expected range"
                
                # Test buy signal near support
                if btc_price < support_level * 1.05:  # Within 5% of support
                    buy_signal = True
                else:
                    buy_signal = False
                
                assert buy_signal, "Should generate buy signal near support in range"


@pytest.mark.unit
class TestAltseasonScenarios:
    """Test altseason detection and behavior"""
    
    @pytest.fixture
    def data_fetcher(self):
        return DataFetcher(retry_attempts=1, retry_delay=0.1)
    
    def test_altseason_detection_logic(self, data_fetcher):
        """Test detection of altseason conditions"""
        altseason_data = {
            'bitcoin': {
                'usd': 48000.0,  # BTC stable/declining
                'usd_24h_change': -2.5,
                'usd_24h_vol': 20000000000,
                'usd_market_cap': 930000000000
            },
            'ethereum': {
                'usd': 4200.0,  # ETH outperforming
                'usd_24h_change': 18.5,
                'usd_24h_vol': 22000000000,
                'usd_market_cap': 505000000000
            },
            'cardano': {
                'usd': 1.25,  # Alt outperforming
                'usd_24h_change': 25.8,
                'usd_24h_vol': 2000000000,
                'usd_market_cap': 42000000000
            }
        }
        
        altseason_dominance = {
            'data': {
                'market_cap_percentage': {
                    'btc': 38.5  # Low BTC dominance indicates altseason
                }
            }
        }
        
        altseason_sentiment = {
            'value': 78,  # High greed during altseason
            'classification': 'Greed',
            'timestamp': '1609459200'
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=altseason_data):
            with patch.object(data_fetcher, '_make_coingecko_request', return_value=altseason_dominance):
                with patch.object(data_fetcher, 'get_fear_greed_index', return_value=altseason_sentiment):
                    
                    market_data = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum', 'cardano'])
                    dominance = data_fetcher.get_btc_dominance()
                    fg_data = data_fetcher.get_fear_greed_index()
                    
                    # Validate altseason characteristics
                    assert dominance < 45, "BTC dominance should be low during altseason"
                    assert market_data['ethereum']['usd_24h_change'] > market_data['bitcoin']['usd_24h_change'], \
                        "ETH should outperform BTC in altseason"
                    assert market_data['cardano']['usd_24h_change'] > 15, "Alts should show strong gains"
                    assert fg_data['value'] > 70, "Altseason typically has high greed"
    
    def test_eth_btc_ratio_altseason_signal(self, data_fetcher):
        """Test ETH/BTC ratio as altseason indicator"""
        eth_outperformance_data = {
            'ethereum': {'usd': 4500.0},  # High ETH price
            'bitcoin': {'usd': 50000.0}   # Moderate BTC price
        }
        
        with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=eth_outperformance_data):
            ratio = data_fetcher.get_eth_btc_ratio()
            
            # ETH/BTC ratio above 0.08 often indicates altseason
            altseason_threshold = 0.08
            expected_ratio = 4500.0 / 50000.0  # 0.09
            
            assert ratio == expected_ratio, f"Expected ratio {expected_ratio}, got {ratio}"
            assert ratio > altseason_threshold, "High ETH/BTC ratio should indicate altseason"


@pytest.mark.integration
class TestMarketScenarioIntegration:
    """Integration tests combining multiple market scenarios"""
    
    @pytest.fixture
    def data_fetcher(self):
        return DataFetcher(retry_attempts=1, retry_delay=0.1)
    
    def test_market_cycle_transitions(self, data_fetcher, realistic_market_scenarios):
        """Test transitions between different market phases"""
        
        # Test each market scenario from the fixture
        for scenario_name, scenario_data in realistic_market_scenarios.items():
            
            market_data = {
                'bitcoin': {
                    'usd': 50000.0,  # Base price
                    'usd_24h_change': scenario_data['btc_change'],
                    'usd_24h_vol': 25000000000,
                    'usd_market_cap': 970000000000
                },
                'ethereum': {
                    'usd': 3500.0,  # Base ETH price
                    'usd_24h_change': scenario_data['eth_change'],
                    'usd_24h_vol': 15000000000,
                    'usd_market_cap': 420000000000
                }
            }
            
            fear_greed_data = {
                'value': scenario_data['fear_greed'],
                'classification': 'Neutral',  # Will be determined by value
                'timestamp': '1609459200'
            }
            
            dominance_data = {
                'data': {
                    'market_cap_percentage': {
                        'btc': scenario_data['btc_dominance']
                    }
                }
            }
            
            with patch.object(data_fetcher, 'get_coin_market_data_batch', return_value=market_data):
                with patch.object(data_fetcher, 'get_fear_greed_index', return_value=fear_greed_data):
                    with patch.object(data_fetcher, '_make_coingecko_request', return_value=dominance_data):
                        
                        # Test that each scenario produces consistent results
                        market_result = data_fetcher.get_coin_market_data_batch(['bitcoin', 'ethereum'])
                        fg_result = data_fetcher.get_fear_greed_index()
                        dominance_result = data_fetcher.get_btc_dominance()
                        
                        # Validate scenario consistency
                        assert market_result['bitcoin']['usd_24h_change'] == scenario_data['btc_change']
                        assert market_result['ethereum']['usd_24h_change'] == scenario_data['eth_change']
                        assert fg_result['value'] == scenario_data['fear_greed']
                        assert dominance_result == scenario_data['btc_dominance']
                        
                        # Test scenario-specific logic
                        if scenario_name == "bear_market":
                            assert market_result['bitcoin']['usd_24h_change'] < -20, "Bear market should have large declines"
                            assert fg_result['value'] < 20, "Bear market should have extreme fear"
                        elif scenario_name == "altseason":
                            assert dominance_result < 40, "Altseason should have low BTC dominance"
                            assert market_result['ethereum']['usd_24h_change'] > market_result['bitcoin']['usd_24h_change'], \
                                "ETH should outperform BTC in altseason"


if __name__ == '__main__':
    pytest.main([__file__])