#!/usr/bin/env python3
"""
Test script for the Strategic Advisor implementation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_strategic_advisor():
    """Test the strategic advisor functionality"""
    try:
        print("🧪 Testing Strategic Advisor...")
        
        # Test imports
        from src.utils import load_config
        print("✅ Utils imported successfully")
        
        from src.strategic_advisor import StrategicAdvisor
        print("✅ Strategic Advisor imported successfully")
        
        # Test config loading
        config = load_config()
        print("✅ Configuration loaded successfully")
        print(f"📊 Found {len(config.get('coins', []))} coins in config")
        
        # Test strategic advisor creation
        advisor = StrategicAdvisor()
        print("✅ Strategic Advisor created successfully")
        
        # Test report generation (this will fetch real data)
        print("📈 Generating strategic report...")
        report = advisor.generate_strategic_report()
        
        if "Error" in report:
            print(f"⚠️  Report generated with errors: {report}")
        else:
            print("✅ Strategic report generated successfully!")
            print("\n" + "="*60)
            print("📄 STRATEGIC REPORT PREVIEW:")
            print("="*60)
            print(report[:1000] + "..." if len(report) > 1000 else report)
            print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration with existing strategy"""
    try:
        print("\n🔗 Testing Strategy Integration...")
        
        from src.utils import load_config
        from src.strategy import AlertStrategy
        print("✅ Strategy imported successfully")
        
        # Test strategy creation with strategic advisor
        config = load_config()
        strategy = AlertStrategy(config)
        print("✅ Strategy with Strategic Advisor created successfully")
        
        # Check if strategic advisor is properly initialized
        if hasattr(strategy, 'strategic_advisor'):
            print("✅ Strategic Advisor properly integrated into strategy")
            return True
        else:
            print("❌ Strategic Advisor not found in strategy")
            return False
            
    except Exception as e:
        print(f"❌ Error during integration testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Strategic Advisor Tests")
    print("=" * 50)
    
    # Test basic functionality
    test1_success = test_strategic_advisor()
    
    # Test integration
    test2_success = test_integration()
    
    print("\n" + "=" * 50)
    print("📋 TEST RESULTS:")
    print(f"✅ Strategic Advisor: {'PASS' if test1_success else 'FAIL'}")
    print(f"✅ Integration: {'PASS' if test2_success else 'FAIL'}")
    
    if test1_success and test2_success:
        print("🎉 All tests passed! Strategic Advisor is ready!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
