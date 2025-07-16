#!/usr/bin/env python3
"""
Article Quality Checker - Quick and Comprehensive Analysis
"""

from reauthenticator import NewsReauthenticator

def main():
    """Run article quality check"""
    print("📊 Article Quality Checker")
    print("=" * 50)
    print("Choose analysis type:")
    print("1. Quick check (basic statistics)")
    print("2. Comprehensive analysis (detailed review of ALL articles)")
    print()
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    reauthenticator = NewsReauthenticator()
    
    if choice == "1":
        print("\n🔍 Running quick check...")
        print("Checking basic title-content match statistics...")
        print()
        reauthenticator.quick_check()
        print("\n✅ Quick check completed!")
        
    elif choice == "2":
        print("\n🔍 Running comprehensive analysis...")
        print("This will analyze EVERY article for various quality issues...")
        print()
        reauthenticator.comprehensive_check()
        print("\n✅ Comprehensive analysis completed!")
        
    else:
        print("Invalid choice. Running quick check by default...")
        reauthenticator.quick_check()
        print("\n✅ Quick check completed!")
    
    print("Check logs/reauthenticator.log for detailed logs.")

if __name__ == "__main__":
    main()