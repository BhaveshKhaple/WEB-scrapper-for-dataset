#!/usr/bin/env python3
"""
Windows-compatible News Scraper Runner
Handles Unicode encoding issues and WebDriver setup for Windows
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
from selenium.webdriver.chrome.service import Service
import cohere

# Set console encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

from config import *

class WindowsNewsScraperAgent:
    def __init__(self, cohere_api_key):
        """Initialize the Windows-compatible News Scraper Agent"""
        self.cohere_client = cohere.Client(cohere_api_key)
        self.driver = None
        self.collected_articles = 0
        self.total_errors = 0
        self.llm_errors = 0
        self.consecutive_errors = 0
        self.collected_urls = set()
        
        # Initialize Excel file
        self.initialize_excel()
        
        print("🚀 Windows News Scraper Agent initialized successfully!")
        print(f"📊 Target: {MIN_ARTICLES}-{MAX_ARTICLES} articles from {START_DATE.year}-{END_DATE.year}")
        
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
        df.to_excel(EXCEL_FILENAME, index=False)
        print(f"📊 Excel file '{EXCEL_FILENAME}' initialized")
        
    def setup_driver(self):
        """Setup Chrome WebDriver for Windows"""
        try:
            chrome_options = Options()
            
            # Basic Chrome options for Windows
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")
            
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try to find Chrome executable manually
            possible_chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Users\\{}\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe".format(os.getenv('USERNAME')),
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            ]
            
            chrome_path = None
            for path in possible_chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if chrome_path:
                chrome_options.binary_location = chrome_path
                print(f"✅ Found Chrome at: {chrome_path}")
            
            # Try to create WebDriver
            try:
                # Try without webdriver-manager first
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✅ Chrome WebDriver initialized successfully (direct)")
            except:
                # Try with webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                try:
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    print("✅ Chrome WebDriver initialized successfully (via manager)")
                except Exception as e:
                    print(f"❌ WebDriver manager failed: {e}")
                    return False
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.set_page_load_timeout(SCRAPING_CONFIG["page_load_timeout"])
            self.driver.implicitly_wait(5)
            
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
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Simple search strategy
            search_query = f'site:{newspaper_domain} after:{date_str} before:{date_str}'
            
            print(f"🔍 Searching Google News: {search_query}")
            
            encoded_query = quote_plus(search_query)
            google_news_url = f"https://news.google.com/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN%3Aen"
            
            self.driver.get(google_news_url)
            
            # Wait for results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
            )
            
            time.sleep(random.uniform(SCRAPING_CONFIG["request_delay_min"], SCRAPING_CONFIG["request_delay_max"]))
            
            # Try to find article links
            selectors = [
                "article h3 a",
                "article a[href*='http']",
                "a[href*='{}']".format(newspaper_domain)
            ]
            
            for selector in selectors:
                try:
                    links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for link in links:
                        href = link.get_attribute("href")
                        if href and newspaper_domain in href and "google.com" not in href:
                            print(f"✅ Found article URL: {href}")
                            return href
                            
                except Exception as e:
                    continue
                    
            print(f"⚠️ No articles found for {newspaper_name} on {date_str}")
            return None
            
        except Exception as e:
            print(f"❌ Google News search failed: {e}")
            return None
            
    def extract_article_content(self, article_url, newspaper_name, newspaper_domain):
        """Extract article content from the newspaper website"""
        try:
            print(f"📰 Extracting content from: {article_url}")
            
            self.driver.get(article_url)
            
            # Verify domain
            if newspaper_domain not in self.driver.current_url:
                print(f"❌ Domain mismatch. Expected: {newspaper_domain}, Got: {self.driver.current_url}")
                return None
                
            # Wait for content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(random.uniform(2, 4))
            
            # Extract components
            headline = self.extract_headline()
            if not headline:
                print("❌ Could not extract headline")
                return None
                
            published_date = self.extract_published_date()
            full_content = self.extract_full_content()
            
            if not full_content or len(full_content) < SCRAPING_CONFIG["min_article_length"]:
                print("❌ Article content too short or not found")
                return None
                
            # Simple front page assessment
            front_page_indicator = self.assess_front_page_likelihood(headline, full_content)
            
            article_data = {
                "Name": STUDENT_NAME,
                "Newspaper": newspaper_name,
                "Published Date": published_date,
                "Article URL": article_url,
                "Headline": headline,
                "Full Content": full_content,
                "Human Summary": "",
                "News Category": "",
                "Front Page News": front_page_indicator
            }
            
            print(f"✅ Article extracted: {headline[:50]}...")
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
                if headline and len(headline) > 10:
                    return headline
            except:
                continue
                
        return None
        
    def extract_published_date(self):
        """Extract published date"""
        selectors = [
            "time[datetime]",
            "[itemprop='datePublished']",
            "[data-timestamp]",
            ".published-date",
            ".date",
            ".timestamp"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # Try datetime attribute
                date_text = element.get_attribute("datetime")
                if date_text:
                    return self.format_date_flexible(date_text)
                    
                # Try element text
                date_text = element.text.strip()
                if date_text:
                    return self.format_date_flexible(date_text)
                        
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
            ".story-body",
            ".article-text"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    content = ""
                    for element in elements:
                        paragraphs = element.find_elements(By.TAG_NAME, "p")
                        for p in paragraphs:
                            text = p.text.strip()
                            if text:
                                content += text + "\n\n"
                    
                    if content.strip():
                        return content.strip()
                        
            except:
                continue
                
        # Fallback: extract from all paragraphs
        try:
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
            content = ""
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 20:
                    content += text + "\n\n"
                    
            return content.strip()
            
        except:
            return None
            
    def format_date_flexible(self, date_string):
        """Parse date string with multiple formats"""
        if not date_string:
            return None
            
        # Clean the date string
        date_string = re.sub(r'[^\w\s:/-]', '', date_string)
        
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%d/%m/%Y",
            "%m/%d/%Y", 
            "%d-%m-%Y",
            "%B %d, %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%d %b %Y"
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_string, fmt)
                return parsed.strftime("%Y-%m-%d")
            except:
                continue
                
        return None
        
    def assess_front_page_likelihood(self, headline, content):
        """Assess if article is likely to be front page news"""
        front_page_keywords = [
            "breaking", "urgent", "exclusive", "major", "historic", "crisis",
            "election", "budget", "parliament", "supreme court", "prime minister",
            "president", "cabinet", "policy", "announcement", "scandal"
        ]
        
        headline_lower = headline.lower()
        content_lower = content.lower()
        
        keyword_count = sum(1 for keyword in front_page_keywords 
                          if keyword in headline_lower or keyword in content_lower)
        
        if keyword_count >= 2:
            return "High likelihood"
        elif keyword_count == 1:
            return "Moderate likelihood"
        else:
            return "Low likelihood"
            
    def generate_summary_and_topic(self, article_data):
        """Generate summary and classify topic using Cohere LLM"""
        try:
            full_content = article_data["Full Content"]
            
            # Generate summary
            summary_prompt = f"""Please provide a concise summary of the following Indian news article in exactly 50-200 words:

