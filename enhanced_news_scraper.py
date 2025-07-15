#!/usr/bin/env python3
"""
Enhanced Agentic News Scraper for Indian English News Articles
Uses configuration file for easy customization
"""

import os
import sys
import time
import random
import re
import traceback
import logging
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
import google.generativeai as genai
from dotenv import load_dotenv

# Import configuration
from config import *

class EnhancedNewsScraperAgent:
    def __init__(self, gemini_api_key=None):
        """Initialize the Enhanced News Scraper Agent"""
        # Load .env file
        load_dotenv()
        
        # Get API key from parameter or .env file
        if gemini_api_key is None:
            gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not gemini_api_key:
            raise ValueError("Gemini API key is required. Please provide it as parameter or set GEMINI_API_KEY in .env file")
        
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.driver = None
        self.collected_articles = 0
        self.total_errors = 0
        self.llm_errors = 0
        self.consecutive_errors = 0
        self.error_log = {}
        self.collected_urls = set()
        
        # Setup logging
        self.setup_logging()
        
        # Initialize Excel file
        self.initialize_excel()
        
        self.logger.info("🚀 Enhanced News Scraper Agent initialized successfully!")
        self.logger.info(f"Target: {MIN_ARTICLES}-{MAX_ARTICLES} articles from {START_DATE.year}-{END_DATE.year}")
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG["log_level"]),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOGGING_CONFIG["log_filename"]) if LOGGING_CONFIG["file_output"] else logging.NullHandler(),
                logging.StreamHandler() if LOGGING_CONFIG["console_output"] else logging.NullHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_excel(self):
        """Initialize Excel file with proper headers matching contents news.md structure"""
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
        self.logger.info(f"📊 Excel file '{EXCEL_FILENAME}' initialized")
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimal configuration"""
        try:
            chrome_options = Options()
            
            # Add all chrome options from config
            for option in CHROME_OPTIONS:
                chrome_options.add_argument(option)
                
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            try:
                # Try to use system Chrome driver first
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e1:
                try:
                    # If that fails, try with ChromeDriverManager
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                except Exception as e2:
                    # If both fail, try with specific Chrome paths
                    chrome_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                    ]
                    for chrome_path in chrome_paths:
                        if os.path.exists(chrome_path):
                            chrome_options.binary_location = chrome_path
                            self.driver = webdriver.Chrome(options=chrome_options)
                            break
                    else:
                        raise Exception(f"Chrome setup failed: {e1}, {e2}")
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            self.driver.set_page_load_timeout(SCRAPING_CONFIG["page_load_timeout"])
            self.driver.implicitly_wait(5)
            
            self.logger.info("✅ Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup WebDriver: {e}")
            return False
            
    def generate_date_range(self):
        """Generate and shuffle date range for diverse sampling"""
        dates = []
        current_date = START_DATE
        
        while current_date <= END_DATE:
            dates.append(current_date)
            current_date += timedelta(days=1)
            
        random.shuffle(dates)
        self.logger.info(f"📅 Generated {len(dates)} dates for scraping")
        return dates
        
    def search_google_news_and_get_article_url(self, target_date, newspaper_name, newspaper_domain):
        """Search Google News for articles from specific newspaper and date"""
        try:
            date_str = target_date.strftime("%Y-%m-%d")
            
            # Multiple search strategies
            search_strategies = [
                f'site:{newspaper_domain} after:{date_str} before:{date_str}',
                f'"{newspaper_name}" site:{newspaper_domain} after:{date_str} before:{date_str}',
                f'site:{newspaper_domain} {target_date.strftime("%B %d, %Y")}',
            ]
            
            for strategy in search_strategies:
                self.logger.info(f"🔍 Trying search strategy: {strategy}")
                
                encoded_query = quote_plus(strategy)
                google_news_url = f"https://news.google.com/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN%3Aen"
                
                self.driver.get(google_news_url)
                
                # Wait for results
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
                )
                
                time.sleep(random.uniform(SCRAPING_CONFIG["request_delay_min"], SCRAPING_CONFIG["request_delay_max"]))
                
                # Try multiple selectors for article links
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
                                self.logger.info(f"✅ Found article URL: {href}")
                                return href
                                
                    except Exception as e:
                        continue
                        
                # Try clicking on Google News links
                try:
                    google_links = self.driver.find_elements(By.CSS_SELECTOR, "article a")
                    
                    for link in google_links[:3]:  # Try first 3 links
                        try:
                            original_url = self.driver.current_url
                            link.click()
                            
                            # Wait for potential redirect
                            WebDriverWait(self.driver, 5).until(
                                lambda d: d.current_url != original_url
                            )
                            
                            current_url = self.driver.current_url
                            if newspaper_domain in current_url:
                                self.logger.info(f"✅ Found article via click: {current_url}")
                                return current_url
                                
                            self.driver.back()
                            time.sleep(2)
                            
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
                    
            self.logger.warning(f"⚠️ No articles found for {newspaper_name} on {date_str}")
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Google News search failed: {e}")
            return None
            
    def extract_article_content(self, article_url, newspaper_name, newspaper_domain):
        """Extract article content from the newspaper website"""
        try:
            self.logger.info(f"📰 Extracting content from: {article_url}")
            
            self.driver.get(article_url)
            
            # Verify domain
            if newspaper_domain not in self.driver.current_url:
                self.logger.warning(f"❌ Domain mismatch. Expected: {newspaper_domain}, Got: {self.driver.current_url}")
                return None
                
            # Wait for content
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(random.uniform(2, 4))
            
            # Extract components
            headline = self.extract_headline()
            if not headline:
                self.logger.warning("❌ Could not extract headline")
                return None
                
            published_date = self.extract_published_date()
            full_content = self.extract_full_content()
            
            if not full_content or len(full_content) < SCRAPING_CONFIG["min_article_length"]:
                self.logger.warning("❌ Article content too short or not found")
                return None
                
            # Check if it's a potential front page article
            front_page_indicator = self.assess_front_page_likelihood(headline, full_content)
            
            article_data = {
                "Name of Newspaper": newspaper_name,
                "Published date of News": published_date,
                "Enter URL or Link of News": article_url,
                "Headline of News Article": headline,
                "Content in detail of News article": full_content,  # Complete article (very clear data)
                "Human Summary For Article": "",  # AI-assisted personal summary (50-200 words)
                "News Category": ""
            }
            
            self.logger.info(f"✅ Article extracted: {headline[:50]}...")
            return article_data
            
        except Exception as e:
            self.logger.error(f"❌ Article extraction failed: {e}")
            return None
            
    def extract_headline(self):
        """Extract headline using multiple selectors"""
        selectors = [
            "h1",
            "h1[class*='headline']",
            "h1[class*='title']",
            "h1[itemprop='headline']",
            "[data-vr-headline]",
            ".headline",
            ".title",
            ".story-headline",
            ".article-title",
            ".entry-title",
            ".post-title"
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
        """Extract published date with flexible parsing"""
        selectors = [
            "time[datetime]",
            "[itemprop='datePublished']",
            "[data-timestamp]",
            ".published-date",
            ".date",
            ".timestamp",
            ".publish-date",
            ".article-date",
            ".post-date"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # Try multiple attributes
                for attr in ["datetime", "data-timestamp", "title", "content"]:
                    date_text = element.get_attribute(attr)
                    if date_text:
                        parsed_date = self.format_date_flexible(date_text)
                        if parsed_date:
                            return parsed_date
                            
                # Try element text
                date_text = element.text.strip()
                if date_text:
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
            ".entry-content",
            ".story-body",
            ".article-text",
            ".news-content"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    content = ""
                    for element in elements:
                        # Get text from paragraphs
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
            "%Y-%m-%dT%H:%M:%S%z",
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
        # Keywords that often indicate front page news
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
        """Generate summary and classify topic using Gemini LLM"""
        try:
            full_content = article_data["Content in detail of News article"]
            
            # Generate human-style summary using AI assistance (50-200 words)
            summary_prompt = f"""Write a clear, human-style summary of this Indian news article in exactly {SCRAPING_CONFIG['summary_min_words']}-{SCRAPING_CONFIG['summary_max_words']} words. Explain the news in your own words as if you're explaining it to someone. Make it sound natural and conversational, not robotic:

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
            
            self.logger.info(f"✅ LLM processing completed. Category: {news_category}")
            return article_data
            
        except Exception as e:
            self.logger.error(f"❌ LLM processing failed: {e}")
            self.llm_errors += 1
            
            article_data["Human Summary For Article"] = "Summary generation failed"
            article_data["News Category"] = "National News"
            
            return article_data
            
    def write_to_excel(self, article_data):
        """Write article data to Excel file"""
        try:
            if article_data["Enter URL or Link of News"] in self.collected_urls:
                self.logger.warning("⚠️ Duplicate URL detected, skipping...")
                return False
                
            try:
                df = pd.read_excel(EXCEL_FILENAME)
            except:
                df = pd.DataFrame()
                
            new_row = pd.DataFrame([article_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            df.to_excel(EXCEL_FILENAME, index=False)
            
            self.collected_urls.add(article_data["Enter URL or Link of News"])
            self.collected_articles += 1
            
            self.logger.info(f"✅ Article saved. Total: {self.collected_articles}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Excel write failed: {e}")
            return False
            
    def handle_driver_error(self):
        """Handle WebDriver errors and recreate driver"""
        try:
            if self.driver:
                self.driver.quit()
                
            self.logger.info("🔄 Recreating WebDriver...")
            time.sleep(ERROR_CONFIG["driver_recreation_delay"])
            
            if self.setup_driver():
                self.logger.info("✅ WebDriver recreated successfully")
                self.consecutive_errors = 0
                return True
            else:
                self.logger.error("❌ Failed to recreate WebDriver")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Driver recreation failed: {e}")
            return False
            
    def run_scraper(self):
        """Main scraping loop"""
        self.logger.info("\n🚀 Starting enhanced news scraping process...")
        
        if not self.setup_driver():
            self.logger.error("❌ Failed to initialize WebDriver. Exiting.")
            return
            
        dates = self.generate_date_range()
        
        for i, current_date in enumerate(dates):
            if self.collected_articles >= MAX_ARTICLES:
                self.logger.info(f"✅ Target reached: {self.collected_articles} articles")
                break
                
            if self.consecutive_errors >= ERROR_CONFIG["max_consecutive_errors"]:
                self.logger.error("❌ Too many consecutive errors. Exiting.")
                break
                
            self.logger.info(f"\n📅 Processing {i+1}/{len(dates)}: {current_date.strftime('%Y-%m-%d')}")
            
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
                    self.logger.info(f"✅ Article {self.collected_articles} processed successfully")
                    self.consecutive_errors = 0
                    
                # Random delay
                time.sleep(random.uniform(
                    SCRAPING_CONFIG["request_delay_min"],
                    SCRAPING_CONFIG["request_delay_max"]
                ))
                
            except WebDriverException as e:
                self.logger.error(f"❌ WebDriver error: {e}")
                self.total_errors += 1
                self.consecutive_errors += 1
                
                if not self.handle_driver_error():
                    self.logger.error("❌ Fatal error: Cannot recover WebDriver")
                    break
                    
            except Exception as e:
                self.logger.error(f"❌ Unexpected error: {e}")
                self.total_errors += 1
                self.consecutive_errors += 1
                time.sleep(ERROR_CONFIG["error_recovery_delay"])
                
        # Cleanup
        if self.driver:
            self.driver.quit()
            
        self.generate_final_report()
        
    def generate_final_report(self):
        """Generate final report and save error log"""
        self.logger.info("\n" + "="*50)
        self.logger.info("📊 FINAL REPORT")
        self.logger.info("="*50)
        self.logger.info(f"✅ Articles collected: {self.collected_articles}")
        self.logger.info(f"❌ Total errors: {self.total_errors}")
        self.logger.info(f"🤖 LLM errors: {self.llm_errors}")
        self.logger.info(f"📁 Excel file: {EXCEL_FILENAME}")
        
        # Save detailed error log
        with open(ERROR_LOG_FILENAME, 'w') as f:
            f.write(f"Enhanced News Scraper Error Log\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Articles Collected: {self.collected_articles}\n")
            f.write(f"Total Errors: {self.total_errors}\n")
            f.write(f"LLM Errors: {self.llm_errors}\n\n")
            
            if self.error_log:
                f.write("Detailed Error Log:\n")
                for error_type, count in self.error_log.items():
                    f.write(f"{error_type}: {count}\n")
                    
        self.logger.info(f"📄 Error log saved: {ERROR_LOG_FILENAME}")
        
        if self.collected_articles >= MIN_ARTICLES:
            self.logger.info("🎉 SUCCESS: Target achieved!")
        else:
            self.logger.warning("⚠️ WARNING: Target not reached")

def main():
    """Main function"""
    print("="*60)
    print("🗞️  ENHANCED AGENTIC NEWS SCRAPER")
    print("="*60)
    
    cohere_api_key = input("Enter your Cohere API key: ").strip()
    
    if not cohere_api_key:
        print("❌ Cohere API key required")
        return
        
    scraper = EnhancedNewsScraperAgent(cohere_api_key)
    scraper.run_scraper()

if __name__ == "__main__":
    main()