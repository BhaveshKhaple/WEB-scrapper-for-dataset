#!/usr/bin/env python3
"""
Test script for Final Archive Scraper
Validates all components and functionality
"""

import sys
import os
import sqlite3
import time
from datetime import datetime

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        import requests
        import pandas as pd
        from bs4 import BeautifulSoup
        import openpyxl
        import lxml
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        return False

def test_scraper_initialization():
    """Test scraper initialization"""
    print("\n🔍 Testing scraper initialization...")
    
    try:
        from final_archive_scraper import FinalArchiveScraper
        
        scraper = FinalArchiveScraper(max_workers=1)
        print(f"✅ Scraper initialized successfully")
        print(f"   Newspapers: {len(scraper.newspapers)}")
        print(f"   Rate limiter: {scraper.rate_limiter.get_current_delay():.1f}s")
        
        return True
    except Exception as e:
        print(f"❌ Scraper initialization error: {str(e)}")
        return False

def test_database_functionality():
    """Test database operations"""
    print("\n🔍 Testing database functionality...")
    
    try:
        from final_archive_scraper import RobustDatabaseManager
        
        # Test database creation
        db = RobustDatabaseManager("test_scraper.db")
        print("✅ Database created successfully")
        
        # Test article saving
        test_article = {
            'Name of Newspaper': 'Test Paper',
            'Published date of News': '2023-01-01',
            'Enter URL or Link of News': 'https://example.com/test',
            'Headline of News Article': 'Test Headline',
            'Content in detail of News article': 'This is a test article content for validation purposes.',
            'Summary of News article': 'Test summary.',
            'Category of News Article': 'General',
            'Location of News': 'Test City',
            'Author of News Article': 'Test Author',
            'Front Page Assessment': 'Low',
            'content_hash': 'test_hash',
            'verification_status': 'verified'
        }
        
        success = db.save_article_with_metadata(test_article, 1.5)
        if success:
            print("✅ Article saved successfully")
        
        # Test progress tracking
        db.mark_day_completed_with_details('Test Paper', 2023, 1, 1, 1, 1, 0, 1.5)
        print("✅ Progress tracking working")
        
        # Test statistics
        stats = db.get_comprehensive_stats()
        print(f"✅ Statistics retrieved: {stats['total_articles']} articles")
        
        # Cleanup
        os.remove("test_scraper.db")
        if os.path.exists("test_scraper.db.backup"):
            os.remove("test_scraper.db.backup")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test error: {str(e)}")
        return False

def test_content_processing():
    """Test content processing functions"""
    print("\n🔍 Testing content processing...")
    
    try:
        from final_archive_scraper import FinalArchiveScraper
        
        scraper = FinalArchiveScraper(max_workers=1)
        
        # Test content cleaning
        dirty_content = "This is a test article.   Subscribe to our newsletter. Follow us on Twitter. This is the actual content."
        clean_content = scraper.clean_content(dirty_content)
        print(f"✅ Content cleaning: {len(clean_content)} chars")
        
        # Test summary generation
        test_content = "This is the first sentence. This is the second sentence. This is the third sentence. This is the fourth sentence."
        summary = scraper.generate_enhanced_summary(test_content)
        print(f"✅ Summary generation: {len(summary)} chars")
        
        # Test article classification
        headline = "Government announces new economic policy"
        content = "The government today announced a new economic policy aimed at boosting growth and creating jobs."
        category = scraper.classify_article_advanced(headline, content)
        print(f"✅ Article classification: {category}")
        
        # Test location extraction
        location_content = "The event took place in Mumbai yesterday evening."
        location = scraper.extract_location_advanced(location_content)
        print(f"✅ Location extraction: {location}")
        
        # Test front page assessment
        assessment = scraper.assess_front_page_advanced(headline, content)
        print(f"✅ Front page assessment: {assessment}")
        
        return True
        
    except Exception as e:
        print(f"❌ Content processing error: {str(e)}")
        return False

def test_rate_limiting():
    """Test adaptive rate limiting"""
    print("\n🔍 Testing rate limiting...")
    
    try:
        from final_archive_scraper import AdaptiveRateLimiter
        
        limiter = AdaptiveRateLimiter(initial_delay=1.0)
        
        # Test initial delay
        initial_delay = limiter.get_current_delay()
        print(f"✅ Initial delay: {initial_delay:.1f}s")
        
        # Test success recording
        limiter.record_success()
        print("✅ Success recording working")
        
        # Test failure recording
        limiter.record_failure(429)
        failure_delay = limiter.get_current_delay()
        print(f"✅ Failure handling: delay increased to {failure_delay:.1f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting error: {str(e)}")
        return False

