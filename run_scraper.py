#!/usr/bin/env python3
"""
Main execution script for the News Scraper
Provides a user-friendly interface to run the scraper
"""

import os
import sys
import time
from datetime import datetime
from config import EXCEL_FILENAME

def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🗞️  INDIAN ENGLISH NEWS SCRAPER")
    print("=" * 70)
    print("📅 Target: 1000-1100 articles from 2010-2020")
    print("🎯 Source: Indian English newspapers via Google News")
    print("📊 Output: Structured Excel file with LLM summaries")
    print("=" * 70)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        "selenium", "webdriver_manager", "pandas", 
        "openpyxl", "cohere", "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_chrome():
    """Check Chrome installation"""
    print("\n🌐 Checking Chrome installation...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.get("https://www.google.com")
        
        if "Google" in driver.title:
            print("✅ Chrome WebDriver is working!")
            driver.quit()
            return True
        else:
            print("❌ Chrome WebDriver test failed")
            driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ Chrome WebDriver error: {e}")
        return False

def get_user_preferences():
    """Get user preferences for scraping"""
    print("\n⚙️  Configuration Options:")
    print("1. Use default settings (recommended)")
    print("2. Custom configuration")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    preferences = {
        "use_enhanced": True,
        "test_mode": False,
        "max_articles": 1100,
        "custom_config": False
    }
    
    if choice == "2":
        preferences["custom_config"] = True
        
        # Ask for enhanced version
        enhanced = input("Use enhanced scraper? (y/n): ").strip().lower()
        preferences["use_enhanced"] = enhanced in ["y", "yes"]
        
        # Ask for test mode
        test = input("Run in test mode (collect only 10 articles)? (y/n): ").strip().lower()
        preferences["test_mode"] = test in ["y", "yes"]
        
        if preferences["test_mode"]:
            preferences["max_articles"] = 10
        else:
            try:
                max_articles = int(input("Maximum articles to collect (default 1100): ").strip() or "1100")
                preferences["max_articles"] = max_articles
            except ValueError:
                preferences["max_articles"] = 1100
    
    return preferences

def setup_test_mode():
    """Configure for test mode"""
    print("\n🧪 Setting up test mode...")
    
    # Create a temporary config for testing
    test_config = """
# Test Configuration
from datetime import datetime

START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2015, 1, 31)
MAX_ARTICLES = 10
MIN_ARTICLES = 5
"""
    
    with open("test_config.py", "w") as f:
        f.write(test_config)
    
    print("✅ Test configuration created")

def run_scraper(preferences):
    """Run the scraper with given preferences"""
    print("\n🚀 Starting news scraper...")
    
    # Get Cohere API key
    cohere_key = input("\nEnter your Cohere API key: ").strip()
    
    if not cohere_key:
        print("❌ Cohere API key is required!")
        return False
    
    # Setup test mode if needed
    if preferences["test_mode"]:
        setup_test_mode()
        print("🧪 Running in test mode (limited articles)")
    
    # Choose scraper version
    if preferences["use_enhanced"]:
        print("🔧 Using enhanced scraper...")
        try:
            from enhanced_news_scraper import EnhancedNewsScraperAgent
            
            # Modify config for test mode
            if preferences["test_mode"]:
                import config
                config.MAX_ARTICLES = preferences["max_articles"]
                config.MIN_ARTICLES = min(5, preferences["max_articles"])
            
            scraper = EnhancedNewsScraperAgent(cohere_key)
            
        except ImportError as e:
            print(f"❌ Enhanced scraper import failed: {e}")
            print("🔄 Falling back to basic scraper...")
            from news_scraper import NewsScraperAgent
            scraper = NewsScraperAgent(cohere_key)
    else:
        print("🔧 Using basic scraper...")
        from news_scraper import NewsScraperAgent
        scraper = NewsScraperAgent(cohere_key)
    
    # Start scraping
    start_time = datetime.now()
    
    try:
        scraper.run_scraper()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n⏱️  Scraping completed in {duration}")
        print(f"📊 Check the Excel file for results")
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Scraping interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Scraping failed: {e}")
        return False

def show_results():
    """Show final results"""
    print("\n📊 Results Summary:")
    
    excel_file = EXCEL_FILENAME
    
    try:
        import pandas as pd
        df = pd.read_excel(excel_file)
        
        print(f"📄 Total articles collected: {len(df)}")
        print(f"📁 Output file: {excel_file}")
        
        if len(df) > 0:
            print(f"🗞️  Newspapers covered: {df['Newspaper'].nunique()}")
            print(f"📅 Date range: {df['Published Date'].min()} to {df['Published Date'].max()}")
            print(f"🏷️  Categories: {df['News Category'].value_counts().head().to_dict()}")
        
    except Exception as e:
        print(f"❌ Could not read results: {e}")

def main():
    """Main execution function"""
    print_banner()
    
    # Check system requirements
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    if not check_chrome():
        print("\n❌ Please fix Chrome WebDriver issues")
        print("Try running: python setup.py")
        return
    
    # Get user preferences
    preferences = get_user_preferences()
    
    print("\n📋 Configuration Summary:")
    print(f"   Enhanced scraper: {'Yes' if preferences['use_enhanced'] else 'No'}")
    print(f"   Test mode: {'Yes' if preferences['test_mode'] else 'No'}")
    print(f"   Max articles: {preferences['max_articles']}")
    
    # Confirm start
    confirm = input("\nStart scraping? (y/n): ").strip().lower()
    
    if confirm not in ["y", "yes"]:
        print("❌ Scraping cancelled")
        return
    
    # Run scraper
    success = run_scraper(preferences)
    
    if success:
        show_results()
        print("\n🎉 Scraping completed successfully!")
    else:
        print("\n❌ Scraping failed or was interrupted")
    
    # Cleanup test files
    if preferences["test_mode"] and os.path.exists("test_config.py"):
        os.remove("test_config.py")

if __name__ == "__main__":
    main()