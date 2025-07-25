"""
Telegram alerts module for sending notifications
Handles Telegram bot integration and message formatting
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import telegram
from telegram.error import TelegramError


class TelegramAlertsManager:
    """Manages Telegram bot integration for sending crypto market alerts"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Telegram alerts manager
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID for sending messages
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=bot_token)
        self.logger = logging.getLogger(__name__)
    
    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a message via Telegram
        
        Args:
            message: Message text to send
            parse_mode: Message parsing mode (HTML, Markdown, or None)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
            self.logger.info(f"Telegram message sent successfully")
            return True
            
        except TelegramError as e:
            self.logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def format_alert_message(self, alert: Dict[str, Any]) -> str:
        """
        Format an alert into a readable Telegram message
        
        Args:
            alert: Alert dictionary
            
        Returns:
            Formatted message string
        """
        message = alert.get('message', 'Unknown alert')
        alert_type = alert.get('type', 'unknown')
        coin = alert.get('coin', 'Unknown')
        priority = alert.get('priority', 'medium')
        
        # Add priority emoji
        priority_emoji = {
            'high': '🚨',
            'medium': '⚠️',
            'low': 'ℹ️'
        }
        
        emoji = priority_emoji.get(priority, 'ℹ️')
        
        # Format timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        formatted_message = f"{emoji} <b>[{timestamp}] {message}</b>\n"
        
        # Add additional details based on alert type
        if alert_type.startswith('price'):
            current_price = alert.get('current_price')
            threshold = alert.get('threshold')
            if current_price and threshold:
                formatted_message += f"💰 Current: ${current_price:,.2f}\n"
                formatted_message += f"🎯 Threshold: ${threshold:,.2f}\n"
        
        elif alert_type.startswith('rsi'):
            rsi_value = alert.get('rsi_value')
            threshold = alert.get('threshold')
            if rsi_value and threshold:
                formatted_message += f"📊 RSI: {rsi_value:.2f}\n"
                formatted_message += f"🎯 Threshold: {threshold}\n"
        
        elif 'dominance' in alert_type:
            value = alert.get('value')
            threshold = alert.get('threshold')
            if value and threshold:
                formatted_message += f"📊 Current: {value:.2f}%\n"
                formatted_message += f"🎯 Threshold: {threshold}%\n"
        
        elif 'ratio' in alert_type:
            value = alert.get('value')
            threshold = alert.get('threshold')
            if value and threshold:
                formatted_message += f"📊 Current: {value:.6f}\n"
                formatted_message += f"🎯 Threshold: {threshold:.6f}\n"
        
        elif alert_type in ['extreme_fear', 'extreme_greed']:
            value = alert.get('value')
            classification = alert.get('classification')
            if value:
                formatted_message += f"📊 Index: {value}/100\n"
            if classification:
                formatted_message += f"📝 Status: {classification}\n"
        
        return formatted_message
    
    def format_summary_message(self, summary: Dict[str, Any], alerts_count: int) -> str:
        """
        Format a market summary message
        
        Args:
            summary: Market summary dictionary
            alerts_count: Number of alerts triggered
            
        Returns:
            Formatted summary message
        """
        timestamp = summary.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"📊 <b>Market Summary - {timestamp}</b>\n\n"
        
        # Market metrics
        market_metrics = summary.get('market_metrics', {})
        if market_metrics:
            message += "🌍 <b>Market Metrics:</b>\n"
            
            btc_dominance = market_metrics.get('btc_dominance')
            if btc_dominance:
                message += f"• BTC Dominance: {btc_dominance:.2f}%\n"
            
            eth_btc_ratio = market_metrics.get('eth_btc_ratio')
            if eth_btc_ratio:
                message += f"• ETH/BTC Ratio: {eth_btc_ratio:.6f}\n"
            
            fear_greed = market_metrics.get('fear_greed_index')
            if fear_greed:
                value = fear_greed.get('value', 0)
                classification = fear_greed.get('value_classification', 'Unknown')
                message += f"• Fear & Greed: {value}/100 ({classification})\n"
            
            message += "\n"
        
        # Coin prices
        coins = summary.get('coins', {})
        if coins:
            message += "💰 <b>Coin Prices:</b>\n"
            for coin_name, coin_data in coins.items():
                price = coin_data.get('price')
                change_24h = coin_data.get('change_24h')
                
                if price:
                    change_emoji = "📈" if change_24h and change_24h > 0 else "📉" if change_24h and change_24h < 0 else "➡️"
                    change_text = f" ({change_24h:+.2f}%)" if change_24h else ""
                    message += f"• {coin_name}: ${price:,.2f}{change_text} {change_emoji}\n"
            
            message += "\n"
        
        # Alerts summary
        message += f"🚨 <b>Active Alerts: {alerts_count}</b>\n"
        
        return message
    
    async def send_alert(self, alert: Dict[str, Any]) -> bool:
        """
        Send a single alert message
        
        Args:
            alert: Alert dictionary
            
        Returns:
            True if sent successfully
        """
        message = self.format_alert_message(alert)
        return await self.send_message(message)
    
    async def send_multiple_alerts(self, alerts: List[Dict[str, Any]], batch_size: int = 5) -> int:
        """
        Send multiple alerts, potentially batching them
        
        Args:
            alerts: List of alert dictionaries
            batch_size: Maximum number of alerts to send in one message
            
        Returns:
            Number of successfully sent messages
        """
        if not alerts:
            return 0
        
        sent_count = 0
        
        # Group alerts by priority
        high_priority = [a for a in alerts if a.get('priority') == 'high']
        other_alerts = [a for a in alerts if a.get('priority') != 'high']
        
        # Send high priority alerts individually
        for alert in high_priority:
            if await self.send_alert(alert):
                sent_count += 1
                await asyncio.sleep(1)  # Rate limiting
        
        # Batch other alerts if there are many
        if len(other_alerts) > batch_size:
            message = f"📊 <b>Market Alert Summary ({len(other_alerts)} alerts)</b>\n\n"
            for alert in other_alerts[:10]:  # Show first 10
                message += f"• {alert.get('message', 'Unknown alert')}\n"
            
            if len(other_alerts) > 10:
                message += f"\n... and {len(other_alerts) - 10} more alerts"
            
            if await self.send_message(message):
                sent_count += 1
        else:
            # Send individually if not too many
            for alert in other_alerts:
                if await self.send_alert(alert):
                    sent_count += 1
                    await asyncio.sleep(1)  # Rate limiting
        
        return sent_count
    
    async def send_summary(self, summary: Dict[str, Any], alerts: List[Dict[str, Any]]) -> bool:
        """
        Send a market summary message
        
        Args:
            summary: Market summary dictionary
            alerts: List of current alerts
            
        Returns:
            True if sent successfully
        """
        message = self.format_summary_message(summary, len(alerts))
        return await self.send_message(message)
    
    async def send_startup_message(self) -> bool:
        """
        Send a startup message when the bot begins monitoring
        
        Returns:
            True if sent successfully
        """
        message = (
            "🤖 <b>Crypto Market Alert Bot Started</b>\n\n"
            "📊 Monitoring cryptocurrency markets...\n"
            "🔔 You'll receive alerts when conditions are met\n\n"
            f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return await self.send_message(message)
    
    async def send_error_message(self, error_type: str, error_details: str) -> bool:
        """
        Send an error notification message
        
        Args:
            error_type: Type of error
            error_details: Error details
            
        Returns:
            True if sent successfully
        """
        message = (
            f"⚠️ <b>Alert System Error</b>\n\n"
            f"🔍 Type: {error_type}\n"
            f"📝 Details: {error_details}\n\n"
            f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        return await self.send_message(message)
    
    async def test_connection(self) -> bool:
        """
        Test the Telegram bot connection
        
        Returns:
            True if connection is working
        """
        try:
            me = await self.bot.get_me()
            self.logger.info(f"Telegram bot connection successful: @{me.username}")
            return True
        except Exception as e:
            self.logger.error(f"Telegram bot connection failed: {e}")
            return False


class AlertsOrchestrator:
    """Orchestrates the alert system with multiple notification channels"""
    
    def __init__(self, telegram_manager: TelegramAlertsManager):
        """
        Initialize alerts orchestrator
        
        Args:
            telegram_manager: Telegram alerts manager instance
        """
        self.telegram = telegram_manager
        self.logger = logging.getLogger(__name__)
    
    async def send_alerts(self, alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Send alerts through all configured channels
        
        Args:
            alerts: List of alerts to send
            
        Returns:
            Dictionary with send results
        """
        results = {
            'telegram_sent': 0,
            'total_alerts': len(alerts)
        }
        
        if alerts:
            self.logger.info(f"Sending {len(alerts)} alerts")
            telegram_sent = await self.telegram.send_multiple_alerts(alerts)
            results['telegram_sent'] = telegram_sent
        
        return results
    
    async def send_periodic_summary(self, summary: Dict[str, Any], alerts: List[Dict[str, Any]]) -> bool:
        """
        Send periodic market summary
        
        Args:
            summary: Market summary data
            alerts: Current alerts list
            
        Returns:
            True if summary sent successfully
        """
        return await self.telegram.send_summary(summary, alerts)
    
    async def initialize(self) -> bool:
        """
        Initialize all notification channels
        
        Returns:
            True if initialization successful
        """
        # Test Telegram connection
        telegram_ok = await self.telegram.test_connection()
        
        if telegram_ok:
            await self.telegram.send_startup_message()
            self.logger.info("Alert system initialized successfully")
            return True
        else:
            self.logger.error("Failed to initialize alert system")
            return False
