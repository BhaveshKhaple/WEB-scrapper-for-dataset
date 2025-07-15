"""
Configuration file for News Scraper
Modify these settings as needed
"""

from datetime import datetime

# Date Range Configuration
START_DATE = datetime(2010, 1, 1)
END_DATE = datetime(2020, 12, 31)

# Article Collection Targets
MAX_ARTICLES = 1100
MIN_ARTICLES = 1000

# Output Configuration - Single Excel file for all operations
EXCEL_FILENAME = "News_Articles_Collection.xlsx"
ERROR_LOG_FILENAME = "scraper_error_log.txt"
STUDENT_NAME = "Tejas Subhash Bagal"

# Indian English Newspaper Sources
NEWSPAPER_SOURCES = {
    "The Times of India": "timesofindia.indiatimes.com",
    "The Hindu": "thehindu.com", 
    "The Economic Times": "economictimes.indiatimes.com",
    "Hindustan Times": "hindustantimes.com",
    "Indian Express": "indianexpress.com",
    "The Telegraph": "telegraphindia.com",
    "Deccan Herald": "deccanherald.com",
    "Business Standard": "business-standard.com",
    "Mint": "livemint.com",
    "DNA": "dnaindia.com",
    "The New Indian Express": "newindianexpress.com",
    "The Statesman": "thestatesman.com",
    "Outlook": "outlookindia.com",
    "India Today": "indiatoday.in",
    "The Wire": "thewire.in",
    "Scroll": "scroll.in",
    "FirstPost": "firstpost.com",
    "News18": "news18.com",
    "NDTV": "ndtv.com",
    "The Quint": "thequint.com",
    "Rediff": "rediff.com",
    "Zee News": "zeenews.india.com",
    "CNN-News18": "cnn-news18.com",
    "Republic World": "republicworld.com",
    "The Print": "theprint.in"
}

# News Categories for Classification
TOPICS = [
    "Politics",
    "Sports", 
    "Business",
    "Science and Technology",
    "Entertainment",
    "National News",
    "International News",
    "Health",
    "Education",
    "Environment",
    "Crime",
    "Social Issues",
    "Culture",
    "Economy",
    "Defense"
]

# Scraping Configuration
SCRAPING_CONFIG = {
    "min_article_length": 100,  # Minimum characters for article content
    "max_retries": 3,           # Maximum retries for failed requests
    "request_delay_min": 2,     # Minimum delay between requests (seconds)
    "request_delay_max": 5,     # Maximum delay between requests (seconds)
    "page_load_timeout": 15,    # Timeout for page loading (seconds)
    "summary_min_words": 50,    # Minimum words for summary
    "summary_max_words": 200,   # Maximum words for summary
}

# Chrome WebDriver Configuration
CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox", 
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
    "--disable-blink-features=AutomationControlled",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript"  # Remove this if sites require JavaScript
]

# Cohere LLM Configuration
COHERE_CONFIG = {
    "model": "command-r-plus",
    "summary_max_tokens": 150,
    "classification_max_tokens": 20,
    "temperature": 0.3
}

# Error Handling Configuration
ERROR_CONFIG = {
    "max_consecutive_errors": 8,  # Increased for better resilience
    "driver_recreation_delay": 10,
    "error_recovery_delay": 5,
    "captcha_wait_time": 30,
    "max_retries_per_article": 3,
    "exponential_backoff_base": 2
}

# Adaptive Rate Limiting Configuration
RATE_LIMITING_CONFIG = {
    "base_delay_range": (2, 6),
    "google_news_delay_range": (3, 8),
    "error_multiplier": 1.5,
    "regular_break_interval": 10,
    "regular_break_duration": (10, 20),
    "domain_specific_delays": {
        "timesofindia.indiatimes.com": (2, 5),
        "thehindu.com": (2, 4),
        "economictimes.indiatimes.com": (2, 5),
        "hindustantimes.com": (2, 4),
        "indianexpress.com": (2, 4),
        "google.com": (3, 8)
    }
}

# Front Page Assessment Configuration
FRONT_PAGE_CONFIG = {
    "keyword_categories": {
        "breaking_news": ["breaking", "urgent", "exclusive", "major", "historic", "crisis"],
        "political": ["parliament", "government", "minister", "election", "policy", "cabinet"],
        "economic": ["budget", "economy", "market", "rupee", "gdp", "inflation"],
        "social": ["protest", "violence", "court", "verdict", "scandal", "arrest"],
        "international": ["china", "pakistan", "usa", "trade", "border", "summit"]
    },
    "scoring_weights": {
        "headline_keywords": 3,
        "content_keywords": 1,
        "url_indicators": 5,
        "content_length_bonus": 15,
        "headline_length_bonus": 10
    },
    "thresholds": {
        "high_likelihood": 70,
        "moderate_likelihood": 40
    }
}

# Logging Configuration
LOGGING_CONFIG = {
    "log_level": "INFO",
    "console_output": True,
    "file_output": True,
    "log_filename": "scraper.log"
}