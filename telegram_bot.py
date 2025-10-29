#!/usr/bin/env python3
"""
Telegram Bot for Crypto Portfolio Management
Handles interactive commands for real-time portfolio information
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from main import CryptoMarketAlertSystem
from src.portfolio_utils import PortfolioAnalyzer
from src.price_history import PriceHistoryTracker
from src.utils import load_environment, get_env_variable


class CryptoPortfolioBot:
    """Telegram bot for interactive crypto portfolio management"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the bot with configuration"""
        # Load environment
        load_environment()
        
        # Get credentials
        self.bot_token = get_env_variable('TELEGRAM_BOT_TOKEN')
        self.chat_id = get_env_variable('TELEGRAM_CHAT_ID')
        
        # Initialize alert system
        self.alert_system = CryptoMarketAlertSystem(config_path)
        self.alert_system.initialize_components()
        
        # Initialize price history tracker
        self.price_tracker = PriceHistoryTracker()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Bot application
        self.app = None
    
    def _fetch_coin_data_with_history(self) -> dict:
        """
        Fetch coin data and enhance with historical 24h change if needed.
        Also records current prices for future tracking.

        Returns:
            Dictionary of coin data enhanced with historical changes
        """
        # Fetch current data
        coin_data = self.alert_system.collect_coin_data()

        if not coin_data:
            return {}

        # Enhance with historical 24h change where API data is missing
        coin_data = self.price_tracker.enhance_coin_data_with_history(coin_data)

        # Record current prices for future tracking
        self.price_tracker.bulk_record_prices(coin_data)

        return coin_data

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "🤖 <b>Crypto Portfolio Bot</b>\n\n"
            "Welcome! I can help you monitor your crypto portfolio in real-time.\n\n"
            "<b>Available Commands:</b>\n"
            "• /portfolio - Full portfolio report with all coins\n"
            "• /summary - Quick portfolio summary\n"
            "• /prices - Current prices of your coins\n"
            "• /goals - Progress toward BTC/ETH accumulation goals\n"
            "• /btc - Bitcoin price and your holdings\n"
            "• /eth - Ethereum price and your holdings\n"
            "• /market - Market overview (dominance, fear & greed)\n"
            "• /help - Show this help message\n\n"
            "💡 Tip: Use these commands anytime for instant updates!"
        )
        
        await update.message.reply_text(welcome_message, parse_mode='HTML')
        self.logger.info(f"User {update.effective_user.id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.start_command(update, context)
    
    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command - detailed portfolio report with table"""
        try:
            # Check authorization
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Unauthorized access")
                self.logger.warning(f"Unauthorized access attempt from chat {update.effective_chat.id}")
                return
            
            await update.message.reply_text("📊 Fetching portfolio data...")
            
            # Collect coin data with historical enhancement
            coin_data = self._fetch_coin_data_with_history()

            if not coin_data:
                await update.message.reply_text("❌ Failed to fetch coin data. Please try again.")
                return
            
            # Generate portfolio report
            analyzer = PortfolioAnalyzer(self.alert_system)
            portfolio_data = analyzer.generate_portfolio_report(coin_data, "telegram")

            # Send detailed table first
            table_message = analyzer.format_detailed_for_telegram(portfolio_data)
            await update.message.reply_text(table_message, parse_mode='HTML')

            # Then send summary with goals
            summary_message = self._format_portfolio_summary(portfolio_data)
            await update.message.reply_text(summary_message, parse_mode='HTML')

            self.logger.info("Portfolio command executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in portfolio command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /summary command - quick portfolio summary"""
        try:
            # Check authorization
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Unauthorized access")
                return

            await update.message.reply_text("📊 Fetching summary data...")
            
            # Collect coin data
            coin_data = self._fetch_coin_data_with_history()
            
            if not coin_data:
                await update.message.reply_text("❌ Failed to fetch coin data. Please try again.")
                return
            
            # Generate summary
            analyzer = PortfolioAnalyzer(self.alert_system)
            portfolio_data = analyzer.generate_portfolio_report(coin_data, "telegram")
            message = self._format_summary(portfolio_data)
            
            await update.message.reply_text(message, parse_mode='HTML')
            self.logger.info("Summary command executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in summary command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def prices_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /prices command - current prices"""
        try:
            # Check authorization
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Unauthorized access")
                return

            await update.message.reply_text("📊 Fetching prices data...")

            # Collect coin data
            coin_data = self._fetch_coin_data_with_history()
            
            if not coin_data:
                await update.message.reply_text("❌ Failed to fetch coin data.")
                return
            
            message = self._format_prices(coin_data)
            await update.message.reply_text(message, parse_mode='HTML')
            self.logger.info("Prices command executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in prices command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def goals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /goals command - progress toward accumulation goals"""
        try:
            # Check authorization
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Unauthorized access")
                return

            await update.message.reply_text("📊 Fetching goals data...")
            
            # Collect coin data
            coin_data = self._fetch_coin_data_with_history()
            
            if not coin_data:
                await update.message.reply_text("❌ Failed to fetch coin data.")
                return
            
            analyzer = PortfolioAnalyzer(self.alert_system)
            portfolio_data = analyzer.generate_portfolio_report(coin_data, "telegram")
            message = self._format_goals(portfolio_data)
            
            await update.message.reply_text(message, parse_mode='HTML')
            self.logger.info("Goals command executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in goals command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def btc_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /btc command - Bitcoin info"""
        try:
            # Check authorization
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Unauthorized access")
                return

            await update.message.reply_text("📊 Fetching BTC data...")
            
            coin_data = self._fetch_coin_data_with_history()
            
            if 'bitcoin' not in coin_data:
                await update.message.reply_text("❌ Failed to fetch Bitcoin data.")
                return
            
            btc_data = coin_data['bitcoin']
            btc_price = btc_data.get('usd', 0)
            btc_change = btc_data.get('usd_24h_change', 0)
            
            # Get user's BTC holdings
            btc_config = next((c for c in self.alert_system.config.get('coins', []) if c.get('name') == 'BTC'), None)
            btc_amount = btc_config.get('current_amount', 0) if btc_config else 0
            btc_avg_price = btc_config.get('avg_price', 0) if btc_config else 0
            btc_value = btc_amount * btc_price
            
            # Calculate P&L
            if btc_avg_price > 0:
                pnl_pct = ((btc_price - btc_avg_price) / btc_avg_price) * 100
                pnl_usd = btc_amount * (btc_price - btc_avg_price)
                pnl_emoji = "🟢" if pnl_pct >= 0 else "🔴"
            else:
                pnl_pct = 0
                pnl_usd = 0
                pnl_emoji = "⚪"
            
            change_emoji = "🟢" if btc_change >= 0 else "🔴"
            
            message = (
                f"₿ <b>BITCOIN (BTC)</b>\n\n"
                f"💵 Current Price: <b>${btc_price:,.2f}</b>\n"
                f"{change_emoji} 24h Change: <b>{btc_change:+.2f}%</b>\n\n"
                f"📊 <b>Your Holdings:</b>\n"
                f"   Amount: {btc_amount:.8f} BTC\n"
                f"   Value: ${btc_value:,.2f}\n"
                f"   Avg Buy: ${btc_avg_price:,.2f}\n"
                f"{pnl_emoji} P&L: {pnl_pct:+.2f}% (${pnl_usd:+,.2f})\n"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
            self.logger.info("BTC command executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in btc command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def eth_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /eth command - Ethereum info"""
        try:
            # Check authorization
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Unauthorized access")
                return

            await update.message.reply_text("📊 Fetching ETH data...")
            
            coin_data = self._fetch_coin_data_with_history()
            
            if 'ethereum' not in coin_data:
                await update.message.reply_text("❌ Failed to fetch Ethereum data.")
                return
            
            eth_data = coin_data['ethereum']
            eth_price = eth_data.get('usd', 0)
            eth_change = eth_data.get('usd_24h_change', 0)
            
            # Get user's ETH holdings
            eth_config = next((c for c in self.alert_system.config.get('coins', []) if c.get('name') == 'ETH'), None)
            eth_amount = eth_config.get('current_amount', 0) if eth_config else 0
            eth_avg_price = eth_config.get('avg_price', 0) if eth_config else 0
            eth_value = eth_amount * eth_price
            
            # Calculate P&L
            if eth_avg_price > 0:
                pnl_pct = ((eth_price - eth_avg_price) / eth_avg_price) * 100
                pnl_usd = eth_amount * (eth_price - eth_avg_price)
                pnl_emoji = "🟢" if pnl_pct >= 0 else "🔴"
            else:
                pnl_pct = 0
                pnl_usd = 0
                pnl_emoji = "⚪"
            
            change_emoji = "🟢" if eth_change >= 0 else "🔴"
            
            message = (
                f"Ξ <b>ETHEREUM (ETH)</b>\n\n"
                f"💵 Current Price: <b>${eth_price:,.2f}</b>\n"
                f"{change_emoji} 24h Change: <b>{eth_change:+.2f}%</b>\n\n"
                f"📊 <b>Your Holdings:</b>\n"
                f"   Amount: {eth_amount:.6f} ETH\n"
                f"   Value: ${eth_value:,.2f}\n"
                f"   Avg Buy: ${eth_avg_price:,.2f}\n"
                f"{pnl_emoji} P&L: {pnl_pct:+.2f}% (${pnl_usd:+,.2f})\n"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
            self.logger.info("ETH command executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in eth command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command - market overview"""
        try:
            # Check authorization
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Unauthorized access")
                return

            await update.message.reply_text("📊 Fetching market data...")
            
            # Collect market data
            market_data = self.alert_system.collect_market_data()
            
            if not market_data:
                await update.message.reply_text("❌ Failed to fetch market data.")
                return
            
            btc_dominance = market_data.get('btc_dominance', 0)
            eth_btc_ratio = market_data.get('eth_btc_ratio', 0)
            fear_greed = market_data.get('fear_greed_index', {})
            fg_value = fear_greed.get('value', 0)
            fg_classification = fear_greed.get('value_classification', 'Unknown')
            
            # Emoji for fear & greed
            if fg_value >= 75:
                fg_emoji = "🔥"
            elif fg_value >= 50:
                fg_emoji = "😊"
            elif fg_value >= 25:
                fg_emoji = "😐"
            else:
                fg_emoji = "😱"
            
            # Market phase
            if btc_dominance < 45:
                market_phase = "🌟 <b>ALTSEASON ACTIVE</b>"
            elif btc_dominance > 60:
                market_phase = "₿ <b>BTC DOMINANCE</b>"
            else:
                market_phase = "⚖️ <b>BALANCED MARKET</b>"
            
            message = (
                f"🌍 <b>MARKET OVERVIEW</b>\n\n"
                f"{market_phase}\n\n"
                f"📊 <b>Market Metrics:</b>\n"
                f"   BTC Dominance: <b>{btc_dominance:.2f}%</b>\n"
                f"   ETH/BTC Ratio: <b>{eth_btc_ratio:.6f}</b>\n\n"
                f"{fg_emoji} <b>Fear & Greed Index:</b>\n"
                f"   Value: <b>{fg_value}/100</b>\n"
                f"   Status: <b>{fg_classification}</b>\n"
            )
            
            await update.message.reply_text(message, parse_mode='HTML')
            self.logger.info("Market command executed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in market command: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    def _format_detailed_portfolio(self, portfolio_data: dict) -> str:
        """Format detailed portfolio report for Telegram"""
        if 'error' in portfolio_data:
            return f"❌ Portfolio analysis failed: {portfolio_data['error']}"
        
        output = []
        output.append("💼 <b>PORTFOLIO REPORT</b>\n")
        output.append(f"⏰ <i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n")
        
        # Top holdings
        output.append("📊 <b>Holdings:</b>")
        for item in portfolio_data['portfolio_items']:
            if item['amount'] > 0:
                # Format based on coin type
                if item['name'] == 'BTC':
                    amount_str = f"{item['amount']:.6f}"
                elif item['name'] == 'ETH':
                    amount_str = f"{item['amount']:.4f}"
                elif item['name'] == 'SHIB':
                    amount_str = f"{item['amount']:,.0f}"
                elif item['amount'] < 1:
                    amount_str = f"{item['amount']:.4f}"
                else:
                    amount_str = f"{item['amount']:.2f}"
                
                # P&L indicator
                pnl = item['gain_loss_pct']
                if pnl > 0:
                    pnl_emoji = "🟢"
                elif pnl < 0:
                    pnl_emoji = "🔴"
                else:
                    pnl_emoji = "⚪"
                
                output.append(
                    f"   {pnl_emoji} <b>{item['name']}</b>: {amount_str}\n"
                    f"      Value: <code>${item['total_usd']:,.2f}</code>\n"
                    f"      ₿{item['btc_equivalent']:.6f} | Ξ{item['eth_equivalent']:.4f}"
                )
        
        # Totals
        totals = portfolio_data['totals']
        output.append("\n💰 <b>Summary:</b>")
        output.append(f"   Total Value: <b>${totals['total_usd']:,.2f}</b>")
        output.append(f"   In BTC: <b>₿{totals['total_btc_equivalent']:.6f}</b>")
        output.append(f"   In ETH: <b>Ξ{totals['total_eth_equivalent']:.4f}</b>")
        output.append(f"   Altcoins: <code>${totals['altcoins_usd']:,.2f}</code>")
        
        # Prices
        output.append(f"\n💵 <b>Current Prices:</b>")
        output.append(f"   BTC: <code>${totals['btc_price']:,.2f}</code>")
        output.append(f"   ETH: <code>${totals['eth_price']:,.2f}</code>")
        
        # Goals
        goals = portfolio_data['goals']
        holdings = portfolio_data['holdings']
        output.append(f"\n🎯 <b>Accumulation Goals:</b>")
        
        btc_bar = self._progress_bar(goals['btc_progress'])
        output.append(
            f"   ₿ BTC: {btc_bar} {goals['btc_progress']:.1f}%\n"
            f"      {holdings['btc_amount']:.6f} / {goals['btc_target']:.1f} BTC"
        )
        
        if goals['btc_needed'] > 0:
            output.append(f"      Need: <b>₿{goals['btc_needed']:.6f}</b> (${goals['btc_needed_usd']:,.2f})")
        else:
            output.append(f"      ✅ <b>Target Achieved!</b>")
        
        eth_bar = self._progress_bar(goals['eth_progress'])
        output.append(
            f"\n   Ξ ETH: {eth_bar} {goals['eth_progress']:.1f}%\n"
            f"      {holdings['eth_amount']:.4f} / {goals['eth_target']:.1f} ETH"
        )
        
        if goals['eth_needed'] > 0:
            output.append(f"      Need: <b>Ξ{goals['eth_needed']:.4f}</b> (${goals['eth_needed_usd']:,.2f})")
        else:
            output.append(f"      ✅ <b>Target Achieved!</b>")
        
        return "\n".join(output)
    
    def _format_summary(self, portfolio_data: dict) -> str:
        """Format quick portfolio summary"""
        if 'error' in portfolio_data:
            return f"❌ Error: {portfolio_data['error']}"
        
        totals = portfolio_data['totals']
        goals = portfolio_data['goals']
        holdings = portfolio_data['holdings']
        
        output = []
        output.append("💼 <b>PORTFOLIO SUMMARY</b>\n")
        output.append(f"💰 <b>Total Value: ${totals['total_usd']:,.2f}</b>")
        output.append(f"   ₿{totals['total_btc_equivalent']:.6f} | Ξ{totals['total_eth_equivalent']:.4f}\n")
        
        output.append(f"📊 <b>Main Holdings:</b>")
        output.append(f"   BTC: {holdings['btc_amount']:.6f} (${holdings['btc_amount'] * totals['btc_price']:,.2f})")
        output.append(f"   ETH: {holdings['eth_amount']:.4f} (${holdings['eth_amount'] * totals['eth_price']:,.2f})")
        output.append(f"   Altcoins: ${totals['altcoins_usd']:,.2f}\n")
        
        output.append(f"🎯 <b>Goals:</b>")
        output.append(f"   BTC: {goals['btc_progress']:.1f}% ({holdings['btc_amount']:.3f}/{goals['btc_target']:.0f})")
        output.append(f"   ETH: {goals['eth_progress']:.1f}% ({holdings['eth_amount']:.2f}/{goals['eth_target']:.0f})")
        
        return "\n".join(output)

    def _format_portfolio_summary(self, portfolio_data: dict) -> str:
        """Format portfolio summary with totals and goals (after detailed table)"""
        if 'error' in portfolio_data:
            return f"❌ Error: {portfolio_data['error']}"

        totals = portfolio_data['totals']
        goals = portfolio_data['goals']
        holdings = portfolio_data['holdings']

        output = []
        output.append("💰 <b>Summary:</b>")
        output.append(f"   Total Value: <b>${totals['total_usd']:,.2f}</b>")
        output.append(f"   In BTC: <b>₿{totals['total_btc_equivalent']:.6f}</b>")
        output.append(f"   In ETH: <b>Ξ{totals['total_eth_equivalent']:.4f}</b>")
        output.append(f"   Altcoins: <code>${totals['altcoins_usd']:,.2f}</code>")

        output.append(f"\n💵 <b>Current Prices:</b>")
        output.append(f"   BTC: <code>${totals['btc_price']:,.2f}</code>")
        output.append(f"   ETH: <code>${totals['eth_price']:,.2f}</code>")

        output.append(f"\n🎯 <b>Accumulation Goals:</b>")

        # BTC Goal
        btc_bar = self._progress_bar(goals['btc_progress'])
        output.append(f"   ₿ BTC: {btc_bar} {goals['btc_progress']:.1f}%")
        output.append(f"      {holdings['btc_amount']:.6f} / {goals['btc_target']:.1f} BTC")
        if goals['btc_needed'] > 0:
            output.append(f"      Need: <b>₿{goals['btc_needed']:.6f}</b> (${goals['btc_needed_usd']:,.2f})")
        else:
            output.append(f"      ✅ <b>Target Achieved!</b>")

        # ETH Goal
        eth_bar = self._progress_bar(goals['eth_progress'])
        output.append(f"\n   Ξ ETH: {eth_bar} {goals['eth_progress']:.1f}%")
        output.append(f"      {holdings['eth_amount']:.4f} / {goals['eth_target']:.1f} ETH")
        if goals['eth_needed'] > 0:
            output.append(f"      Need: <b>Ξ{goals['eth_needed']:.4f}</b> (${goals['eth_needed_usd']:,.2f})")
        else:
            output.append(f"      ✅ <b>Target Achieved!</b>")

        return "\n".join(output)
    
    def _format_prices(self, coin_data: dict) -> str:
        """Format current prices"""
        output = []
        output.append("💵 <b>CURRENT PRICES</b>\n")
        
        # Get configured coins
        coins_config = self.alert_system.config.get('coins', [])
        
        # Sort by importance (BTC, ETH first, then by market cap/value)
        priority_order = ['bitcoin', 'ethereum', 'binancecoin']
        
        # Priority coins first
        for coin_id in priority_order:
            if coin_id in coin_data:
                coin_config = next((c for c in coins_config if c.get('coingecko_id') == coin_id), None)
                if coin_config:
                    data = coin_data[coin_id]
                    price = data.get('usd', 0)
                    change = data.get('usd_24h_change', 0)
                    emoji = "🟢" if change >= 0 else "🔴"
                    
                    output.append(
                        f"{emoji} <b>{coin_config['name']}</b>: ${price:,.4f} "
                        f"({change:+.2f}%)"
                    )
        
        # Other coins
        for coin_config in coins_config:
            coin_id = coin_config.get('coingecko_id')
            if coin_id in coin_data and coin_id not in priority_order:
                data = coin_data[coin_id]
                price = data.get('usd', 0)
                change = data.get('usd_24h_change', 0)
                emoji = "🟢" if change >= 0 else "🔴"
                
                output.append(
                    f"{emoji} <b>{coin_config['name']}</b>: ${price:,.6f} "
                    f"({change:+.2f}%)"
                )
        
        return "\n".join(output)
    
    def _format_goals(self, portfolio_data: dict) -> str:
        """Format accumulation goals progress"""
        if 'error' in portfolio_data:
            return f"❌ Error: {portfolio_data['error']}"
        
        goals = portfolio_data['goals']
        holdings = portfolio_data['holdings']
        totals = portfolio_data['totals']
        
        output = []
        output.append("🎯 <b>ACCUMULATION GOALS</b>\n")
        
        # BTC Goal
        btc_bar = self._progress_bar(goals['btc_progress'])
        output.append(f"₿ <b>BITCOIN</b>")
        output.append(f"{btc_bar} <b>{goals['btc_progress']:.1f}%</b>\n")
        output.append(f"Current: <b>{holdings['btc_amount']:.6f} BTC</b>")
        output.append(f"Target: {goals['btc_target']:.1f} BTC")
        output.append(f"Value: <code>${holdings['btc_amount'] * totals['btc_price']:,.2f}</code>")
        
        if goals['btc_needed'] > 0:
            output.append(f"\n🎯 <b>Still Need:</b>")
            output.append(f"   ₿{goals['btc_needed']:.6f} BTC")
            output.append(f"   <code>${goals['btc_needed_usd']:,.2f}</code>")
        else:
            output.append(f"\n✅ <b>BTC Target Achieved!</b> 🎉")
        
        # ETH Goal
        output.append("\n" + "─" * 30 + "\n")
        eth_bar = self._progress_bar(goals['eth_progress'])
        output.append(f"Ξ <b>ETHEREUM</b>")
        output.append(f"{eth_bar} <b>{goals['eth_progress']:.1f}%</b>\n")
        output.append(f"Current: <b>{holdings['eth_amount']:.4f} ETH</b>")
        output.append(f"Target: {goals['eth_target']:.1f} ETH")
        output.append(f"Value: <code>${holdings['eth_amount'] * totals['eth_price']:,.2f}</code>")
        
        if goals['eth_needed'] > 0:
            output.append(f"\n🎯 <b>Still Need:</b>")
            output.append(f"   Ξ{goals['eth_needed']:.4f} ETH")
            output.append(f"   <code>${goals['eth_needed_usd']:,.2f}</code>")
        else:
            output.append(f"\n✅ <b>ETH Target Achieved!</b> 🎉")
        
        # Total investment needed
        total_needed = goals['btc_needed_usd'] + goals['eth_needed_usd']
        if total_needed > 0:
            output.append(f"\n💰 <b>Total Investment Needed:</b>")
            output.append(f"   <code>${total_needed:,.2f}</code>")
        
        return "\n".join(output)
    
    def _progress_bar(self, percentage: float, length: int = 10) -> str:
        """Generate a text progress bar"""
        filled = int((percentage / 100) * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        self.logger.error(f"Update {update} caused error {context.error}")
    
    def run(self):
        """Start the bot"""
        self.logger.info("Starting Crypto Portfolio Bot...")
        
        # Create application
        self.app = Application.builder().token(self.bot_token).build()
        
        # Register command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.app.add_handler(CommandHandler("summary", self.summary_command))
        self.app.add_handler(CommandHandler("prices", self.prices_command))
        self.app.add_handler(CommandHandler("goals", self.goals_command))
        self.app.add_handler(CommandHandler("btc", self.btc_command))
        self.app.add_handler(CommandHandler("eth", self.eth_command))
        self.app.add_handler(CommandHandler("market", self.market_command))
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
        
        self.logger.info("Bot is ready! Listening for commands...")
        
        # Start polling
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    try:
        bot = CryptoPortfolioBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

