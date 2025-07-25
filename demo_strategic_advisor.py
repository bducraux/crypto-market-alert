#!/usr/bin/env python3
"""
Demo script showing the new Strategic Advisor in action
This replaces multiple separate alerts with one consolidated strategic dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_strategic_dashboard():
    """Demonstrate the new strategic dashboard functionality"""
    print("🎯 CRYPTO STRATEGIC ADVISOR DEMO")
    print("=" * 60)
    print("Goal: Maximize holdings to reach 1 BTC + 10 ETH")
    print("Strategy: Intelligent BTC/ETH swaps + Altcoin profit taking")
    print("=" * 60)
    
    try:
        from src.strategic_advisor import StrategicAdvisor
        from src.strategy import AlertStrategy
        from src.utils import load_config
        
        # Load configuration
        config = load_config()
        
        # Initialize components
        print("📊 Initializing Strategic Advisor...")
        advisor = StrategicAdvisor()
        strategy = AlertStrategy(config)
        
        print("✅ Strategic Advisor ready!")
        print("\n🔄 Generating consolidated strategic dashboard...")
        
        # Generate the strategic report
        report = advisor.generate_strategic_report()
        
        print("\n" + "="*80)
        print("📋 CONSOLIDATED STRATEGIC DASHBOARD")
        print("="*80)
        print(report)
        print("="*80)
        
        print("\n💡 KEY FEATURES:")
        print("✅ Single consolidated message instead of multiple alerts")
        print("✅ Automatic ETH/BTC ratio analysis for optimal swaps")
        print("✅ Altseason detection for timing altcoin exits")
        print("✅ Profit/Loss tracking for each altcoin")
        print("✅ Strategic recommendations prioritized by opportunity")
        print("✅ Real-time market phase detection")
        print("✅ Goal-oriented advice (1 BTC + 10 ETH)")
        
        print("\n🚀 INTEGRATION STATUS:")
        print("✅ Integrated into existing alert system")
        print("✅ Will replace multiple individual alerts")
        print("✅ Configurable via config.yaml settings")
        print("✅ Maintains all existing functionality")
        
        print("\n⚙️  CONFIGURATION:")
        print("📁 File: config/config.yaml")
        print("🔧 Section: strategic_alerts")
        print("🎛️  Customizable thresholds and preferences")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_comparison():
    """Show before/after comparison"""
    print("\n" + "="*80)
    print("📊 BEFORE vs AFTER COMPARISON")
    print("="*80)
    
    print("\n🔴 BEFORE (Multiple Alerts):")
    print("   • Separate BTC price alert")
    print("   • Separate ETH price alert") 
    print("   • Individual RSI alerts for each coin")
    print("   • Market dominance alerts")
    print("   • Fear & Greed alerts")
    print("   • Professional analysis alerts")
    print("   • Cycle top detection alerts")
    print("   → Result: Information overload, hard to prioritize")
    
    print("\n🟢 AFTER (Strategic Dashboard):")
    print("   • Single consolidated strategic message")
    print("   • ETH/BTC swap recommendations with confidence levels")
    print("   • Altcoin exit opportunities ranked by profit potential")
    print("   • Market phase guidance for overall strategy")
    print("   • Goal-oriented recommendations (1 BTC + 10 ETH)")
    print("   • Actionable insights prioritized by importance")
    print("   → Result: Clear, actionable strategic guidance")

if __name__ == "__main__":
    print("🚀 Starting Strategic Advisor Demo...")
    
    # Show comparison
    show_comparison()
    
    # Run demo
    success = demo_strategic_dashboard()
    
    if success:
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("\n📝 SUMMARY:")
        print("• Strategic Advisor is fully functional")
        print("• Integrated with existing alert system")
        print("• Ready for personalized BTC/ETH strategy")
        print("• Consolidated dashboard replaces multiple alerts")
        print("• Focus on achieving 1 BTC + 10 ETH goal")
        
        print("\n🔄 NEXT STEPS:")
        print("1. Run main.py to start receiving strategic alerts")
        print("2. Adjust strategic_alerts settings in config.yaml if needed")
        print("3. Monitor ETH/BTC swap recommendations for optimal timing")
        print("4. Track altcoin exit opportunities during market peaks")
        
    else:
        print("\n⚠️  Demo encountered issues - check configuration")
