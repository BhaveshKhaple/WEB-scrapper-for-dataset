# Indian News Scraper

A Python-based web scraper for collecting Indian news articles from major newspapers and storing them in both Excel and SQLite database formats.

## Features

- 🗞️ **Multi-source scraping**: Indian Express and The Hindu archives
- 📊 **Dual output**: Excel files and SQLite database
- 🧹 **Clean data**: Automatically removes metadata, timestamps, and formatting artifacts
- 📅 **Date range support**: Scrape articles from specific date ranges
- 🔄 **Duplicate prevention**: Avoids storing duplicate articles
- ⚡ **Progress tracking**: Real-time progress updates during scraping

## Quick Start

```bash
# Install dependencies
pip install -r config/requirements.txt

# Run the scraper
python run_scraper.py
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd scrapper
   ```

2. **Install dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Run the scraper**
   ```bash
   python run_scraper.py
   ```

## Usage

### Basic Usage

```bash
python run_scraper.py
```

The scraper will prompt you for:
- **Start year** (e.g., 2010)
- **End year** (e.g., 2020)
- **Maximum articles** to scrape (e.g., 1000)

### Example Session

```
=== INDIAN NEWS SCRAPER ===
Enter start year (e.g., 2010): 2015
Enter end year (e.g., 2020): 2016
Enter maximum articles to scrape (e.g., 1000): 500

Starting scraper...
✅ Scraping completed!
📊 Total articles scraped: 500
📁 Excel file: data/excel_files/new_excel.xlsx
🗄️ Database: data/database/final_scraper.db
```

### Testing the Scraper

```bash
python quick_test.py
```

This runs a quick test to verify the scraper is working correctly.

## Project Structure

```
scrapper/
├── config/
│   ├── requirements.txt      # Python dependencies
│   └── scraper_config.py     # Configuration settings
├── data/
│   ├── database/
│   │   ├── .gitkeep
│   │   └── final_scraper.db  # SQLite database (created after first run)
│   └── excel_files/
│       ├── .gitkeep
│       └── new_excel.xlsx    # Main Excel output (created after first run)
├── scripts/
│   └── scrapers/
│       └── fixed_scraper_with_correct_urls.py  # Main scraper logic
├── .gitignore
├── README.md
├── run_scraper.py           # Main entry point
└── quick_test.py           # Test script
```

## Output Format

### Excel File (`data/excel_files/new_excel.xlsx`)

The Excel file contains the following columns:

| Column | Description |
|--------|-------------|
| Name of Newspaper | Source newspaper (Indian Express, The Hindu) |
| Published date of News | Publication date |
| Enter URL or Link of News | Original article URL |
| Headline of News Article | Article headline |
| Content in detail of News article | **Clean article content** (metadata removed) |
| Summary of News article | Brief summary |
| Category of News Article | News category |
| Location of News | Location mentioned in article |
| Author of News Article | Article author |
| Front Page Assessment | Assessment of article importance |

### SQLite Database (`data/database/final_scraper.db`)

The database contains an `articles` table with detailed metadata including:
- Content hash for duplicate detection
- Verification status
- Word count
- Scraping timestamp
- Processing time

## Data Cleaning

The scraper automatically cleans article content by removing:

- ✅ **Bylines**: "By:PTI", "By:ANI", "Written by..."
- ✅ **Timestamps**: "New Delhi |January 2, 2020 22:27 IST"
- ✅ **Reading indicators**: "4 min read", "PRINT"
- ✅ **Photo references**: "(File Photo)", "(Representative Image)"
- ✅ **Advertisement text**: "Story continues below this ad"
- ✅ **Location prefixes**: "Mumbai |", "New Delhi |"

### Before vs After Cleaning

**Before:**
```
By:PTINew Delhi |January 2, 2020 22:27 IST4 min readPRINT"If you see Pakistan's statement...
```

**After:**
```
"If you see Pakistan's statement, it has said that it is envisaged...
```

## Configuration

Edit `config/scraper_config.py` to modify:
- Database paths
- Excel file paths
- Scraping parameters
- Request delays

## Troubleshooting

### Common Issues

1. **Import Error**
   ```bash
   # Make sure you're in the project directory
   cd scrapper
   python run_scraper.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r config/requirements.txt
   ```

3. **Permission Error**
   - Close Excel file if it's open
   - Run with administrator privileges if needed

4. **Network Issues**
   - Check internet connection
   - The scraper includes retry logic for failed requests

### Checking Status

- **Excel file**: Open `data/excel_files/new_excel.xlsx`
- **Database**: Use SQLite browser or run queries on `data/database/final_scraper.db`
- **Test run**: Execute `python quick_test.py`

## Requirements

- Python 3.7+
- Internet connection
- Dependencies listed in `config/requirements.txt`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and research purposes. Please respect the terms of service of the websites being scraped.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run `python quick_test.py` to verify setup
3. Check that all dependencies are installed


#created by @bhaveshkhaple