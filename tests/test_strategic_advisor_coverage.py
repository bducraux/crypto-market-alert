"""
Strategic Advisor Coverage Tests
Tests specifically designed to improve coverage for strategic_advisor.py
Focuses on error handling, edge cases, and uncovered code paths
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.strategic_advisor import StrategicAdvisor


class TestStrategicAdvisorErrorHandling:
    """Test error handling and edge cases in StrategicAdvisor"""
    
    @pytest.fixture
    def advisor(self):
        """Create StrategicAdvisor instance for testing"""
        with patch('src.strategic_advisor.load_config') as mock_config:
            mock_config.return_value = {
                'coins': [
                    {'symbol': 'BTC', 'coingecko_id': 'bitcoin', 'avg_price': 30000},
                    {'symbol': 'ETH', 'coingecko_id': 'ethereum', 'avg_price': 2000}
                ]
            }
            return StrategicAdvisor()
    
    def test_analyze_strategic_position_exception_handling(self, advisor):
        """Test exception handling in analyze_strategic_position - covers line 84-85"""
        with patch.object(advisor.data_fetcher, 'get_coin_market_data_batch', side_effect=Exception("API Error")):
            result = advisor.analyze_strategic_position()
            
            assert 'error' in result
            assert 'API Error' in result['error']
    
    def test_eth_btc_analysis_missing_btc_data(self, advisor):
        """Test ETH/BTC analysis with missing BTC data - covers line 94"""
        data = {
            'ethereum': {'usd': 3000}
            # Missing bitcoin data
        }
        
        result = advisor._analyze_eth_btc_ratio(data)
        
        assert 'error' in result
        assert 'Missing BTC or ETH data' in result['error']
    
    def test_eth_btc_analysis_missing_eth_data(self, advisor):
        """Test ETH/BTC analysis with missing ETH data - covers line 94"""
        data = {
            'bitcoin': {'usd': 50000}
            # Missing ethereum data
        }
        
        result = advisor._analyze_eth_btc_ratio(data)
        
        assert 'error' in result
        assert 'Missing BTC or ETH data' in result['error']
    
    def test_eth_btc_analysis_zero_btc_price(self, advisor):
        """Test ETH/BTC analysis with zero BTC price - covers line 100"""
        data = {
            'bitcoin': {'usd': 0},  # Zero price
            'ethereum': {'usd': 3000}
        }
        
        result = advisor._analyze_eth_btc_ratio(data)
        
        assert 'error' in result
        assert 'Invalid price data' in result['error']
    
    def test_eth_btc_analysis_zero_eth_price(self, advisor):
        """Test ETH/BTC analysis with zero ETH price - covers line 100"""
        data = {
            'bitcoin': {'usd': 50000},
            'ethereum': {'usd': 0}  # Zero price
        }
        
        result = advisor._analyze_eth_btc_ratio(data)
        
        assert 'error' in result
        assert 'Invalid price data' in result['error']
    
    def test_eth_btc_analysis_btc_indicators_exception(self, advisor):
        """Test BTC indicators calculation exception - covers line 120-121"""
        data = {
            'bitcoin': {
                'usd': 50000,
                'historical': pd.DataFrame({'close': [50000, 51000, 49000]})
            },
            'ethereum': {'usd': 3000}
        }
        
        with patch.object(advisor.indicators, 'get_latest_indicator_values', side_effect=Exception("Indicator error")):
            result = advisor._analyze_eth_btc_ratio(data)
            
            # Should handle exception gracefully and use default values
            assert 'error' not in result
            assert result['btc_rsi'] == 50  # Default value
    
    def test_eth_btc_analysis_eth_indicators_exception(self, advisor):
        """Test ETH indicators calculation exception - covers line 130-131"""
        data = {
            'bitcoin': {'usd': 50000},
            'ethereum': {
                'usd': 3000,
                'historical': pd.DataFrame({'close': [3000, 3100, 2900]})
            }
        }
        
        # Mock indicators to always fail
        with patch.object(advisor.indicators, 'get_latest_indicator_values', side_effect=Exception("Indicator error")):
            result = advisor._analyze_eth_btc_ratio(data)
            
            # Should handle exception gracefully and use default values
            assert 'error' not in result
            assert result['eth_rsi'] == 50  # Default value
            assert result['btc_rsi'] == 50  # Default value
    
    def test_eth_btc_analysis_general_exception(self, advisor):
        """Test general exception in ETH/BTC analysis - covers line 155-156"""
        data = {
            'bitcoin': {'usd': 50000},
            'ethereum': {'usd': 3000}
        }
        
        with patch.object(advisor, '_calculate_swap_signal', side_effect=Exception("Swap calculation error")):
            result = advisor._analyze_eth_btc_ratio(data)
            
            assert 'error' in result
            assert 'Swap calculation error' in result['error']


class TestStrategicAdvisorSwapSignalEdgeCases:
    """Test swap signal calculation edge cases"""
    
    @pytest.fixture
    def advisor(self):
        with patch('src.strategic_advisor.load_config') as mock_config:
            mock_config.return_value = {'coins': []}
            return StrategicAdvisor()
    
    def test_swap_signal_eth_oversold_high_confidence(self, advisor):
        """Test ETH oversold scenario with high confidence - covers lines 174-176"""
        # ETH heavily oversold vs BTC
        ratio = 0.03  # Below ratio_low (0.04)
        btc_rsi = 65   # Above 60
        eth_rsi = 35   # Below 40
        btc_vs_ma200 = 10
        eth_vs_ma200 = 5
        
        result = advisor._calculate_swap_signal(ratio, btc_rsi, eth_rsi, btc_vs_ma200, eth_vs_ma200)
        
        assert result['action'] == 'SWAP_BTC_TO_ETH'
        assert result['confidence'] == 'HIGH'
        assert 'ETH heavily oversold vs BTC' in result['signals']
    
    def test_swap_signal_btc_overextended_eth_lagging(self, advisor):
        """Test BTC overextended, ETH lagging scenario - covers lines 178-180"""
        ratio = 0.03  # Below ratio_low
        btc_rsi = 55   # Not > 60
        eth_rsi = 45   # Not < 40
        btc_vs_ma200 = 25  # Above 20
        eth_vs_ma200 = -5  # Below 0
        
        result = advisor._calculate_swap_signal(ratio, btc_rsi, eth_rsi, btc_vs_ma200, eth_vs_ma200)
        
        assert result['action'] == 'SWAP_BTC_TO_ETH'
        assert result['confidence'] == 'MEDIUM'
        assert 'BTC overextended, ETH lagging' in result['signals']
    
    def test_swap_signal_eth_overbought_high_confidence(self, advisor):
        """Test ETH overbought scenario - covers lines 185-187"""
        ratio = 0.09  # Above ratio_high (0.08)
        btc_rsi = 45   # Below 50
        eth_rsi = 75   # Above 70
        btc_vs_ma200 = 5
        eth_vs_ma200 = 15
        
        result = advisor._calculate_swap_signal(ratio, btc_rsi, eth_rsi, btc_vs_ma200, eth_vs_ma200)
        
        assert result['action'] == 'SWAP_ETH_TO_BTC'
        assert result['confidence'] == 'HIGH'
        assert 'ETH overbought vs BTC' in result['signals']
    
    def test_swap_signal_eth_extremely_expensive(self, advisor):
        """Test ETH extremely expensive scenario - covers lines 189-191"""
        ratio = 0.11  # Above ratio_extreme_high (0.10)
        btc_rsi = 55
        eth_rsi = 65
        btc_vs_ma200 = 10
        eth_vs_ma200 = 20
        
        result = advisor._calculate_swap_signal(ratio, btc_rsi, eth_rsi, btc_vs_ma200, eth_vs_ma200)
        
        assert result['action'] == 'SWAP_ETH_TO_BTC'
        assert result['confidence'] == 'HIGH'
        assert 'ETH extremely expensive vs BTC' in result['signals']
    
    def test_swap_signal_btc_momentum_favor_eth(self, advisor):
        """Test BTC momentum scenario favoring ETH - covers lines 195-198"""
        ratio = 0.06  # Normal range
        btc_rsi = 85   # Above 80
        eth_rsi = 35   # Below 40
        btc_vs_ma200 = 15
        eth_vs_ma200 = 5
        
        result = advisor._calculate_swap_signal(ratio, btc_rsi, eth_rsi, btc_vs_ma200, eth_vs_ma200)
        
        assert result['action'] == 'FAVOR_ETH'
        assert result['confidence'] == 'MEDIUM'
        assert 'Strong BTC momentum, ETH lagging - consider ETH' in result['signals']


class TestStrategicAdvisorAltseasonAnalysis:
    """Test altseason analysis edge cases"""
    
    @pytest.fixture
    def advisor(self):
        with patch('src.strategic_advisor.load_config') as mock_config:
            mock_config.return_value = {'coins': []}
            return StrategicAdvisor()
    
    def test_altseason_analysis_missing_btc_dominance(self, advisor):
        """Test altseason analysis with missing BTC dominance - covers error handling"""
        data = {
            'bitcoin': {'usd': 50000, 'usd_24h_change': 5.0},
            'ethereum': {'usd': 3000, 'usd_24h_change': 8.0}
        }
        market_metrics = {}  # Missing btc_dominance
        
        result = advisor._analyze_altseason(data, market_metrics)
        
        # Should handle missing dominance gracefully
        assert 'score' in result
        assert result['score'] >= 0
    
    def test_altseason_analysis_extreme_dominance_values(self, advisor):
        """Test altseason analysis with extreme dominance values"""
        data = {
            'bitcoin': {'usd': 50000, 'usd_24h_change': -2.0},
            'ethereum': {'usd': 3000, 'usd_24h_change': 15.0}
        }
        market_metrics = {'btc_dominance': 25.0}  # Very low dominance
        
        result = advisor._analyze_altseason(data, market_metrics)
        
        assert result['score'] >= 40  # Should indicate altseason activity
        assert 'ALTSEASON' in result['phase']


class TestStrategicAdvisorAltcoinAnalysis:
    """Test altcoin analysis edge cases"""
    
    @pytest.fixture
    def advisor(self):
        with patch('src.strategic_advisor.load_config') as mock_config:
            mock_config.return_value = {
                'coins': [
                    {'symbol': 'ADA', 'coingecko_id': 'cardano', 'avg_price': 0.5}
                ]
            }
            return StrategicAdvisor()
    
    def test_altcoin_analysis_missing_coin_data(self, advisor):
        """Test altcoin analysis with missing coin data - covers error paths"""
        data = {}  # No coin data
        
        result = advisor._analyze_altcoins(data)
        
        assert isinstance(result, list)
        assert len(result) == 0  # Should return empty list for missing data
    
    def test_single_altcoin_analysis_missing_price(self, advisor):
        """Test single altcoin analysis with missing price data"""
        coin_config = {'symbol': 'ADA', 'avg_price': 0.5}
        coin_data = {}  # Missing price data
        
        result = advisor._analyze_single_altcoin(coin_config, coin_data)
        
        # Should handle missing price gracefully
        assert result is None or 'error' in result
    
    def test_altcoin_opportunity_score_extreme_values(self, advisor):
        """Test opportunity score calculation with extreme values"""
        # Test with extreme profit - should still be reasonable score
        score = advisor._calculate_altcoin_opportunity_score(
            pnl_percent=500.0,  # 500% profit
            rsi=20,  # Oversold
            above_ma_50=False,
            above_ma_200=False
        )
        assert score >= 0  # Should be valid score
        assert score <= 100  # Should be within bounds
        
        # Test with extreme loss
        score = advisor._calculate_altcoin_opportunity_score(
            pnl_percent=-80.0,  # 80% loss
            rsi=80,  # Overbought
            above_ma_50=True,
            above_ma_200=True
        )
        assert score >= 0  # Should be valid score
        assert score <= 100  # Should be within bounds


class TestStrategicAdvisorPortfolioCalculations:
    """Test portfolio calculation edge cases"""
    
    @pytest.fixture
    def advisor(self):
        with patch('src.strategic_advisor.load_config') as mock_config:
            mock_config.return_value = {
                'coins': [
                    {'symbol': 'BTC', 'coingecko_id': 'bitcoin', 'avg_price': 30000},
                    {'symbol': 'ETH', 'coingecko_id': 'ethereum', 'avg_price': 2000}
                ]
            }
            return StrategicAdvisor()
    
    def test_goal_progress_missing_data(self, advisor):
        """Test goal progress calculation with missing data - covers error paths"""
        data = {}  # No coin data
        
        result = advisor._calculate_goal_progress(data)
        
        assert 'goal_value_usd' in result
        assert result['goal_value_usd'] == 0.0  # Should default to 0
    
    def test_portfolio_achievement_empty_altcoins(self, advisor):
        """Test portfolio achievement with empty altcoins list"""
        altcoins = []  # Empty list
        progress = {'total_value': 0, 'btc_equivalent': 0}
        
        result = advisor._calculate_portfolio_achievement(altcoins, progress)
        
        # Should handle empty altcoins gracefully
        assert isinstance(result, dict)  # Should return a dict even if empty
    
    def test_cycle_top_risk_missing_analysis(self, advisor):
        """Test cycle top risk with missing analysis data"""
        analysis = {}  # Empty analysis
        
        result = advisor._calculate_cycle_top_risk(analysis)
        
        assert 'score' in result
        assert 0 <= result['score'] <= 100


if __name__ == '__main__':
    pytest.main([__file__])