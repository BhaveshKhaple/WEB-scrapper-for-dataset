#!/usr/bin/env python3
"""
Simple News Scraper using requests and BeautifulSoup
Works without Chrome driver issues
"""

import os
import sys
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import google.generativeai as genai
from dotenv import load_dotenv

# Import configuration
from config import *

class SimpleNewsScraperAgent:
    def __init__(self):
        """Initialize the Simple News Scraper Agent"""
        # Load .env file
        load_dotenv()
        
        # Get API key from .env file
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not gemini_api_key:
            raise ValueError("Gemini API key is required. Please set GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.collected_articles = 0
        self.total_errors = 0
        self.llm_errors = 0
        self.collected_urls = set()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize Excel file
        self.initialize_excel()
        
        # Setup requests session
        self.setup_session()
        
        self.logger.info("🚀 Simple News Scraper Agent initialized successfully!")
        self.logger.info(f"Target: {MIN_ARTICLES}-{MAX_ARTICLES} articles")
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_excel(self):
        """Initialize Excel file with proper headers"""
        headers = [
            "Name of Newspaper",
            "Published date of News", 
            "Enter URL or Link of News",
            "Headline of News Article",
            "Content in detail of News article",
            "Human Summary For Article",
            "News Category"
        ]
        
        df = pd.DataFrame(columns=headers)
        df.to_excel(EXCEL_FILENAME, index=False)
        self.logger.info(f"Excel file '{EXCEL_FILENAME}' initialized")
        
    def setup_session(self):
        """Setup requests session with headers"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def get_rss_articles(self, newspaper_name, domain):
        """Get articles from RSS feeds"""
        rss_urls = [
            f"https://{domain}/rss",
            f"https://{domain}/feed",
            f"https://{domain}/rss.xml",
            f"https://{domain}/feed.xml"
        ]
        
        for rss_url in rss_urls:
            try:
                response = self.session.get(rss_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')[:5]  # Get first 5 articles
                    
                    articles = []
                    for item in items:
                        try:
                            title = item.find('title').text.strip()
                            link = item.find('link').text.strip()
                            pub_date = item.find('pubDate')
                            pub_date = pub_date.text.strip() if pub_date else "Date not found"
                            
                            if link not in self.collected_urls:
                                articles.append({
                                    'title': title,
                                    'url': link,
                                    'pub_date': pub_date
                                })
                        except Exception as e:
                            continue
                    
                    if articles:
                        self.logger.info(f"Found {len(articles)} articles from {newspaper_name} RSS")
                        return articles
                        
            except Exception as e:
                continue
                
        return []
        
    def scrape_article_content(self, url):
        """Scrape article content from URL"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
                
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract headline
            headline = None
            headline_selectors = ['h1', 'h1.headline', 'h1.title', '.headline', '.title']
            for selector in headline_selectors:
                element = soup.select_one(selector)
                if element:
                    headline = element.get_text().strip()
                    break
            
            if not headline:
                return None
                
            # Extract content
            content = ""
            content_selectors = [
                '.article-content', '.story-content', '.content', 
                '.article-body', '.post-content', '.entry-content'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        content += element.get_text().strip() + " "
                    break
            
            # If no content found, try paragraphs
            if not content:
                paragraphs = soup.find_all('p')
                content = " ".join([p.get_text().strip() for p in paragraphs[:10]])
            
            if len(content) < 100:
                return None
                
            return {
                'headline': headline,
                'content': content.strip()
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
            
    def generate_summary_and_topic(self, article_data):
        """Generate summary and classify topic using Gemini LLM"""
        try:
            full_content = article_data["Content in detail of News article"]
            
            # Generate human-style summary using AI assistance (50-200 words)
            summary_prompt = f"""Write a clear, human-style summary of this Indian news article in exactly 50-200 words. Explain the news in your own words as if you're explaining it to someone. Make it sound natural and conversational, not robotic:

Article: {full_content[:2000]}...

Human Summary:"""

            summary_response = self.gemini_model.generate_content(summary_prompt)
            human_summary = summary_response.text.strip()
            
            # Classify topic
            topic_prompt = f"""Classify this Indian news article into exactly one of these categories: {', '.join(TOPICS)}

Article: {full_content[:1000]}...

Return only the category name:"""

            topic_response = self.gemini_model.generate_content(topic_prompt)
            news_category = topic_response.text.strip()
            
            # Validate category
            if news_category not in TOPICS:
                news_category = "National News"
                
            article_data["Human Summary For Article"] = human_summary
            article_data["News Category"] = news_category
            
            self.logger.info(f"LLM processing completed. Category: {news_category}")
            return article_data
            
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            self.llm_errors += 1
            
            article_data["Human Summary For Article"] = "Summary generation failed"
            article_data["News Category"] = "National News"
            
            return article_data
            
    def write_to_excel(self, article_data):
        """Write article data to Excel file"""
        try:
            if article_data["Enter URL or Link of News"] in self.collected_urls:
                self.logger.warning("Duplicate URL detected, skipping...")
                return False
                
            # Try multiple times in case file is temporarily locked
            for attempt in range(3):
                try:
                    df = pd.read_excel(EXCEL_FILENAME)
                    break
                except FileNotFoundError:
                    df = pd.DataFrame()
                    break
                except Exception as e:
                    if attempt == 2:
                        self.logger.error(f"Cannot read Excel file after 3 attempts: {e}")
                        return False
                    time.sleep(1)
                    
            new_row = pd.DataFrame([article_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Try to write with retry mechanism
            for attempt in range(3):
                try:
                    df.to_excel(EXCEL_FILENAME, index=False)
                    break
                except Exception as e:
                    if attempt == 2:
                        self.logger.error(f"Excel write failed after 3 attempts: {e}")
                        self.logger.warning("Please close Excel file if it's open and try again")
                        return False
                    self.logger.warning(f"Excel write attempt {attempt + 1} failed, retrying...")
                    time.sleep(2)
            
            self.collected_urls.add(article_data["Enter URL or Link of News"])
            self.collected_articles += 1
            
            self.logger.info(f"Article saved. Total: {self.collected_articles}")
            return True
            
        except Exception as e:
            self.logger.error(f"Excel write failed: {e}")
            return False
            
    def run_scraper(self):
        """Run the scraper process"""
        self.logger.info("Starting simple news scraping process...")
        
        for newspaper_name, domain in NEWSPAPER_SOURCES.items():
            if self.collected_articles >= MAX_ARTICLES:
                break
                
            self.logger.info(f"Processing {newspaper_name}...")
            
            # Get articles from RSS
            articles = self.get_rss_articles(newspaper_name, domain)
            
            for article in articles:
                if self.collected_articles >= MAX_ARTICLES:
                    break
                    
                # Scrape article content
                content_data = self.scrape_article_content(article['url'])
                
                if not content_data:
                    continue
                    
                # Create article data
                article_data = {
                    "Name of Newspaper": newspaper_name,
                    "Published date of News": article['pub_date'],
                    "Enter URL or Link of News": article['url'],
                    "Headline of News Article": content_data['headline'],
                    "Content in detail of News article": content_data['content'],
                    "Human Summary For Article": "",
                    "News Category": ""
                }
                
                # Generate summary and topic
                article_data = self.generate_summary_and_topic(article_data)
                
                # Write to Excel
                if self.write_to_excel(article_data):
                    self.logger.info(f"Successfully processed: {content_data['headline'][:50]}...")
                    
                # Add delay between requests
                time.sleep(random.uniform(2, 5))
                
        self.logger.info(f"Scraping completed. Total articles collected: {self.collected_articles}")
        self.logger.info(f"Excel file: {EXCEL_FILENAME}")

if __name__ == "__main__":
    try:
        scraper = SimpleNewsScraperAgent()
        scraper.run_scraper()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()