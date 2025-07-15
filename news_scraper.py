#!/usr/bin/env python3
"""
Agentic News Scraper for Indian English News Articles
Collects 1000-1100 articles from 2010-2020 using Google News and original sources
"""

import os
import sys
import time
import random
import re
import traceback
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import cohere
from config import (
    START_DATE, END_DATE, MAX_ARTICLES, MIN_ARTICLES, 
    EXCEL_FILENAME, ERROR_LOG_FILENAME, STUDENT_NAME, 
    NEWSPAPER_SOURCES, TOPICS, SCRAPING_CONFIG, CHROME_OPTIONS
)

# Configuration now imported from config.py

class NewsScraperAgent:
    def __init__(self, cohere_api_key):
        """Initialize the News Scraper Agent"""
        self.cohere_client = cohere.Client(cohere_api_key)
        self.driver = None
        self.collected_articles = 0
        self.total_errors = 0
        self.llm_errors = 0
        self.error_log = {}
        self.collected_urls = set()  # Track URLs to avoid duplicates
        self.excel_file = EXCEL_FILENAME
        
        # Initialize Excel file
        self.initialize_excel()
        
        print("🚀 News Scraper Agent initialized successfully!")
        print(f"Target: {MIN_ARTICLES}-{MAX_ARTICLES} articles from {START_DATE.year}-{END_DATE.year}")
        
    def initialize_excel(self):
        """Initialize Excel file with proper headers"""
        headers = [
            "Name",
            "Newspaper", 
            "Published Date",
            "Article URL",
            "Headline",
            "Full Content",
            "Human Summary",
            "News Category",
            "Front Page News"
        ]
        
        df = pd.DataFrame(columns=headers)
        df.to_excel(self.excel_file, index=False)
        print(f"📊 Excel file '{self.excel_file}' initialized")
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimal configuration"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup WebDriver: {e}")
            return False
            
    def generate_date_range(self):
        """Generate and shuffle date range for diverse sampling"""
        dates = []
        current_date = START_DATE
        
        while current_date <= END_DATE:
            dates.append(current_date)
            current_date += timedelta(days=1)
            
        random.shuffle(dates)
        print(f"📅 Generated {len(dates)} dates for scraping")
        return dates
        
    def search_google_news_and_get_article_url(self, target_date, newspaper_name, newspaper_domain):
        """Search Google News for articles from specific newspaper and date"""
        try:
            # Format date for Google News search
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Construct Google News search URL
            search_query = f'site:{newspaper_domain} after:{date_str} before:{date_str}'
            encoded_query = quote_plus(search_query)
            google_news_url = f"https://news.google.com/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN%3Aen"
            
            print(f"🔍 Searching Google News for {newspaper_name} on {date_str}")
            
            self.driver.get(google_news_url)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
            
            time.sleep(random.uniform(2, 4))  # Random delay to avoid detection
            
            # Find article links
            article_links = self.driver.find_elements(By.CSS_SELECTOR, "article h3 a")
            
            for link in article_links:
                try:
                    href = link.get_attribute("href")
                    if href and newspaper_domain in href:
                        # Clean the URL (remove Google News redirect)
                        if "google.com" in href:
                            # Extract actual URL from Google News redirect
                            continue
                        return href
                        
                except Exception as e:
                    continue
                    
            # If no direct links found, try alternative approach
            google_links = self.driver.find_elements(By.CSS_SELECTOR, "article a[href*='google.com/url']")
            
            for link in google_links[:5]:  # Check first 5 links
                try:
                    link.click()
                    time.sleep(2)
                    
                    # Check if redirected to target newspaper
                    current_url = self.driver.current_url
                    if newspaper_domain in current_url:
                        return current_url
                        
                    self.driver.back()
                    time.sleep(1)
                    
                except Exception as e:
                    continue
                    
            return None
            
        except Exception as e:
            print(f"❌ Google News search failed: {e}")
            return None
            
    def extract_article_content(self, article_url, newspaper_name, newspaper_domain):
        """Extract article content from the newspaper website"""
        try:
            print(f"📰 Extracting content from: {article_url}")
            
            self.driver.get(article_url)
            
            # Verify we're on the correct domain
            if newspaper_domain not in self.driver.current_url:
                print(f"❌ Unexpected redirect. Expected: {newspaper_domain}, Got: {self.driver.current_url}")
                return None
                
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(random.uniform(2, 4))
            
            # Extract headline using multiple selectors
            headline = self.extract_headline()
            if not headline:
                print("❌ Could not extract headline")
                return None
                
            # Extract published date
            published_date = self.extract_published_date()
            
            # Extract full content
            full_content = self.extract_full_content()
            if not full_content or len(full_content) < 100:
                print("❌ Article content too short or not found")
                return None
                
            article_data = {
                "Name": "Tejas Subhash Bagal",
                "Newspaper": newspaper_name,
                "Published Date": published_date,
                "Article URL": article_url,
                "Headline": headline,
                "Full Content": full_content,
                "Human Summary": "",
                "News Category": "",
                "Front Page News": "Attempted to Infer"
            }
            
            print(f"✅ Article extracted successfully: {headline[:50]}...")
            return article_data
            
        except Exception as e:
            print(f"❌ Article extraction failed: {e}")
            return None
            
    def extract_headline(self):
        """Extract headline using multiple selectors"""
        selectors = [
            "h1",
            "h1[class*='headline']",
            "h1[class*='title']",
            "h1[itemprop='headline']",
            ".headline",
            ".title",
            ".story-headline",
            ".article-title"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                headline = element.text.strip()
                if headline:
                    return headline
            except:
                continue
                
        return None
        
    def extract_published_date(self):
        """Extract published date with flexible parsing"""
        selectors = [
            "time[datetime]",
            "[itemprop='datePublished']",
            ".published-date",
            ".date",
            ".timestamp",
            ".publish-date"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                date_text = element.get_attribute("datetime") or element.text.strip()
                
                # Try to parse the date
                parsed_date = self.format_date_flexible(date_text)
                if parsed_date:
                    return parsed_date
                    
            except:
                continue
                
        return "Date not found"
        
    def extract_full_content(self):
        """Extract article body content"""
        selectors = [
            "[itemprop='articleBody']",
            ".article-content",
            ".story-content",
            ".content",
            ".article-body",
            ".post-content",
            ".entry-content"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    content = ""
                    for element in elements:
                        # Extract text from paragraphs
                        paragraphs = element.find_elements(By.TAG_NAME, "p")
                        for p in paragraphs:
                            content += p.text.strip() + "\n\n"
                    
                    if content.strip():
                        return content.strip()
                        
            except:
                continue
                
        # Fallback: try to extract from all paragraphs
        try:
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
            content = ""
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 20:  # Filter out short paragraphs
                    content += text + "\n\n"
                    
            return content.strip()
            
        except:
            return None
            
    def format_date_flexible(self, date_string):
        """Parse date string with multiple formats"""
        if not date_string:
            return None
            
        # Common date formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%B %d, %Y",
            "%d %B %Y",
            "%Y-%m-%dT%H:%M:%S%z"
        ]
        
        # Clean the date string
        date_string = re.sub(r'[^\w\s:/-]', '', date_string)
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_string, fmt)
                return parsed.strftime("%Y-%m-%d")
            except:
                continue
                
        return None
        
    def generate_summary_and_topic(self, article_data):
        """Generate summary and classify topic using Cohere LLM"""
        try:
            full_content = article_data["Full Content"]
            
            # Generate summary
            summary_prompt = f"""Please provide a concise summary of the following news article in 50-200 words:

Article: {full_content[:2000]}...

Summary:"""

            summary_response = self.cohere_client.generate(
                model='command-xlarge-nightly',
                prompt=summary_prompt,
                max_tokens=150,
                temperature=0.3
            )
            
            summary = summary_response.generations[0].text.strip()
            
            # Classify topic
            topic_prompt = f"""Classify the following news article into one of these categories: {', '.join(TOPICS)}

Article: {full_content[:1000]}...

Category:"""

            topic_response = self.cohere_client.generate(
                model='command-xlarge-nightly',
                prompt=topic_prompt,
                max_tokens=20,
                temperature=0.1
            )
            
            news_category = topic_response.generations[0].text.strip()
            
            # Validate category
            if news_category not in TOPICS:
                news_category = "National News"  # Default category
                
            article_data["Human Summary"] = summary
            article_data["News Category"] = news_category
            
            print(f"✅ LLM processing completed. Category: {news_category}")
            return article_data
            
        except Exception as e:
            print(f"❌ LLM processing failed: {e}")
            self.llm_errors += 1
            
            # Provide fallback values
            article_data["Human Summary"] = "Summary generation failed"
            article_data["News Category"] = "National News"
            
            return article_data
            
    def write_to_excel(self, article_data):
        """Write article data to Excel file"""
        try:
            # Check for duplicate URLs
            if article_data["Article URL"] in self.collected_urls:
                print(f"⚠️ Duplicate URL detected, skipping...")
                return False
                
            # Read existing data
            try:
                df = pd.read_excel(self.excel_file)
            except:
                df = pd.DataFrame()
                
            # Add new row
            new_row = pd.DataFrame([article_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save to Excel
            df.to_excel(self.excel_file, index=False)
            
            # Add to collected URLs
            self.collected_urls.add(article_data["Article URL"])
            self.collected_articles += 1
            
            print(f"✅ Article saved to Excel. Total collected: {self.collected_articles}")
            return True
            
        except Exception as e:
            print(f"❌ Excel write failed: {e}")
            return False
            
    def handle_driver_error(self):
        """Handle WebDriver errors and recreate driver"""
        try:
            if self.driver:
                self.driver.quit()
                
            print("🔄 Recreating WebDriver...")
            time.sleep(random.uniform(5, 10))
            
            if self.setup_driver():
                print("✅ WebDriver recreated successfully")
                return True
            else:
                print("❌ Failed to recreate WebDriver")
                return False
                
        except Exception as e:
            print(f"❌ Driver recreation failed: {e}")
            return False
            
    def run_scraper(self):
        """Main scraping loop"""
        print("\n🚀 Starting news scraping process...")
        
        if not self.setup_driver():
            print("❌ Failed to initialize WebDriver. Exiting.")
            return
            
        dates = self.generate_date_range()
        
        for i, current_date in enumerate(dates):
            if self.collected_articles >= MAX_ARTICLES:
                print(f"✅ Target reached: {self.collected_articles} articles collected")
                break
                
            print(f"\n📅 Processing date {i+1}/{len(dates)}: {current_date.strftime('%Y-%m-%d')}")
            
            # Randomly select newspaper
            newspaper_name = random.choice(list(NEWSPAPER_SOURCES.keys()))
            newspaper_domain = NEWSPAPER_SOURCES[newspaper_name]
            
            try:
                # Search Google News
                article_url = self.search_google_news_and_get_article_url(
                    current_date, newspaper_name, newspaper_domain
                )
                
                if not article_url:
                    print(f"⚠️ No articles found for {newspaper_name} on {current_date.strftime('%Y-%m-%d')}")
                    continue
                    
                # Extract article content
                article_data = self.extract_article_content(
                    article_url, newspaper_name, newspaper_domain
                )
                
                if not article_data:
                    continue
                    
                # Generate summary and classify topic
                article_data = self.generate_summary_and_topic(article_data)
                
                # Write to Excel
                if self.write_to_excel(article_data):
                    print(f"✅ Article {self.collected_articles} successfully processed")
                    
                # Random delay between requests
                time.sleep(random.uniform(3, 7))
                
            except WebDriverException as e:
                print(f"❌ WebDriver error: {e}")
                self.total_errors += 1
                
                if not self.handle_driver_error():
                    print("❌ Fatal error: Cannot recover WebDriver. Exiting.")
                    break
                    
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                self.total_errors += 1
                time.sleep(random.uniform(2, 5))
                
        # Cleanup
        if self.driver:
            self.driver.quit()
            
        self.generate_final_report()
        
    def generate_final_report(self):
        """Generate final report and save error log"""
        print("\n" + "="*50)
        print("📊 FINAL REPORT")
        print("="*50)
        print(f"✅ Articles collected: {self.collected_articles}")
        print(f"❌ Total errors: {self.total_errors}")
        print(f"🤖 LLM errors: {self.llm_errors}")
        print(f"📁 Excel file: {self.excel_file}")
        
        # Save error log
        error_log_file = "google_news_scraper_error_log.txt"
        with open(error_log_file, 'w') as f:
            f.write(f"News Scraper Error Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Articles Collected: {self.collected_articles}\n")
            f.write(f"Total Errors: {self.total_errors}\n")
            f.write(f"LLM Errors: {self.llm_errors}\n\n")
            
            if self.error_log:
                f.write("Detailed Error Log:\n")
                for error_type, count in self.error_log.items():
                    f.write(f"{error_type}: {count}\n")
                    
        print(f"📄 Error log saved: {error_log_file}")
        
        if self.collected_articles >= MIN_ARTICLES:
            print("🎉 SUCCESS: Minimum target achieved!")
        else:
            print("⚠️ WARNING: Minimum target not reached")

def main():
    """Main function to run the scraper"""
    print("="*60)
    print("🗞️  AGENTIC NEWS SCRAPER FOR INDIAN ENGLISH ARTICLES")
    print("="*60)
    
    # Get Cohere API key
    cohere_api_key = input("Enter your Cohere API key: ").strip()
    
    if not cohere_api_key:
        print("❌ Cohere API key is required. Exiting.")
        return
        
    # Initialize and run scraper
    scraper = NewsScraperAgent(cohere_api_key)
    scraper.run_scraper()

if __name__ == "__main__":
    main()