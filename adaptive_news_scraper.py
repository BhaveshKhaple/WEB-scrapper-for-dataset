#!/usr/bin/env python3
"""
Adaptive News Scraper with Enhanced Robustness
Addresses HTML structure changes, rate limiting, and API monitoring
"""

import os
import sys
import time
import random
import re
import json
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

from config import *

class AdaptiveNewsScraperAgent:
    def __init__(self, cohere_api_key):
        """Initialize the Adaptive News Scraper Agent"""
        self.cohere_client = cohere.Client(cohere_api_key)
        self.driver = None
        self.collected_articles = 0
        self.total_errors = 0
        self.llm_errors = 0
        self.consecutive_errors = 0
        self.error_log = {}
        self.collected_urls = set()
        
        # Adaptive selector tracking
        self.successful_selectors = {
            'headline': {},
            'date': {},
            'content': {}
        }
        
        # Rate limiting tracking
        self.last_request_time = {}
        self.request_count = 0
        
        # LLM API monitoring
        self.llm_api_usage = {
            'total_requests': 0,
            'failed_requests': 0,
            'tokens_used': 0,
            'rate_limit_hits': 0
        }
        
        # Front page assessment weights
        self.front_page_indicators = {
            'headline_keywords': ['breaking', 'urgent', 'exclusive', 'major', 'historic', 'crisis'],
            'political_keywords': ['parliament', 'government', 'minister', 'election', 'policy'],
            'economic_keywords': ['budget', 'economy', 'market', 'rupee', 'gdp'],
            'social_keywords': ['protest', 'violence', 'court', 'verdict', 'scandal']
        }
        
        # Initialize tracking files
        self.initialize_tracking()
        self.initialize_excel()
        
        print("🚀 Adaptive News Scraper initialized with enhanced robustness!")
        
    def initialize_tracking(self):
        """Initialize tracking files for adaptive learning"""
        self.selector_tracking_file = "selector_success_tracking.json"
        self.api_usage_file = "llm_api_usage.json"
        
        # Load existing selector success data
        try:
            with open(self.selector_tracking_file, 'r') as f:
                self.successful_selectors = json.load(f)
        except FileNotFoundError:
            self.save_selector_tracking()
            
        # Load existing API usage data
        try:
            with open(self.api_usage_file, 'r') as f:
                self.llm_api_usage = json.load(f)
        except FileNotFoundError:
            self.save_api_usage()
    
    def save_selector_tracking(self):
        """Save successful selector patterns for adaptive learning"""
        try:
            with open(self.selector_tracking_file, 'w') as f:
                json.dump(self.successful_selectors, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save selector tracking: {e}")
    
    def save_api_usage(self):
        """Save LLM API usage statistics"""
        try:
            with open(self.api_usage_file, 'w') as f:
                json.dump(self.llm_api_usage, f, indent=2)
        except Exception as e:
            print(f"⚠️ Could not save API usage: {e}")
    
    def initialize_excel(self):
        """Initialize Excel file with proper headers"""
        headers = [
            "Name", "Newspaper", "Published Date", "Article URL", 
            "Headline", "Full Content", "Human Summary", "News Category", 
            "Front Page News", "Extraction Success Rate", "API Usage Status"
        ]
        
        df = pd.DataFrame(columns=headers)
        df.to_excel(EXCEL_FILENAME, index=False)
        print(f"📊 Excel file '{EXCEL_FILENAME}' initialized with tracking columns")
    
    def setup_driver(self):
        """Setup Chrome WebDriver with enhanced stealth configuration"""
        try:
            chrome_options = Options()
            
            # Enhanced stealth options
            stealth_options = [
                "--headless",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080",
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-default-apps",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-field-trial-config",
                "--disable-hang-monitor",
                "--disable-ipc-flooding-protection",
                "--disable-sync",
                "--metrics-recording-only",
                "--no-first-run",
                "--safebrowsing-disable-auto-update",
                "--enable-automation",
                "--password-store=basic",
                "--use-mock-keychain"
            ]
            
            for option in stealth_options:
                chrome_options.add_argument(option)
                
            # Randomized user agent
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ]
            
            chrome_options.add_argument(f"--user-agent={random.choice(user_agents)}")
            
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Disable images and CSS for faster loading
            prefs = {
                "profile.managed_default_content_settings.images": 2,
                "profile.managed_default_content_settings.stylesheets": 2,
                "profile.managed_default_content_settings.plugins": 2,
                "profile.managed_default_content_settings.popups": 2,
                "profile.managed_default_content_settings.geolocation": 2,
                "profile.managed_default_content_settings.media_stream": 2,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Enhanced stealth JavaScript
            stealth_js = """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            window.chrome = {runtime: {}};
            """
            
            self.driver.execute_script(stealth_js)
            
            # Set timeouts
            self.driver.set_page_load_timeout(SCRAPING_CONFIG["page_load_timeout"])
            self.driver.implicitly_wait(3)
            
            print("✅ Enhanced Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup WebDriver: {e}")
            return False
    
    def adaptive_rate_limiting(self, domain):
        """Implement adaptive rate limiting based on domain and response patterns"""
        current_time = time.time()
        
        # Check if this is a new domain
        if domain not in self.last_request_time:
            self.last_request_time[domain] = 0
        
        # Calculate time since last request to this domain
        time_since_last = current_time - self.last_request_time[domain]
        
        # Adaptive delays based on domain patterns
        domain_delay_patterns = {
            'google.com': (3, 8),      # Google News - more conservative
            'timesofindia.indiatimes.com': (2, 5),
            'thehindu.com': (2, 4),
            'economictimes.indiatimes.com': (2, 5),
            'hindustantimes.com': (2, 4),
            'indianexpress.com': (2, 4),
            'default': (2, 6)
        }
        
        # Get delay pattern for domain
        delay_pattern = domain_delay_patterns.get(domain, domain_delay_patterns['default'])
        
        # Increase delays if we've had recent errors
        if self.consecutive_errors > 2:
            delay_pattern = (delay_pattern[0] * 1.5, delay_pattern[1] * 2)
        
        # Calculate required delay
        min_delay, max_delay = delay_pattern
        required_delay = random.uniform(min_delay, max_delay)
        
        # Add extra delay if requests are too frequent
        if time_since_last < min_delay:
            additional_delay = (min_delay - time_since_last) + random.uniform(1, 3)
            required_delay += additional_delay
        
        # Implement the delay
        if required_delay > 0:
            print(f"⏱️ Rate limiting: waiting {required_delay:.2f} seconds for {domain}")
            time.sleep(required_delay)
        
        # Update last request time
        self.last_request_time[domain] = time.time()
        self.request_count += 1
        
        # Extra delay every 10 requests
        if self.request_count % 10 == 0:
            extra_delay = random.uniform(10, 20)
            print(f"⏱️ Regular break: waiting {extra_delay:.2f} seconds")
            time.sleep(extra_delay)
    
    def generate_date_range(self):
        """Generate and shuffle date range for diverse sampling"""
        dates = []
        current_date = START_DATE
        
        while current_date <= END_DATE:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Shuffle for diversity
        random.shuffle(dates)
        print(f"📅 Generated {len(dates)} dates for scraping")
        return dates
    
    def search_google_news_with_fallback(self, target_date, newspaper_name, newspaper_domain):
        """Enhanced Google News search with multiple fallback strategies"""
        date_str = target_date.strftime("%Y-%m-%d")
        
        # Apply rate limiting for Google
        self.adaptive_rate_limiting('google.com')
        
        # Multiple search strategies in order of preference
        search_strategies = [
            # Strategy 1: Exact site and date
            f'site:{newspaper_domain} after:{date_str} before:{date_str}',
            
            # Strategy 2: Include newspaper name
            f'"{newspaper_name}" site:{newspaper_domain} after:{date_str} before:{date_str}',
            
            # Strategy 3: Broader date range
            f'site:{newspaper_domain} after:{target_date.strftime("%Y-%m-%d")} before:{(target_date + timedelta(days=1)).strftime("%Y-%m-%d")}',
            
            # Strategy 4: Different date format
            f'site:{newspaper_domain} "{target_date.strftime("%B %d, %Y")}"',
            
            # Strategy 5: Year and month only
            f'site:{newspaper_domain} after:{target_date.strftime("%Y-%m-01")} before:{target_date.strftime("%Y-%m-31")}',
            
            # Strategy 6: Just domain with year
            f'site:{newspaper_domain} {target_date.year}'
        ]
        
        for strategy_num, strategy in enumerate(search_strategies, 1):
            print(f"🔍 Google News Strategy {strategy_num}: {strategy}")
            
            try:
                encoded_query = quote_plus(strategy)
                google_news_url = f"https://news.google.com/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN%3Aen"
                
                self.driver.get(google_news_url)
                
                # Wait for results with timeout
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article, .xrnccd"))
                    )
                except TimeoutException:
                    print(f"⚠️ Strategy {strategy_num}: No results loaded")
                    continue
                
                # Random delay after loading
                time.sleep(random.uniform(2, 4))
                
                # Multiple approaches to find article links
                article_url = self.extract_article_url_from_google_news(newspaper_domain, strategy_num)
                
                if article_url:
                    print(f"✅ Found article via strategy {strategy_num}: {article_url}")
                    return article_url
                
            except Exception as e:
                print(f"❌ Strategy {strategy_num} failed: {e}")
                continue
        
        print(f"⚠️ All Google News strategies failed for {newspaper_name} on {date_str}")
        return None
    
    def extract_article_url_from_google_news(self, newspaper_domain, strategy_num):
        """Extract article URLs from Google News with adaptive selectors"""
        
        # Multiple selector approaches
        selector_approaches = [
            # Approach 1: Direct article links
            ("article h3 a", "href"),
            ("article a[href*='http']", "href"),
            
            # Approach 2: Google News specific selectors
            (".xrnccd", "href"),
            ("a[href*='{}']".format(newspaper_domain), "href"),
            
            # Approach 3: Try clicking on articles
            ("article", "click"),
            
            # Approach 4: Look for specific classes
            (".JtKRv", "href"),
            (".WwrzSb", "href"),
            
            # Approach 5: Generic link selectors
            ("a[href*='{}']".format(newspaper_domain.split('.')[0]), "href"),
        ]
        
        for approach_num, (selector, action) in enumerate(selector_approaches, 1):
            try:
                if action == "href":
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and newspaper_domain in href and "google.com" not in href:
                            print(f"✅ Direct link found (approach {approach_num}): {href}")
                            return href
                
                elif action == "click":
                    # Try clicking on articles to get redirected
                    articles = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for i, article in enumerate(articles[:3]):  # Try first 3 articles
                        try:
                            original_url = self.driver.current_url
                            
                            # Try to find a clickable link within the article
                            clickable_link = article.find_element(By.CSS_SELECTOR, "a")
                            clickable_link.click()
                            
                            # Wait for potential redirect
                            time.sleep(3)
                            
                            current_url = self.driver.current_url
                            if newspaper_domain in current_url:
                                print(f"✅ Click redirect found (approach {approach_num}): {current_url}")
                                return current_url
                            
                            # Go back if not the right domain
                            self.driver.back()
                            time.sleep(2)
                            
                        except Exception as e:
                            continue
                            
            except Exception as e:
                print(f"⚠️ Approach {approach_num} failed: {e}")
                continue
        
        return None
    
    def adaptive_extract_article_content(self, article_url, newspaper_name, newspaper_domain):
        """Extract article content with adaptive selector learning"""
        
        # Apply rate limiting for the newspaper domain
        self.adaptive_rate_limiting(newspaper_domain)
        
        try:
            print(f"📰 Extracting content from: {article_url}")
            
            self.driver.get(article_url)
            
            # Verify domain
            if newspaper_domain not in self.driver.current_url:
                print(f"❌ Domain mismatch. Expected: {newspaper_domain}, Got: {self.driver.current_url}")
                return None
            
            # Wait for content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(random.uniform(2, 4))
            
            # Extract components using adaptive selectors
            headline = self.adaptive_extract_headline(newspaper_domain)
            published_date = self.adaptive_extract_date(newspaper_domain)
            full_content = self.adaptive_extract_content(newspaper_domain)
            
            if not headline:
                print("❌ Could not extract headline")
                return None
            
            if not full_content or len(full_content) < SCRAPING_CONFIG["min_article_length"]:
                print("❌ Article content too short or not found")
                return None
            
            # Enhanced front page assessment
            front_page_score = self.assess_front_page_comprehensive(headline, full_content, article_url)
            
            # Calculate extraction success rate
            extraction_success_rate = self.calculate_extraction_success_rate(newspaper_domain)
            
            article_data = {
                "Name": STUDENT_NAME,
                "Newspaper": newspaper_name,
                "Published Date": published_date,
                "Article URL": article_url,
                "Headline": headline,
                "Full Content": full_content,
                "Human Summary": "",
                "News Category": "",
                "Front Page News": front_page_score,
                "Extraction Success Rate": f"{extraction_success_rate:.2f}%",
                "API Usage Status": "Pending"
            }
            
            print(f"✅ Article extracted: {headline[:50]}...")
            return article_data
            
        except Exception as e:
            print(f"❌ Article extraction failed: {e}")
            return None
    
    def adaptive_extract_headline(self, domain):
        """Extract headline using adaptive selector learning"""
        
        # Get previously successful selectors for this domain
        domain_selectors = self.successful_selectors['headline'].get(domain, {})
        
        # Combine with default selectors, prioritizing successful ones
        all_selectors = [
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
            ".post-title",
            ".main-title",
            ".news-title",
            "h1.story-headline",
            "h1.article-headline",
            ".story-title",
            ".article-header h1",
            ".content-header h1"
        ]
        
        # Prioritize previously successful selectors
        prioritized_selectors = []
        for selector, success_count in sorted(domain_selectors.items(), key=lambda x: x[1], reverse=True):
            if selector not in prioritized_selectors:
                prioritized_selectors.append(selector)
        
        # Add remaining selectors
        for selector in all_selectors:
            if selector not in prioritized_selectors:
                prioritized_selectors.append(selector)
        
        for selector in prioritized_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                headline = element.text.strip()
                
                if headline and len(headline) > 10:
                    # Record successful selector
                    self.record_successful_selector('headline', domain, selector)
                    return headline
                    
            except Exception:
                continue
        
        return None
    
    def adaptive_extract_date(self, domain):
        """Extract published date using adaptive selector learning"""
        
        domain_selectors = self.successful_selectors['date'].get(domain, {})
        
        all_selectors = [
            "time[datetime]",
            "[itemprop='datePublished']",
            "[data-timestamp]",
            ".published-date",
            ".date",
            ".timestamp",
            ".publish-date",
            ".article-date",
            ".post-date",
            ".story-date",
            ".news-date",
            ".byline-date",
            ".meta-date",
            ".date-time",
            "time",
            ".publish-time",
            ".article-time"
        ]
        
        # Prioritize successful selectors
        prioritized_selectors = []
        for selector, success_count in sorted(domain_selectors.items(), key=lambda x: x[1], reverse=True):
            if selector not in prioritized_selectors:
                prioritized_selectors.append(selector)
        
        for selector in all_selectors:
            if selector not in prioritized_selectors:
                prioritized_selectors.append(selector)
        
        for selector in prioritized_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                
                # Try multiple attributes
                for attr in ["datetime", "data-timestamp", "title", "content", "data-date"]:
                    date_text = element.get_attribute(attr)
                    if date_text:
                        parsed_date = self.format_date_flexible(date_text)
                        if parsed_date:
                            self.record_successful_selector('date', domain, selector)
                            return parsed_date
                
                # Try element text
                date_text = element.text.strip()
                if date_text:
                    parsed_date = self.format_date_flexible(date_text)
                    if parsed_date:
                        self.record_successful_selector('date', domain, selector)
                        return parsed_date
                        
            except Exception:
                continue
        
        return "Date not found"
    
    def adaptive_extract_content(self, domain):
        """Extract article content using adaptive selector learning"""
        
        domain_selectors = self.successful_selectors['content'].get(domain, {})
        
        all_selectors = [
            "[itemprop='articleBody']",
            ".article-content",
            ".story-content",
            ".content",
            ".article-body",
            ".post-content",
            ".entry-content",
            ".story-body",
            ".article-text",
            ".news-content",
            ".main-content",
            ".article-detail",
            ".story-text",
            ".news-body",
            ".content-body",
            ".article-container",
            ".story-container",
            ".news-article",
            ".full-details"
        ]
        
        # Prioritize successful selectors
        prioritized_selectors = []
        for selector, success_count in sorted(domain_selectors.items(), key=lambda x: x[1], reverse=True):
            if selector not in prioritized_selectors:
                prioritized_selectors.append(selector)
        
        for selector in all_selectors:
            if selector not in prioritized_selectors:
                prioritized_selectors.append(selector)
        
        for selector in prioritized_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    content = ""
                    for element in elements:
                        # Extract text from paragraphs
                        paragraphs = element.find_elements(By.TAG_NAME, "p")
                        for p in paragraphs:
                            text = p.text.strip()
                            if text:
                                content += text + "\n\n"
                    
                    if content.strip() and len(content.strip()) > 100:
                        self.record_successful_selector('content', domain, selector)
                        return content.strip()
                        
            except Exception:
                continue
        
        # Fallback: extract from all paragraphs
        try:
            paragraphs = self.driver.find_elements(By.TAG_NAME, "p")
            content = ""
            for p in paragraphs:
                text = p.text.strip()
                if len(text) > 20:  # Filter out short paragraphs
                    content += text + "\n\n"
            
            if content.strip():
                return content.strip()
                
        except Exception:
            pass
        
        return None
    
    def record_successful_selector(self, selector_type, domain, selector):
        """Record successful selector for adaptive learning"""
        if domain not in self.successful_selectors[selector_type]:
            self.successful_selectors[selector_type][domain] = {}
        
        if selector not in self.successful_selectors[selector_type][domain]:
            self.successful_selectors[selector_type][domain][selector] = 0
        
        self.successful_selectors[selector_type][domain][selector] += 1
        
        # Save tracking data periodically
        if self.collected_articles % 10 == 0:
            self.save_selector_tracking()
    
    def calculate_extraction_success_rate(self, domain):
        """Calculate extraction success rate for a domain"""
        total_attempts = 0
        successful_attempts = 0
        
        for selector_type in ['headline', 'date', 'content']:
            domain_data = self.successful_selectors[selector_type].get(domain, {})
            for selector, count in domain_data.items():
                total_attempts += count
                successful_attempts += count
        
        if total_attempts == 0:
            return 0.0
        
        return (successful_attempts / total_attempts) * 100
    
    def assess_front_page_comprehensive(self, headline, content, url):
        """Comprehensive front page assessment with multiple indicators"""
        
        score = 0
        max_score = 100
        
        headline_lower = headline.lower()
        content_lower = content.lower()
        
        # 1. Keyword Analysis (30 points)
        keyword_score = 0
        for category, keywords in self.front_page_indicators.items():
            for keyword in keywords:
                if keyword in headline_lower:
                    keyword_score += 3  # Headline keywords are more important
                elif keyword in content_lower:
                    keyword_score += 1
        
        score += min(keyword_score, 30)
        
        # 2. URL Analysis (20 points)
        url_indicators = [
            ('news', 5),
            ('top', 5),
            ('main', 5),
            ('breaking', 10),
            ('exclusive', 10),
            ('special', 5)
        ]
        
        url_lower = url.lower()
        for indicator, points in url_indicators:
            if indicator in url_lower:
                score += points
        
        score = min(score, 50)  # Cap URL score at 20
        
        # 3. Content Length Analysis (15 points)
        content_length = len(content)
        if content_length > 2000:  # Longer articles often more important
            score += 15
        elif content_length > 1000:
            score += 10
        elif content_length > 500:
            score += 5
        
        # 4. Headline Characteristics (20 points)
        headline_length = len(headline)
        if 40 <= headline_length <= 100:  # Optimal length for main stories
            score += 10
        
        # Check for question marks (often important stories)
        if '?' in headline:
            score += 5
        
        # Check for numbers (often data-driven important stories)
        if re.search(r'\d+', headline):
            score += 5
        
        # 5. Sentence Structure Analysis (15 points)
        sentences = content.split('.')
        if len(sentences) > 10:  # Detailed coverage
            score += 15
        elif len(sentences) > 5:
            score += 10
        elif len(sentences) > 3:
            score += 5
        
        # Convert to percentage and categorize
        percentage = (score / max_score) * 100
        
        if percentage >= 70:
            return f"High likelihood ({percentage:.1f}%)"
        elif percentage >= 40:
            return f"Moderate likelihood ({percentage:.1f}%)"
        else:
            return f"Low likelihood ({percentage:.1f}%)"
    
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
            "%d %b %Y",
            "%Y/%m/%d",
            "%d.%m.%Y",
            "%Y.%m.%d"
        ]
        
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_string, fmt)
                # Validate date is within our range
                if START_DATE <= parsed <= END_DATE:
                    return parsed.strftime("%Y-%m-%d")
            except Exception:
                continue
        
        return None
    
    def generate_summary_and_topic_with_monitoring(self, article_data):
        """Generate summary and topic with comprehensive API monitoring"""
        
        try:
            # Check API usage limits
            if self.llm_api_usage['total_requests'] >= 800:  # Conservative limit
                print("⚠️ Approaching API limit, skipping LLM processing")
                article_data["Human Summary"] = "API limit reached - summary not generated"
                article_data["News Category"] = "National News"
                article_data["API Usage Status"] = "Limit Reached"
                return article_data
            
            full_content = article_data["Full Content"]
            
            # Generate summary with retry logic
            summary = self.generate_summary_with_retry(full_content)
            
            # Classify topic with retry logic
            news_category = self.classify_topic_with_retry(full_content)
            
            # Update article data
            article_data["Human Summary"] = summary
            article_data["News Category"] = news_category
            article_data["API Usage Status"] = "Success"
            
            # Update API usage tracking
            self.llm_api_usage['total_requests'] += 2  # Summary + Classification
            self.save_api_usage()
            
            print(f"✅ LLM processing completed. Category: {news_category}")
            print(f"📊 API Usage: {self.llm_api_usage['total_requests']} requests")
            
            return article_data
            
        except Exception as e:
            print(f"❌ LLM processing failed: {e}")
            self.llm_errors += 1
            self.llm_api_usage['failed_requests'] += 1
            
            # Fallback values
            article_data["Human Summary"] = "Summary generation failed"
            article_data["News Category"] = "National News"
            article_data["API Usage Status"] = "Failed"
            
            return article_data
    
    def generate_summary_with_retry(self, content, max_retries=3):
        """Generate summary with retry logic and rate limiting"""
        
        for attempt in range(max_retries):
            try:
                # Rate limiting for API calls
                if attempt > 0:
                    time.sleep(2 ** attempt)  # Exponential backoff
                
                summary_prompt = f"""Please provide a concise summary of the following Indian news article in exactly {SCRAPING_CONFIG['summary_min_words']}-{SCRAPING_CONFIG['summary_max_words']} words:

Article: {content[:2000]}...

Summary:"""
                
                response = self.cohere_client.generate(
                    model=COHERE_CONFIG["model"],
                    prompt=summary_prompt,
                    max_tokens=COHERE_CONFIG["summary_max_tokens"],
                    temperature=COHERE_CONFIG["temperature"]
                )
                
                summary = response.generations[0].text.strip()
                
                # Validate summary length
                word_count = len(summary.split())
                if SCRAPING_CONFIG['summary_min_words'] <= word_count <= SCRAPING_CONFIG['summary_max_words']:
                    return summary
                elif word_count > 0:  # Accept if not empty
                    return summary
                    
            except Exception as e:
                if "rate limit" in str(e).lower():
                    self.llm_api_usage['rate_limit_hits'] += 1
                    print(f"⚠️ Rate limit hit, waiting longer...")
                    time.sleep(10)
                
                print(f"❌ Summary attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    return "Summary generation failed after retries"
        
        return "Summary generation failed"
    
    def classify_topic_with_retry(self, content, max_retries=3):
        """Classify topic with retry logic"""
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(2 ** attempt)
                
                topic_prompt = f"""Classify this Indian news article into exactly one of these categories: {', '.join(TOPICS)}

Article: {content[:1000]}...

Return only the category name:"""
                
                response = self.cohere_client.generate(
                    model=COHERE_CONFIG["model"],
                    prompt=topic_prompt,
                    max_tokens=COHERE_CONFIG["classification_max_tokens"],
                    temperature=0.1
                )
                
                news_category = response.generations[0].text.strip()
                
                # Validate category
                if news_category in TOPICS:
                    return news_category
                
                # Try to find partial match
                for topic in TOPICS:
                    if topic.lower() in news_category.lower():
                        return topic
                
                # Default fallback
                return "National News"
                
            except Exception as e:
                if "rate limit" in str(e).lower():
                    self.llm_api_usage['rate_limit_hits'] += 1
                    time.sleep(10)
                
                print(f"❌ Classification attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    return "National News"
        
        return "National News"
    
    def write_to_excel(self, article_data):
        """Write article data to Excel with enhanced tracking"""
        try:
            # Check for duplicates
            if article_data["Article URL"] in self.collected_urls:
                print("⚠️ Duplicate URL detected, skipping...")
                return False
            
            # Read existing data
            try:
                df = pd.read_excel(EXCEL_FILENAME)
            except Exception:
                df = pd.DataFrame()
            
            # Add new row
            new_row = pd.DataFrame([article_data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save to Excel
            df.to_excel(EXCEL_FILENAME, index=False)
            
            # Update tracking
            self.collected_urls.add(article_data["Article URL"])
            self.collected_articles += 1
            
            print(f"✅ Article saved. Total: {self.collected_articles}")
            print(f"📊 Success rate: {self.calculate_overall_success_rate():.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Excel write failed: {e}")
            return False
    
    def calculate_overall_success_rate(self):
        """Calculate overall extraction success rate"""
        if self.request_count == 0:
            return 0.0
        return (self.collected_articles / max(self.request_count, 1)) * 100
    
    def handle_driver_error(self):
        """Enhanced driver error handling with recovery strategies"""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(2)
            
            print("🔄 Recreating WebDriver with enhanced recovery...")
            
            # Exponential backoff based on consecutive errors
            delay = min(ERROR_CONFIG["driver_recreation_delay"] * (2 ** min(self.consecutive_errors, 4)), 60)
            time.sleep(delay)
            
            # Try multiple times to recreate driver
            for attempt in range(3):
                if self.setup_driver():
                    print("✅ WebDriver recreated successfully")
                    self.consecutive_errors = 0
                    return True
                else:
                    print(f"❌ Driver recreation attempt {attempt + 1} failed")
                    time.sleep(5)
            
            return False
            
        except Exception as e:
            print(f"❌ Driver recreation failed: {e}")
            return False
    
    def run_scraper(self):
        """Main scraping loop with enhanced robustness"""
        print("\n🚀 Starting adaptive news scraping process...")
        
        if not self.setup_driver():
            print("❌ Failed to initialize WebDriver. Exiting.")
            return
        
        dates = self.generate_date_range()
        
        for i, current_date in enumerate(dates):
            # Check termination conditions
            if self.collected_articles >= MAX_ARTICLES:
                print(f"✅ Target reached: {self.collected_articles} articles")
                break
            
            if self.consecutive_errors >= ERROR_CONFIG["max_consecutive_errors"]:
                print("❌ Too many consecutive errors. Exiting.")
                break
            
            print(f"\n📅 Processing {i+1}/{len(dates)}: {current_date.strftime('%Y-%m-%d')}")
            
            # Randomly select newspaper
            newspaper_name = random.choice(list(NEWSPAPER_SOURCES.keys()))
            newspaper_domain = NEWSPAPER_SOURCES[newspaper_name]
            
            try:
                # Search Google News with fallback strategies
                article_url = self.search_google_news_with_fallback(
                    current_date, newspaper_name, newspaper_domain
                )
                
                if not article_url:
                    continue
                
                # Extract article content adaptively
                article_data = self.adaptive_extract_article_content(
                    article_url, newspaper_name, newspaper_domain
                )
                
                if not article_data:
                    continue
                
                # Generate summary and classify with monitoring
                article_data = self.generate_summary_and_topic_with_monitoring(article_data)
                
                # Write to Excel
                if self.write_to_excel(article_data):
                    print(f"✅ Article {self.collected_articles} processed successfully")
                    self.consecutive_errors = 0
                
                # Print periodic statistics
                if self.collected_articles % 25 == 0:
                    self.print_progress_stats()
                
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
                
                # Log error for analysis
                error_type = type(e).__name__
                if error_type not in self.error_log:
                    self.error_log[error_type] = 0
                self.error_log[error_type] += 1
                
                time.sleep(ERROR_CONFIG["error_recovery_delay"])
        
        # Cleanup
        if self.driver:
            self.driver.quit()
        
        # Save final tracking data
        self.save_selector_tracking()
        self.save_api_usage()
        
        self.generate_comprehensive_report()
    
    def print_progress_stats(self):
        """Print detailed progress statistics"""
        print("\n" + "="*50)
        print("📊 PROGRESS STATISTICS")
        print("="*50)
        print(f"✅ Articles collected: {self.collected_articles}")
        print(f"🔄 Total requests: {self.request_count}")
        print(f"📈 Success rate: {self.calculate_overall_success_rate():.1f}%")
        print(f"❌ Total errors: {self.total_errors}")
        print(f"🤖 LLM API usage: {self.llm_api_usage['total_requests']}")
        print(f"⚠️ Rate limit hits: {self.llm_api_usage['rate_limit_hits']}")
        print("="*50)
    
    def generate_comprehensive_report(self):
        """Generate comprehensive final report"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE FINAL REPORT")
        print("="*60)
        
        # Basic statistics
        print(f"✅ Articles collected: {self.collected_articles}")
        print(f"❌ Total errors: {self.total_errors}")
        print(f"🤖 LLM errors: {self.llm_errors}")
        print(f"📁 Excel file: {EXCEL_FILENAME}")
        
        # Success rates
        overall_success = self.calculate_overall_success_rate()
        print(f"📈 Overall success rate: {overall_success:.1f}%")
        
        # API usage statistics
        print(f"\n🤖 LLM API USAGE:")
        print(f"   Total requests: {self.llm_api_usage['total_requests']}")
        print(f"   Failed requests: {self.llm_api_usage['failed_requests']}")
        print(f"   Rate limit hits: {self.llm_api_usage['rate_limit_hits']}")
        
        # Adaptive learning statistics
        print(f"\n🧠 ADAPTIVE LEARNING:")
        for selector_type in ['headline', 'date', 'content']:
            total_domains = len(self.successful_selectors[selector_type])
            print(f"   {selector_type.capitalize()} selectors learned: {total_domains} domains")
        
        # Top performing domains
        print(f"\n🏆 TOP PERFORMING DOMAINS:")
        domain_performance = {}
        for selector_type in ['headline', 'date', 'content']:
            for domain, selectors in self.successful_selectors[selector_type].items():
                if domain not in domain_performance:
                    domain_performance[domain] = 0
                domain_performance[domain] += sum(selectors.values())
        
        for domain, score in sorted(domain_performance.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {domain}: {score} successful extractions")
        
        # Error breakdown
        if self.error_log:
            print(f"\n❌ ERROR BREAKDOWN:")
            for error_type, count in sorted(self.error_log.items(), key=lambda x: x[1], reverse=True):
                print(f"   {error_type}: {count}")
        
        # Save comprehensive error log
        self.save_comprehensive_error_log()
        
        # Final assessment
        if self.collected_articles >= MIN_ARTICLES:
            print("\n🎉 SUCCESS: Target achieved with enhanced robustness!")
        else:
            print("\n⚠️ WARNING: Target not reached - check adaptive learning data")
        
        print("="*60)
    
    def save_comprehensive_error_log(self):
        """Save comprehensive error log with all statistics"""
        try:
            with open(ERROR_LOG_FILENAME, 'w') as f:
                f.write("ADAPTIVE NEWS SCRAPER - COMPREHENSIVE ERROR LOG\n")
                f.write("="*60 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Basic statistics
                f.write("BASIC STATISTICS:\n")
                f.write(f"Articles Collected: {self.collected_articles}\n")
                f.write(f"Total Errors: {self.total_errors}\n")
                f.write(f"LLM Errors: {self.llm_errors}\n")
                f.write(f"Success Rate: {self.calculate_overall_success_rate():.1f}%\n\n")
                
                # API usage
                f.write("LLM API USAGE:\n")
                for key, value in self.llm_api_usage.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n")
                
                # Error breakdown
                if self.error_log:
                    f.write("ERROR BREAKDOWN:\n")
                    for error_type, count in sorted(self.error_log.items(), key=lambda x: x[1], reverse=True):
                        f.write(f"{error_type}: {count}\n")
                    f.write("\n")
                
                # Adaptive learning data
                f.write("ADAPTIVE LEARNING DATA:\n")
                for selector_type in ['headline', 'date', 'content']:
                    f.write(f"\n{selector_type.upper()} SELECTORS:\n")
                    for domain, selectors in self.successful_selectors[selector_type].items():
                        f.write(f"  {domain}:\n")
                        for selector, count in sorted(selectors.items(), key=lambda x: x[1], reverse=True):
                            f.write(f"    {selector}: {count} successes\n")
                
            print(f"📄 Comprehensive error log saved: {ERROR_LOG_FILENAME}")
            
        except Exception as e:
            print(f"⚠️ Could not save comprehensive error log: {e}")

def main():
    """Main function"""
    print("="*70)
    print("🗞️  ADAPTIVE NEWS SCRAPER WITH ENHANCED ROBUSTNESS")
    print("="*70)
    
    cohere_api_key = input("Enter your Cohere API key: ").strip()
    
    if not cohere_api_key:
        print("❌ Cohere API key required")
        return
    
    scraper = AdaptiveNewsScraperAgent(cohere_api_key)
    scraper.run_scraper()

if __name__ == "__main__":
    main()