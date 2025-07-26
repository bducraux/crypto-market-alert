"""
Comprehensive tests for alerts module
Tests Telegram integration, message formatting, and alert orchestration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from telegram.error import TelegramError

from src.alerts import TelegramAlertsManager, AlertsOrchestrator


class TestTelegramAlertsManager:
    """Test Telegram alerts manager functionality"""
    
    @pytest.fixture
    def telegram_manager(self):
        """Create a TelegramAlertsManager instance for testing"""
        return TelegramAlertsManager(
            bot_token="test_token",
            chat_id="test_chat_id"
        )
    
    @pytest.fixture
    def mock_bot(self, telegram_manager):
        """Mock the Telegram bot"""
        with patch.object(telegram_manager, 'bot') as mock:
            mock.send_message = AsyncMock(return_value=True)
            mock.get_me = AsyncMock(return_value=Mock(username="test_bot"))
            yield mock
    
    def test_init(self):
        """Test TelegramAlertsManager initialization"""
        manager = TelegramAlertsManager("token123", "chat456")
        assert manager.bot_token == "token123"
        assert manager.chat_id == "chat456"
        assert manager.bot is not None
        assert manager.logger is not None
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, telegram_manager, mock_bot):
        """Test successful message sending"""
        result = await telegram_manager.send_message("Test message")
        
        assert result is True
        mock_bot.send_message.assert_called_once_with(
            chat_id="test_chat_id",
            text="Test message",
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    
    @pytest.mark.asyncio
    async def test_send_message_telegram_error(self, telegram_manager, mock_bot):
        """Test handling of Telegram errors"""
        mock_bot.send_message.side_effect = TelegramError("API error")
        
        result = await telegram_manager.send_message("Test message")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_send_message_unexpected_error(self, telegram_manager, mock_bot):
        """Test handling of unexpected errors"""
        mock_bot.send_message.side_effect = Exception("Unexpected error")
        
        result = await telegram_manager.send_message("Test message")
        
        assert result is False
    
    def test_format_alert_message_basic(self, telegram_manager):
        """Test basic alert message formatting"""
        alert = {
            'message': 'Test alert',
            'type': 'test',
            'coin': 'BTC',
            'priority': 'high'
        }
        
        formatted = telegram_manager.format_alert_message(alert)
        
        assert '🚨' in formatted  # High priority emoji
        assert 'Test alert' in formatted
        assert '[' in formatted  # Timestamp bracket
        assert ']' in formatted
    
    @pytest.mark.parametrize("current_price,threshold", [
        (45000.50, 45000.00), (67890.12, 67000.00), (32500.75, 32000.00),
        (89123.45, 89000.00), (123456.78, 123000.00)
    ])
    def test_format_alert_message_price_alert(self, telegram_manager, current_price, threshold):
        """Test price alert formatting with realistic price ranges"""
        alert = {
            'message': 'BTC price alert',
            'type': 'price_breakout',
            'coin': 'BTC',
            'priority': 'medium',
            'current_price': current_price,
            'threshold': threshold
        }
        
        formatted = telegram_manager.format_alert_message(alert)
        
        # Test actual formatting logic instead of hardcoded assertions
        assert '⚠️' in formatted  # Medium priority emoji
        assert 'BTC price alert' in formatted
        assert '💰' in formatted
        assert '🎯' in formatted
        
        # Verify price formatting is correct
        formatted_current = f"${current_price:,.2f}"
        formatted_threshold = f"${threshold:,.2f}"
        assert formatted_current in formatted
        assert formatted_threshold in formatted
    
    @pytest.mark.parametrize("rsi_value,threshold", [
        (78.5, 70), (85.2, 70), (72.3, 70), (25.8, 30), (15.4, 30)
    ])
    def test_format_alert_message_rsi_alert(self, telegram_manager, rsi_value, threshold):
        """Test RSI alert formatting with realistic RSI ranges"""
        alert_type = 'rsi_overbought' if rsi_value > 50 else 'rsi_oversold'
        message = 'RSI overbought' if rsi_value > 50 else 'RSI oversold'
        
        alert = {
            'message': message,
            'type': alert_type,
            'coin': 'ETH',
            'priority': 'low',
            'rsi_value': rsi_value,
            'threshold': threshold
        }
        
        formatted = telegram_manager.format_alert_message(alert)
        
        # Test actual RSI formatting logic instead of hardcoded assertions
        assert 'ℹ️' in formatted  # Low priority emoji
        assert message in formatted
        assert '📊' in formatted
        
        # Verify RSI formatting is correct
        formatted_rsi = f"RSI: {rsi_value:.2f}"
        formatted_threshold = f"Threshold: {threshold}"
        assert formatted_rsi in formatted
        assert formatted_threshold in formatted
        assert 0 <= rsi_value <= 100  # Valid RSI range
    
    def test_format_alert_message_dominance_alert(self, telegram_manager):
        """Test dominance alert formatting"""
        alert = {
            'message': 'BTC dominance high',
            'type': 'btc_dominance_high',
            'coin': 'BTC',
            'priority': 'medium',
            'value': 65.5,
            'threshold': 65.0
        }
        
        formatted = telegram_manager.format_alert_message(alert)
        
        assert 'BTC dominance high' in formatted
        assert 'Current: 65.50%' in formatted
        assert 'Threshold: 65.0%' in formatted
    
    def test_format_alert_message_ratio_alert(self, telegram_manager):
        """Test ratio alert formatting"""
        alert = {
            'message': 'ETH/BTC ratio alert',
            'type': 'eth_btc_ratio_low',
            'coin': 'ETH',
            'priority': 'medium',
            'value': 0.065432,
            'threshold': 0.065000
        }
        
        formatted = telegram_manager.format_alert_message(alert)
        
        assert 'ETH/BTC ratio alert' in formatted
        assert 'Current: 0.065432' in formatted
        assert 'Threshold: 0.065000' in formatted
    
    def test_format_alert_message_fear_greed_alert(self, telegram_manager):
        """Test Fear & Greed alert formatting"""
        alert = {
            'message': 'Extreme fear detected',
            'type': 'extreme_fear',
            'coin': 'Market',
            'priority': 'high',
            'value': 15,
            'classification': 'Extreme Fear'
        }
        
        formatted = telegram_manager.format_alert_message(alert)
        
        assert 'Extreme fear detected' in formatted
        assert 'Index: 15/100' in formatted
        assert 'Status: Extreme Fear' in formatted
    
    def test_format_alert_message_missing_fields(self, telegram_manager):
        """Test formatting with missing fields"""
        alert = {}
        
        formatted = telegram_manager.format_alert_message(alert)
        
        assert 'Unknown alert' in formatted
        assert '⚠️' in formatted  # Default medium priority
    
    def test_format_summary_message(self, telegram_manager):
        """Test market summary formatting"""
        summary = {
            'timestamp': datetime(2024, 1, 15, 10, 30, 0),
            'market_metrics': {
                'btc_dominance': 65.5,
                'eth_btc_ratio': 0.065432,
                'fear_greed_index': {
                    'value': 45,
                    'value_classification': 'Neutral'
                }
            },
            'coins': {
                'BTC': {
                    'price': 45000.50,
                    'change_24h': 2.5
                },
                'ETH': {
                    'price': 2800.75,
                    'change_24h': -1.2
                }
            }
        }
        
        formatted = telegram_manager.format_summary_message(summary, 3)
        
        assert 'Market Summary' in formatted
        assert 'BTC Dominance: 65.50%' in formatted
        assert 'ETH/BTC Ratio: 0.065432' in formatted
        assert 'Fear & Greed: 45/100 (Neutral)' in formatted
        assert 'BTC: $45,000.50 (+2.50%)' in formatted
        assert 'ETH: $2,800.75 (-1.20%)' in formatted
        assert 'Active Alerts: 3' in formatted
        assert '📈' in formatted  # BTC positive change
        assert '📉' in formatted  # ETH negative change
    
    def test_format_summary_message_minimal(self, telegram_manager):
        """Test summary formatting with minimal data"""
        summary = {}
        
        formatted = telegram_manager.format_summary_message(summary, 0)
        
        assert 'Market Summary' in formatted
        assert 'Active Alerts: 0' in formatted
    
    @pytest.mark.asyncio
    async def test_send_alert(self, telegram_manager, mock_bot):
        """Test sending a single alert"""
        alert = {
            'message': 'Test alert',
            'type': 'test',
            'priority': 'medium'
        }
        
        result = await telegram_manager.send_alert(alert)
        
        assert result is True
        mock_bot.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_multiple_alerts_small_batch(self, telegram_manager, mock_bot):
        """Test sending a small batch of alerts"""
        alerts = [
            {'message': 'Alert 1', 'priority': 'medium'},
            {'message': 'Alert 2', 'priority': 'low'},
            {'message': 'Alert 3', 'priority': 'high'}
        ]
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            sent_count = await telegram_manager.send_multiple_alerts(alerts)
        
        assert sent_count == 3
        assert mock_bot.send_message.call_count == 3
    
    @pytest.mark.asyncio
    async def test_send_multiple_alerts_large_batch(self, telegram_manager, mock_bot):
        """Test sending a large batch of alerts (should be summarized)"""
        alerts = [
            {'message': f'Alert {i}', 'priority': 'low'} 
            for i in range(10)
        ]
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            sent_count = await telegram_manager.send_multiple_alerts(alerts, batch_size=5)
        
        assert sent_count == 1  # Should send one summary message
        mock_bot.send_message.assert_called_once()
        
        # Check that the message contains summary
        call_args = mock_bot.send_message.call_args
        message = call_args.kwargs['text']
        assert 'Market Alert Summary' in message
    
    @pytest.mark.asyncio
    async def test_send_multiple_alerts_mixed_priorities(self, telegram_manager, mock_bot):
        """Test sending alerts with mixed priorities"""
        alerts = [
            {'message': 'High priority alert', 'priority': 'high'},
            {'message': 'Low priority alert 1', 'priority': 'low'},
            {'message': 'Low priority alert 2', 'priority': 'low'}
        ]
        
        with patch('asyncio.sleep', new_callable=AsyncMock):
            sent_count = await telegram_manager.send_multiple_alerts(alerts)
        
        assert sent_count == 3
        assert mock_bot.send_message.call_count == 3
    
    @pytest.mark.asyncio
    async def test_send_multiple_alerts_empty_list(self, telegram_manager, mock_bot):
        """Test sending empty alerts list"""
        sent_count = await telegram_manager.send_multiple_alerts([])
        
        assert sent_count == 0
        mock_bot.send_message.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_summary(self, telegram_manager, mock_bot):
        """Test sending market summary"""
        summary = {'timestamp': datetime.now()}
        alerts = [{'message': 'Test alert'}]
        
        result = await telegram_manager.send_summary(summary, alerts)
        
        assert result is True
        mock_bot.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_startup_message(self, telegram_manager, mock_bot):
        """Test sending startup message"""
        result = await telegram_manager.send_startup_message()
        
        assert result is True
        mock_bot.send_message.assert_called_once()
        
        call_args = mock_bot.send_message.call_args
        message = call_args.kwargs['text']
        assert 'Crypto Market Alert Bot Started' in message
        assert 'Monitoring cryptocurrency markets' in message
    
    @pytest.mark.asyncio
    async def test_send_error_message(self, telegram_manager, mock_bot):
        """Test sending error message"""
        result = await telegram_manager.send_error_message("API Error", "Connection failed")
        
        assert result is True
        mock_bot.send_message.assert_called_once()
        
        call_args = mock_bot.send_message.call_args
        message = call_args.kwargs['text']
        assert 'Alert System Error' in message
        assert 'API Error' in message
        assert 'Connection failed' in message
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, telegram_manager, mock_bot):
        """Test successful connection test"""
        result = await telegram_manager.test_connection()
        
        assert result is True
        mock_bot.get_me.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, telegram_manager, mock_bot):
        """Test failed connection test"""
        mock_bot.get_me.side_effect = Exception("Connection failed")
        
        result = await telegram_manager.test_connection()
        
        assert result is False


class TestAlertsOrchestrator:
    """Test alerts orchestrator functionality"""
    
    @pytest.fixture
    def mock_telegram_manager(self):
        """Create a mock TelegramAlertsManager"""
        mock = Mock(spec=TelegramAlertsManager)
        mock.send_multiple_alerts = AsyncMock(return_value=5)
        mock.send_summary = AsyncMock(return_value=True)
        mock.test_connection = AsyncMock(return_value=True)
        mock.send_startup_message = AsyncMock(return_value=True)
        return mock
    
    @pytest.fixture
    def orchestrator(self, mock_telegram_manager):
        """Create an AlertsOrchestrator instance"""
        return AlertsOrchestrator(mock_telegram_manager)
    
    @pytest.mark.asyncio
    async def test_send_alerts(self, orchestrator, mock_telegram_manager):
        """Test sending alerts through orchestrator"""
        alerts = [
            {'message': 'Alert 1', 'priority': 'high'},
            {'message': 'Alert 2', 'priority': 'medium'}
        ]
        
        results = await orchestrator.send_alerts(alerts)
        
        assert results['total_alerts'] == 2
        assert results['telegram_sent'] == 5
        mock_telegram_manager.send_multiple_alerts.assert_called_once_with(alerts)
    
    @pytest.mark.asyncio
    async def test_send_alerts_empty_list(self, orchestrator, mock_telegram_manager):
        """Test sending empty alerts list"""
        results = await orchestrator.send_alerts([])
        
        assert results['total_alerts'] == 0
        assert results['telegram_sent'] == 0
        mock_telegram_manager.send_multiple_alerts.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_periodic_summary(self, orchestrator, mock_telegram_manager):
        """Test sending periodic summary"""
        summary = {'timestamp': datetime.now()}
        alerts = [{'message': 'Test alert'}]
        
        result = await orchestrator.send_periodic_summary(summary, alerts)
        
        assert result is True
        mock_telegram_manager.send_summary.assert_called_once_with(summary, alerts)
    
    @pytest.mark.asyncio
    async def test_initialize_success(self, orchestrator, mock_telegram_manager):
        """Test successful orchestrator initialization"""
        result = await orchestrator.initialize()
        
        assert result is True
        mock_telegram_manager.test_connection.assert_called_once()
        mock_telegram_manager.send_startup_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_failure(self, orchestrator, mock_telegram_manager):
        """Test failed orchestrator initialization"""
        mock_telegram_manager.test_connection.return_value = False
        
        result = await orchestrator.initialize()
        
        assert result is False
        mock_telegram_manager.test_connection.assert_called_once()
        mock_telegram_manager.send_startup_message.assert_not_called()


class TestAlertsIntegration:
    """Integration tests for alerts system"""
    
    @pytest.mark.asyncio
    async def test_complete_alert_flow(self):
        """Test complete alert flow from creation to sending"""
        # Create real manager (but mock the bot)
        manager = TelegramAlertsManager("test_token", "test_chat")
        
        with patch.object(manager, 'bot') as mock_bot:
            mock_bot.send_message = AsyncMock(return_value=True)
            mock_bot.get_me = AsyncMock(return_value=Mock(username="test_bot"))
            
            # Create orchestrator
            orchestrator = AlertsOrchestrator(manager)
            
            # Initialize
            init_result = await orchestrator.initialize()
            assert init_result is True
            
            # Create test alerts
            alerts = [
                {
                    'message': 'BTC price breakout',
                    'type': 'price_breakout',
                    'coin': 'BTC',
                    'priority': 'high',
                    'current_price': 45000,
                    'threshold': 44500
                },
                {
                    'message': 'ETH RSI oversold',
                    'type': 'rsi_oversold',
                    'coin': 'ETH',
                    'priority': 'medium',
                    'rsi_value': 25,
                    'threshold': 30
                }
            ]
            
            # Send alerts
            with patch('asyncio.sleep', new_callable=AsyncMock):
                results = await orchestrator.send_alerts(alerts)
            
            assert results['total_alerts'] == 2
            assert results['telegram_sent'] == 2
            
            # Send summary
            summary = {
                'timestamp': datetime.now(),
                'market_metrics': {
                    'btc_dominance': 65.0,
                    'fear_greed_index': {'value': 25, 'value_classification': 'Fear'}
                }
            }
            
            summary_result = await orchestrator.send_periodic_summary(summary, alerts)
            assert summary_result is True
            
            # Verify all calls were made
            assert mock_bot.send_message.call_count >= 4  # startup + 2 alerts + summary
    
    @pytest.mark.asyncio
    async def test_error_handling_in_flow(self):
        """Test error handling in complete flow"""
        manager = TelegramAlertsManager("test_token", "test_chat")
        
        with patch.object(manager, 'bot') as mock_bot:
            # Simulate connection failure
            mock_bot.get_me.side_effect = Exception("Connection failed")
            
            orchestrator = AlertsOrchestrator(manager)
            
            # Initialization should fail
            init_result = await orchestrator.initialize()
            assert init_result is False
            
            # But sending alerts should still work if we fix the connection
            mock_bot.get_me.side_effect = None
            mock_bot.get_me.return_value = Mock(username="test_bot")
            mock_bot.send_message = AsyncMock(return_value=True)
            
            alerts = [{'message': 'Test alert', 'priority': 'medium'}]
            results = await orchestrator.send_alerts(alerts)
            
            assert results['total_alerts'] == 1
            assert results['telegram_sent'] == 1


class TestAlertsEdgeCases:
    """Test critical edge cases and boundary conditions for alerts system"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager("test_token", "test_chat")
    
    def test_message_length_limit_handling(self, telegram_manager):
        """Test handling of messages exceeding Telegram's 4096 character limit"""
        # Create alert with very long message (exceeds 4096 char limit)
        long_message = "A" * 5000
        alert = {
            'message': long_message,
            'type': 'test',
            'priority': 'high',
            'coin': 'BTC'
        }
        
        formatted = telegram_manager.format_alert_message(alert)
        
        # Should be truncated or handled appropriately to stay within Telegram limits
        assert len(formatted) <= 4096, f"Message too long: {len(formatted)} chars > 4096"
    
    def test_html_injection_protection(self, telegram_manager):
        """Test protection against HTML injection in alert messages"""
        malicious_alerts = [
            {
                'message': '<script>alert("xss")</script>BTC price alert',
                'type': 'price_alert',
                'priority': 'high',
                'coin': 'BTC'
            },
            {
                'message': 'BTC price: <img src="x" onerror="alert(1)">',
                'type': 'price_alert',
                'priority': 'medium',
                'coin': 'BTC'
            },
            {
                'message': 'Alert with <b>bold</b> and <i>italic</i> tags',
                'type': 'test',
                'priority': 'low',
                'coin': 'ETH'
            }
        ]
        
        for alert in malicious_alerts:
            formatted = telegram_manager.format_alert_message(alert)
            
            # Should not contain dangerous script tags
            assert '<script>' not in formatted
            assert 'onerror=' not in formatted
            # But should preserve safe HTML formatting
            assert len(formatted) > 0
    
    def test_missing_alert_fields_handling(self, telegram_manager):
        """Test handling of alerts with missing or None fields"""
        incomplete_alerts = [
            {'message': 'Test alert'},  # Missing type, priority, coin
            {'type': 'price_alert'},    # Missing message
            {'message': None, 'type': 'test', 'priority': 'high'},  # None message
            {'message': '', 'type': 'test', 'priority': 'high'},    # Empty message
            {'message': 'Test', 'priority': None},  # None priority
            {'message': 'Test', 'coin': None}       # None coin
        ]
        
        for alert in incomplete_alerts:
            # Should not crash with missing fields
            formatted = telegram_manager.format_alert_message(alert)
            assert isinstance(formatted, str)
            assert len(formatted) > 0
    
    def test_extreme_numeric_values_in_alerts(self, telegram_manager):
        """Test handling of extreme numeric values in alert data"""
        extreme_alerts = [
            {
                'message': 'Extreme price alert',
                'type': 'price_breakout',
                'current_price': 1e15,  # Very large number
                'threshold': 1e14,
                'priority': 'high'
            },
            {
                'message': 'Tiny price alert',
                'type': 'price_breakdown',
                'current_price': 1e-10,  # Very small number
                'threshold': 1e-9,
                'priority': 'medium'
            },
            {
                'message': 'Zero price alert',
                'type': 'price_alert',
                'current_price': 0,
                'threshold': 100,
                'priority': 'high'
            },
            {
                'message': 'Negative RSI alert',
                'type': 'rsi_alert',
                'rsi_value': -50,  # Invalid RSI value
                'threshold': 30,
                'priority': 'medium'
            }
        ]
        
        for alert in extreme_alerts:
            formatted = telegram_manager.format_alert_message(alert)
            assert len(formatted) > 0
            # Should handle extreme values gracefully without crashing
    
    def test_unicode_and_special_characters(self, telegram_manager):
        """Test handling of unicode and special characters in alerts"""
        unicode_alerts = [
            {
                'message': 'Bitcoin price: ₿50,000 💰',
                'type': 'price_alert',
                'coin': '₿TC',
                'priority': 'high'
            },
            {
                'message': 'Ethereum alert: Ξ3,000 🚀',
                'type': 'price_alert',
                'coin': 'ΞTH',
                'priority': 'medium'
            },
            {
                'message': 'Special chars: <>&"\'',
                'type': 'test',
                'priority': 'low'
            }
        ]
        
        for alert in unicode_alerts:
            formatted = telegram_manager.format_alert_message(alert)
            assert len(formatted) > 0
            
            # Check specific handling for each alert type
            if 'Bitcoin price' in alert['message']:
                # Should preserve unicode characters like ₿ and 💰
                assert '₿' in formatted and '💰' in formatted
            elif 'Ethereum alert' in alert['message']:
                # Should preserve unicode characters like Ξ and 🚀
                assert 'Ξ' in formatted and '🚀' in formatted
            elif 'Special chars' in alert['message']:
                # Should escape HTML special characters
                assert '&lt;' in formatted and '&gt;' in formatted and '&amp;' in formatted


