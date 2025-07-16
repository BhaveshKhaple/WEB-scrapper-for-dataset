# 📰 News Scraper & Summarization System

A comprehensive news scraping, validation, and AI-powered summarization system that collects news articles from multiple sources and generates concise summaries using local AI models.

## 🏗️ Project Structure

```
scrapper/
├── 📁 scrapers/           # News scraping modules
├── 📁 checkers/           # Data validation and verification tools
├── 📁 summarizers/        # AI summarization modules
├── 📁 utilities/          # Helper tools and utilities
├── 📁 logs/              # Log files
├── 📄 config.py          # Configuration settings
├── 📄 setup.py           # Environment setup
├── 📄 requirements.txt   # Python dependencies
└── 📄 README.md          # This file
```

## 🚀 Quick Start Guide

### 1. Environment Setup
```bash
# Install dependencies
python setup.py

# Or manually install
pip install -r requirements.txt
```

### 2. Install Ollama (for AI summarization)
```bash
# Download and install Ollama from https://ollama.ai
# Then pull the recommended model
ollama pull gemma3:4b
```

### 3. Complete Workflow (Scraping → Validation → Summarization)
```bash
# Step 1: Scrape news articles
python scrapers/news_scraper.py

# Step 2: Validate and fix content
python utilities/reauthenticator.py

# Step 3: Generate AI summaries
python summarizers/production_summarizer.py
```

## 📋 Detailed Module Documentation

### 🕷️ Scrapers Module (`scrapers/`)

#### `news_scraper.py`
**Purpose**: Clean scraper for collecting exactly 200 articles
**Usage**:
```bash
python scrapers/news_scraper.py
```
**Features**:
- Collects exactly 200 articles from multiple sources
- Generates random dates between 2000-2020
- Saves to `new_excel.xlsx`
- Includes content validation

#### `continuous_news_scraper.py`
**Purpose**: Continuous scraping for ongoing data collection
**Usage**:
```bash
python scrapers/continuous_news_scraper.py
```
**Features**:
- Runs multiple scraping cycles
- Saves to `continuous_news.xlsx`
- Configurable cycle count
- Automatic duplicate removal

### 🔍 Checkers Module (`checkers/`)

#### `check_new_excel.py`
**Purpose**: Verify title-content matching in new_excel.xlsx
**Usage**:
```bash
python checkers/check_new_excel.py
```
**Features**:
- Analyzes title-content correlation
- Shows date range validation
- Attempts to fix mismatched content
- Provides detailed statistics

#### `check_excel.py`
**Purpose**: General Excel file validation
**Usage**:
```bash
python checkers/check_excel.py
```
**Features**:
- File structure validation
- Data quality checks
- Missing field detection

#### `verify_excel.py`
**Purpose**: Comprehensive Excel file verification
**Usage**:
```bash
python checkers/verify_excel.py
```

#### `preview_excel.py`
**Purpose**: Quick preview of Excel file contents
**Usage**:
```bash
python checkers/preview_excel.py
```

#### `view_excel_details.py`
**Purpose**: Detailed Excel file analysis
**Usage**:
```bash
python checkers/view_excel_details.py
```

### 🤖 Summarizers Module (`summarizers/`)

#### `production_summarizer.py`
**Purpose**: AI-powered article summarization using Ollama
**Usage**:
```bash
python summarizers/production_summarizer.py
```
**Features**:
- Processes articles in batches of 10
- Uses Ollama with gemma3:4b model
- Generates clean, concise summaries
- Automatic progress saving
- Comprehensive error handling

**Configuration**:
- Model: `gemma3:4b`
- Batch size: 10 articles
- Processing order: continuous_news.xlsx → new_excel.xlsx

### 🛠️ Utilities Module (`utilities/`)

#### `reauthenticator.py` ⭐ **ENHANCED**
**Purpose**: Comprehensive article validation and quality assurance for ALL articles
**Usage**:
```bash
python utilities/reauthenticator.py
```
**Enhanced Options**:
1. **Quick check** - Basic title-content match statistics
2. **Comprehensive check** - Detailed analysis of ALL articles with quality metrics
3. **Full reauthentication** - Check and fix mismatched articles

**Enhanced Features**:
- ✅ **Analyzes EVERY article** in both Excel files
- ✅ **Multiple quality checks**:
  - Title-content matching (30% word overlap threshold)
  - Empty titles detection
  - Empty content detection  
  - Short content detection (<100 characters)
