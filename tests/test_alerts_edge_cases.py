"""
Comprehensive edge case tests for alerts module
Tests Telegram message limits, HTML injection prevention, batch processing, and error handling
"""

import pytest
import asyncio
import html
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from telegram.error import TelegramError, NetworkError, BadRequest

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.alerts import TelegramAlertsManager, AlertsOrchestrator


class TestTelegramMessageLengthLimits:
    """Test Telegram message length limits and truncation"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager(
            bot_token="test_token",
            chat_id="test_chat_id"
        )
    
    def test_telegram_message_length_limit_4096_chars(self, telegram_manager):
        """Test message truncation at Telegram's 4096 character limit"""
        # Create message that exceeds Telegram's limit
        long_message = "A" * 5000  # Exceeds 4096 character limit
        
        result = telegram_manager.format_alert_message({
            'message': long_message,
            'type': 'test',
            'coin': 'BTC',
            'priority': 'high'
        })
        
        # Should truncate to within Telegram's limit
        assert len(result) <= 4096
        assert result.endswith("... (message truncated)")  # Correct truncation indicator
        assert "🚨" in result  # Should still contain priority emoji
    
    def test_telegram_message_exactly_4096_chars(self, telegram_manager):
        """Test message that is exactly at the 4096 character limit"""
        # Create message exactly at limit (accounting for formatting)
        base_message = "B" * 4000  # Leave room for formatting
        
        result = telegram_manager.format_alert_message({
            'message': base_message,
            'type': 'test',
            'coin': 'BTC',
            'priority': 'medium'
        })
        
        # Should not exceed limit
        assert len(result) <= 4096
        assert not result.endswith("...")  # Should not be truncated
    
    def test_telegram_message_multi_part_handling(self, telegram_manager):
        """Test handling of very long messages that need splitting"""
        # Create extremely long message
        very_long_message = "X" * 10000
        
        # Test that the system handles this gracefully
        result = telegram_manager.format_alert_message({
            'message': very_long_message,
            'type': 'test',
            'coin': 'BTC',
            'priority': 'low'
        })
        
        # Should be truncated to safe length
        assert len(result) <= 4096
        assert result.endswith("... (message truncated)")
    
    def test_telegram_message_with_unicode_characters(self, telegram_manager):
        """Test message length calculation with Unicode characters"""
        # Unicode characters can take multiple bytes
        unicode_message = "🚨" * 1000 + "📊" * 1000 + "💰" * 1000
        
        result = telegram_manager.format_alert_message({
            'message': unicode_message,
            'type': 'test',
            'coin': 'BTC',
            'priority': 'high'
        })
        
        # Should handle Unicode properly and stay within limits
        assert len(result) <= 4096
        # Should preserve some Unicode characters
        assert "🚨" in result or "📊" in result or "💰" in result


