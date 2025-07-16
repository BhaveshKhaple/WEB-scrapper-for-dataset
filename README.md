# Indian English News Scraper

A comprehensive agentic workflow for collecting 1000-1100 Indian English news articles from 2010-2020 using Google News search and original newspaper sources.

## 🎯 Project Overview

This project implements an autonomous AI Data Collection Agent that:
- Collects unique Indian English news articles from multiple newspapers
- Uses Google News as a discovery mechanism
- Extracts full content from original newspaper sources
- Generates summaries and categorizes articles using LLM
- Outputs structured data in Excel format

## 📋 Requirements

### Target Specifications
- **Quantity**: 1000-1100 unique articles
- **Date Range**: January 1, 2010 - December 31, 2020
- **Source**: Indian English newspapers via Google News
- **Language**: English only
- **Format**: Structured Excel output

### Data Structure
Each article contains:
1. **Name**: Student name (Tejas Subhash Bagal)
2. **Newspaper**: Original newspaper name
3. **Published Date**: YYYY-MM-DD format
4. **Article URL**: Direct link to original article
5. **Headline**: Exact title from source
6. **Full Content**: Complete article text
7. **Human Summary**: 50-200 word LLM summary
8. **News Category**: Classified topic
9. **Front Page News**: Prominence indicator

## 🚀 Quick Start

### 1. Environment Setup

For Google Colab:
```bash
python setup.py
```

For local Linux environment:
```bash
pip install -r requirements.txt
```

### 2. Configuration

Edit `config.py` to customize:
- Date ranges
- Newspaper sources
- Article targets
- LLM settings
- Chrome options

### 3. Testing

Run component tests:
```bash
python test_scraper.py all
```

### 4. Run Scraper

Basic version:
```bash
python news_scraper.py
```
python simple_news_scraper.py --process-summaries

Enhanced version (recommended):
```bash
python enhanced_news_scraper.py
```

## 📁 File Structure

```
scrapper/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── config.py                   # Configuration settings
├── setup.py                    # Environment setup script
├── news_scraper.py             # Basic scraper implementation
├── enhanced_news_scraper.py    # Enhanced scraper with config
├── test_scraper.py             # Testing utilities
├── News_Submissions_GoogleNews_Approach.xlsx  # Output file
└── google_news_scraper_error_log.txt          # Error log
```

## 🔧 Configuration Options

### Newspaper Sources
The scraper includes 25+ Indian English newspapers:
- The Times of India, The Hindu, Economic Times
- Hindustan Times, Indian Express, Telegraph
- And many more...

### News Categories
- Politics, Sports, Business
- Science and Technology, Entertainment
- National News, International News
- Health, Education, Environment
- Crime, Social Issues

### Scraping Parameters
- **Request delays**: 2-5 seconds between requests
- **Page timeout**: 15 seconds
- **Retry logic**: 3 attempts per failed request
- **Error recovery**: Automatic WebDriver recreation

## 🛠️ Technical Implementation

### Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Google News   │───▶│   Newspaper     │───▶│   Content       │
│   Search        │    │   Website       │    │   Extraction    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Date Range    │    │   URL Discovery │    │   Text Parsing  │
│   Generation    │    │   & Validation  │    │   & Cleaning    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM Processing│    │   Data Storage  │    │   Error Handling│
│   (Cohere API)  │    │   (Excel)       │    │   & Recovery    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features
- **Robust Error Handling**: Automatic retry and recovery
- **Anti-Detection**: Randomized delays and user agents
- **Flexible Parsing**: Multiple selectors for different websites
- **Duplicate Prevention**: URL tracking to avoid duplicates
- **Progress Tracking**: Real-time collection statistics

## 🔍 Search Strategy

### Google News Search
1. **Date-specific searches**: `site:domain after:date before:date`
2. **Newspaper-specific**: Include newspaper name in query
3. **Fallback strategies**: Alternative search patterns
4. **Link extraction**: Multiple methods for URL discovery

### Content Extraction
1. **Multi-selector approach**: Try multiple CSS selectors
2. **Flexible date parsing**: Handle various date formats
3. **Content validation**: Length and quality checks
4. **Domain verification**: Ensure no unwanted redirects

## 🤖 LLM Integration

### Cohere API Usage
- **Summarization**: 50-200 word summaries
- **Classification**: Topic categorization
- **Error handling**: Fallback for API failures
- **Token optimization**: Efficient prompt design

### Supported Models
- `command-xlarge-nightly` (recommended)
- Custom temperature settings
- Configurable token limits

## 📊 Output Format

### Excel Structure
```
Name | Newspaper | Published Date | Article URL | Headline | Full Content | Human Summary | News Category | Front Page News
-----|-----------|---------------|-------------|----------|--------------|---------------|---------------|---------------
Tejas Subhash Bagal | The Times of India | 2015-01-01 | https://... | Sample Headline | Full article text... | AI-generated summary... | Politics | High likelihood
```

### Quality Assurance
- URL uniqueness validation
- Content length verification
- Date format standardization
- Category validation against predefined list

## 🚨 Enhanced Error Handling & Robustness

### Adaptability Features
- **Dynamic Selector Learning**: Automatically learns successful selectors for each domain
- **Fallback Strategy Engine**: Multiple search approaches for Google News
- **HTML Structure Adaptation**: Handles changing website layouts automatically
- **Selector Success Tracking**: Prioritizes previously successful extraction methods

### Rate Limiting & Anti-Detection
- **Adaptive Rate Limiting**: Domain-specific delays that adjust based on response patterns
- **Exponential Backoff**: Increases delays after consecutive errors
- **Randomized Delays**: Prevents detection through timing analysis
- **User Agent Rotation**: Multiple browser fingerprints for stealth
- **Request Pattern Diversification**: Varies timing and approach strategies

