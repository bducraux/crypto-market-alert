"""
Utility functions for the crypto market alert system
"""

import logging
import yaml
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration data
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {e}")


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured logger instance
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_file = log_config.get('file', 'logs/crypto_alerts.log')
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger('crypto_alert')
    return logger


def load_environment() -> None:
    """Load environment variables from .env file"""
    load_dotenv()


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with optional default
    
    Args:
        var_name: Name of the environment variable
        default: Default value if variable is not found
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If variable is not found and no default provided
    """
    value = os.getenv(var_name, default)
    if value is None:
        raise ValueError(f"Environment variable {var_name} not found")
    return value


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format currency amount for display
    
    Args:
        amount: Amount to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.6f} {currency}"


def format_percentage(value: float) -> str:
    """
    Format percentage for display
    
    Args:
        value: Percentage value
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.2f}%"


def is_market_open() -> bool:
    """
    Check if crypto market is considered 'active'
    (Crypto markets are 24/7, but this can be used for timing)
    
    Returns:
        Always True for crypto markets
    """
    return True


def calculate_time_ago(timestamp: datetime) -> str:
    """
    Calculate human-readable time difference
    
    Args:
        timestamp: Timestamp to compare
        
    Returns:
        Human-readable time difference string
    """
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration structure and required fields
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_sections = ['coins', 'indicators', 'general']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate coins configuration
    if not config['coins']:
        raise ValueError("At least one coin must be configured")
    
    for coin in config['coins']:
        required_coin_fields = ['symbol', 'name', 'coingecko_id']
        for field in required_coin_fields:
            if field not in coin:
                raise ValueError(f"Missing required field '{field}' in coin configuration")
    
    # Validate indicators
    indicator_config = config['indicators']
    required_indicators = ['rsi_period', 'ma_short', 'ma_long']
    for indicator in required_indicators:
        if indicator not in indicator_config:
            raise ValueError(f"Missing required indicator configuration: {indicator}")
    
    return True


class CooldownManager:
    """Manage alert cooldown periods to prevent spam"""
    
    def __init__(self):
        self.last_alerts = {}
    
    def can_send_alert(self, alert_type: str, coin: str, cooldown_minutes: int) -> bool:
        """
        Check if enough time has passed since last alert of this type
        
        Args:
            alert_type: Type of alert (e.g., 'price', 'rsi')
            coin: Coin symbol
            cooldown_minutes: Cooldown period in minutes
            
        Returns:
            True if alert can be sent
        """
        key = f"{alert_type}_{coin}"
        now = datetime.now()
        
        if key not in self.last_alerts:
            self.last_alerts[key] = now
            return True
        
        time_diff = now - self.last_alerts[key]
        if time_diff >= timedelta(minutes=cooldown_minutes):
            self.last_alerts[key] = now
            return True
        
        return False
    
    def clear_cooldowns(self):
        """Clear all cooldown timers"""
        self.last_alerts.clear()
