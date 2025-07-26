"""
Tests for utility functions
"""

import pytest
import unittest.mock as mock
import os
import sys
import tempfile
import yaml
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils import (
    load_config, validate_config, setup_logging,
    format_percentage, format_currency,
    calculate_time_ago, is_market_open,
    get_env_variable, load_environment,
    CooldownManager
)


class TestConfigUtils:
    """Test configuration utilities"""
    
    def test_load_config_success(self):
        """Test successful config loading"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'coins': [{'symbol': 'BTC', 'name': 'Bitcoin', 'coingecko_id': 'bitcoin'}],
                'indicators': {'rsi_period': 14, 'ma_short': 20, 'ma_long': 50},
                'general': {'update_interval': 300}
            }, f)
            f.flush()
            
            config = load_config(f.name)
            assert 'coins' in config
            assert 'indicators' in config
            assert 'general' in config
            
        os.unlink(f.name)
    
    def test_load_config_file_not_found(self):
        """Test config loading with missing file"""
        with pytest.raises(FileNotFoundError):
            load_config('nonexistent.yaml')
    
    def test_load_config_invalid_yaml(self):
        """Test config loading with invalid YAML"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('invalid: yaml: content: [')
            f.flush()
            
            with pytest.raises(ValueError):
                load_config(f.name)
                
        os.unlink(f.name)
    
    def test_validate_config_valid(self):
        """Test config validation with valid config"""
        valid_config = {
            'coins': [{'symbol': 'BTC', 'name': 'Bitcoin', 'coingecko_id': 'bitcoin'}],
            'indicators': {'rsi_period': 14, 'ma_short': 20, 'ma_long': 50},
            'general': {'update_interval': 300}
        }
        
        assert validate_config(valid_config) == True
    
    def test_validate_config_missing_section(self):
        """Test config validation with missing section"""
        invalid_config = {
            'coins': [{'symbol': 'BTC', 'name': 'Bitcoin', 'coingecko_id': 'bitcoin'}],
            'general': {'update_interval': 300}
            # Missing 'indicators' section
        }
        
        with pytest.raises(ValueError, match="Missing required configuration section: indicators"):
            validate_config(invalid_config)
    
    def test_validate_config_empty_coins(self):
        """Test config validation with empty coins"""
        invalid_config = {
            'coins': [],  # Empty coins list
            'indicators': {'rsi_period': 14, 'ma_short': 20, 'ma_long': 50},
            'general': {'update_interval': 300}
        }
        
        with pytest.raises(ValueError, match="At least one coin must be configured"):
            validate_config(invalid_config)
    
    def test_validate_config_missing_coin_fields(self):
        """Test config validation with missing coin fields"""
        invalid_config = {
            'coins': [{'symbol': 'BTC', 'name': 'Bitcoin'}],  # Missing coingecko_id
            'indicators': {'rsi_period': 14, 'ma_short': 20, 'ma_long': 50},
            'general': {'update_interval': 300}
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            validate_config(invalid_config)


class TestLoggingUtils:
    """Test logging utilities"""
    
    def test_setup_logging_default(self):
        """Test default logging setup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'test.log')
            config = {'logging': {'level': 'INFO', 'file': log_file}}
            
            logger = setup_logging(config)
            assert logger is not None
            assert hasattr(logger, 'handlers')
    
    def test_setup_logging_debug_level(self):
        """Test debug level logging setup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, 'test_debug.log')
            config = {'logging': {'level': 'DEBUG', 'file': log_file}}
            
            logger = setup_logging(config)
            assert logger is not None
            assert hasattr(logger, 'handlers')


class TestEnvironmentUtils:
    """Test environment variable utilities"""
    
    @mock.patch('src.utils.load_dotenv')
    def test_load_environment(self, mock_load_dotenv):
        """Test environment loading"""
        load_environment()
        mock_load_dotenv.assert_called_once()
    
    def test_get_env_variable_exists(self):
        """Test getting existing environment variable"""
        with mock.patch.dict(os.environ, {'TEST_VAR': 'test_value'}):
            result = get_env_variable('TEST_VAR')
            assert result == 'test_value'
    
    def test_get_env_variable_with_default(self):
        """Test getting environment variable with default"""
        result = get_env_variable('MISSING_VAR', 'default_value')
        assert result == 'default_value'
    
    def test_get_env_variable_missing_required(self):
        """Test getting missing required environment variable"""
        with pytest.raises(ValueError, match="Environment variable MISSING_REQUIRED not found"):
            get_env_variable('MISSING_REQUIRED')


class TestFormatUtils:
    """Test formatting utilities"""
    
    def test_format_currency_usd_default(self):
        """Test USD currency formatting"""
        assert format_currency(1234.56) == "$1,234.56"
        assert format_currency(0.01) == "$0.01"
    
    def test_format_currency_other_currencies(self):
        """Test other currency formatting"""
        result = format_currency(1234.56, 'BTC')
        assert 'BTC' in result
        assert '1,234.560000' in result
    
    def test_format_currency_negative(self):
        """Test negative currency formatting"""
        result = format_currency(-1234.56)
        assert '$' in result
        assert '1,234.56' in result
        assert '-' in result
    
    def test_format_currency_zero(self):
        """Test zero currency formatting"""
        assert format_currency(0.0) == "$0.00"
    
    def test_format_percentage_positive(self):
        """Test positive percentage formatting"""
        assert format_percentage(12.34) == "12.34%"
        assert format_percentage(0.1) == "0.10%"
    
    def test_format_percentage_negative(self):
        """Test negative percentage formatting"""
        assert format_percentage(-12.34) == "-12.34%"
        assert format_percentage(-0.1) == "-0.10%"
    
    def test_format_percentage_zero(self):
        """Test zero percentage formatting"""
        assert format_percentage(0.0) == "0.00%"
    
    def test_format_percentage_edge_cases(self):
        """Test percentage formatting edge cases"""
        assert format_percentage(100.0) == "100.00%"
        assert format_percentage(0.001) == "0.00%"