### Front Page News Assessment
- **Multi-Factor Analysis**: Combines keyword analysis, URL patterns, content characteristics
- **Scoring Algorithm**: Comprehensive scoring system for news importance
- **Contextual Indicators**: Considers article length, headline structure, and content depth
- **Likelihood Categorization**: High/Moderate/Low likelihood ratings with confidence scores

### LLM API Management
- **Usage Monitoring**: Real-time tracking of API requests and quotas
- **Rate Limit Detection**: Automatically handles API rate limiting
- **Exponential Backoff**: Intelligent retry mechanisms for failed requests
- **Quota Management**: Prevents exceeding API limits with proactive monitoring
- **Fallback Strategies**: Graceful degradation when API limits are reached

### Error Recovery Mechanisms
- **Driver Recreation**: Automatic browser restart with enhanced configuration
- **Session Recovery**: Maintains progress across driver failures
- **Adaptive Delays**: Increases wait times based on error patterns
- **Multiple Retry Strategies**: Different approaches for different error types
- **Graceful Degradation**: Continues operation with partial functionality

## 📈 Performance Optimization

### Efficiency Features
- **Headless browsing**: Faster execution
- **Optimized selectors**: Efficient DOM parsing
- **Batch processing**: Bulk operations where possible
- **Memory management**: Proper resource cleanup

### Scalability
- **Configurable limits**: Adjustable article targets
- **Modular design**: Easy to extend and modify
- **Logging system**: Comprehensive activity tracking
- **Resource monitoring**: Memory and CPU optimization

## 🧪 Testing

### Test Coverage
- **WebDriver setup**: Browser initialization
- **Search functionality**: Google News queries
- **Content extraction**: Article parsing
- **Excel operations**: Data storage
- **API integration**: LLM services

### Running Tests
```bash
# Run all tests
python test_scraper.py all

# Run specific test
python test_scraper.py driver
python test_scraper.py search
python test_scraper.py extract
python test_scraper.py excel
python test_scraper.py cohere
```

## 🔒 Security & Ethics

### Rate Limiting
- Random delays between requests
- Respectful crawling practices
- User agent rotation
- Session management

### Data Privacy
- No personal data collection
- Public content only
- Proper attribution
- Compliance with robots.txt

## 🐛 Troubleshooting

### Common Issues

**Chrome WebDriver Issues**
```bash
# Reinstall Chrome
python setup.py
```

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Google News Access**
- Check internet connection
- Verify Chrome installation
- Clear browser cache
- Try different IP if blocked

**Cohere API Issues**
- Verify API key
- Check quota limits
- Monitor rate limits
- Handle API downtime

### Debug Mode
Enable detailed logging in `config.py`:
```python
LOGGING_CONFIG = {
    "log_level": "DEBUG",
    "console_output": True,
    "file_output": True
}
```

## 📞 Support

For issues and questions:
1. Check the error log file
2. Run the test suite
3. Review configuration settings
4. Check network connectivity

## 📄 License

This project is for educational purposes only. Please respect newspaper terms of service and copyright policies.

## 🎉 Success Metrics

- **Target Achievement**: 1000-1100 articles collected
- **Quality Assurance**: >95% valid articles
- **Error Rate**: <5% failure rate
- **Performance**: <10 seconds per article average

## 🚀 Quick Start Guide

### 1. **Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# For Google Colab
python setup.py

# Test installation
python test_scraper.py all
```

### 2. **Choose Your Scraper Version**

**Basic Version** (Original implementation):
```bash
python news_scraper.py
```

**Enhanced Version** (With configuration support):
```bash
python enhanced_news_scraper.py
```

**Adaptive Version** (Recommended - Maximum robustness):
```bash
python adaptive_news_scraper.py
```

**Interactive Version** (User-friendly):
```bash
python run_scraper.py
```

### 3. **Monitoring & Analysis**
```bash
# Real-time monitoring
python monitor_scraper.py monitor

# Full analysis
python monitor_scraper.py analyze

# Test adaptive features
python test_adaptive_features.py
```

### 4. **Configuration Options**

Edit `config.py` to customize:
- Collection targets and date ranges
- Newspaper sources and categories
- Rate limiting parameters
- API usage limits
- Chrome browser options

### 5. **Best Practices**

1. **Start with Testing**:
   ```bash
   python test_scraper.py all
   ```

2. **Monitor Progress**:
   ```bash
   python monitor_scraper.py monitor 60
   ```

3. **Use Adaptive Version** for production:
   ```bash
   python adaptive_news_scraper.py
   ```

4. **Check Results Regularly**:
   - Monitor API usage
   - Review success rates
   - Analyze adaptive learning progress

### 6. **Troubleshooting**

**Chrome Issues**:
```bash
python setup.py  # Reinstall Chrome
```

**Rate Limiting**:
- Increase delays in `config.py`
- Use adaptive version for automatic adjustment

**API Limits**:
- Monitor usage with `monitor_scraper.py`
- Consider upgrading Cohere plan

**Low Success Rate**:
- Review adaptive learning data
- Test individual newspaper extraction
- Update selectors if needed

---

**Happy Scraping!** 🗞️✨

## 📞 Additional Resources

- **Test Suite**: `test_adaptive_features.py` - Comprehensive testing
- **Monitoring**: `monitor_scraper.py` - Real-time analytics
- **Configuration**: `config.py` - Easy customization
- **Documentation**: This README - Complete guide