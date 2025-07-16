#!/usr/bin/env python3
"""
Quick status check for scraping progress
"""

import os
import glob

def check_status():
    """Check current scraping status"""
    
    # Check for Excel files
    excel_files = glob.glob(r'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/*.xlsx')
    
    print("📊 SCRAPING STATUS CHECK")
    print("=" * 40)
    
    if excel_files:
        for file in excel_files:
            filename = os.path.basename(file)
            size = os.path.getsize(file)
            print(f"📁 Found: {filename}")
            print(f"   Size: {size} bytes")
            
            # Try to read and show basic info
            try:
                import pandas as pd
                df = pd.read_excel(file)
                print(f"   Articles: {len(df)}")
                
                if 'Name of Newspaper' in df.columns:
                    newspapers = df['Name of Newspaper'].value_counts()
                    print(f"   Newspapers: {newspapers.to_dict()}")
                
                if 'Published date of News' in df.columns:
                    dates = pd.to_datetime(df['Published date of News'])
                    print(f"   Date range: {dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}")
                
            except Exception as e:
                print(f"   Error reading file: {e}")
    else:
        print("❌ No Excel files found yet")
        print("   Scraper may still be collecting initial articles...")
    
    print("=" * 40)

if __name__ == "__main__":
    check_status()