- ✅ **Health scoring** - Overall quality percentage per file
- ✅ **Detailed reporting** - Specific issues identified per article
- ✅ **Actionable recommendations** - Clear next steps provided
- ✅ **Automatic content recollection** from URLs for mismatched articles
- ✅ **Progress tracking** with comprehensive statistics
- ✅ **Enhanced logging** to `logs/reauthenticator.log`

#### `quick_check_reauthenticator.py` ⭐ **ENHANCED**
**Purpose**: Article quality checker with quick and comprehensive analysis options
**Usage**:
```bash
python utilities/quick_check_reauthenticator.py
```
**Options**:
1. **Quick check** - Basic statistics only
2. **Comprehensive analysis** - Detailed review of ALL articles

**Features**:
- Fast quality assessment
- Comprehensive article analysis
- Health score calculation
- Issue identification and reporting

#### `comprehensive_check.py` 🆕 **NEW**
**Purpose**: Dedicated comprehensive analysis of ALL articles
**Usage**:
```bash
python utilities/comprehensive_check.py
```
**Features**:
- Analyzes EVERY article for quality issues
- Detailed metrics and health scoring
- Specific recommendations for improvements
- Complete data quality assessment

#### `run_reauthenticator.py`
**Purpose**: Auto-run reauthenticator without user input
**Usage**:
```bash
python utilities/run_reauthenticator.py
```

#### `check_ollama.py`
**Purpose**: Verify Ollama setup and available models
**Usage**:
```bash
python utilities/check_ollama.py
```
**Features**:
- Checks Ollama connection
- Lists available models
- Tests model functionality
- Provides installation guidance

#### `quick_status.py`
**Purpose**: Quick overview of project status
**Usage**:
```bash
python utilities/quick_status.py
```

## 🔄 Complete Workflow Guide

### Phase 1: Data Collection
```bash
# Option A: Collect exactly 200 articles
python scrapers/news_scraper.py

# Option B: Continuous scraping
python scrapers/continuous_news_scraper.py
```

### Phase 2: Enhanced Data Validation ⭐ **ENHANCED**
```bash
# Option A: Quick quality check
python utilities/quick_check_reauthenticator.py
# Choose option 1 for basic statistics

# Option B: Comprehensive analysis of ALL articles
python utilities/quick_check_reauthenticator.py
# Choose option 2 for detailed analysis

# Option C: Dedicated comprehensive check
python utilities/comprehensive_check.py

# Option D: Full validation and fixing
python utilities/reauthenticator.py
# Choose option 3 for complete reauthentication

# Legacy checker (still available)
python checkers/check_new_excel.py
```

**Enhanced Validation Features**:
- ✅ **ALL articles analyzed** - No article is skipped
- ✅ **Multiple quality metrics** - Title-content matching, empty fields, short content
- ✅ **Health scoring** - Overall quality assessment per file
- ✅ **Detailed reporting** - Specific issues identified
- ✅ **Actionable recommendations** - Clear improvement steps

### Phase 3: AI Summarization
```bash
# First, verify Ollama setup
python utilities/check_ollama.py

# Generate summaries
python summarizers/production_summarizer.py
```

### Phase 4: Quality Assurance
```bash
# Check final results
python utilities/quick_status.py

# Verify Excel files
python checkers/verify_excel.py
```

## 📊 Data Structure

### Excel File Columns:
- `Headline of News Article`: Article title
- `Content in detail of News article`: Full article content
- `Enter URL or Link of News`: Source URL
- `Name of Newspaper`: News source name
- `Published date of News`: Publication date (2000-2020)
- `Category`: News category
- `Summary Status`: Summarization status (NOT_SUMMARIZED/SUMMARIZED/FAILED)
- `AI Summary`: Generated summary

## 🔧 Configuration

### `config.py`
Contains news sources and categories:
```python
NEWS_SOURCES = {
    'Technology': {
        'TechCrunch': 'https://techcrunch.com',
        'The Verge': 'https://theverge.com'
    },
    'Business': {
        'Reuters': 'https://reuters.com/business',
        'Bloomberg': 'https://bloomberg.com'
    }
    # ... more sources
}
```

## 📝 Logging

All modules generate detailed logs in the `logs/` directory:
- `continuous_scraper.log`: Continuous scraping logs
- `production_summarizer.log`: Summarization logs
- `reauthenticator.log`: Content validation logs

## 🚨 Troubleshooting

### Common Issues:

