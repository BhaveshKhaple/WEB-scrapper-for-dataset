"""
Configuration file for Indian News Archive Scraper
Easy customization of scraping parameters
"""

# Date Range Configuration
START_YEAR = 2010
END_YEAR = 2020

# Scraping Behavior
MAX_ARTICLES_PER_DAY = 15  # Limit articles per day per newspaper
REQUEST_DELAY_MIN = 1      # Minimum delay between requests (seconds)
REQUEST_DELAY_MAX = 3      # Maximum delay between requests (seconds)
DAY_DELAY_MIN = 2          # Minimum delay between days (seconds)
DAY_DELAY_MAX = 5          # Maximum delay between days (seconds)

# Request Configuration
REQUEST_TIMEOUT = 15       # Request timeout in seconds
MAX_RETRIES = 3           # Maximum retry attempts

# Indian News Sites Configuration
INDIAN_NEWS_SITES = {
    "The Hindu": {
        "base_url": "https://www.thehindu.com",
        "archive_pattern": "https://www.thehindu.com/archive/web/{year}/{month:02d}/{day:02d}/",
        "selectors": {
            "article_links": "a[href*='/news/'], a[href*='/article/']",
            "headline": "h1, .headline, .title",
            "content": ".content, .story-content, article p, .articleBody",
            "author": ".author, .byline, .writer"
        },
        "active": True
    },
    
    "Hindustan Times": {
        "base_url": "https://www.hindustantimes.com",
        "archive_pattern": "https://www.hindustantimes.com/archive/web/{year}/{month:02d}/{day:02d}/",
        "selectors": {
            "article_links": "a[href*='/news/'], a[href*='/story/']",
            "headline": "h1, .headline, .hdg1",
            "content": ".story-content, .detail, .story-details",
            "author": ".author, .byline"
        },
        "active": True
    },
    
    "Indian Express": {
        "base_url": "https://indianexpress.com",
        "archive_pattern": "https://indianexpress.com/archive/{year}/{month:02d}/{day:02d}/",
        "selectors": {
            "article_links": "a[href*='/article/'], a[href*='/news/']",
            "headline": "h1, .native_story_title, .heading",
            "content": ".story-element-text, .ie-contentbox, .full-details",
            "author": ".author, .editor"
        },
        "active": True
    },
    
    "Times of India": {
        "base_url": "https://timesofindia.indiatimes.com",
        "archive_pattern": "https://timesofindia.indiatimes.com/archive/year-{year},month-{month},starttime-{start_time}.cms",
        "selectors": {
            "article_links": "a[href*='/articleshow/']",
            "headline": "h1, .HNMDR, .headline",
            "content": ".Normal, .story-content, .ga-headlines",
            "author": ".author, .byline"
        },
        "active": True,
        "special_handling": "times_group"
    },
    
    "Economic Times": {
        "base_url": "https://economictimes.indiatimes.com",
        "archive_pattern": "https://economictimes.indiatimes.com/archive/year-{year},month-{month},starttime-{start_time}.cms",
        "selectors": {
            "article_links": "a[href*='/articleshow/'], a[href*='/news/']",
            "headline": "h1, .artTitle, .headline",
            "content": ".artText, .Normal, .story-content",
            "author": ".author, .byline"
        },
        "active": True,
        "special_handling": "times_group"
    },
    
    "The Telegraph": {
        "base_url": "https://www.telegraphindia.com",
        "archive_pattern": "https://www.telegraphindia.com/archive/{year}/{month:02d}/{day:02d}/",
        "selectors": {
            "article_links": "a[href*='/news/'], a[href*='/story/']",
            "headline": "h1, .headline, .story-headline",
            "content": ".story-content, .story-text, .content",
            "author": ".author, .byline"
        },
        "active": True
    },
    
    "Deccan Chronicle": {
        "base_url": "https://www.deccanchronicle.com",
        "archive_pattern": "https://www.deccanchronicle.com/archive/{year}/{month:02d}/{day:02d}/",
        "selectors": {
            "article_links": "a[href*='/news/'], a[href*='/story/']",
            "headline": "h1, .headline, .story-headline",
            "content": ".story-content, .story-text, .content",
            "author": ".author, .byline"
        },
        "active": True
    },
    
    "Business Standard": {
        "base_url": "https://www.business-standard.com",
        "archive_pattern": "https://www.business-standard.com/archive/{year}/{month:02d}/{day:02d}/",
        "selectors": {
            "article_links": "a[href*='/news/'], a[href*='/article/']",
            "headline": "h1, .headline, .story-headline",
            "content": ".story-content, .story-text, .content",
            "author": ".author, .byline"
        },
        "active": True
    }
}

