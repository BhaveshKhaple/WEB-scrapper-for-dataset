#!/usr/bin/env python3
"""
Main News Scraper Runner
"""

import sys
import os
sys.path.append(os.path.join('scripts', 'scrapers'))

def main():
    print("INDIAN NEWS SCRAPER")
    print("="*40)
    
    try:
        from fixed_scraper_with_correct_urls import FixedArchiveScraper
        
        print("Output: data/excel_files/new_excel.xlsx")
        print("Database: data/database/final_scraper.db")
        print("="*40)
        
        scraper = FixedArchiveScraper()
        
        start_year = int(input("Start year (default 2020): ") or "2020")
        end_year = int(input("End year (default 2023): ") or "2023")
        max_articles = int(input("Max articles (default 50): ") or "50")
        
        print(f"\nStarting scraper: {start_year}-{end_year}, max {max_articles} articles")
        
        total = scraper.scrape_date_range(start_year, end_year, max_articles)
        
        print(f"\nCOMPLETED! Scraped {total} articles")
        print("Check: data/excel_files/new_excel.xlsx")
        
    except ImportError:
        print("ERROR: Scraper not found. Check scripts/scrapers/ directory")
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
