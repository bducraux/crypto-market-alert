"""
Unit tests for strategic advisor module
"""

import pytest
from unittest.mock import Mock, patch
from src.strategic_advisor import StrategicAdvisor
from src.utils import load_config


class TestStrategicAdvisor:
    """Test cases for StrategicAdvisor class"""
    
    @pytest.fixture
    def advisor(self):
        """Create a StrategicAdvisor instance for testing"""
        return StrategicAdvisor()
    
    @pytest.fixture
    def mock_config(self):
        """Create mock configuration for testing"""
        return {
            'coins': [
                {'symbol': 'BTC', 'name': 'Bitcoin'},
                {'symbol': 'ETH', 'name': 'Ethereum'}
            ],
            'alerts': {
                'enabled': True
            }
        }
    
    def test_initialization(self, advisor):
        """Test StrategicAdvisor initialization"""
        assert advisor is not None
        assert hasattr(advisor, 'config')
        assert hasattr(advisor, 'data_fetcher')
        assert hasattr(advisor, 'indicators')
    
    @patch('src.strategic_advisor.load_config')
    def test_generate_strategic_report_success(self, mock_load_config, advisor):
        """Test successful strategic report generation"""
        mock_load_config.return_value = {
            'coins': [{'symbol': 'BTC', 'name': 'Bitcoin'}]
        }
        
        report = advisor.generate_strategic_report()
        
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_generate_strategic_report_error_handling(self, advisor):
        """Test error handling in strategic report generation"""
        with patch.object(advisor, 'data_fetcher') as mock_fetcher:
            mock_fetcher.get_coin_market_data_batch.side_effect = Exception("Network error")
            
            report = advisor.generate_strategic_report()
            
            assert "Erro" in report or "Error" in report


class TestStrategicAdvisorIntegration:
    """Integration tests for StrategicAdvisor"""
    
    @patch('src.utils.load_config')
    def test_strategy_integration(self, mock_load_config):
        """Test strategic advisor integration with strategy"""
        mock_load_config.return_value = {
            'coins': [{'symbol': 'BTC', 'name': 'Bitcoin'}],
            'alerts': {'enabled': True}
        }
        
        try:
            from src.strategy import AlertStrategy
            strategy = AlertStrategy(mock_load_config.return_value)
            
            # Check if strategic advisor is available
            assert strategy is not None
            
        except ImportError:
            pytest.skip("AlertStrategy not available for integration test")
