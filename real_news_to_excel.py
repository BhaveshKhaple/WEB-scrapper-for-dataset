#!/usr/bin/env python3
"""
Real News Scraper - Collects actual news articles and saves to Excel
"""

import os
import sys
import random
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import re
import hashlib
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('real_news_scraper.log'),
        logging.StreamHandler()
    ]
)

class RealNewsToExcelScraper:
    """
    Real News Scraper that collects actual articles and saves to Excel
    """
    
    def __init__(self, excel_file=r'C:\Users\yadne\OneDrive - MIT - Chhatrapati Sambhajinagar\Desktop\scrapper\News_Articles_Collection.xlsx'):
        self.logger = logging.getLogger(__name__)
        self.excel_file = excel_file
        self.setup_session()
        
        # Current working news websites
        self.news_sites = {
            'The Hindu': {
                'base_url': 'https://www.thehindu.com',
                'sections': [
                    'https://www.thehindu.com/news/national/',
                    'https://www.thehindu.com/news/international/',
                    'https://www.thehindu.com/opinion/',
                    'https://www.thehindu.com/business/',
                    'https://www.thehindu.com/sport/',
                    'https://www.thehindu.com/sci-tech/',
                    'https://www.thehindu.com/news/cities/'
                ],
                'article_selectors': ['h3 a', '.story-card h3 a', '.story-card-list a'],
                'headline_selectors': ['h1', '.headline', 'h1.title'],
                'content_selectors': ['.story-element-text', 'div[data-component="paragraph"]', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date-line', '.update-time']
            },
            'Indian Express': {
                'base_url': 'https://indianexpress.com',
                'sections': [
                    'https://indianexpress.com/section/india/',
                    'https://indianexpress.com/section/world/',
                    'https://indianexpress.com/section/opinion/',
                    'https://indianexpress.com/section/business/',
                    'https://indianexpress.com/section/sports/',
                    'https://indianexpress.com/section/technology/',
                    'https://indianexpress.com/section/cities/'
                ],
                'article_selectors': ['h3 a', '.articles h2 a', '.ie-story h3 a'],
                'headline_selectors': ['h1', '.native_story_title', '.story-title'],
                'content_selectors': ['.story-element-text', '.ie-content', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'NDTV': {
                'base_url': 'https://www.ndtv.com',
                'sections': [
                    'https://www.ndtv.com/india-news',
                    'https://www.ndtv.com/world-news',
                    'https://www.ndtv.com/opinion',
                    'https://www.ndtv.com/business',
                    'https://www.ndtv.com/sports',
                    'https://www.ndtv.com/science',
                    'https://www.ndtv.com/cities'
                ],
                'article_selectors': ['h3 a', '.story-list h3 a', '.news_Itm h3 a'],
                'headline_selectors': ['h1', '.sp-cn h1', '.story-title'],
                'content_selectors': ['.story-element-text', '.sp-cn div', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'Hindustan Times': {
                'base_url': 'https://www.hindustantimes.com',
                'sections': [
                    'https://www.hindustantimes.com/india-news',
                    'https://www.hindustantimes.com/world-news',
                    'https://www.hindustantimes.com/opinion',
                    'https://www.hindustantimes.com/business',
                    'https://www.hindustantimes.com/sports',
                    'https://www.hindustantimes.com/tech',
                    'https://www.hindustantimes.com/cities'
                ],
                'article_selectors': ['h3 a', '.story-list h3 a', '.listView h3 a'],
                'headline_selectors': ['h1', '.story-title', '.headline'],
                'content_selectors': ['.story-element-text', '.detail p', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'Times of India': {
                'base_url': 'https://timesofindia.indiatimes.com',
                'sections': [
                    'https://timesofindia.indiatimes.com/india',
                    'https://timesofindia.indiatimes.com/world',
                    'https://timesofindia.indiatimes.com/business',
                    'https://timesofindia.indiatimes.com/sports',
                    'https://timesofindia.indiatimes.com/entertainment',
                    'https://timesofindia.indiatimes.com/tech',
                    'https://timesofindia.indiatimes.com/city'
                ],
                'article_selectors': ['h3 a', '.story-list h3 a', '.col_l_8 h3 a'],
                'headline_selectors': ['h1', '.story-title', '.headline'],
                'content_selectors': ['.story-element-text', '.Normal', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'News18': {
                'base_url': 'https://www.news18.com',
                'sections': [
                    'https://www.news18.com/india/',
                    'https://www.news18.com/world/',
                    'https://www.news18.com/business/',
                    'https://www.news18.com/sports/',
                    'https://www.news18.com/tech/',
                    'https://www.news18.com/opinion/',
                    'https://www.news18.com/cities/'
                ],
                'article_selectors': ['h3 a', '.story-card h3 a', '.uberstory h3 a'],
                'headline_selectors': ['h1', '.story-title', '.headline'],
                'content_selectors': ['.story-element-text', '.story-content p', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'Republic World': {
                'base_url': 'https://www.republicworld.com',
                'sections': [
                    'https://www.republicworld.com/india-news/',
                    'https://www.republicworld.com/world-news/',
                    'https://www.republicworld.com/business-news/',
                    'https://www.republicworld.com/sports-news/',
                    'https://www.republicworld.com/technology-news/',
                    'https://www.republicworld.com/entertainment-news/',
                    'https://www.republicworld.com/opinion/'
                ],
                'article_selectors': ['h3 a', '.story-card h3 a', '.news-card h3 a'],
                'headline_selectors': ['h1', '.story-title', '.headline'],
                'content_selectors': ['.story-element-text', '.story-content p', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'India Today': {
                'base_url': 'https://www.indiatoday.in',
                'sections': [
                    'https://www.indiatoday.in/india',
                    'https://www.indiatoday.in/world',
                    'https://www.indiatoday.in/business',
                    'https://www.indiatoday.in/sports',
                    'https://www.indiatoday.in/technology',
                    'https://www.indiatoday.in/opinion',
                    'https://www.indiatoday.in/cities'
                ],
                'article_selectors': ['h3 a', '.story-card h3 a', '.catagory-listing h3 a'],
                'headline_selectors': ['h1', '.story-title', '.headline'],
                'content_selectors': ['.story-element-text', '.description p', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'Zee News': {
                'base_url': 'https://zeenews.india.com',
                'sections': [
                    'https://zeenews.india.com/india',
                    'https://zeenews.india.com/world',
                    'https://zeenews.india.com/business',
                    'https://zeenews.india.com/sports',
                    'https://zeenews.india.com/technology',
                    'https://zeenews.india.com/entertainment',
                    'https://zeenews.india.com/opinion'
                ],
                'article_selectors': ['h3 a', '.story-card h3 a', '.news-list h3 a'],
                'headline_selectors': ['h1', '.story-title', '.headline'],
                'content_selectors': ['.story-element-text', '.article-content p', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            },
            'Economic Times': {
                'base_url': 'https://economictimes.indiatimes.com',
                'sections': [
                    'https://economictimes.indiatimes.com/news',
                    'https://economictimes.indiatimes.com/markets',
                    'https://economictimes.indiatimes.com/industry',
                    'https://economictimes.indiatimes.com/tech',
                    'https://economictimes.indiatimes.com/opinion',
                    'https://economictimes.indiatimes.com/politics-and-nation',
                    'https://economictimes.indiatimes.com/international'
                ],
                'article_selectors': ['h3 a', '.story-card h3 a', '.eachStory h3 a'],
                'headline_selectors': ['h1', '.story-title', '.headline'],
                'content_selectors': ['.story-element-text', '.artText', 'p'],
                'author_selectors': ['.author', '.byline'],
                'date_selectors': ['.date', '.publish-date']
            }
        }
        
        # Storage
        self.collected_articles = []
        self.unique_urls = set()
        self.processed_urls = set()
        self.unique_headlines = set()  # Added for headline duplicate checking
        
        # Load existing data if file exists
        self.load_existing_data()
    
    def setup_session(self):
        """Setup requests session with retry strategy"""
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def load_existing_data(self):
        """Load existing data from Excel file and JSON archives"""
        try:
            # First load from Excel if it exists
            if os.path.exists(self.excel_file):
                df = pd.read_excel(self.excel_file)
                self.logger.info(f"Loaded {len(df)} existing articles from Excel")
                
                # Add existing URLs and headlines to processed sets
                for _, row in df.iterrows():
                    if pd.notna(row.get('Enter URL or Link of News')):
                        url_hash = hashlib.md5(str(row['Enter URL or Link of News']).encode()).hexdigest()
                        self.unique_urls.add(url_hash)
                        self.processed_urls.add(str(row['Enter URL or Link of News']))
                    
                    # Also track headlines to avoid duplicates
                    if pd.notna(row.get('Headline of News Article')):
                        headline_hash = hashlib.md5(str(row['Headline of News Article']).lower().encode()).hexdigest()
                        self.unique_headlines.add(headline_hash)
                
                # Convert to list for appending
                self.collected_articles = df.to_dict('records')
            else:
                self.logger.info(f"No existing Excel file found.")
                self.collected_articles = []
            
            # Load from JSON archives to recover the 200+ articles
            json_files = [
                'The_Hindu_historical_archive.json',
                'Hindustan_Times_historical_archive.json'
            ]
            
            initial_count = len(self.collected_articles)
            
            for json_file in json_files:
                if os.path.exists(json_file):
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if 'articles' in data:
                                for article in data['articles']:
                                    # Check for duplicates
                                    url = article.get('source_url', '')
                                    headline = article.get('headline', '')
                                    
                                    if url and headline and len(headline) > 10:
                                        url_hash = hashlib.md5(url.encode()).hexdigest()
                                        headline_hash = hashlib.md5(headline.lower().encode()).hexdigest()
                                        
                                        # More lenient duplicate checking for recovery
                                        if url_hash not in self.unique_urls:
                                            # Convert to Excel format
                                            formatted_article = {
                                                'Name of Newspaper': article.get('site_name', 'Unknown'),
                                                'Published date of News': article.get('publication_date', datetime.now().strftime('%Y-%m-%d')),
                                                'Enter URL or Link of News': url,
                                                'Headline of News Article': headline,
                                                'Content in detail of News article': article.get('content', ''),
                                                'Human Summary For Article': '',
                                                'News Category': article.get('category', 'General News'),
                                                'Summary Status': 'NEEDS_SUMMARY'
                                            }
                                            
                                            self.collected_articles.append(formatted_article)
                                            self.unique_urls.add(url_hash)
                                            self.unique_headlines.add(headline_hash)
                                            self.processed_urls.add(url)
                                
                                self.logger.info(f"Loaded {len(data['articles'])} articles from {json_file}")
                    except Exception as e:
                        self.logger.error(f"Error loading from {json_file}: {e}")
            
            recovered_count = len(self.collected_articles) - initial_count
            if recovered_count > 0:
                self.logger.info(f"Recovered {recovered_count} articles from JSON archives")
                self.logger.info(f"Total articles now: {len(self.collected_articles)}")
                
                # Save the recovered data to Excel immediately
                self.save_to_excel()
                
        except Exception as e:
            self.logger.error(f"Error loading existing data: {e}")
            self.collected_articles = []
    
    def create_url_hash(self, url: str) -> str:
        """Create a hash for URL uniqueness"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def create_headline_hash(self, headline: str) -> str:
        """Create a hash for headline uniqueness"""
        return hashlib.md5(headline.lower().encode()).hexdigest()
    
    def is_duplicate_article(self, url: str, headline: str) -> bool:
        """Check if article is duplicate by URL or headline"""
        url_hash = self.create_url_hash(url)
        headline_hash = self.create_headline_hash(headline)
        
        return url_hash in self.unique_urls or headline_hash in self.unique_headlines
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove unwanted characters
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\"\'\/\&]', '', text)
        return text
    
    def extract_article_content(self, url: str, site_config: Dict) -> Optional[Dict]:
        """Extract article content from URL"""
        try:
            if url in self.processed_urls:
                return None
            
            self.logger.info(f"Extracting: {url}")
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract headline
            headline = ""
            for selector in site_config['headline_selectors']:
                try:
                    elem = soup.select_one(selector)
                    if elem:
                        headline = self.clean_text(elem.get_text())
                        if headline and len(headline) > 10:
                            break
                except:
                    continue
            
            # Extract content
            content_parts = []
            for selector in site_config['content_selectors']:
                try:
                    elems = soup.select(selector)
                    for elem in elems:
                        text = self.clean_text(elem.get_text())
                        if text and len(text) > 30:
                            content_parts.append(text)
                except:
                    continue
            
            content = ' '.join(content_parts)
            
            # Extract author
            author = ""
            for selector in site_config['author_selectors']:
                try:
                    elem = soup.select_one(selector)
                    if elem:
                        author = self.clean_text(elem.get_text())
                        if author:
                            break
                except:
                    continue
            
            # Extract date
            pub_date = ""
            for selector in site_config['date_selectors']:
                try:
                    elem = soup.select_one(selector)
                    if elem:
                        pub_date = self.clean_text(elem.get_text())
                        if pub_date:
                            break
                except:
                    continue
            
            # Validate content
            if not headline or len(headline) < 10:
                self.logger.warning(f"Invalid headline for {url}")
                return None
            
            if not content or len(content) < 100:
                self.logger.warning(f"Invalid content for {url}")
                return None
            
            # Check for duplicates
            if self.is_duplicate_article(url, headline):
                self.logger.info(f"Duplicate article found, skipping: {headline[:50]}...")
                return None
            
            # Categorize based on URL and content
            category = self.categorize_article(url, headline, content)
            
            return {
                'headline': headline,
                'content': content[:1500],  # Limit content
                'author': author or "Unknown",
                'publication_date': pub_date or datetime.now().strftime('%Y-%m-%d'),
                'source_url': url,
                'category': category
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting {url}: {e}")
            return None
    
    def categorize_article(self, url: str, headline: str, content: str) -> str:
        """Categorize article based on URL and content"""
        url_lower = url.lower()
        text_lower = (headline + " " + content).lower()
        
        # Category keywords
        categories = {
            'Politics': ['politics', 'government', 'parliament', 'minister', 'election', 'party', 'bjp', 'congress', 'modi', 'rahul'],
            'Sports': ['sports', 'cricket', 'football', 'tennis', 'olympics', 'match', 'team', 'player', 'ipl', 'bcci'],
            'Business': ['business', 'economy', 'market', 'stock', 'finance', 'rupee', 'inflation', 'gdp', 'corporate', 'company'],
            'Technology': ['technology', 'tech', 'ai', 'software', 'internet', 'digital', 'startup', 'app', 'data', 'cyber'],
            'Health': ['health', 'medical', 'doctor', 'hospital', 'covid', 'vaccine', 'disease', 'treatment', 'medicine'],
            'Education': ['education', 'school', 'college', 'university', 'student', 'exam', 'cbse', 'neet', 'jee'],
            'Entertainment': ['entertainment', 'movie', 'film', 'actor', 'bollywood', 'hollywood', 'music', 'celebrity'],
            'Science': ['science', 'research', 'space', 'isro', 'nasa', 'discovery', 'study', 'scientist']
        }
        
        # Check URL first
        for category, keywords in categories.items():
            if any(keyword in url_lower for keyword in keywords):
                return category
        
        # Check content
        for category, keywords in categories.items():
            keyword_count = sum(1 for keyword in keywords if keyword in text_lower)
            if keyword_count >= 2:
                return category
        
        return 'General News'
    
    def find_articles_from_section(self, site_name: str, section_url: str, limit: int = 10) -> List[str]:
        """Find article URLs from a news section"""
        try:
            self.logger.info(f"Scraping section: {section_url}")
            
            response = self.session.get(section_url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            site_config = self.news_sites[site_name]
            
            article_links = []
            for selector in site_config['article_selectors']:
                try:
                    links = soup.select(selector)
                    for link in links:
                        href = link.get('href')
                        if href:
                            if href.startswith('/'):
                                href = urljoin(site_config['base_url'], href)
                            elif not href.startswith('http'):
                                href = urljoin(site_config['base_url'], href)
                            
                            if self.is_valid_article_url(href):
                                article_links.append(href)
                except:
                    continue
            
            # Remove duplicates and limit
            unique_links = list(dict.fromkeys(article_links))[:limit]
            self.logger.info(f"Found {len(unique_links)} articles from {section_url}")
            return unique_links
            
        except Exception as e:
            self.logger.error(f"Error scraping section {section_url}: {e}")
            return []
    
    def is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid article URL"""
        if not url:
            return False
        
        # Skip common non-article URLs
        exclude_patterns = [
            'javascript:', 'mailto:', '#', 'about:', 'contact',
            'subscribe', 'login', 'register', 'search', 'category',
            'tag', 'page', 'archive', 'rss', 'xml', 'sitemap'
        ]
        
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        # Must be a reasonable length
        if len(url) < 30:
            return False
        
        return True
    
    def scrape_site(self, site_name: str, articles_per_section: int = 5) -> List[Dict]:
        """Scrape articles from a news site"""
        self.logger.info(f"Scraping {site_name}")
        
        site_config = self.news_sites[site_name]
        articles = []
        
        for section_url in site_config['sections']:
            try:
                # Find articles from this section
                article_urls = self.find_articles_from_section(site_name, section_url, articles_per_section)
                
                for url in article_urls:
                    if self.create_url_hash(url) in self.unique_urls:
                        continue
                    
                    article_data = self.extract_article_content(url, site_config)
                    if article_data:
                        article_data['site_name'] = site_name
                        article_data['scraped_date'] = datetime.now().strftime('%Y-%m-%d')
                        articles.append(article_data)
                        
                        # Track duplicates
                        self.unique_urls.add(self.create_url_hash(url))
                        self.processed_urls.add(url)
                        self.unique_headlines.add(self.create_headline_hash(article_data['headline']))
                        
                        self.logger.info(f"Collected: {article_data['headline'][:50]}...")
                        
                        # Delay between requests
                        time.sleep(2)
                
                # Delay between sections
                time.sleep(3)
                
            except Exception as e:
                self.logger.error(f"Error scraping section {section_url}: {e}")
                continue
        
        self.logger.info(f"Collected {len(articles)} articles from {site_name}")
        return articles
    
    def save_to_excel(self):
        """Save collected articles to Excel file"""
        try:
            if not self.collected_articles:
                self.logger.warning("No articles to save")
                return
            
            # Create DataFrame from collected articles
            df = pd.DataFrame(self.collected_articles)
            
            # Check if data is already in Excel format or internal format
            if 'Name of Newspaper' in df.columns:
                # Already in Excel format (from recovery)
                df_mapped = df
            else:
                # Map our columns to required format
                df_mapped = pd.DataFrame()
                df_mapped['Name of Newspaper'] = df['site_name'] if 'site_name' in df.columns else 'Unknown'
                df_mapped['Published date of News'] = df['publication_date'] if 'publication_date' in df.columns else datetime.now().strftime('%Y-%m-%d')
                df_mapped['Enter URL or Link of News'] = df['source_url'] if 'source_url' in df.columns else ''
                df_mapped['Headline of News Article'] = df['headline'] if 'headline' in df.columns else ''
                df_mapped['Content in detail of News article'] = df['content'] if 'content' in df.columns else ''
                df_mapped['Human Summary For Article'] = ''  # Will be filled later
                df_mapped['News Category'] = df['category'] if 'category' in df.columns else 'General News'
                df_mapped['Summary Status'] = 'NEEDS_SUMMARY'
            
            # Save to Excel
            df_mapped.to_excel(self.excel_file, index=False)
            self.logger.info(f"Saved {len(df_mapped)} articles to {self.excel_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {e}")
            # Debug info
            if self.collected_articles:
                self.logger.info(f"Sample article structure: {self.collected_articles[0]}")
                self.logger.info(f"Article keys: {list(self.collected_articles[0].keys()) if isinstance(self.collected_articles[0], dict) else 'Not a dict'}")
    
    def run_scraper(self, target_articles: int = 100):
        """Run the main scraping process"""
        self.logger.info(f"Starting news scraping for {target_articles} articles")
        
        current_count = len(self.collected_articles)
        self.logger.info(f"Starting with {current_count} existing articles")
        
        remaining = target_articles - current_count
        if remaining <= 0:
            self.logger.info("Target already reached!")
            return
        
        articles_per_site = remaining // len(self.news_sites)
        
        for site_name in self.news_sites:
            try:
                new_articles = self.scrape_site(site_name, articles_per_site // 7)  # Distribute across sections
                self.collected_articles.extend(new_articles)
                
                # Save progress
                self.save_to_excel()
                
                current_total = len(self.collected_articles)
                self.logger.info(f"Progress: {current_total}/{target_articles} articles collected")
                
                if current_total >= target_articles:
                    break
                    
            except Exception as e:
                self.logger.error(f"Error scraping {site_name}: {e}")
                continue
        
        final_count = len(self.collected_articles)
        self.logger.info(f"Scraping completed! Collected {final_count} total articles")
        
        # Final save
        self.save_to_excel()
        
        return final_count

def main():
    """Main function"""
    scraper = RealNewsToExcelScraper()
    
    try:
        total_articles = scraper.run_scraper(target_articles=300)
        print(f"\nScraping completed successfully!")
        print(f"Total articles collected: {total_articles}")
        print(f"Saved to: {scraper.excel_file}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        scraper.save_to_excel()
    except Exception as e:
        print(f"Error during scraping: {e}")
        scraper.save_to_excel()

if __name__ == "__main__":
    main()