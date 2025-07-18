#!/usr/bin/env python3
"""
Check Project Status
"""

import os
import pandas as pd

def check_project_status():
    print("PROJECT STATUS CHECK")
    print("="*40)
    
    # Check directory structure
    print("Directory Structure:")
    dirs = ["data", "data/excel_files", "data/database", "scripts", "scripts/scrapers", "scripts/utilities", "docs"]
    for directory in dirs:
        status = "✓" if os.path.exists(directory) else "✗"
        print(f"  {status} {directory}/")
    
    # Check essential files
    print("\nEssential Files:")
    files = [
        "run_scraper.py",
        "README.md", 
        "scripts/scrapers/fixed_scraper_with_correct_urls.py",
        "data/excel_files/new_excel.xlsx",
        "data/database/final_scraper.db"
    ]
    
    for file in files:
        status = "✓" if os.path.exists(file) else "✗"
        size = ""
        if os.path.exists(file):
            size = f" ({os.path.getsize(file)/1024:.1f} KB)"
        print(f"  {status} {file}{size}")
    
    # Check Excel file content if it exists
    excel_path = "data/excel_files/new_excel.xlsx"
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path)
            print(f"\nExcel File Content:")
            print(f"  Articles: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            if len(df) > 0:
                print(f"  Date range: {df['Published date of News'].min()} to {df['Published date of News'].max()}")
                newspapers = df['Name of Newspaper'].unique()
                print(f"  Newspapers: {', '.join(newspapers)}")
        except Exception as e:
            print(f"\nExcel file exists but couldn't read: {e}")
    
    print(f"\nProject Status:")
    if os.path.exists("run_scraper.py") and os.path.exists("scripts/scrapers/fixed_scraper_with_correct_urls.py"):
        print("  ✓ Ready to use")
        print("  Run: python run_scraper.py")
    else:
        print("  ✗ Missing essential files")
    
    print("="*40)

if __name__ == "__main__":
    check_project_status()