#!/usr/bin/env python3
"""
Fixed Scraper with Correct Archive URLs
Uses the actual working archive URL patterns provided
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime, timedelta
import sqlite3
import logging
import random
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FixedArchiveScraper:
    def __init__(self):
        # Get the project root directory (2 levels up from this script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        
        # Use absolute paths
        self.db_path = os.path.join(project_root, "data", "database", "final_scraper.db")
        self.excel_file = os.path.join(project_root, "data", "excel_files", "new_excel.xlsx")
        
        # Ensure directories exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.excel_file), exist_ok=True)
        
        # Initialize counters for this session
        self.article_count = 0  # Count of NEW articles added in this session
        self.session_start_time = datetime.now()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Correct archive URL patterns
        self.archive_patterns = {
            'The Hindu': 'https://www.thehindu.com/archive/{year}/{month:02d}/{day:02d}/',
            'Indian Express': 'https://indianexpress.com/archive/{year}/{month:02d}/{day:02d}/',
            # Deccan Chronicle doesn't have public archives, skip for now
        }
        
        self.init_database()
    
    def init_database(self):
        """Initialize database with correct schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                newspaper TEXT NOT NULL,
                date TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                headline TEXT,
                content TEXT,
                summary TEXT,
                category TEXT,
                location TEXT,
                author TEXT,
                front_page_assessment TEXT,
                content_hash TEXT,
                verification_status TEXT DEFAULT 'verified',
                word_count INTEGER,
                scraping_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                processing_time REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("✅ Database initialized")
    
    def scrape_archive_page(self, newspaper, year, month, day):
        """Scrape articles from archive page"""
        if newspaper not in self.archive_patterns:
            logging.warning(f"❌ No archive pattern for {newspaper}")
            return []
        
        # Build archive URL
        archive_url = self.archive_patterns[newspaper].format(
            year=year, month=month, day=day
        )
        
        logging.info(f"📰 Scraping {newspaper} - {year}-{month:02d}-{day:02d}")
        logging.info(f"🔗 Archive URL: {archive_url}")
        
        try:
            response = self.session.get(archive_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                articles = []
                
                # Extract article links based on newspaper
                if newspaper == 'The Hindu':
                    articles = self.extract_hindu_articles(soup, archive_url, year, month, day)
                elif newspaper == 'Indian Express':
                    articles = self.extract_express_articles(soup, archive_url, year, month, day)
                
                logging.info(f"✅ Found {len(articles)} articles for {year}-{month:02d}-{day:02d}")
                return articles
                
            else:
                logging.warning(f"❌ Archive page not accessible: {response.status_code}")
                return []
                
        except Exception as e:
            logging.error(f"❌ Error scraping archive: {str(e)}")
            return []
    
    def extract_hindu_articles(self, soup, base_url, year, month, day):
        """Extract articles from The Hindu archive page"""
        articles = []
        
        # Look for article links in The Hindu archive
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            href = link.get('href', '')
            
            # Filter for actual article URLs
            if any(pattern in href for pattern in ['/news/', '/opinion/', '/business/', '/sport/', '/sci-tech/']):
                if not href.startswith('http'):
                    href = 'https://www.thehindu.com' + href
                
                # Extract article content
                article = self.extract_article_content(href, 'The Hindu', f"{year}-{month:02d}-{day:02d}")
                if article:
                    articles.append(article)
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                    # Limit articles per day
                    if len(articles) >= 5:
                        break
        
        return articles
    
    def extract_express_articles(self, soup, base_url, year, month, day):
        """Extract articles from Indian Express archive page"""
        articles = []
        
        # Look for article links in Indian Express archive
        article_links = soup.find_all('a', href=True)
        
        for link in article_links:
            href = link.get('href', '')
            
            # Filter for actual article URLs
            if any(pattern in href for pattern in ['/article/', '/news/', '/opinion/', '/business/', '/sports/']):
                if not href.startswith('http'):
                    href = 'https://indianexpress.com' + href
                
                # Extract article content
                article = self.extract_article_content(href, 'Indian Express', f"{year}-{month:02d}-{day:02d}")
                if article:
                    articles.append(article)
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                    # Limit articles per day
                    if len(articles) >= 5:
                        break
        
        return articles
    
    def extract_article_content(self, url, newspaper, date):
        """Extract content from individual article"""
        try:
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract headline
                headline = self.extract_headline(soup, newspaper)
                
                # Extract content
                content = self.extract_content(soup, newspaper)
                
                # Extract author
                author = self.extract_author(soup, newspaper)
                
                # Validate article
                if headline and content and len(content) > 100:
                    article = {
                        'newspaper': newspaper,
                        'date': date,
                        'url': url,
                        'headline': headline,
                        'content': content,
                        'summary': content[:300] + "..." if len(content) > 300 else content,
                        'category': self.categorize_article(headline, content),
                        'location': self.extract_location(content),
                        'author': author,
                        'front_page_assessment': self.assess_importance(headline, content),
                        'word_count': len(content.split()),
                        'content_hash': str(hash(content))
                    }
                    
                    logging.info(f"✅ Extracted: {headline[:50]}...")
                    return article
                else:
                    logging.warning(f"❌ Invalid article: {url}")
                    return None
            else:
                logging.warning(f"❌ Article not accessible: {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Error extracting article: {str(e)}")
            return None
    
    def extract_headline(self, soup, newspaper):
        """Extract headline based on newspaper"""
        selectors = {
            'The Hindu': ['h1.title', 'h1', '.headline', '.article-title'],
            'Indian Express': ['h1', '.headline', '.story-title', '.article-title']
        }
        
        for selector in selectors.get(newspaper, ['h1']):
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ""
    
    def extract_content(self, soup, newspaper):
        """Extract content based on newspaper"""
        selectors = {
            'The Hindu': ['.article-content', '.story-content', '.content', 'div[data-component="text"]'],
            'Indian Express': ['.story-content', '.article-content', '.full-details', '.content']
        }
        
        for selector in selectors.get(newspaper, ['.content']):
            elements = soup.select(selector)
            if elements:
                content = ""
                for element in elements:
                    content += element.get_text(strip=True) + " "
                return content.strip()
        
        return ""
    
    def extract_author(self, soup, newspaper):
        """Extract author based on newspaper"""
        selectors = {
            'The Hindu': ['.author', '.byline', '.writer-name', '.author-name'],
            'Indian Express': ['.author', '.byline', '.writer', '.author-name']
        }
        
        for selector in selectors.get(newspaper, ['.author']):
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "Unknown"
    
    def categorize_article(self, headline, content):
        """Categorize article based on content"""
        categories = {
            'Politics': ['government', 'minister', 'parliament', 'election', 'policy', 'political'],
            'Business': ['economy', 'market', 'business', 'financial', 'company', 'trade'],
            'Sports': ['cricket', 'football', 'sports', 'match', 'tournament', 'player'],
            'Technology': ['technology', 'digital', 'internet', 'software', 'tech', 'innovation'],
            'Health': ['health', 'medical', 'hospital', 'disease', 'treatment', 'healthcare'],
            'Education': ['education', 'school', 'university', 'student', 'academic', 'learning']
        }
        
        text = (headline + " " + content).lower()
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General'
    
    def extract_location(self, content):
        """Extract location from content"""
        indian_cities = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore', 'Hyderabad', 
                        'Pune', 'Ahmedabad', 'Surat', 'Jaipur', 'Lucknow', 'Kanpur']
        
        for city in indian_cities:
            if city.lower() in content.lower():
                return city
        
        return 'India'
    
    def assess_importance(self, headline, content):
        """Assess article importance"""
        high_importance_keywords = ['breaking', 'urgent', 'major', 'significant', 'important', 
                                   'crisis', 'emergency', 'historic', 'landmark']
        
        text = (headline + " " + content).lower()
        
        if any(keyword in text for keyword in high_importance_keywords):
            return 'High'
        elif len(content) > 1000:
            return 'Medium'
        else:
            return 'Low'
    
    def save_article(self, article):
        """Save article to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if article already exists
            cursor.execute('SELECT id FROM articles WHERE url = ?', (article['url'],))
            existing = cursor.fetchone()
            
            if existing:
                logging.info(f"⚠️ Article already exists: {article['headline'][:50]}...")
                conn.close()
                return False
            
            # Insert new article
            cursor.execute('''
                INSERT INTO articles 
                (newspaper, date, url, headline, content, summary, category, location, 
                 author, front_page_assessment, content_hash, verification_status, 
                 word_count, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article['newspaper'],
                article['date'],
                article['url'],
                article['headline'],
                article['content'],
                article['summary'],
                article['category'],
                article['location'],
                article['author'],
                article['front_page_assessment'],
                article['content_hash'],
                'verified',
                article['word_count'],
                2.0
            ))
            
            conn.commit()
            conn.close()
            
            # Update Excel every 5 articles
            self.article_count += 1
            if self.article_count % 5 == 0:
                self.update_excel_file()
                logging.info(f"✅ Excel updated after {self.article_count} new articles")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ Error saving article: {str(e)}")
            return False
    
    def update_excel_file(self):
        """Update new_excel.xlsx with current data"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Get all articles
            articles_df = pd.read_sql_query('''
                SELECT newspaper, date, url, headline, content, summary, category, 
                       location, author, front_page_assessment
                FROM articles 
                ORDER BY date DESC, newspaper
            ''', conn)
            
            if not articles_df.empty:
                # Map to Excel columns
                column_mapping = {
                    'newspaper': 'Name of Newspaper',
                    'date': 'Published date of News',
                    'url': 'Enter URL or Link of News',
                    'headline': 'Headline of News Article',
                    'content': 'Content in detail of News article',
                    'summary': 'Summary of News article',
                    'category': 'Category of News Article',
                    'location': 'Location of News',
                    'author': 'Author of News Article',
                    'front_page_assessment': 'Front Page Assessment'
                }
                
                excel_df = articles_df.rename(columns=column_mapping)
                
                required_columns = [
                    'Name of Newspaper',
                    'Published date of News',
                    'Enter URL or Link of News',
                    'Headline of News Article',
                    'Content in detail of News article',
                    'Summary of News article',
                    'Category of News Article',
                    'Location of News',
                    'Author of News Article',
                    'Front Page Assessment'
                ]
                
                final_df = excel_df[required_columns]
                final_df.to_excel(self.excel_file, index=False)
                
                logging.info(f"✅ Updated {self.excel_file} with {len(final_df)} total articles ({self.article_count} new in this session)")
                return True
            
            conn.close()
            
        except Exception as e:
            logging.error(f"❌ Error updating Excel: {str(e)}")
            return False
    
    def scrape_date_range(self, start_year=2020, end_year=2023, max_articles=50):
        """Scrape articles from date range"""
        logging.info(f"🚀 Starting scrape from {start_year} to {end_year}")
        
        total_articles = 0
        
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                for day in range(1, 32):
                    try:
                        # Check if date is valid
                        test_date = datetime(year, month, day)
                        
                        # Skip future dates
                        if test_date > datetime.now():
                            continue
                        
                        # Scrape each newspaper
                        for newspaper in self.archive_patterns.keys():
                            articles = self.scrape_archive_page(newspaper, year, month, day)
                            
                            for article in articles:
                                if self.save_article(article):
                                    total_articles += 1
                                    
                                    if total_articles >= max_articles:
                                        logging.info(f"🎯 Reached target of {max_articles} articles")
                                        self.update_excel_file()  # Final update
                                        return total_articles
                            
                            # Rate limiting between newspapers
                            time.sleep(random.uniform(2, 5))
                        
                        # Rate limiting between days
                        time.sleep(random.uniform(1, 3))
                        
                    except ValueError:
                        # Invalid date (like Feb 30)
                        continue
                    except Exception as e:
                        logging.error(f"❌ Error processing {year}-{month:02d}-{day:02d}: {str(e)}")
                        continue
        
        # Final Excel update
        self.update_excel_file()
        logging.info(f"🎉 Scraping completed! Total articles: {total_articles}")
        return total_articles