# Article Classification Categories
ARTICLE_CATEGORIES = {
    'Politics': ['government', 'minister', 'parliament', 'election', 'policy', 'cabinet', 'congress', 'bjp', 'political'],
    'Sports': ['cricket', 'football', 'match', 'player', 'game', 'tournament', 'team', 'sport', 'stadium'],
    'Business': ['market', 'economy', 'company', 'financial', 'stock', 'revenue', 'profit', 'investment', 'corporate'],
    'Entertainment': ['film', 'movie', 'actor', 'bollywood', 'music', 'cinema', 'television', 'celebrity'],
    'National News': ['india', 'indian', 'nation', 'national', 'country', 'state', 'central', 'domestic'],
    'International News': ['international', 'world', 'global', 'foreign', 'overseas', 'abroad', 'diplomatic'],
    'Crime': ['crime', 'police', 'arrest', 'murder', 'theft', 'court', 'case', 'investigation', 'criminal'],
    'Health': ['health', 'medical', 'hospital', 'disease', 'treatment', 'doctor', 'patient', 'medicine'],
    'Science and Technology': ['technology', 'science', 'research', 'innovation', 'development', 'tech', 'scientific'],
    'Environment': ['environment', 'climate', 'pollution', 'green', 'carbon', 'renewable', 'conservation']
}

# Major Indian Cities for Location Extraction
INDIAN_CITIES = [
    'Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad',
    'Surat', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Thane', 'Bhopal',
    'Visakhapatnam', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Agra', 'Nashik',
    'Faridabad', 'Meerut', 'Rajkot', 'Varanasi', 'Srinagar', 'Amritsar', 'Allahabad',
    'Coimbatore', 'Jabalpur', 'Gwalior', 'Vijayawada', 'Madurai', 'Guwahati', 'Chandigarh',
    'Thiruvananthapuram', 'Solapur', 'Mysore', 'Tiruppur', 'Gurgaon', 'Aligarh', 'Jalandhar',
    'Bhubaneswar', 'Salem', 'Warangal', 'Guntur', 'Bhiwandi', 'Saharanpur', 'Gorakhpur',
    'Bikaner', 'Amravati', 'Noida', 'Jamshedpur', 'Bhilai', 'Cuttack', 'Firozabad',
    'Kochi', 'Bhavnagar', 'Dehradun', 'Durgapur', 'Asansol', 'Nanded', 'Kolhapur',
    'Ajmer', 'Akola', 'Gulbarga', 'Jamnagar', 'Ujjain', 'Siliguri', 'Jhansi'
]

# Indian States
INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa',
    'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
    'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland',
    'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Delhi', 'Chandigarh', 'Puducherry'
]

# Front Page Assessment Keywords
FRONT_PAGE_KEYWORDS = {
    'high_priority': ['breaking', 'urgent', 'major', 'important', 'announced', 'exclusive', 'crisis', 'emergency'],
    'medium_priority': ['significant', 'development', 'decision', 'statement', 'launches', 'introduces'],
    'low_priority': ['reports', 'says', 'claims', 'suggests', 'indicates']
}

# Data Quality Configuration
MIN_HEADLINE_LENGTH = 10
MIN_CONTENT_LENGTH = 50
MAX_CONTENT_LENGTH = 50000

# File Output Configuration
OUTPUT_FILENAME_PREFIX = "Indian_News_Archive"
PROGRESS_SAVE_FREQUENCY = 50  # Save progress every N articles
ENABLE_PROGRESS_FILES = True

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'indian_news_scraper.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Excel Output Columns
EXCEL_COLUMNS = [
    'Name of Newspaper',
    'Published date of News',
    'Enter URL or Link of News',
    'Headline of News Article',
    'Content in detail of News article',
    'Summary of News article',
    'Category of News Article',
    'Location of News',
    'Author of News Article',
    'Front Page Assessment'
]

# User Agent for requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Print configuration when imported
if __name__ == "__main__":
    print("Indian News Archive Scraper Configuration")
    print("="*50)
    print(f"Date Range: {START_YEAR} - {END_YEAR}")
    print(f"Active News Sites: {sum(1 for site in INDIAN_NEWS_SITES.values() if site.get('active', True))}")
    print(f"Max Articles per Day: {MAX_ARTICLES_PER_DAY}")
    print(f"Request Delay: {REQUEST_DELAY_MIN}-{REQUEST_DELAY_MAX}s")
    print(f"Categories: {len(ARTICLE_CATEGORIES)}")
    print(f"Cities: {len(INDIAN_CITIES)}")
    print(f"States: {len(INDIAN_STATES)}")
    print("="*50)
    
    print("\nActive News Sites:")
    for i, (name, config) in enumerate(INDIAN_NEWS_SITES.items(), 1):
        if config.get('active', True):
            print(f"{i:2d}. {name}")
    
    print("\nArticle Categories:")
    for category, keywords in ARTICLE_CATEGORIES.items():
        print(f"  {category}: {len(keywords)} keywords")