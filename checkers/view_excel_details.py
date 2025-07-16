#!/usr/bin/env python3
"""
Detailed view of the Excel file contents
"""

import pandas as pd
import os

def view_excel_details():
    """Show detailed Excel file contents"""
    
    excel_file = r'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/new_excel.xlsx'
    
    if not os.path.exists(excel_file):
        print("❌ Excel file not found!")
        return
    
    print("📊 DETAILED EXCEL FILE VIEW")
    print("=" * 80)
    
    try:
        df = pd.read_excel(excel_file)
        
        print(f"📁 File: new_excel.xlsx")
        print(f"📊 Total Articles: {len(df)}")
        print(f"💾 File Size: {os.path.getsize(excel_file)} bytes")
        
        # Show column structure
        print(f"\n📋 COLUMN STRUCTURE:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i}. {col}")
        
        # Show newspaper distribution
        if 'Name of Newspaper' in df.columns:
            print(f"\n📰 NEWSPAPER DISTRIBUTION:")
            newspaper_counts = df['Name of Newspaper'].value_counts()
            for newspaper, count in newspaper_counts.items():
                print(f"   • {newspaper}: {count} articles")
        
        # Show date range
        if 'Published date of News' in df.columns:
            dates = pd.to_datetime(df['Published date of News'])
            print(f"\n📅 DATE RANGE:")
            print(f"   From: {dates.min().strftime('%Y-%m-%d')}")
            print(f"   To: {dates.max().strftime('%Y-%m-%d')}")
            print(f"   Span: {dates.max().year - dates.min().year + 1} years")
        
        # Show categories
        if 'Category' in df.columns:
            print(f"\n📂 CATEGORIES:")
            category_counts = df['Category'].value_counts()
            for category, count in category_counts.items():
                print(f"   • {category}: {count} articles")
        
        # Show detailed sample articles
        print(f"\n📋 DETAILED SAMPLE ARTICLES:")
        print("=" * 80)
        
        for i, row in df.head(10).iterrows():
            print(f"\n🔸 ARTICLE {i+1}:")
            print(f"   📰 Newspaper: {row['Name of Newspaper']}")
            print(f"   📅 Date: {row['Published date of News']}")
            print(f"   📂 Category: {row['Category']}")
            print(f"   📰 Headline: {row['Headline of News Article']}")
            print(f"   🔗 URL: {row['Enter URL or Link of News'][:60]}...")
            print(f"   📝 Content Preview: {str(row['Content in detail of News article'])[:150]}...")
            print(f"   📊 Summary Status: {row['Summary Status']}")
            print("-" * 60)
        
        # Show content quality metrics
        print(f"\n📊 CONTENT QUALITY METRICS:")
        headline_lengths = df['Headline of News Article'].str.len()
        content_lengths = df['Content in detail of News article'].str.len()
        
        print(f"   📰 Headlines:")
        print(f"      Average length: {headline_lengths.mean():.1f} characters")
        print(f"      Min length: {headline_lengths.min()} characters")
        print(f"      Max length: {headline_lengths.max()} characters")
        
        print(f"   📝 Content:")
        print(f"      Average length: {content_lengths.mean():.1f} characters")
        print(f"      Min length: {content_lengths.min()} characters")
        print(f"      Max length: {content_lengths.max()} characters")
        
        print("=" * 80)
        print("✅ Excel file analysis completed!")
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    view_excel_details()