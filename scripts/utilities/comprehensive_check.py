#!/usr/bin/env python3
"""
Comprehensive Article Checker
Performs detailed analysis of ALL articles in both Excel files
"""

from reauthenticator import NewsReauthenticator

def main():
    """Run comprehensive check on all articles"""
    print("🔍 Comprehensive Article Analysis")
    print("=" * 60)
    print("This will analyze EVERY article in both Excel files for:")
    print("• Title-content matching issues")
    print("• Empty titles or content")
    print("• Short content (less than 100 characters)")
    print("• Overall data quality metrics")
    print("• Detailed recommendations")
    print()
    
    response = input("Do you want to proceed with comprehensive analysis? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        print("\n🚀 Starting comprehensive analysis...")
        print("This may take a few minutes to analyze all articles.")
        print()
        
        reauthenticator = NewsReauthenticator()
        reauthenticator.comprehensive_check()
        
        print("\n✅ Comprehensive analysis completed!")
        print("Check logs/reauthenticator.log for detailed logs.")
    else:
        print("Analysis cancelled.")

if __name__ == "__main__":
    main()