1. **Ollama Connection Error**
   ```bash
   # Check if Ollama is running
   python utilities/check_ollama.py
   
   # Start Ollama service
   ollama serve
   ```

2. **Excel File Not Found**
   ```bash
   # Check file existence
   python utilities/quick_status.py
   ```

3. **Content Quality Issues** ⭐ **ENHANCED**
   ```bash
   # Quick quality assessment of ALL articles
   python utilities/quick_check_reauthenticator.py
   # Choose option 2 for comprehensive analysis
   
   # Dedicated comprehensive check
   python utilities/comprehensive_check.py
   
   # Fix identified issues automatically
   python utilities/reauthenticator.py
   # Choose option 3 for full reauthentication
   ```

4. **Summarization Failures**
   ```bash
   # Check Ollama model availability
   ollama list
   
   # Pull required model if missing
   ollama pull gemma3:4b
   ```

## 📈 Performance Metrics

### Typical Processing Times:
- **Scraping**: ~2-3 seconds per article
- **Content Validation**: ~3-5 seconds per mismatched article
- **Summarization**: ~5-10 seconds per article (depends on model)

### Batch Sizes:
- **Scraping**: 5 articles per source
- **Summarization**: 10 articles per batch
- **Validation**: Processes all at once

## 🔒 Best Practices ⭐ **ENHANCED**

1. **Enhanced Quality Assurance Workflow**:
   - Run comprehensive analysis after scraping: `python utilities/comprehensive_check.py`
   - Use enhanced reauthenticator for validation: `python utilities/reauthenticator.py` (option 3)
   - Monitor article health scores and fix issues proactively

2. **Regular Quality Monitoring**:
   - Use `python utilities/quick_check_reauthenticator.py` for routine checks
   - Aim for 95%+ health scores across all files
   - Address empty content and short articles promptly

3. **Pre-Summarization Checks**:
   - Verify Ollama setup: `python utilities/check_ollama.py`
   - Ensure high content quality before AI processing
   - Check progress regularly: `python utilities/check_progress.py`

4. **System Maintenance**:
   - Monitor logs in `logs/` directory for errors and performance issues
   - Run in batches to avoid overwhelming target websites
   - Regular backups of Excel files before major operations

5. **Quality Thresholds**:
   - Maintain 95%+ title-content match rate
   - Keep empty content below 5%
   - Ensure articles have substantial content (>100 characters)

## 📞 Support

For issues or questions:
1. Check the logs in the `logs/` directory
2. Run diagnostic tools in `utilities/`
3. Verify configuration in `config.py`

## 🔍 **ENHANCED QUALITY ASSURANCE COMMANDS** ⭐ **NEW**

### **📊 Article Quality Analysis (ALL Articles)**
```bash
# Quick statistics for all articles
python utilities/quick_check_reauthenticator.py
# Choose option 1

# Comprehensive analysis of ALL articles
python utilities/quick_check_reauthenticator.py  
# Choose option 2

# Dedicated comprehensive check
python utilities/comprehensive_check.py

# Full validation with automatic fixing
python utilities/reauthenticator.py
# Choose option 3
```

### **🎯 Quality Check Results**
The enhanced quality checker analyzes **EVERY article** for:
- ✅ **Title-content matching** (30% word overlap threshold)
- ✅ **Empty titles** detection
- ✅ **Empty content** detection
- ✅ **Short content** detection (<100 characters)
- ✅ **Health scoring** per file and overall
- ✅ **Specific issue identification** with recommendations

### **📈 Sample Output**
```
📊 new_excel.xlsx Summary:
   Total articles: 40
   ❌ Title-content mismatches: 0 (0.0%)
   📝 Empty titles: 0 (0.0%)
   📄 Empty content: 0 (0.0%)
   ⚠️  Short content (<100 chars): 0 (0.0%)
   💚 Health score: 100.0%

💡 RECOMMENDATIONS:
   🎉 All articles are in good condition!
```

## 🎯 Quick Commands Reference

```bash
# Complete workflow with enhanced validation
python scrapers/news_scraper.py && python utilities/reauthenticator.py && python summarizers/production_summarizer.py

# Enhanced quality checks
python utilities/quick_check_reauthenticator.py  # Choose option 2 for comprehensive
python utilities/comprehensive_check.py         # Dedicated comprehensive analysis

# Status checks
python utilities/quick_status.py               # Project overview
python utilities/check_progress.py             # Summarization progress

# System checks
python utilities/check_ollama.py               # AI model verification

# Legacy validation (still available)
python utilities/reauthenticator.py            # Choose option 3 for full fixing
```