class TestAlertsBatchProcessing:
    """Test batch processing edge cases and boundary conditions"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager("test_token", "test_chat")
    
    @pytest.mark.asyncio
    async def test_batch_size_boundary_conditions(self, telegram_manager):
        """Test batch processing at exact boundary conditions"""
        batch_size = 5
        
        # Test with exactly batch_size alerts
        alerts_exact = [
            {'message': f'Alert {i}', 'priority': 'medium', 'type': 'test'}
            for i in range(batch_size)
        ]
        
        with patch.object(telegram_manager, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            sent_count = await telegram_manager.send_multiple_alerts(alerts_exact, batch_size)
            
            # Should send each alert individually (not batched)
            assert sent_count == batch_size
            assert mock_send.call_count == batch_size
        
        # Test with batch_size + 1 alerts (triggers batching)
        alerts_over = [
            {'message': f'Alert {i}', 'priority': 'medium', 'type': 'test'}
            for i in range(batch_size + 1)
        ]
        
        with patch.object(telegram_manager, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            sent_count = await telegram_manager.send_multiple_alerts(alerts_over, batch_size)
            
            # Should batch the alerts into summary message
            assert sent_count == 1
            assert mock_send.call_count == 1
    
    @pytest.mark.asyncio
    async def test_priority_based_alert_grouping(self, telegram_manager):
        """Test that high priority alerts are sent individually"""
        mixed_priority_alerts = [
            {'message': 'High priority 1', 'priority': 'high', 'type': 'critical'},
            {'message': 'Medium priority 1', 'priority': 'medium', 'type': 'info'},
            {'message': 'High priority 2', 'priority': 'high', 'type': 'critical'},
            {'message': 'Low priority 1', 'priority': 'low', 'type': 'info'},
            {'message': 'Medium priority 2', 'priority': 'medium', 'type': 'info'}
        ]
        
        with patch.object(telegram_manager, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = True
            sent_count = await telegram_manager.send_multiple_alerts(mixed_priority_alerts, batch_size=3)
            
            # High priority alerts (2) should be sent individually
            # Other alerts (3) should be sent individually since < batch_size
            assert sent_count == 5
            assert mock_send.call_count == 5
    
    @pytest.mark.asyncio
    async def test_empty_alerts_list(self, telegram_manager):
        """Test handling of empty alerts list"""
        with patch.object(telegram_manager, 'send_message', new_callable=AsyncMock) as mock_send:
            sent_count = await telegram_manager.send_multiple_alerts([])
            
            assert sent_count == 0
            assert mock_send.call_count == 0
    
    @pytest.mark.asyncio
    async def test_partial_batch_failure_recovery(self, telegram_manager):
        """Test recovery from partial failures during batch sending"""
        alerts = [
            {'message': f'Alert {i}', 'priority': 'medium', 'type': 'test'}
            for i in range(3)
        ]
        
        with patch.object(telegram_manager, 'send_message', new_callable=AsyncMock) as mock_send:
            # First call succeeds, second fails, third succeeds
            mock_send.side_effect = [True, False, True]
            
            sent_count = await telegram_manager.send_multiple_alerts(alerts)
            
            # Should attempt to send all alerts despite partial failures
            assert mock_send.call_count == 3
            assert sent_count == 2  # Only successful sends counted


class TestAlertsConnectionFailures:
    """Test connection failure scenarios and recovery"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager("test_token", "test_chat")
    
    @pytest.mark.asyncio
    async def test_telegram_api_connection_failure(self, telegram_manager):
        """Test handling of Telegram API connection failures"""
        alert = {'message': 'Test alert', 'priority': 'high', 'type': 'test'}
        
        # Mock the entire bot object
        mock_bot = AsyncMock()
        mock_bot.send_message.side_effect = TelegramError("Network error")
        telegram_manager.bot = mock_bot
        
        result = await telegram_manager.send_alert(alert)
        
        assert result is False
        assert mock_bot.send_message.call_count == 1
    
    @pytest.mark.asyncio
    async def test_bot_connection_test_failure(self, telegram_manager):
        """Test bot connection test with various failure scenarios"""
        # Test connection timeout
        mock_bot = AsyncMock()
        mock_bot.get_me.side_effect = asyncio.TimeoutError("Connection timeout")
        telegram_manager.bot = mock_bot
        
        result = await telegram_manager.test_connection()
        
        assert result is False
        
        # Test Telegram API error
        mock_bot.get_me.side_effect = TelegramError("Invalid bot token")
        
        result = await telegram_manager.test_connection()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_message_send_with_rate_limiting(self, telegram_manager):
        """Test message sending with rate limiting errors"""
        alert = {'message': 'Test alert', 'priority': 'medium', 'type': 'test'}
        
        # Mock the entire bot object
        mock_bot = AsyncMock()
        mock_bot.send_message.side_effect = TelegramError("Too Many Requests: retry after 30")
        telegram_manager.bot = mock_bot
        
        result = await telegram_manager.send_alert(alert)
        
        assert result is False
        assert mock_bot.send_message.call_count == 1
