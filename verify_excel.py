#!/usr/bin/env python3
"""
Simple Excel Verification Script
Checks if the Excel file has all required columns and data
"""

import os
import pandas as pd
from datetime import datetime

def verify_excel_file():
    """Verify the Excel file structure and content"""
    
    excel_file = r'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/News_Articles_Collection.xlsx'
    
    # Required columns (exact names as specified)
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
    
    print("🔍 Excel File Verification")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists(excel_file):
        print("❌ Excel file not found!")
        return False
    
    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        print(f"✅ Excel file found")
        print(f"📊 Total rows: {len(df)}")
        print(f"📋 Total columns: {len(df.columns)}")
        
        # Check columns
        print("\n📂 Column Check:")
        missing_columns = []
        for col in required_columns:
            if col in df.columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} - MISSING")
                missing_columns.append(col)
        
        if missing_columns:
            print(f"\n❌ Missing columns: {missing_columns}")
            return False
        
        # Data quality check
        print(f"\n📊 Data Quality:")
        for col in required_columns:
            filled_count = df[col].notna().sum()
            empty_count = df[col].isna().sum()
            print(f"  {col}: {filled_count} filled, {empty_count} empty")
        
        # Check for duplicates
        url_duplicates = df['Enter URL or Link of News'].duplicated().sum()
        headline_duplicates = df['Headline of News Article'].duplicated().sum()
        
        print(f"\n🔍 Duplicate Check:")
        print(f"  URL duplicates: {url_duplicates}")
        print(f"  Headline duplicates: {headline_duplicates}")
        
        # Summary by newspaper
        print(f"\n📰 Articles by Newspaper:")
        newspaper_counts = df['Name of Newspaper'].value_counts()
        for newspaper, count in newspaper_counts.items():
            print(f"  {newspaper}: {count} articles")
        
        # Summary by category
        print(f"\n📂 Articles by Category:")
        category_counts = df['Category'].value_counts()
        for category, count in category_counts.items():
            print(f"  {category}: {count} articles")
        
        # Show sample articles
        print(f"\n📋 Sample Articles (First 3):")
        for i, row in df.head(3).iterrows():
            print(f"\n{i+1}. {row['Headline of News Article'][:60]}...")
            print(f"   Source: {row['Name of Newspaper']}")
            print(f"   Category: {row['Category']}")
            print(f"   URL: {row['Enter URL or Link of News'][:50]}...")
        
        print("\n" + "=" * 50)
        print("✅ Excel file verification completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return False

if __name__ == "__main__":
    verify_excel_file()