## 🎯 **COMPLETE WORKFLOW - FROM SCRAPING TO SUMMARIZATION**

### **🚀 Full Automation Command**
```bash
# Run everything in sequence (recommended)
python scrapers/news_scraper.py && python utilities/reauthenticator.py && python summarizers/production_summarizer.py
```

### **📋 Step-by-Step Manual Process**

#### **Step 1: Environment Setup**
```bash
# 1. Install all dependencies
python setup.py

# 2. Verify Ollama installation
python utilities/check_ollama.py

# 3. Check current project status
python utilities/quick_status.py
```

#### **Step 2: Data Collection**
```bash
# Option A: Collect exactly 200 new articles
python scrapers/news_scraper.py

# Option B: Run continuous scraping (multiple cycles)
python scrapers/continuous_news_scraper.py

# Check what was collected
python checkers/preview_excel.py
```

#### **Step 3: Enhanced Data Validation & Quality Assurance** ⭐ **ENHANCED**
```bash
# 1. Comprehensive analysis of ALL articles (RECOMMENDED)
python utilities/comprehensive_check.py

# 2. Alternative: Quick quality assessment
python utilities/quick_check_reauthenticator.py
# Choose option 2 for detailed analysis

# 3. Fix identified issues automatically (CRITICAL!)
python utilities/reauthenticator.py
# Choose option 3 for full reauthentication

# 4. Verify fixes were applied
python utilities/quick_check_reauthenticator.py
# Choose option 1 for quick verification

# 5. Legacy checker (still available)
python checkers/check_new_excel.py
```

**Enhanced Validation Features**:
- ✅ **ALL articles analyzed** - No article is skipped
- ✅ **Multiple quality metrics** - Beyond just title-content matching
- ✅ **Health scoring** - Overall quality assessment
- ✅ **Specific issue identification** - Know exactly what needs fixing
- ✅ **Actionable recommendations** - Clear improvement steps

#### **Step 4: AI Summarization**
```bash
# 1. Final Ollama check before summarization
python utilities/check_ollama.py

# 2. Generate AI summaries for all articles
python summarizers/production_summarizer.py

# 3. Check summarization progress
python utilities/quick_status.py
```

#### **Step 5: Final Verification**
```bash
# 1. Comprehensive Excel file verification
python checkers/verify_excel.py

# 2. View detailed results
python checkers/view_excel_details.py

# 3. Final status check
python utilities/quick_status.py
```

### **⚡ Quick Commands for Different Scenarios**

#### **🔄 Daily Maintenance**
```bash
# Quick health check
python utilities/quick_status.py

# Check for content issues
python utilities/quick_check_reauthenticator.py

# Verify Ollama is working
python utilities/check_ollama.py
```

#### **🛠️ Troubleshooting**
```bash
# If scraping fails
python checkers/check_new_excel.py

# If content doesn't match titles
python utilities/reauthenticator.py

# If summarization fails
python utilities/check_ollama.py
```

#### **📊 Progress Monitoring**
```bash
# Check overall progress
python utilities/quick_status.py

# View Excel file details
python checkers/view_excel_details.py

# Preview collected articles
python checkers/preview_excel.py
```

### **🎯 Production-Ready Workflow**

For production use, follow this exact sequence:

```bash
# 1. Setup and verification
python setup.py
python utilities/check_ollama.py
python utilities/quick_status.py

# 2. Data collection
python scrapers/news_scraper.py

# 3. Quality assurance (CRITICAL STEP)
python utilities/reauthenticator.py  # Choose option 2

# 4. AI processing
python summarizers/production_summarizer.py

# 5. Final verification
python checkers/verify_excel.py
python utilities/quick_status.py
```

### **📈 Expected Timeline**

- **Setup**: 2-5 minutes
- **Scraping 200 articles**: 10-20 minutes
- **Content validation**: 5-15 minutes (depending on mismatches)
- **AI summarization**: 30-60 minutes (for all articles)
- **Total time**: ~1-2 hours for complete workflow

### **🔍 Quality Checkpoints**

After each major step, verify:

1. **After Scraping**: 
   ```bash
   python checkers/preview_excel.py
   ```

2. **After Validation**: 
   ```bash
   python utilities/quick_check_reauthenticator.py
   ```

3. **After Summarization**: 
   ```bash
   python utilities/quick_status.py
   ```

This comprehensive workflow ensures high-quality data collection, validation, and AI-powered summarization of news articles!