Article: {full_content[:2000]}...

Summary:"""

            summary_response = self.cohere_client.chat(
                model=COHERE_CONFIG["model"],
                message=summary_prompt,
                max_tokens=150,
                temperature=0.3
            )
            
            summary = summary_response.text.strip()
            
            # Classify topic
            topic_prompt = f"""Classify this Indian news article into exactly one of these categories: {', '.join(TOPICS)}

Article: {full_content[:1000]}...

Return only the category name:"""

            topic_response = self.cohere_client.chat(
                model=COHERE_CONFIG["model"],
                message=topic_prompt,
                max_tokens=20,
                temperature=0.1
            )
            
            news_category = topic_response.text.strip()
            
            # Validate category
            if news_category not in TOPICS:
                news_category = "National News"
                
            article_data["Human Summary"] = summary
            article_data["News Category"] = news_category
            
            print(f"✅ LLM processing completed. Category: {news_category}")
            return article_data
            
        except Exception as e:
            print(f"❌ LLM processing failed: {e}")
            self.llm_errors += 1
            
            article_data["Human Summary"] = "Summary generation failed"
            article_data["News Category"] = "National News"
            
            return article_data
            
    def write_to_excel(self, article_data):
        """Write article data to Excel file"""
        try:
            if article_data["Article URL"] in self.collected_urls:
                print("⚠️ Duplicate URL detected, skipping...")
                return False
                
            try:
                df = pd.read_excel(EXCEL_FILENAME)
            except:
                df = pd.DataFrame()
                
            new_row = pd.DataFrame([article_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            df.to_excel(EXCEL_FILENAME, index=False)
            
            self.collected_urls.add(article_data["Article URL"])
            self.collected_articles += 1
            
            print(f"✅ Article saved. Total: {self.collected_articles}")
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
            time.sleep(10)
            
            if self.setup_driver():
                print("✅ WebDriver recreated successfully")
                self.consecutive_errors = 0
                return True
            else:
                print("❌ Failed to recreate WebDriver")
                return False
                
        except Exception as e:
            print(f"❌ Driver recreation failed: {e}")
            return False
            
    def run_scraper(self):
        """Main scraping loop"""
        print("\n🚀 Starting Windows news scraping process...")
        
        if not self.setup_driver():
            print("❌ Failed to initialize WebDriver. Exiting.")
            return
            
        dates = self.generate_date_range()
        
        for i, current_date in enumerate(dates):
            if self.collected_articles >= MAX_ARTICLES:
                print(f"✅ Target reached: {self.collected_articles} articles")
                break
                
            if self.consecutive_errors >= 5:
                print("❌ Too many consecutive errors. Exiting.")
                break
                
            print(f"\n📅 Processing {i+1}/{len(dates)}: {current_date.strftime('%Y-%m-%d')}")
            
            # Randomly select newspaper
            newspaper_name = random.choice(list(NEWSPAPER_SOURCES.keys()))
            newspaper_domain = NEWSPAPER_SOURCES[newspaper_name]
            
            try:
                # Search Google News
                article_url = self.search_google_news_and_get_article_url(
                    current_date, newspaper_name, newspaper_domain
                )
                
                if not article_url:
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
                    print(f"✅ Article {self.collected_articles} processed successfully")
                    self.consecutive_errors = 0
                    
                # Random delay
                time.sleep(random.uniform(3, 7))
                
            except WebDriverException as e:
                print(f"❌ WebDriver error: {e}")
                self.total_errors += 1
                self.consecutive_errors += 1
                
                if not self.handle_driver_error():
                    print("❌ Fatal error: Cannot recover WebDriver")
                    break
                    
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                self.total_errors += 1
                self.consecutive_errors += 1
                time.sleep(5)
                
        # Cleanup
        if self.driver:
            self.driver.quit()
            
        self.generate_final_report()
        
    def generate_final_report(self):
        """Generate final report"""
        print("\n" + "="*50)
        print("📊 FINAL REPORT")
        print("="*50)
        print(f"✅ Articles collected: {self.collected_articles}")
        print(f"❌ Total errors: {self.total_errors}")
        print(f"🤖 LLM errors: {self.llm_errors}")
        print(f"📁 Excel file: {EXCEL_FILENAME}")
        
        if self.collected_articles >= MIN_ARTICLES:
            print("🎉 SUCCESS: Target achieved!")
        else:
            print("⚠️ WARNING: Target not reached")

def main():
    """Main function"""
    print("="*60)
    print("🗞️  WINDOWS NEWS SCRAPER")
    print("="*60)
    
    cohere_api_key = input("Enter your Cohere API key: ").strip()
    
    if not cohere_api_key:
        print("❌ Cohere API key required")
        return
        
    scraper = WindowsNewsScraperAgent(cohere_api_key)
    scraper.run_scraper()

if __name__ == "__main__":
    main()