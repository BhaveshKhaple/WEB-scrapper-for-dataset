#!/usr/bin/env python3
"""
Start the enhanced news scraper with Gemini API
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the scraper
from enhanced_news_scraper import EnhancedNewsScraperAgent

def main():
    """Main execution function"""
    print("🚀 Starting Enhanced News Scraper with Gemini API...")
    print("📋 Target: Collect 100 articles from various Indian English news sources")
    print("🔧 Using Gemini API for AI-powered summaries and categorization")
    print("=" * 60)
    
    try:
        # Initialize the scraper (will use .env file automatically)
        scraper = EnhancedNewsScraperAgent()
        
        # Start scraping
        scraper.run()
        
    except Exception as e:
        print(f"❌ Error starting scraper: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()