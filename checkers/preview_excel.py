#!/usr/bin/env python3
"""
Excel File Preview - Shows detailed content of the Excel file
"""

import os
import pandas as pd
import glob

def preview_excel_file():
    """Show detailed preview of the Excel file"""
    
    # Find all Excel files
    excel_files = glob.glob(r'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/News_Articles_*.xlsx')
    
    if not excel_files:
        print("❌ No Excel files found!")
        return
    
    # Get the latest file
    latest_file = max(excel_files, key=os.path.getctime)
    
    print(f"📁 Excel File: {os.path.basename(latest_file)}")
    print(f"📍 Location: {latest_file}")
    print("=" * 80)
    
    try:
        df = pd.read_excel(latest_file)
        
        print(f"📊 SUMMARY:")
        print(f"   Total Articles: {len(df)}")
        print(f"   Total Columns: {len(df.columns)}")
        print(f"   File Size: {os.path.getsize(latest_file)} bytes")
        
        print(f"\n📋 COLUMN STRUCTURE:")
        for i, col in enumerate(df.columns, 1):
            filled_count = df[col].notna().sum()
            empty_count = df[col].isna().sum()
            print(f"   {i}. {col}")
            print(f"      - Filled: {filled_count}, Empty: {empty_count}")
        
        print(f"\n📰 NEWSPAPERS:")
        if 'Name of Newspaper' in df.columns:
            newspaper_counts = df['Name of Newspaper'].value_counts()
            for newspaper, count in newspaper_counts.items():
                print(f"   • {newspaper}: {count} articles")
        
        print(f"\n📂 CATEGORIES:")
        if 'Category' in df.columns:
            category_counts = df['Category'].value_counts()
            for category, count in category_counts.items():
                print(f"   • {category}: {count} articles")
        
        print(f"\n📋 DETAILED ARTICLE PREVIEW (First 5 articles):")
        print("=" * 80)
        
        for i, row in df.head(5).iterrows():
            print(f"\n🔸 ARTICLE {i+1}:")
            print(f"   Newspaper: {row['Name of Newspaper']}")
            print(f"   Date: {row['Published date of News']}")
            print(f"   Category: {row['Category']}")
            print(f"   Headline: {row['Headline of News Article']}")
            print(f"   URL: {row['Enter URL or Link of News']}")
            print(f"   Content Preview: {str(row['Content in detail of News article'])[:200]}...")
            print(f"   Summary: {row['Human Summary For Article News'] if row['Human Summary For Article News'] else 'Not available'}")
            print(f"   Summary Status: {row['Summary Status']}")
            print("-" * 60)
        
        # Show data types
        print(f"\n📊 DATA TYPES:")
        for col in df.columns:
            print(f"   {col}: {df[col].dtype}")
        
        # Check for duplicates
        url_duplicates = df['Enter URL or Link of News'].duplicated().sum()
        headline_duplicates = df['Headline of News Article'].duplicated().sum()
        
        print(f"\n🔍 DUPLICATE CHECK:")
        print(f"   URL duplicates: {url_duplicates}")
        print(f"   Headline duplicates: {headline_duplicates}")
        
        print("=" * 80)
        print("✅ Excel file preview completed!")
        
        # Show file path for easy access
        print(f"\n📁 You can open this file at:")
        print(f"   {latest_file}")
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    preview_excel_file()