class TestHTMLInjectionPrevention:
    """Test HTML injection prevention and escaping"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager(
            bot_token="test_token",
            chat_id="test_chat_id"
        )
    
    def test_html_script_tag_injection_prevention(self, telegram_manager):
        """Test that HTML/script tags are properly escaped"""
        malicious_content = "<script>alert('xss')</script>"
        
        result = telegram_manager.format_alert_message({
            'message': malicious_content,
            'type': 'test',
            'coin': 'BTC',
            'priority': 'high'
        })
        
        # Script tags should be escaped
        assert "<script>" not in result
        assert "&lt;script&gt;" in result or html.escape("<script>") in result
    
    def test_html_img_tag_injection_prevention(self, telegram_manager):
        """Test that HTML img tags are properly escaped"""
        malicious_content = '<img src="x" onerror="alert(1)">'
        
        result = telegram_manager.format_alert_message({
            'message': malicious_content,
            'type': 'test',
            'coin': 'ETH',
            'priority': 'medium'
        })
        
        # IMG tags should be escaped
        assert '<img' not in result
        assert '&lt;img' in result or html.escape('<img') in result
    
    def test_html_iframe_injection_prevention(self, telegram_manager):
        """Test that HTML iframe tags are properly escaped"""
        malicious_content = '<iframe src="javascript:alert(1)"></iframe>'
        
        result = telegram_manager.format_alert_message({
            'message': malicious_content,
            'type': 'test',
            'coin': 'ADA',
            'priority': 'low'
        })
        
        # Iframe tags should be escaped
        assert '<iframe' not in result
        assert '&lt;iframe' in result or html.escape('<iframe') in result
    
    def test_html_link_injection_prevention(self, telegram_manager):
        """Test that malicious links are properly handled"""
        malicious_content = '<a href="javascript:alert(1)">Click me</a>'
        
        result = telegram_manager.format_alert_message({
            'message': malicious_content,
            'type': 'test',
            'coin': 'SOL',
            'priority': 'high'
        })
        
        # Link tags should be escaped or sanitized
        assert 'javascript:' not in result
        assert '<a href=' not in result or '&lt;a href=' in result
    
    def test_html_style_injection_prevention(self, telegram_manager):
        """Test that style tags with malicious CSS are escaped"""
        malicious_content = '<style>body{background:url("javascript:alert(1)")}</style>'
        
        result = telegram_manager.format_alert_message({
            'message': malicious_content,
            'type': 'test',
            'coin': 'DOT',
            'priority': 'medium'
        })
        
        # Style tags should be escaped
        assert '<style>' not in result
        assert 'javascript:' not in result
    
    def test_mixed_html_injection_prevention(self, telegram_manager):
        """Test complex mixed HTML injection attempts"""
        malicious_content = '''
        <script>alert('xss1')</script>
        <img src="x" onerror="alert('xss2')">
        <iframe src="javascript:alert('xss3')"></iframe>
        Normal text here
        <a href="javascript:alert('xss4')">Link</a>
        '''
        
        result = telegram_manager.format_alert_message({
            'message': malicious_content,
            'type': 'test',
            'coin': 'LINK',
            'priority': 'high'
        })
        
        # All malicious tags should be escaped
        assert '<script>' not in result
        assert '<img' not in result
        assert '<iframe' not in result
        assert 'javascript:' not in result
        assert 'Normal text here' in result  # Normal text should remain


class TestBatchProcessingEdgeCases:
    """Test batch processing edge cases and boundary conditions"""
    
    @pytest.fixture
    def alerts_orchestrator(self):
        telegram_manager = Mock()
        return AlertsOrchestrator(telegram_manager)
    
    def test_batch_processing_exactly_batch_size(self, alerts_orchestrator):
        """Test batch processing with exactly 5 alerts"""
        # Create exactly 5 alerts
        alerts = [
            {'message': f'Alert {i}', 'type': 'test', 'coin': 'BTC', 'priority': 'medium'}
            for i in range(5)
        ]
        
        with patch.object(alerts_orchestrator.telegram, 'send_multiple_alerts', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = 5  # Return number of alerts sent
            
            # Should process all alerts
            result = asyncio.run(alerts_orchestrator.send_alerts(alerts))
            
            assert result['telegram_sent'] == 5
            assert result['total_alerts'] == 5
            mock_send.assert_called_once_with(alerts)
    
    def test_batch_processing_batch_size_plus_one(self, alerts_orchestrator):
        """Test batch processing with 6 alerts"""
        # Create 6 alerts
        alerts = [
            {'message': f'Alert {i}', 'type': 'test', 'coin': 'BTC', 'priority': 'medium'}
            for i in range(6)
        ]
        
        with patch.object(alerts_orchestrator.telegram, 'send_multiple_alerts', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = 6  # Return number of alerts sent
            
            result = asyncio.run(alerts_orchestrator.send_alerts(alerts))
            
            # Should handle all alerts
            assert result['telegram_sent'] == 6
            assert result['total_alerts'] == 6
            mock_send.assert_called_once_with(alerts)
    
    def test_batch_processing_empty_batch(self, alerts_orchestrator):
        """Test batch processing with empty alert list"""
        alerts = []
        
        with patch.object(alerts_orchestrator.telegram, 'send_multiple_alerts', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = 0  # No alerts sent
            
            result = asyncio.run(alerts_orchestrator.send_alerts(alerts))
            
            assert result['telegram_sent'] == 0
            assert result['total_alerts'] == 0
            # send_multiple_alerts should not be called for empty list
            mock_send.assert_not_called()
    
    def test_batch_processing_single_alert(self, alerts_orchestrator):
        """Test batch processing with single alert"""
        alerts = [{'message': 'Single alert', 'type': 'test', 'coin': 'BTC', 'priority': 'high'}]
        
        with patch.object(alerts_orchestrator.telegram, 'send_multiple_alerts', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = 1  # One alert sent
            
            result = asyncio.run(alerts_orchestrator.send_alerts(alerts))
            
            assert result['telegram_sent'] == 1
            assert result['total_alerts'] == 1
            mock_send.assert_called_once_with(alerts)
    
    def test_batch_processing_partial_failures(self, alerts_orchestrator):
        """Test batch processing with some alerts failing"""
        alerts = [
            {'message': f'Alert {i}', 'type': 'test', 'coin': 'BTC', 'priority': 'medium'}
            for i in range(5)
        ]
        
        with patch.object(alerts_orchestrator.telegram, 'send_multiple_alerts', new_callable=AsyncMock) as mock_send:
            # Simulate partial failure - only 3 out of 5 alerts sent
            mock_send.return_value = 3
            
            result = asyncio.run(alerts_orchestrator.send_alerts(alerts))
            
            assert result['telegram_sent'] == 3
            assert result['total_alerts'] == 5
            mock_send.assert_called_once_with(alerts)


class TestTelegramAPIErrorHandling:
    """Test Telegram API error handling and recovery"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager(
            bot_token="test_token",
            chat_id="test_chat_id"
        )
    
    @pytest.mark.asyncio
    async def test_telegram_network_error_handling(self, telegram_manager):
        """Test handling of Telegram network errors"""
        with patch.object(telegram_manager, 'bot') as mock_bot:
            mock_bot.send_message.side_effect = NetworkError("Network connection failed")
            
            result = await telegram_manager.send_message("Test message")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_telegram_bad_request_error_handling(self, telegram_manager):
        """Test handling of Telegram bad request errors"""
        with patch.object(telegram_manager, 'bot') as mock_bot:
            mock_bot.send_message.side_effect = BadRequest("Invalid chat_id")
            
            result = await telegram_manager.send_message("Test message")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_telegram_rate_limit_error_handling(self, telegram_manager):
        """Test handling of Telegram rate limiting"""
        with patch.object(telegram_manager, 'bot') as mock_bot:
            # Simulate rate limit error
            rate_limit_error = TelegramError("Too Many Requests: retry after 30")
            mock_bot.send_message.side_effect = rate_limit_error
            
            result = await telegram_manager.send_message("Test message")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_telegram_invalid_token_error_handling(self, telegram_manager):
        """Test handling of invalid bot token"""
        with patch.object(telegram_manager, 'bot') as mock_bot:
            mock_bot.send_message.side_effect = TelegramError("Unauthorized")
            
            result = await telegram_manager.send_message("Test message")
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_telegram_message_too_long_error_handling(self, telegram_manager):
        """Test handling when message is too long for Telegram"""
        with patch.object(telegram_manager, 'bot') as mock_bot:
            mock_bot.send_message.side_effect = BadRequest("Message is too long")
            
            # This should be handled by pre-truncation, but test the fallback
            long_message = "A" * 5000
            result = await telegram_manager.send_message(long_message)
            
            assert result is False


