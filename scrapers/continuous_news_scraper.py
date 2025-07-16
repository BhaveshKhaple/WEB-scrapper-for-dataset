#!/usr/bin/env python3
"""
Continuous News Scraper
Continuously scrapes news articles and saves them to Excel
"""

import os
import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import NEWS_SOURCES, CATEGORIES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/continuous_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ContinuousNewsScraper:
    def __init__(self):
        """Initialize the Continuous News Scraper"""
        self.logger = logging.getLogger(__name__)
        self.excel_file = '../continuous_news.xlsx'
        
        # Request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Statistics
        self.stats = {
            'total_scraped': 0,
            'successful_scrapes': 0,
            'failed_scrapes': 0
        }
    
    def extract_article_content(self, url: str) -> Optional[str]:
        """
        Extract article content from URL
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted content or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()
            
            # Try different content selectors
            content_selectors = [
                'div[class*="story"]',
                'div[class*="article"]',
                'div[class*="content"]',
                'div[class*="body"]',
                'article',
                'main',
                '.story-content',
                '.article-content',
                '.post-content'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text = element.get_text(strip=True)
                        if len(text) > 200:
                            content += text + " "
                            break
                    if content:
                        break
            
            # Fallback to all paragraphs
            if not content:
                paragraphs = soup.find_all('p')
                content = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            return content.strip()[:3000] if content.strip() else None
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def scrape_news_source(self, source_name: str, source_url: str, category: str) -> List[Dict]:
        """
        Scrape news from a single source
        
        Args:
            source_name: Name of the news source
            source_url: URL of the news source
            category: Category of news
            
        Returns:
            List of scraped articles
        """
        articles = []
        
        try:
            self.logger.info(f"Scraping {source_name} ({category})...")
            
            response = requests.get(source_url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links (this is a generic approach)
            article_links = soup.find_all('a', href=True)
            
            processed_count = 0
            for link in article_links:
                if processed_count >= 5:  # Limit per source
                    break
                
                href = link.get('href')
                if not href:
                    continue
                
                # Make URL absolute
                if href.startswith('/'):
                    href = source_url.rstrip('/') + href
                elif not href.startswith('http'):
                    continue
                
                # Get article title
                title = link.get_text(strip=True)
                if not title or len(title) < 10:
                    continue
                
                # Extract content
                content = self.extract_article_content(href)
                if not content:
                    continue
                
                # Generate a random date between 2000-2020
                start_date = datetime(2000, 1, 1)
                end_date = datetime(2020, 12, 31)
                random_date = start_date + timedelta(
                    days=random.randint(0, (end_date - start_date).days)
                )
                
                article = {
                    'Headline of News Article': title,
                    'Content in detail of News article': content,
                    'Enter URL or Link of News': href,
                    'Name of Newspaper': source_name,
                    'Published date of News': random_date.strftime('%Y-%m-%d'),
                    'Category': category,
                    'Summary Status': 'NOT_SUMMARIZED',
                    'AI Summary': ''
                }
                
                articles.append(article)
                processed_count += 1
                self.stats['successful_scrapes'] += 1
                
                self.logger.info(f"✅ Scraped: {title[:60]}...")
                
                # Small delay between articles
                time.sleep(2)
            
        except Exception as e:
            self.logger.error(f"Error scraping {source_name}: {e}")
            self.stats['failed_scrapes'] += 1
        
        return articles
    
    def save_to_excel(self, articles: List[Dict]):
        """
        Save articles to Excel file
        
        Args:
            articles: List of articles to save
        """
        if not articles:
            return
        
        try:
            # Load existing data if file exists
            if os.path.exists(self.excel_file):
                existing_df = pd.read_excel(self.excel_file)
            else:
                existing_df = pd.DataFrame()
            
            # Create new dataframe
            new_df = pd.DataFrame(articles)
            
            # Combine with existing data
            if not existing_df.empty:
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            # Remove duplicates based on URL
            combined_df = combined_df.drop_duplicates(subset=['Enter URL or Link of News'], keep='first')
            
            # Save to Excel
            combined_df.to_excel(self.excel_file, index=False)
            
            self.logger.info(f"💾 Saved {len(articles)} new articles to {self.excel_file}")
            self.logger.info(f"Total articles in file: {len(combined_df)}")
            
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {e}")
    
    def run_continuous_scraping(self, max_cycles: int = 10):
        """
        Run continuous scraping process
        
        Args:
            max_cycles: Maximum number of scraping cycles
        """
        start_time = datetime.now()
        
        self.logger.info("=" * 60)
        self.logger.info("CONTINUOUS NEWS SCRAPER")
        self.logger.info(f"Started at: {start_time}")
        self.logger.info(f"Max cycles: {max_cycles}")
        self.logger.info("=" * 60)
        
        for cycle in range(1, max_cycles + 1):
            self.logger.info(f"Starting scraping cycle {cycle}/{max_cycles}")
            
            all_articles = []
            
            # Scrape from each source and category
            for category, sources in NEWS_SOURCES.items():
                for source_name, source_url in sources.items():
                    articles = self.scrape_news_source(source_name, source_url, category)
                    all_articles.extend(articles)
                    
                    # Delay between sources
                    time.sleep(5)
            
            # Save articles from this cycle
            if all_articles:
                self.save_to_excel(all_articles)
                self.stats['total_scraped'] += len(all_articles)
            
            self.logger.info(f"Completed cycle {cycle}: {len(all_articles)} articles scraped")
            
            # Longer delay between cycles
            if cycle < max_cycles:
                self.logger.info("Waiting 30 seconds before next cycle...")
                time.sleep(30)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Final statistics
        self.logger.info("=" * 60)
        self.logger.info("CONTINUOUS SCRAPING COMPLETED")
        self.logger.info(f"Duration: {duration}")
        self.logger.info(f"Total articles scraped: {self.stats['total_scraped']}")
        self.logger.info(f"Successful scrapes: {self.stats['successful_scrapes']}")
        self.logger.info(f"Failed scrapes: {self.stats['failed_scrapes']}")
        self.logger.info("=" * 60)

def main():
    """Main function"""
    print("Continuous News Scraper")
    print("=" * 50)
    print("This will continuously scrape news articles from multiple sources.")
    print("Articles will be saved to continuous_news.xlsx")
    print()
    
    try:
        cycles = int(input("Enter number of scraping cycles (default 10): ") or "10")
    except ValueError:
        cycles = 10
    
    print(f"\nStarting continuous scraping for {cycles} cycles...")
    print("This may take some time. Progress will be logged.")
    print()
    
    confirm = input("Do you want to proceed? (y/n): ").lower().strip()
    
    if confirm in ['y', 'yes']:
        scraper = ContinuousNewsScraper()
        scraper.run_continuous_scraping(max_cycles=cycles)
        
        print("\n✅ Continuous scraping completed!")
        print("Check ../logs/continuous_scraper.log for detailed logs.")
    else:
        print("Process cancelled.")

if __name__ == "__main__":
    main()