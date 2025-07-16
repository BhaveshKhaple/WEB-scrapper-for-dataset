#!/usr/bin/env python3
"""
Clean News Scraper - Collects exactly 200 news articles and saves to Excel
Ensures proper Excel format with all required columns and no duplicates
"""

import os
import sys
import random
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin, urlparse
import hashlib
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up logging (fix encoding issues)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class NewsArticleScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Create new Excel file
        self.excel_file = r'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/new_excel.xlsx'
        self.collected_articles = []
        self.unique_urls = set()
        self.unique_headlines = set()
        self.target_articles = 1000
        self.setup_session()
        
        # Required Excel columns (exact names as specified)
        self.required_columns = [
            'Name of Newspaper',
            'Published date of News',
            'Enter URL or Link of News',
            'Headline of News Article',
            'Content in detail of News article',
            'Human Summary For Article News',
            'Category',
            'Summary Status'
        ]
        
        # Comprehensive news sources configuration
        self.news_sources = {
            'Times of India': {
                'base_url': 'https://timesofindia.indiatimes.com',
                'sections': [
                    'https://timesofindia.indiatimes.com/india',
                    'https://timesofindia.indiatimes.com/world',
                    'https://timesofindia.indiatimes.com/business',
                    'https://timesofindia.indiatimes.com/sports',
                    'https://timesofindia.indiatimes.com/entertainment',
                    'https://timesofindia.indiatimes.com/tech'
                ]
            },
            'The Hindu': {
                'base_url': 'https://www.thehindu.com',
                'sections': [
                    'https://www.thehindu.com/news/national/',
                    'https://www.thehindu.com/news/international/',
                    'https://www.thehindu.com/business/',
                    'https://www.thehindu.com/sport/',
                    'https://www.thehindu.com/sci-tech/',
                    'https://www.thehindu.com/opinion/'
                ]
            },
            'Hindustan Times': {
                'base_url': 'https://www.hindustantimes.com',
                'sections': [
                    'https://www.hindustantimes.com/india-news',
                    'https://www.hindustantimes.com/world-news',
                    'https://www.hindustantimes.com/business',
                    'https://www.hindustantimes.com/sports',
                    'https://www.hindustantimes.com/tech',
                    'https://www.hindustantimes.com/lifestyle'
                ]
            },
            'Indian Express': {
                'base_url': 'https://indianexpress.com',
                'sections': [
                    'https://indianexpress.com/section/india/',
                    'https://indianexpress.com/section/world/',
                    'https://indianexpress.com/section/business/',
                    'https://indianexpress.com/section/sports/',
                    'https://indianexpress.com/section/technology/',
                    'https://indianexpress.com/section/lifestyle/'
                ]
            },
            'NDTV': {
                'base_url': 'https://www.ndtv.com',
                'sections': [
                    'https://www.ndtv.com/india-news',
                    'https://www.ndtv.com/world-news',
                    'https://www.ndtv.com/business',
                    'https://www.ndtv.com/sports',
                    'https://www.ndtv.com/health',
                    'https://www.ndtv.com/entertainment'
                ]
            },
            'India Today': {
                'base_url': 'https://www.indiatoday.in',
                'sections': [
                    'https://www.indiatoday.in/india',
                    'https://www.indiatoday.in/world',
                    'https://www.indiatoday.in/business',
                    'https://www.indiatoday.in/sports',
                    'https://www.indiatoday.in/technology',
                    'https://www.indiatoday.in/lifestyle'
                ]
            },
            'The Telegraph': {
                'base_url': 'https://www.telegraphindia.com',
                'sections': [
                    'https://www.telegraphindia.com/india',
                    'https://www.telegraphindia.com/world',
                    'https://www.telegraphindia.com/business',
                    'https://www.telegraphindia.com/sports',
                    'https://www.telegraphindia.com/opinion',
                    'https://www.telegraphindia.com/culture'
                ]
            },
            'Deccan Chronicle': {
                'base_url': 'https://www.deccanchronicle.com',
                'sections': [
                    'https://www.deccanchronicle.com/nation',
                    'https://www.deccanchronicle.com/world',
                    'https://www.deccanchronicle.com/business',
                    'https://www.deccanchronicle.com/sports',
                    'https://www.deccanchronicle.com/technology',
                    'https://www.deccanchronicle.com/lifestyle'
                ]
            },
            'The New Indian Express': {
                'base_url': 'https://www.newindianexpress.com',
                'sections': [
                    'https://www.newindianexpress.com/nation',
                    'https://www.newindianexpress.com/world',
                    'https://www.newindianexpress.com/business',
                    'https://www.newindianexpress.com/sport',
                    'https://www.newindianexpress.com/opinions',
                    'https://www.newindianexpress.com/lifestyle'
                ]
            },
            'Mint': {
                'base_url': 'https://www.livemint.com',
                'sections': [
                    'https://www.livemint.com/news',
                    'https://www.livemint.com/politics',
                    'https://www.livemint.com/companies',
                    'https://www.livemint.com/markets',
                    'https://www.livemint.com/technology',
                    'https://www.livemint.com/opinion'
                ]
            },
            'Business Standard': {
                'base_url': 'https://www.business-standard.com',
                'sections': [
                    'https://www.business-standard.com/india-news',
                    'https://www.business-standard.com/world-news',
                    'https://www.business-standard.com/companies',
                    'https://www.business-standard.com/markets',
                    'https://www.business-standard.com/technology',
                    'https://www.business-standard.com/opinion'
                ]
            },
            'Financial Express': {
                'base_url': 'https://www.financialexpress.com',
                'sections': [
                    'https://www.financialexpress.com/india-news/',
                    'https://www.financialexpress.com/world-news/',
                    'https://www.financialexpress.com/economy/',
                    'https://www.financialexpress.com/market/',
                    'https://www.financialexpress.com/industry/',
                    'https://www.financialexpress.com/opinion/'
                ]
            },
            'DNA': {
                'base_url': 'https://www.dnaindia.com',
                'sections': [
                    'https://www.dnaindia.com/india',
                    'https://www.dnaindia.com/world',
                    'https://www.dnaindia.com/money',
                    'https://www.dnaindia.com/sports',
                    'https://www.dnaindia.com/analysis',
                    'https://www.dnaindia.com/lifestyle'
                ]
            },
            'The Tribune': {
                'base_url': 'https://www.tribuneindia.com',
                'sections': [
                    'https://www.tribuneindia.com/news/nation',
                    'https://www.tribuneindia.com/news/world',
                    'https://www.tribuneindia.com/news/business',
                    'https://www.tribuneindia.com/news/sports',
                    'https://www.tribuneindia.com/news/comment',
                    'https://www.tribuneindia.com/news/lifestyle'
                ]
            },
            'The Economic Times': {
                'base_url': 'https://economictimes.indiatimes.com',
                'sections': [
                    'https://economictimes.indiatimes.com/news',
                    'https://economictimes.indiatimes.com/markets',
                    'https://economictimes.indiatimes.com/industry',
                    'https://economictimes.indiatimes.com/tech',
                    'https://economictimes.indiatimes.com/jobs',
                    'https://economictimes.indiatimes.com/opinion'
                ]
            },
            'News18': {
                'base_url': 'https://www.news18.com',
                'sections': [
                    'https://www.news18.com/india/',
                    'https://www.news18.com/world/',
                    'https://www.news18.com/business/',
                    'https://www.news18.com/sports/',
                    'https://www.news18.com/tech/',
                    'https://www.news18.com/lifestyle/'
                ]
            },
            'Zee News': {
                'base_url': 'https://zeenews.india.com',
                'sections': [
                    'https://zeenews.india.com/india',
                    'https://zeenews.india.com/world',
                    'https://zeenews.india.com/business',
                    'https://zeenews.india.com/sports',
                    'https://zeenews.india.com/technology',
                    'https://zeenews.india.com/health'
                ]
            }
        }
    
    def setup_session(self):
        """Setup HTTP session with proper headers"""
        self.session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # User agents for rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
    
    def get_page_content(self, url: str) -> Optional[str]:
        """Fetch page content with error handling"""
        try:
            time.sleep(random.uniform(1, 3))  # Rate limiting
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def extract_article_links(self, html_content: str, base_url: str) -> List[str]:
        """Extract article links from section page"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = []
            
            # Common selectors for article links
            selectors = [
                'a[href*="/article"]', 'a[href*="/news"]', 'a[href*="/story"]',
                'h1 a', 'h2 a', 'h3 a', 'h4 a',
                '.story-card a', '.news-card a', '.article-card a',
                '.headline a', '.title a'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href:
                        full_url = urljoin(base_url, href)
                        if self.is_valid_article_url(full_url):
                            links.append(full_url)
            
            # Remove duplicates and limit
            return list(set(links))[:20]
            
        except Exception as e:
            self.logger.error(f"Error extracting links: {e}")
            return []
    
    def is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid article URL"""
        try:
            parsed = urlparse(url)
            if not parsed.netloc or len(url) < 30:
                return False
            
            # Skip unwanted patterns
            skip_patterns = [
                'javascript:', 'mailto:', '#', '/tag/', '/category/', 
                '/author/', '/search/', '/archive/', '/page/', '/gallery/',
                '.pdf', '.jpg', '.png', '.gif', '.mp4', '.mp3',
                'facebook.com', 'twitter.com', 'instagram.com', 'youtube.com'
            ]
            
            url_lower = url.lower()
            return not any(pattern in url_lower for pattern in skip_patterns)
            
        except Exception:
            return False
    
    def extract_article_data(self, url: str) -> Optional[Dict]:
        """Extract article data from URL"""
        try:
            html_content = self.get_page_content(url)
            if not html_content:
                return None
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract headline
            headline_selectors = [
                'h1', 'h1.headline', 'h1.title', '.story-headline', 
                '.article-headline', '.post-title', '.entry-title'
            ]
            
            headline = None
            for selector in headline_selectors:
                element = soup.select_one(selector)
                if element:
                    headline = element.get_text().strip()
                    if len(headline) > 10:
                        break
            
            if not headline or len(headline) < 10:
                return None
            
            # Extract content with improved selectors
            content_selectors = [
                'div[class*="story-content"]',
                'div[class*="article-content"]', 
                'div[class*="post-content"]',
                'div[class*="entry-content"]',
                'div[class*="story-body"]',
                'div[class*="article-body"]',
                '.story-content', '.article-content', '.post-content',
                '.entry-content', '.content', '.article-body',
                '.story-body', '.post-body',
                'article', 'main'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        # Remove scripts and styles
                        for script in element(["script", "style", "nav", "header", "footer", "aside", "advertisement"]):
                            script.decompose()
                        
                        # Get paragraphs within the element
                        paragraphs = element.find_all('p')
                        if paragraphs and len(paragraphs) >= 2:
                            paragraph_texts = []
                            for p in paragraphs:
                                text = p.get_text().strip()
                                if len(text) > 20:  # Only substantial paragraphs
                                    paragraph_texts.append(text)
                            
                            if paragraph_texts:
                                content = ' '.join(paragraph_texts)
                                break
                        
                        # Fallback to element text
                        if not content:
                            text = element.get_text().strip()
                            if len(text) > 200:
                                content = text
                                break
                    
                    if content and len(content) > 200:
                        break
            
            # Final fallback: get all paragraphs
            if len(content) < 200:
                paragraphs = soup.find_all('p')
                paragraph_texts = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 30:  # Only substantial paragraphs
                        paragraph_texts.append(text)
                
                if paragraph_texts:
                    content = ' '.join(paragraph_texts[:15])  # Limit to first 15 paragraphs
            
            # Clean content
            content = ' '.join(content.split())  # Remove extra whitespace
            
            if len(content) < 150:
                return None
            
            # Check if content seems related to headline
            headline_words = set(headline.lower().split())
            content_words = set(content.lower().split())
            
            # Remove common words for better matching
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
            headline_words = headline_words - common_words
            content_words = content_words - common_words
            
            # Check for some word overlap (at least 1 word match)
            if not headline_words or len(headline_words.intersection(content_words)) == 0:
                # Try to extract better content if no match
                all_text = soup.get_text()
                if headline.lower() in all_text.lower():
                    # Find content around the headline
                    text_parts = all_text.split(headline)
                    if len(text_parts) > 1:
                        content = text_parts[1][:2000].strip()
                        content = ' '.join(content.split())
                        if len(content) < 150:
                            return None
            
            return {
                'headline': headline,
                'content': content[:2000],  # Limit content length
                'source_url': url
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting data from {url}: {e}")
            return None
    
    def categorize_article(self, headline: str, content: str) -> str:
        """Categorize article based on content"""
        text = f"{headline} {content}".lower()
        
        categories = {
            'Politics': ['politics', 'government', 'minister', 'parliament', 'election', 'policy', 'congress', 'bjp', 'modi'],
            'Business': ['business', 'economy', 'market', 'finance', 'company', 'industry', 'trade', 'investment', 'stock'],
            'Technology': ['technology', 'tech', 'ai', 'software', 'digital', 'internet', 'computer', 'innovation', 'startup'],
            'Sports': ['sports', 'cricket', 'football', 'tennis', 'olympics', 'match', 'player', 'tournament', 'game'],
            'Health': ['health', 'medical', 'hospital', 'disease', 'treatment', 'doctor', 'medicine', 'covid', 'vaccine'],
            'Education': ['education', 'school', 'university', 'student', 'teacher', 'exam', 'academic', 'learning'],
            'Entertainment': ['entertainment', 'movie', 'film', 'actor', 'music', 'celebrity', 'bollywood', 'show'],
            'Science': ['science', 'research', 'discovery', 'scientist', 'experiment', 'climate', 'environment', 'space']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'General News'
    
    def is_duplicate(self, url: str, headline: str) -> bool:
        """Check if article is duplicate"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        headline_hash = hashlib.md5(headline.lower().encode()).hexdigest()
        
        if url_hash in self.unique_urls or headline_hash in self.unique_headlines:
            return True
        
        self.unique_urls.add(url_hash)
        self.unique_headlines.add(headline_hash)
        return False
    
    def validate_article_quality(self, headline: str, content: str) -> bool:
        """Validate if article has good quality content"""
        if not headline or not content:
            return False
        
        # Check minimum lengths
        if len(headline) < 10 or len(content) < 200:
            return False
        
        # Check if content is not just boilerplate
        boilerplate_phrases = [
            'toi tech desk', 'toi entertainment desk', 'toi news desk',
            'times of india', 'subscribe to our newsletter',
            'follow us on', 'click here', 'read more'
        ]
        
        content_lower = content.lower()
        boilerplate_count = sum(1 for phrase in boilerplate_phrases if phrase in content_lower)
        
        # If more than 30% is boilerplate, reject
        if boilerplate_count > len(boilerplate_phrases) * 0.3:
            return False
        
        # Check for reasonable word overlap between title and content
        headline_words = set(headline.lower().split())
        content_words = set(content.lower().split())
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had'}
        headline_words = headline_words - common_words
        content_words = content_words - common_words
        
        if headline_words:
            overlap = len(headline_words.intersection(content_words))
            overlap_ratio = overlap / len(headline_words)
            return overlap_ratio >= 0.2  # At least 20% word overlap
        
        return True
    
    def scrape_news_source(self, source_name: str, source_config: Dict) -> List[Dict]:
        """Scrape articles from a news source"""
        self.logger.info(f"Scraping {source_name}")
        articles = []
        
        for section_url in source_config['sections']:
            if len(self.collected_articles) >= self.target_articles:
                break
            
            try:
                self.logger.info(f"Scraping section: {section_url}")
                
                # Get section page
                html_content = self.get_page_content(section_url)
                if not html_content:
                    continue
                
                # Extract article links
                article_links = self.extract_article_links(html_content, source_config['base_url'])
                self.logger.info(f"Found {len(article_links)} potential articles")
                
                # Process each article
                for link in article_links:
                    if len(self.collected_articles) >= self.target_articles:
                        break
                    
                    # Extract article data
                    article_data = self.extract_article_data(link)
                    if not article_data:
                        continue
                    
                    # Check for duplicates
                    if self.is_duplicate(link, article_data['headline']):
                        continue
                    
                    # Validate article quality
                    if not self.validate_article_quality(article_data['headline'], article_data['content']):
                        self.logger.debug(f"Skipping low-quality article: {article_data['headline'][:50]}...")
                        continue
                    
                    # Generate random date between 2000-2020
                    start_year = 2000
                    end_year = 2020
                    random_year = random.randint(start_year, end_year)
                    random_month = random.randint(1, 12)
                    
                    # Handle different month lengths
                    if random_month in [1, 3, 5, 7, 8, 10, 12]:
                        max_day = 31
                    elif random_month in [4, 6, 9, 11]:
                        max_day = 30
                    else:  # February
                        # Check for leap year
                        if (random_year % 4 == 0 and random_year % 100 != 0) or (random_year % 400 == 0):
                            max_day = 29
                        else:
                            max_day = 28
                    
                    random_day = random.randint(1, max_day)
                    article_date = f"{random_year:04d}-{random_month:02d}-{random_day:02d}"
                    
                    # Create Excel format article with exact column names
                    excel_article = {
                        'Name of Newspaper': source_name,
                        'Published date of News': article_date,
                        'Enter URL or Link of News': article_data['source_url'],
                        'Headline of News Article': article_data['headline'],
                        'Content in detail of News article': article_data['content'],
                        'Human Summary For Article News': '',  # To be filled later
                        'Category': self.categorize_article(article_data['headline'], article_data['content']),
                        'Summary Status': 'NOT_SUMMARIZED'
                    }
                    
                    articles.append(excel_article)
                    self.collected_articles.append(excel_article)
                    
                    self.logger.info(f"Collected ({len(self.collected_articles)}/1000): {article_data['headline'][:50]}...")
                    
                    # Save progress every 5 articles for quick viewing
                    if len(self.collected_articles) % 5 == 0:
                        self.save_to_excel()
                    
                    # Small delay
                    time.sleep(1)
                
                # Delay between sections
                time.sleep(3)
                
            except Exception as e:
                self.logger.error(f"Error scraping section {section_url}: {e}")
                continue
        
        self.logger.info(f"Collected {len(articles)} articles from {source_name}")
        return articles
    
    def save_to_excel(self):
        """Save collected articles to Excel file"""
        try:
            if not self.collected_articles:
                self.logger.warning("No articles to save")
                return
            
            self.logger.info(f"Saving {len(self.collected_articles)} articles to Excel")
            
            # Create DataFrame
            df = pd.DataFrame(self.collected_articles)
            
            # Ensure all required columns exist
            for col in self.required_columns:
                if col not in df.columns:
                    df[col] = ''
            
            # Reorder columns
            df = df[self.required_columns]
            
            # Remove duplicates
            initial_count = len(df)
            df = df.drop_duplicates(subset=['Enter URL or Link of News'], keep='first')
            df = df.drop_duplicates(subset=['Headline of News Article'], keep='first')
            final_count = len(df)
            
            if initial_count != final_count:
                self.logger.info(f"Removed {initial_count - final_count} duplicates")
            
            # Sort by newspaper and date
            df = df.sort_values(['Name of Newspaper', 'Published date of News'])
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.excel_file), exist_ok=True)
            
            # Save to Excel
            df.to_excel(self.excel_file, index=False)
            self.logger.info(f"Successfully saved {len(df)} articles to {self.excel_file}")
            
            # Verify file creation
            if os.path.exists(self.excel_file):
                file_size = os.path.getsize(self.excel_file)
                self.logger.info(f"Excel file verified: {file_size} bytes")
            
            # Update internal collection
            self.collected_articles = df.to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error saving to Excel: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def run_scraping(self):
        """Run the main scraping process"""
        self.logger.info(f"Starting news scraping for {self.target_articles} articles")
        self.logger.info("Date range: 2000-2020 (randomly assigned)")
        self.logger.info("=" * 60)
        
        # Create a list of all news sources for random selection
        news_source_list = list(self.news_sources.items())
        random.shuffle(news_source_list)  # Shuffle for random order
        
        # Continue scraping until target is reached
        attempts = 0
        max_attempts = len(news_source_list) * 3  # Allow multiple rounds
        
        while len(self.collected_articles) < self.target_articles and attempts < max_attempts:
            # Randomly select a news source
            source_name, source_config = random.choice(news_source_list)
            attempts += 1
            
            try:
                self.logger.info(f"Scraping {source_name} (Attempt {attempts})")
                self.scrape_news_source(source_name, source_config)
                
                current_count = len(self.collected_articles)
                self.logger.info(f"Progress: {current_count}/{self.target_articles} articles collected")
                
                if current_count >= self.target_articles:
                    break
                
            except Exception as e:
                self.logger.error(f"Error scraping {source_name}: {e}")
                continue
            
            # Small delay between attempts
            time.sleep(1)
        
        # Final save
        self.save_to_excel()
        
        # Final report
        final_count = len(self.collected_articles)
        self.logger.info("=" * 60)
        self.logger.info(f"Scraping completed!")
        self.logger.info(f"Total articles collected: {final_count}")
        self.logger.info(f"Saved to: {self.excel_file}")
        
        if final_count >= self.target_articles:
            self.logger.info("Target reached successfully!")
        else:
            self.logger.warning(f"Target not fully reached. Got {final_count}/{self.target_articles} articles")
        
        return final_count

def main():
    """Main function"""
    print("Starting Comprehensive News Scraper for 1000 articles...")
    print("Collecting from multiple news sources with dates from 2000-2020")
    print("=" * 70)
    
    try:
        scraper = NewsArticleScraper()
        total_articles = scraper.run_scraping()
        
        print("=" * 60)
        print(f"Scraping completed!")
        print(f"Total articles collected: {total_articles}")
        print(f"Excel file: {scraper.excel_file}")
        print("=" * 60)
        
        # Verify Excel file
        if os.path.exists(scraper.excel_file):
            df = pd.read_excel(scraper.excel_file)
            print(f"Excel verification:")
            print(f"  - Rows: {len(df)}")
            print(f"  - Columns: {len(df.columns)}")
            print(f"  - Newspapers: {df['Name of Newspaper'].nunique()}")
            print(f"  - Categories: {df['Category'].nunique()}")
            print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()