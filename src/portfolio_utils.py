"""
Portfolio utilities for valuation and reporting
Provides unified portfolio analysis for both testing and Telegram messages
"""

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """Unified portfolio analysis and reporting"""
    
    def __init__(self, alert_system):
        self.alert_system = alert_system
        self.config = alert_system.config
    
    def generate_portfolio_report(self, coin_data: Dict, format_type: str = "detailed") -> Dict:
        """
        Generate portfolio valuation report
        
        Args:
            coin_data: Current market data for all coins
            format_type: "detailed" for --test, "telegram" for messages
            
        Returns:
            Dictionary with portfolio analysis
        """
        try:
            total_usd = 0.0
            total_btc_equivalent = 0.0
            total_eth_equivalent = 0.0
            altcoins_usd = 0.0
            altcoins_btc_equivalent = 0.0
            btc_price = 0.0
            eth_price = 0.0
            
            # Get Bitcoin and Ethereum prices
            if 'bitcoin' in coin_data:
                btc_price = coin_data['bitcoin'].get('usd', 0)
            if 'ethereum' in coin_data:
                eth_price = coin_data['ethereum'].get('usd', 0)
            
            portfolio_items = []
            btc_amount = 0.0
            eth_amount = 0.0
            
            # Process each coin in configuration
            for coin_config in self.config.get('coins', []):
                coin_id = coin_config.get('coingecko_id')
                coin_name = coin_config.get('name', coin_id)
                current_amount = coin_config.get('current_amount', 0)
                avg_price = float(coin_config.get('avg_price', 0) or 0)
                
                if coin_id in coin_data and current_amount > 0:
                    current_price = float(coin_data[coin_id].get('usd', 0) or 0)
                    total_value_usd = current_amount * current_price
                    
                    # Calculate BTC/ETH equivalents
                    btc_equivalent = (total_value_usd / btc_price) if btc_price > 0 else 0
                    eth_equivalent = (total_value_usd / eth_price) if eth_price > 0 else 0
                    
                    # Gain/Loss relative to avg price
                    invested_usd = current_amount * avg_price if avg_price > 0 else 0.0
                    gain_loss_usd = (total_value_usd - invested_usd) if avg_price > 0 else 0.0
                    gain_loss_pct = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0.0
                    
                    portfolio_items.append({
                        'name': coin_name,
                        'symbol': coin_config.get('symbol', coin_name),
                        'amount': current_amount,
                        'price': current_price,
                        'avg_price': avg_price,
                        'total_usd': total_value_usd,
                        'invested_usd': invested_usd,
                        'btc_equivalent': btc_equivalent,
                        'eth_equivalent': eth_equivalent,
                        'gain_loss_usd': gain_loss_usd,
                        'gain_loss_pct': gain_loss_pct
                    })
                    
                    # Track BTC and ETH amounts
                    if coin_name == 'BTC':
                        btc_amount = current_amount
                    elif coin_name == 'ETH':
                        eth_amount = current_amount
                    else:
                        # Count as altcoin
                        altcoins_usd += total_value_usd
                        altcoins_btc_equivalent += btc_equivalent
                    
                    total_usd += total_value_usd
                    total_btc_equivalent += btc_equivalent
                    total_eth_equivalent += eth_equivalent
            
            # Sort by total USD value (descending)
            portfolio_items.sort(key=lambda x: x['total_usd'], reverse=True)
            
            # Calculate progress toward goals
            btc_target = self.config.get('strategic_alerts', {}).get('accumulation_targets', {}).get('btc_target', 1.0)
            eth_target = self.config.get('strategic_alerts', {}).get('accumulation_targets', {}).get('eth_target', 10.0)
            
            btc_progress = (btc_amount / btc_target) * 100 if btc_target > 0 else 0
            eth_progress = (eth_amount / eth_target) * 100 if eth_target > 0 else 0
            
            # Calculate how much more needed
            btc_needed = max(0, btc_target - btc_amount)
            eth_needed = max(0, eth_target - eth_amount)
            btc_needed_usd = btc_needed * btc_price
            eth_needed_usd = eth_needed * eth_price
            
            return {
                'portfolio_items': portfolio_items,
                'totals': {
                    'total_usd': total_usd,
                    'total_btc_equivalent': total_btc_equivalent,
                    'total_eth_equivalent': total_eth_equivalent,
                    'altcoins_usd': altcoins_usd,
                    'altcoins_btc_equivalent': altcoins_btc_equivalent,
                    'btc_price': btc_price,
                    'eth_price': eth_price
                },
                'holdings': {
                    'btc_amount': btc_amount,
                    'eth_amount': eth_amount
                },
                'goals': {
                    'btc_target': btc_target,
                    'eth_target': eth_target,
                    'btc_progress': btc_progress,
                    'eth_progress': eth_progress,
                    'btc_needed': btc_needed,
                    'eth_needed': eth_needed,
                    'btc_needed_usd': btc_needed_usd,
                    'eth_needed_usd': eth_needed_usd
                }
            }
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {'error': str(e)}
    
    def format_for_test(self, portfolio_data: Dict) -> str:
        """Format portfolio data for --test display"""
        if 'error' in portfolio_data:
            return f"❌ Portfolio analysis failed: {portfolio_data['error']}"
        
        output = []
        output.append("=" * 60)
        output.append("📊 Current Holdings:")
        
        # Individual holdings
        for item in portfolio_data['portfolio_items']:
            if item['amount'] > 0:
                # Format amount based on coin
                if item['name'] in ['BTC']:
                    amount_str = f"{item['amount']:.8f}"
                elif item['name'] in ['ETH']:
                    amount_str = f"{item['amount']:.6f}"
                elif item['name'] in ['SHIB']:
                    amount_str = f"{item['amount']:,.0f}"
                elif item['amount'] < 1:
                    amount_str = f"{item['amount']:.6f}"
                elif item['amount'] < 100:
                    amount_str = f"{item['amount']:.4f}"
                else:
                    amount_str = f"{item['amount']:.2f}"
                
                output.append(f"   {amount_str} {item['name']:<6} -> ${item['total_usd']:>10,.2f} (₿{item['btc_equivalent']:.6f} | Ξ{item['eth_equivalent']:.6f})")
        
        # Summary
        totals = portfolio_data['totals']
        output.append("-" * 60)
        output.append("📈 Portfolio Summary:")
        output.append(f"   Total Altcoins USD Value: ${totals['altcoins_usd']:,.2f}")
        output.append(f"   Total Altcoins BTC Equivalent: ₿{totals['altcoins_btc_equivalent']:.6f}")
        output.append(f"   Total Portfolio USD Value: ${totals['total_usd']:,.2f}")
        output.append(f"   Total Portfolio BTC Equivalent: ₿{totals['total_btc_equivalent']:.6f}")
        output.append(f"   Total Portfolio ETH Equivalent: Ξ{totals['total_eth_equivalent']:.6f}")
        output.append("")
        output.append(f"   Bitcoin Price: ${totals['btc_price']:,.2f}")
        output.append(f"   Ethereum Price: ${totals['eth_price']:,.2f}")
        
        # Progress
        goals = portfolio_data['goals']
        output.append("")
        output.append("🎯 Progress Toward Goals:")
        output.append(f"   BTC: {goals['btc_progress']:.1f}% ({portfolio_data['holdings']['btc_amount']:.6f} / {goals['btc_target']:.1f})")
        output.append(f"   ETH: {goals['eth_progress']:.1f}% ({portfolio_data['holdings']['eth_amount']:.6f} / {goals['eth_target']:.1f})")
        
        if goals['btc_needed'] > 0:
            output.append(f"   Need {goals['btc_needed']:.6f} more BTC (${goals['btc_needed_usd']:,.2f})")
        else:
            output.append(f"   ✅ BTC target achieved!")
            
        if goals['eth_needed'] > 0:
            output.append(f"   Need {goals['eth_needed']:.6f} more ETH (${goals['eth_needed_usd']:,.2f})")
        else:
            output.append(f"   ✅ ETH target achieved!")
        
        output.append("=" * 60)
        return "\n".join(output)
    
    def format_for_telegram(self, portfolio_data: Dict) -> str:
        """Format portfolio data for Telegram messages"""
        if 'error' in portfolio_data:
            return f"❌ Portfolio analysis failed"
        
        output = []
        output.append("💰 PORTFOLIO VALUATION:")
        
        # Main holdings (top 6 by value)
        main_holdings = portfolio_data['portfolio_items'][:6]
        for item in main_holdings:
            if item['amount'] > 0:
                # Format amount based on coin
                if item['name'] in ['BTC']:
                    amount_str = f"{item['amount']:.6f}"
                elif item['name'] in ['ETH']:
                    amount_str = f"{item['amount']:.4f}"
                elif item['name'] in ['SHIB']:
                    amount_str = f"{item['amount']:,.0f}"
                elif item['amount'] < 1:
                    amount_str = f"{item['amount']:.4f}"
                elif item['amount'] < 100:
                    amount_str = f"{item['amount']:.2f}"
                else:
                    amount_str = f"{item['amount']:.1f}"
                
                output.append(f"   {amount_str} {item['name']} -> ${item['total_usd']:,.0f}")
        
        # Summary
        totals = portfolio_data['totals']
        goals = portfolio_data['goals']
        
        output.append("   ---")
        output.append(f"   Total Altcoins: ${totals['altcoins_usd']:,.0f}")
        output.append(f"   Total Portfolio: ${totals['total_usd']:,.0f} (₿{totals['total_btc_equivalent']:.3f})")
        output.append(f"   BTC: ${totals['btc_price']:,.0f} | ETH: ${totals['eth_price']:,.0f}")
        
        # Progress (compact)
        output.append("")
        output.append("🎯 GOAL PROGRESS:")
        output.append(f"   BTC: {goals['btc_progress']:.1f}% ({portfolio_data['holdings']['btc_amount']:.3f}/{goals['btc_target']:.0f})")
        output.append(f"   ETH: {goals['eth_progress']:.1f}% ({portfolio_data['holdings']['eth_amount']:.1f}/{goals['eth_target']:.0f})")
        
        return "\n".join(output)
    
    def format_detailed_for_telegram(self, portfolio_data: Dict) -> str:
        """Format detailed portfolio table for Telegram (HTML parse mode)."""
        if 'error' in portfolio_data:
            return "❌ Falha na análise do portfólio"
        
        # Header and table columns
        lines = []
        lines.append("🔎 Detailed Portfolio Analysis")
        lines.append("<pre>")
        lines.append(f"{'Coin':<8} {'Invested':>14} {'Current':>14} {'Avg Price':>14} {'BTC':>12} {'ETH':>12} {'G/L $ (%)':>16}")
        lines.append(f"{'-'*8} {'-'*14} {'-'*14} {'-'*14} {'-'*12} {'-'*12} {'-'*16}")
        
        # Sort by most profitable (gain/loss USD descending)
        items = [it for it in portfolio_data['portfolio_items'] if it.get('amount', 0) > 0]
        items.sort(key=lambda x: x.get('gain_loss_usd', 0.0), reverse=True)
        
        for item in items:
            name = item.get('name', '')
            invested = item.get('invested_usd', 0.0)
            current_usd = item.get('total_usd', 0.0)
            avg = item.get('avg_price', 0.0)
            btc = item.get('btc_equivalent', 0.0)
            eth = item.get('eth_equivalent', 0.0)
            gl_usd = item.get('gain_loss_usd', 0.0)
            gl_pct = item.get('gain_loss_pct', 0.0)
            sign = '+' if gl_usd >= 0 else '-'
            gl_text = f"{sign}${abs(gl_usd):,.2f} ({gl_pct:+.2f}%)"
            lines.append(
                f"{name:<8} ${invested:>13,.2f} ${current_usd:>13,.2f} ${avg:>13,.2f} {btc:>12.6f} {eth:>12.6f} {gl_text:>16}"
            )
        
        lines.append("")
        totals = portfolio_data['totals']
        lines.append(f"Total USD: ${totals['total_usd']:,.2f}")
        lines.append(f"Total BTC: ₿{totals['total_btc_equivalent']:.6f}")
        lines.append(f"Total ETH: Ξ{totals['total_eth_equivalent']:.6f}")
        lines.append("</pre>")
        
        return "\n".join(lines)