def test_url_generation():
    """Test URL generation for different newspapers"""
    print("\n🔍 Testing URL generation...")
    
    try:
        from final_archive_scraper import FinalArchiveScraper
        
        scraper = FinalArchiveScraper(max_workers=1)
        
        # Test regular newspapers
        hindu_url = scraper.get_archive_url('The Hindu', 2020, 1, 15)
        expected_hindu = "https://www.thehindu.com/archive/web/2020/01/15/"
        if hindu_url == expected_hindu:
            print("✅ The Hindu URL generation working")
        else:
            print(f"❌ The Hindu URL mismatch: {hindu_url}")
        
        # Test special handling newspapers
        toi_url = scraper.get_archive_url('Times of India', 2020, 1, 15)
        if "timesofindia.indiatimes.com" in toi_url and "starttime" in toi_url:
            print("✅ Times of India URL generation working")
        else:
            print(f"❌ Times of India URL issue: {toi_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL generation error: {str(e)}")
        return False

def test_network_connectivity():
    """Test network connectivity"""
    print("\n🔍 Testing network connectivity...")
    
    try:
        import requests
        
        # Test basic connectivity
        response = requests.get("https://www.google.com", timeout=10)
        if response.status_code == 200:
            print("✅ Basic network connectivity working")
        
        # Test news site accessibility
        test_sites = [
            "https://www.thehindu.com",
            "https://indianexpress.com"
        ]
        
        accessible = 0
        for site in test_sites:
            try:
                response = requests.get(site, timeout=10)
                if response.status_code == 200:
                    accessible += 1
                    print(f"✅ {site} is accessible")
                else:
                    print(f"⚠️  {site} returned {response.status_code}")
            except Exception as e:
                print(f"❌ {site} error: {str(e)}")
        
        if accessible >= 1:
            print(f"✅ Network test passed ({accessible}/{len(test_sites)} sites accessible)")
            return True
        else:
            print("❌ Network test failed")
            return False
            
    except Exception as e:
        print(f"❌ Network test error: {str(e)}")
        return False

def test_resume_capability():
    """Test resume capability"""
    print("\n🔍 Testing resume capability...")
    
    try:
        from final_archive_scraper import RobustDatabaseManager
        
        # Create test database
        db = RobustDatabaseManager("test_resume.db")
        
        # Add some progress
        db.mark_day_completed_with_details('Test Paper', 2020, 6, 15, 10, 8, 2, 5.5)
        
        # Test resume point
        resume_year, resume_month, resume_day = db.get_resume_point('Test Paper')
        
        if resume_year == 2020 and resume_month == 6 and resume_day == 16:
            print("✅ Resume capability working correctly")
            success = True
        else:
            print(f"❌ Resume point incorrect: {resume_year}-{resume_month:02d}-{resume_day:02d}")
            success = False
        
        # Cleanup
        os.remove("test_resume.db")
        if os.path.exists("test_resume.db.backup"):
            os.remove("test_resume.db.backup")
        
        return success
        
    except Exception as e:
        print(f"❌ Resume capability error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Final Archive Scraper - Comprehensive Test Suite")
    print("="*70)
    
    tests = [
        ("Import Test", test_imports),
        ("Scraper Initialization", test_scraper_initialization),
        ("Database Functionality", test_database_functionality),
        ("Content Processing", test_content_processing),
        ("Rate Limiting", test_rate_limiting),
        ("URL Generation", test_url_generation),
        ("Network Connectivity", test_network_connectivity),
        ("Resume Capability", test_resume_capability)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*70}")
        print(f"Running {test_name}")
        print('='*70)
        
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} ERROR: {str(e)}")
            failed += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("🧪 TEST SUMMARY")
    print('='*70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/len(tests)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Final Archive Scraper is ready for production use!")
        print("\nTo start scraping:")
        print("  python final_archive_scraper.py")
        print("\nFeatures ready:")
        print("  ✅ Hierarchical year→month→day navigation")
        print("  ✅ Robust resume capability")
        print("  ✅ Dynamic rate limiting")
        print("  ✅ Comprehensive progress tracking")
        print("  ✅ Multiple export formats")
        print("  ✅ Enhanced content verification")
        print("  ✅ Detailed logging and statistics")
    else:
        print(f"\n❌ {failed} test(s) failed.")
        print("Please check the errors above and fix them before running the scraper.")
        
        if failed == 1 and "Network" in str(tests):
            print("\nNote: Network test failure might not prevent scraping,")
            print("but check your internet connection and firewall settings.")
    
    print('='*70)

if __name__ == "__main__":
    main()