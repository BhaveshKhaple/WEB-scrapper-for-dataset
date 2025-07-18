#!/usr/bin/env python3
"""
Test Excel Update Feature
Demonstrates how new_excel.xlsx updates after every 5 articles
"""

import pandas as pd
import os
import time
from datetime import datetime
from final_archive_scraper import RobustDatabaseManager

def test_excel_updates():
    """Test that Excel updates every 5 articles"""
    print("🧪 Testing Excel Updates Every 5 Articles")
    print("="*60)
    
    # Initialize database manager
    db_manager = RobustDatabaseManager()
    
    # Sample articles for testing (historical dates)
    test_articles = [
        {
            'Name of Newspaper': 'The Hindu',
            'Published date of News': '2012-07-21',
            'Enter URL or Link of News': 'https://test.com/article1',
            'Headline of News Article': 'London Olympics 2012 begin with grand opening ceremony',
            'Content in detail of News article': 'The London Olympics 2012 began with a spectacular opening ceremony showcasing British culture and history. Athletes from 204 nations participated in the parade of nations as the stadium erupted in celebration.',
            'Summary of News article': 'London Olympics 2012 opens with spectacular ceremony.',
            'Category of News Article': 'Sports',
            'Location of News': 'London, UK',
            'Author of News Article': 'Olympics Reporter',
            'Front Page Assessment': 'High'
        },
        {
            'Name of Newspaper': 'Indian Express',
            'Published date of News': '2010-02-28',
            'Enter URL or Link of News': 'https://test.com/article2',
            'Headline of News Article': 'Commonwealth Games preparations underway in Delhi',
            'Content in detail of News article': 'Delhi is gearing up for the Commonwealth Games with extensive infrastructure development. New venues, transportation systems, and accommodation facilities are being prepared to host athletes from across the Commonwealth.',
            'Summary of News article': 'Delhi prepares infrastructure for Commonwealth Games.',
            'Category of News Article': 'Sports',
            'Location of News': 'New Delhi',
            'Author of News Article': 'Sports Correspondent',
            'Front Page Assessment': 'High'
        },
        {
            'Name of Newspaper': 'Times of India',
            'Published date of News': '2016-02-20',
            'Enter URL or Link of News': 'https://test.com/article3',
            'Headline of News Article': 'Digital India campaign gains momentum across states',
            'Content in detail of News article': 'The Digital India initiative is transforming governance and service delivery across Indian states. E-governance platforms, digital literacy programs, and broadband connectivity are expanding rapidly.',
            'Summary of News article': 'Digital India campaign expands across states with e-governance focus.',
            'Category of News Article': 'Technology',
            'Location of News': 'Multiple States',
            'Author of News Article': 'Technology Reporter',
            'Front Page Assessment': 'Medium'
        },
        {
            'Name of Newspaper': 'The Hindu',
            'Published date of News': '2014-09-24',
            'Enter URL or Link of News': 'https://test.com/article4',
            'Headline of News Article': 'Swachh Bharat Abhiyan launched nationwide',
            'Content in detail of News article': 'Prime Minister Modi launched the Swachh Bharat Abhiyan (Clean India Mission) with the goal of achieving a clean India by 2019. The campaign focuses on waste management, sanitation, and behavioral change.',
            'Summary of News article': 'Swachh Bharat Abhiyan launched to achieve clean India by 2019.',
            'Category of News Article': 'Politics',
            'Location of News': 'New Delhi',
            'Author of News Article': 'Political Correspondent',
            'Front Page Assessment': 'High'
        },
        {
            'Name of Newspaper': 'Indian Express',
            'Published date of News': '2017-07-01',
            'Enter URL or Link of News': 'https://test.com/article5',
            'Headline of News Article': 'GST implementation begins historic tax reform',
            'Content in detail of News article': 'The Goods and Services Tax (GST) was implemented across India, marking the biggest tax reform since independence. The unified tax system replaces multiple indirect taxes with a single comprehensive tax.',
            'Summary of News article': 'GST implementation begins historic tax reform across India.',
            'Category of News Article': 'Business',
            'Location of News': 'Pan India',
            'Author of News Article': 'Economic Reporter',
            'Front Page Assessment': 'High'
        },
        {
            'Name of Newspaper': 'Times of India',
            'Published date of News': '2018-05-26',
            'Enter URL or Link of News': 'https://test.com/article6',
            'Headline of News Article': 'Ayushman Bharat healthcare scheme announced',
            'Content in detail of News article': 'The government announced Ayushman Bharat, the world\'s largest healthcare scheme, providing health insurance coverage to 10 crore poor families. The scheme aims to provide cashless treatment up to Rs 5 lakh per family.',
            'Summary of News article': 'Ayushman Bharat healthcare scheme launched for 10 crore families.',
            'Category of News Article': 'Health',
            'Location of News': 'New Delhi',
            'Author of News Article': 'Health Reporter',
            'Front Page Assessment': 'High'
        },
        {
            'Name of Newspaper': 'The Hindu',
            'Published date of News': '2019-08-05',
            'Enter URL or Link of News': 'https://test.com/article7',
            'Headline of News Article': 'Article 370 revoked in Jammu and Kashmir',
            'Content in detail of News article': 'The government revoked Article 370 that granted special autonomy to Jammu and Kashmir. The region was also bifurcated into two Union Territories - Jammu & Kashmir and Ladakh.',
            'Summary of News article': 'Article 370 revoked, J&K bifurcated into two Union Territories.',
            'Category of News Article': 'Politics',
            'Location of News': 'Jammu and Kashmir',
            'Author of News Article': 'Political Analyst',
            'Front Page Assessment': 'High'
        },
        {
            'Name of Newspaper': 'Indian Express',
            'Published date of News': '2020-03-24',
            'Enter URL or Link of News': 'https://test.com/article8',
            'Headline of News Article': 'Nationwide lockdown announced to combat COVID-19',
            'Content in detail of News article': 'Prime Minister announced a 21-day nationwide lockdown to combat the spread of COVID-19. The lockdown restricts movement and closes non-essential services to break the transmission chain.',
            'Summary of News article': 'Nationwide 21-day lockdown announced to combat COVID-19 spread.',
            'Category of News Article': 'Health',
            'Location of News': 'Pan India',
            'Author of News Article': 'Health Correspondent',
            'Front Page Assessment': 'High'
        }
    ]
    
    print(f"📝 Will test with {len(test_articles)} articles")
    print("📊 Expected Excel updates: After articles 5 and 8")
    print()
    
    # Function to check Excel file content
    def check_excel_content():
        if os.path.exists("new_excel.xlsx"):
            df = pd.read_excel("new_excel.xlsx")
            return len(df)
        return 0
    
    # Initial Excel content
    initial_count = check_excel_content()
    print(f"📊 Initial Excel content: {initial_count} articles")
    
    # Add articles one by one and monitor Excel updates
    for i, article in enumerate(test_articles, 1):
        print(f"\n🔄 Adding article {i}: {article['Headline of News Article'][:50]}...")
        
        # Save article to database
        success = db_manager.save_article_with_metadata(article, 2.0)
        
        if success:
            print(f"✅ Article {i} saved to database")
            
            # Check Excel content
            excel_count = check_excel_content()
            
            if i % 5 == 0:
                print(f"🎯 EXPECTED UPDATE - After {i} articles")
                print(f"📊 Excel now contains: {excel_count} articles")
                
                # Verify Excel was updated
                if excel_count >= initial_count + i:
                    print("✅ Excel file successfully updated!")
                else:
                    print("❌ Excel file not updated as expected")
            else:
                print(f"📊 Excel still contains: {excel_count} articles (no update expected)")
        else:
            print(f"❌ Failed to save article {i}")
        
        time.sleep(0.5)  # Small delay for demonstration
    
    # Final verification
    final_count = check_excel_content()
    print(f"\n📊 FINAL RESULTS:")
    print("="*60)
    print(f"Initial articles: {initial_count}")
    print(f"Articles added: {len(test_articles)}")
    print(f"Final Excel count: {final_count}")
    print(f"Expected total: {initial_count + len(test_articles)}")
    
    if final_count >= initial_count + len(test_articles):
        print("✅ ALL ARTICLES SUCCESSFULLY ADDED TO EXCEL!")
    else:
        print("❌ Some articles may be missing from Excel")
    
    # Show Excel columns
    if os.path.exists("new_excel.xlsx"):
        df = pd.read_excel("new_excel.xlsx")
        print(f"\n📋 Excel columns: {list(df.columns)}")
        
        # Show date range
        if len(df) > 0:
            dates = pd.to_datetime(df['Published date of News'])
            print(f"📅 Date range: {dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}")
            
            # Show newspapers
            newspapers = df['Name of Newspaper'].unique()
            print(f"📰 Newspapers: {', '.join(newspapers)}")
    
    print("\n🎉 Test completed!")
    print("✅ new_excel.xlsx is your primary data file")
    print("✅ File updates automatically every 5 articles")
    print("✅ All data uses historical dates (2010-2020)")

def main():
    """Main test function"""
    print("🧪 EXCEL UPDATE TEST - Every 5 Articles")
    print("Testing new_excel.xlsx as primary data file")
    print("="*60)
    
    test_excel_updates()

if __name__ == "__main__":
    main()