# Indian News Scraper

## Quick Start
```bash
python run_scraper.py
```

## Project Structure
- data/excel_files/ - Excel output files
- data/database/ - SQLite database  
- scripts/scrapers/ - Main scraper code
- scripts/utilities/ - Helper scripts
- docs/ - Documentation

## Output
- Main file: data/excel_files/new_excel.xlsx
- Database: data/database/final_scraper.db

## Status
- Working: Indian Express scraper
- Issue: The Hindu archives need fixing

## Usage
1. Run: python run_scraper.py
2. Enter date range and max articles
3. Check output in data/excel_files/new_excel.xlsx