class TestTimeUtils:
    """Test time-related utilities"""
    
    def test_is_market_open_crypto(self):
        """Test crypto market always open"""
        assert is_market_open() == True
    
    def test_calculate_time_ago_seconds(self):
        """Test time calculation for seconds"""
        timestamp = datetime.now() - timedelta(seconds=30)
        result = calculate_time_ago(timestamp)
        assert "Just now" in result
    
    def test_calculate_time_ago_minutes(self):
        """Test time calculation for minutes"""
        timestamp = datetime.now() - timedelta(minutes=30)
        result = calculate_time_ago(timestamp)
        assert "30 minute" in result
    
    def test_calculate_time_ago_hours(self):
        """Test time calculation for hours"""
        timestamp = datetime.now() - timedelta(hours=2)
        result = calculate_time_ago(timestamp)
        assert "2 hour" in result
    
    def test_calculate_time_ago_days(self):
        """Test time calculation for days"""
        timestamp = datetime.now() - timedelta(days=3)
        result = calculate_time_ago(timestamp)
        assert "3 day" in result
    
    def test_calculate_time_ago_future(self):
        """Test time calculation for future timestamp"""
        timestamp = datetime.now() + timedelta(hours=1)
        result = calculate_time_ago(timestamp)
        # Should handle future timestamps gracefully
        assert isinstance(result, str)


class TestCooldownManager:
    """Test cooldown management"""
    
    def test_cooldown_manager_initialization(self):
        """Test cooldown manager initialization"""
        cm = CooldownManager()
        assert cm.last_alerts == {}
    
    def test_can_send_alert_first_time(self):
        """Test first alert is always allowed"""
        cm = CooldownManager()
        assert cm.can_send_alert('price', 'BTC', 60) == True
    
    def test_can_send_alert_within_cooldown(self):
        """Test alert blocked within cooldown period"""
        cm = CooldownManager()
        
        # Send first alert
        assert cm.can_send_alert('price', 'BTC', 60) == True
        
        # Try to send again immediately - should be blocked
        assert cm.can_send_alert('price', 'BTC', 60) == False
    
    def test_can_send_alert_after_cooldown(self):
        """Test alert allowed after cooldown period"""
        cm = CooldownManager()
        
        # Mock the current time to simulate cooldown expiry
        with mock.patch('src.utils.datetime') as mock_datetime:
            # First call
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            assert cm.can_send_alert('price', 'BTC', 60) == True
            
            # Second call after cooldown period
            mock_datetime.now.return_value = datetime(2023, 1, 1, 13, 1, 0)  # 61 minutes later
            assert cm.can_send_alert('price', 'BTC', 60) == True
    
    def test_can_send_alert_different_coins(self):
        """Test alerts for different coins are independent"""
        cm = CooldownManager()
        
        assert cm.can_send_alert('price', 'BTC', 60) == True
        assert cm.can_send_alert('price', 'ETH', 60) == True  # Different coin
    
    def test_can_send_alert_different_types(self):
        """Test different alert types are independent"""
        cm = CooldownManager()
        
        assert cm.can_send_alert('price', 'BTC', 60) == True
        assert cm.can_send_alert('rsi', 'BTC', 60) == True  # Different type
    
    def test_clear_cooldowns(self):
        """Test clearing all cooldowns"""
        cm = CooldownManager()
        
        cm.can_send_alert('price', 'BTC', 60)
        assert len(cm.last_alerts) > 0
        
        cm.clear_cooldowns()
        assert cm.last_alerts == {}
    
    def test_cooldown_key_generation(self):
        """Test cooldown key generation consistency"""
        cm = CooldownManager()
        
        cm.can_send_alert('price', 'BTC', 60)
        assert 'price_BTC' in cm.last_alerts


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_format_currency_invalid_currency(self):
        """Test currency formatting with invalid currency"""
        result = format_currency(1234.56, 'INVALID')
        assert 'INVALID' in result
        assert '1,234.560000' in result
    
    def test_format_percentage_extreme_values(self):
        """Test percentage formatting with extreme values"""
        assert format_percentage(999999.99) == "999999.99%"
        assert format_percentage(-999999.99) == "-999999.99%"
    
    def test_calculate_time_ago_edge_cases(self):
        """Test time calculation edge cases"""
        # Test with very recent timestamp
        timestamp = datetime.now() - timedelta(milliseconds=500)
        result = calculate_time_ago(timestamp)
        assert "Just now" in result
    
    def test_validate_config_edge_cases(self):
        """Test config validation edge cases"""
        # Test with minimal valid config
        minimal_config = {
            'coins': [{'symbol': 'BTC', 'name': 'Bitcoin', 'coingecko_id': 'bitcoin'}],
            'indicators': {'rsi_period': 14, 'ma_short': 20, 'ma_long': 50},
            'general': {}
        }
        assert validate_config(minimal_config) == True
    
    def test_cooldown_manager_edge_cases(self):
        """Test cooldown manager edge cases"""
        cm = CooldownManager()
        
        # Test with zero cooldown
        assert cm.can_send_alert('test', 'BTC', 0) == True
        assert cm.can_send_alert('test', 'BTC', 0) == True  # Should allow immediately
    
    def test_get_env_variable_empty_string(self):
        """Test environment variable with empty string value"""
        with mock.patch.dict(os.environ, {'EMPTY_VAR': ''}):
            result = get_env_variable('EMPTY_VAR', 'default')
            assert result == ''  # Empty string is a valid value