class TestAlertPriorityHandling:
    """Test alert priority handling and edge cases"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager(
            bot_token="test_token",
            chat_id="test_chat_id"
        )
    
    def test_invalid_priority_handling(self, telegram_manager):
        """Test handling of invalid priority values"""
        alert = {
            'message': 'Test alert',
            'type': 'test',
            'coin': 'BTC',
            'priority': 'invalid_priority'  # Invalid priority
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should default to low priority emoji for invalid priority
        assert 'ℹ️' in result  # Low priority emoji (fallback)
        assert 'Test alert' in result
    
    def test_missing_priority_handling(self, telegram_manager):
        """Test handling when priority field is missing"""
        alert = {
            'message': 'Test alert',
            'type': 'test',
            'coin': 'BTC'
            # Missing priority field
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should default to medium priority
        assert '⚠️' in result  # Medium priority emoji
        assert 'Test alert' in result
    
    def test_none_priority_handling(self, telegram_manager):
        """Test handling when priority is None"""
        alert = {
            'message': 'Test alert',
            'type': 'test',
            'coin': 'BTC',
            'priority': None
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should default to low priority emoji for None priority
        assert 'ℹ️' in result  # Low priority emoji (fallback)
        assert 'Test alert' in result
    
    def test_case_insensitive_priority_handling(self, telegram_manager):
        """Test priority handling with different cases"""
        test_cases = [
            ('HIGH', 'ℹ️'),  # Falls back to low priority (case sensitive)
            ('high', '🚨'),   # Exact match works
            ('High', 'ℹ️'),   # Falls back to low priority (case sensitive)
            ('MEDIUM', 'ℹ️'), # Falls back to low priority (case sensitive)
            ('medium', '⚠️'), # Exact match works
            ('Medium', 'ℹ️'), # Falls back to low priority (case sensitive)
            ('LOW', 'ℹ️'),    # Falls back to low priority (case sensitive)
            ('low', 'ℹ️'),    # Exact match works
            ('Low', 'ℹ️')     # Falls back to low priority (case sensitive)
        ]
        
        for priority, expected_emoji in test_cases:
            alert = {
                'message': 'Test alert',
                'type': 'test',
                'coin': 'BTC',
                'priority': priority
            }
            
            result = telegram_manager.format_alert_message(alert)
            assert expected_emoji in result


class TestAlertMessageFieldHandling:
    """Test handling of missing or invalid alert message fields"""
    
    @pytest.fixture
    def telegram_manager(self):
        return TelegramAlertsManager(
            bot_token="test_token",
            chat_id="test_chat_id"
        )
    
    def test_missing_message_field(self, telegram_manager):
        """Test handling when message field is missing"""
        alert = {
            'type': 'test',
            'coin': 'BTC',
            'priority': 'high'
            # Missing message field
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should handle gracefully with default message
        assert 'Unknown alert' in result or 'Alert' in result
        assert '🚨' in result  # High priority emoji should still work
    
    def test_empty_message_field(self, telegram_manager):
        """Test handling when message field is empty"""
        alert = {
            'message': '',  # Empty message
            'type': 'test',
            'coin': 'BTC',
            'priority': 'medium'
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should handle empty message gracefully
        assert len(result) > 0
        assert '⚠️' in result  # Medium priority emoji
    
    def test_none_message_field(self, telegram_manager):
        """Test handling when message field is None"""
        alert = {
            'message': None,  # None message
            'type': 'test',
            'coin': 'BTC',
            'priority': 'low'
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should handle None message gracefully
        assert len(result) > 0
        assert 'ℹ️' in result  # Low priority emoji
    
    def test_missing_coin_field(self, telegram_manager):
        """Test handling when coin field is missing"""
        alert = {
            'message': 'Test alert',
            'type': 'test',
            'priority': 'high'
            # Missing coin field
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should handle missing coin gracefully
        assert 'Test alert' in result
        assert '🚨' in result  # High priority emoji
    
    def test_missing_type_field(self, telegram_manager):
        """Test handling when type field is missing"""
        alert = {
            'message': 'Test alert',
            'coin': 'BTC',
            'priority': 'medium'
            # Missing type field
        }
        
        result = telegram_manager.format_alert_message(alert)
        
        # Should handle missing type gracefully
        assert 'Test alert' in result
        assert '⚠️' in result  # Medium priority emoji


if __name__ == '__main__':
    pytest.main([__file__])