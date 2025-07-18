#!/usr/bin/env python3
"""
Quick Excel File Checker
"""

import os
import pandas as pd
import glob

def check_latest_excel():
    """Check the latest Excel file"""
    
    # Find all Excel files
    excel_files = glob.glob(r'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/News_Articles_*.xlsx')
    
    if not excel_files:
        print("No Excel files found!")
        return
    
    # Get the latest file
    latest_file = max(excel_files, key=os.path.getctime)
    
    print(f"Checking: {os.path.basename(latest_file)}")
    print("=" * 50)
    
    try:
        df = pd.read_excel(latest_file)
        
        print(f"Total articles: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        
        # Check required columns
        required_columns = [
            'Name of Newspaper',
            'Published date of News', 
            'Enter URL or Link of News',
            'Headline of News Article',
            'Content in detail of News article',
            'Human Summary For Article News',
            'Category',
            'Summary Status'
        ]
        
        print("\nColumns check:")
        for col in required_columns:
            if col in df.columns:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} - MISSING")
        
        # Data summary
        if 'Name of Newspaper' in df.columns:
            print(f"\nNewspapers: {df['Name of Newspaper'].nunique()}")
            newspaper_counts = df['Name of Newspaper'].value_counts()
            for newspaper, count in newspaper_counts.items():
                print(f"  {newspaper}: {count}")
        
        if 'Category' in df.columns:
            print(f"\nCategories: {df['Category'].nunique()}")
            category_counts = df['Category'].value_counts()
            for category, count in category_counts.items():
                print(f"  {category}: {count}")
        
        # Sample articles
        print(f"\nSample articles:")
        for i, row in df.head(3).iterrows():
            print(f"{i+1}. {row['Headline of News Article'][:60]}...")
            print(f"   Source: {row['Name of Newspaper']}")
            print(f"   Category: {row['Category']}")
        
        print("=" * 50)
        print("✓ Excel file check completed!")
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    check_latest_excel()