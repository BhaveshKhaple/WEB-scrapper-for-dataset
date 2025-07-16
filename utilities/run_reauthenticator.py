#!/usr/bin/env python3
"""
Auto-run reauthenticator without user input
"""

from reauthenticator import NewsReauthenticator

def main():
    """Run reauthenticator automatically"""
    print("Auto News Article Reauthenticator")
    print("=" * 50)
    print("Checking and fixing title-content mismatches...")
    print()
    
    reauthenticator = NewsReauthenticator()
    results = reauthenticator.run_reauthentication()
    
    print(f"\n✅ Reauthentication completed!")
    print(f"Articles processed: {results['processed']}")
    print(f"Articles fixed: {results['fixed']}")
    print(f"Failed to fix: {results['failed']}")
    print("\nCheck reauthenticator.log for detailed logs.")

if __name__ == "__main__":
    main()