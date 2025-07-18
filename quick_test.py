#!/usr/bin/env python3
"""
Quick test of the fixed scraper
"""

import sys
import os

# Add the scripts directory to the Python path
scripts_path = os.path.join(os.path.dirname(__file__), 'scripts')
sys.path.append(scripts_path)

def quick_test():
    print("QUICK SCRAPER TEST")
    print("="*30)
    
    try:
        from scrapers.fixed_scraper_with_correct_urls import FixedArchiveScraper
        
        scraper = FixedArchiveScraper()
        
        # Check current count
        import sqlite3
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        before_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"Articles before: {before_count}")
        
        # Test with a date that should have new articles
        print("Testing 2010-01-11...")
        total = scraper.scrape_date_range(2010, 2010, 5)  # Just 5 articles max
        
        # Check final count
        conn = sqlite3.connect(scraper.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles")
        after_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"Articles after: {after_count}")
        print(f"New articles added: {after_count - before_count}")
        print(f"Session counter: {scraper.article_count}")
        
        if after_count > before_count:
            print("✅ SUCCESS: New articles are being appended!")
        else:
            print("⚠️ No new articles (might be duplicates)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()