def main():
    """Main function"""
    print("🚀 FIXED ARCHIVE SCRAPER WITH CORRECT URLs")
    print("="*60)
    print("Using correct archive patterns:")
    print("📰 The Hindu: https://www.thehindu.com/archive/YYYY/MM/DD/")
    print("📰 Indian Express: https://indianexpress.com/archive/YYYY/MM/DD/")
    print("="*60)
    
    scraper = FixedArchiveScraper()
    
    # Get user input
    try:
        start_year = int(input("Enter start year (default 2020): ") or "2020")
        end_year = int(input("Enter end year (default 2023): ") or "2023")
        max_articles = int(input("Enter max articles to scrape (default 50): ") or "50")
        
        print(f"\n🎯 Configuration:")
        print(f"   Date Range: {start_year}-{end_year}")
        print(f"   Max Articles: {max_articles}")
        print(f"   Excel File: new_excel.xlsx")
        print("="*60)
        
        # Start scraping
        total = scraper.scrape_date_range(start_year, end_year, max_articles)
        
        print(f"\n🎉 SCRAPING COMPLETED!")
        print(f"✅ Total articles scraped: {total}")
        print(f"📄 Excel file: new_excel.xlsx")
        print(f"💾 Database: final_scraper.db")
        
    except KeyboardInterrupt:
        print("\n⏹️ Scraping stopped by user")
        scraper.update_excel_file()
        print("✅ Data saved to new_excel.xlsx")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    main()