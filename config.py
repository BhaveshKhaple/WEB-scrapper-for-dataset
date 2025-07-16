"""
Configuration file for News Scraper
Modify these settings as needed
"""

from datetime import datetime

# Date Range Configuration - Historical News (2000-2020)
START_DATE = datetime(2000, 1, 1)
END_DATE = datetime(2020, 12, 31)

# Article Collection Targets
MAX_ARTICLES = 200
MIN_ARTICLES = 200

# Output Configuration - Single Excel file for all operations
EXCEL_FILENAME = "News_Articles_Collection.xlsx"
ERROR_LOG_FILENAME = "scraper_error_log.txt"
STUDENT_NAME = "Tejas Subhash Bagal"

# Indian English Newspaper Sources (2000-2020 Historical Collection)
NEWSPAPER_SOURCES = {
    "The Hindu": "thehindu.com",
    "Hindustan Times": "hindustantimes.com", 
    "Indian Express": "indianexpress.com",
    "The Telegraph": "telegraphindia.com",
    "Deccan Chronicle": "deccanchronicle.com",
    "The New Indian Express": "newindianexpress.com",
    "Mint": "livemint.com",
    "Business Standard": "business-standard.com",
    "Financial Express": "financialexpress.com",
    "DNA": "dnaindia.com",
    "The Tribune": "tribuneindia.com",
    "The Statesman": "thestatesman.com",
    "The Asian Age": "asianage.com",
    "The Pioneer": "dailypioneer.com",
    "The Free Press Journal": "freepressjournal.in",
    "The Economic Times": "economictimes.indiatimes.com",
    "The Afternoon Despatch & Courier": "afternoondc.in",
    "The Sentinel": "sentinelassam.com",
    "The Navhind Times": "navhindtimes.in",
    "Goa Chronicle": "goachronicleonline.com",
    "The Assam Tribune": "assamtribune.com",
    "The Arunachal Times": "arunachaltimes.in",
    "The Shillong Times": "theshillongtimes.com",
    "The Imphal Free Press": "ifp.co.in",
    "The Sikkim Express": "sikkimexpress.com",
    "The Hans India": "thehansindia.com",
    "The Orissa Post": "orissapost.com",
    "The Daily Post": "thedailypost.in",
    "The Hitavada": "thehitavada.com",
    "The Meghalaya Guardian": "meghalayaguardian.com",
    "The Morung Express": "morungexpress.com",
    "The Sangai Express": "sangaiexpress.com",
    "The Arunachal Front": "arunachalfront.com"
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

# Gemini LLM Configuration
GEMINI_CONFIG = {
    "model": "gemini-pro",
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