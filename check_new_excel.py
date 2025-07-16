#!/usr/bin/env python3
"""
Check the new_excel.xlsx file and verify title-content matching
"""

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

def check_title_content_match(title, content):
    """Check if title and content are related"""
    if not title or not content:
        return False
    
    # Simple check - see if key words from title appear in content
    title_words = set(title.lower().split())
    content_words = set(content.lower().split())
    
    # Remove common words
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
    
    title_words = title_words - common_words
    content_words = content_words - common_words
    
    if len(title_words) == 0:
        return True  # Can't determine, assume match
    
    # Check if at least 30% of title words appear in content
    matching_words = title_words.intersection(content_words)
    match_ratio = len(matching_words) / len(title_words)
    
    return match_ratio >= 0.3

def extract_full_content(url):
    """Extract full content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
            element.decompose()
        
        # Try different content selectors
        content_selectors = [
            'div[class*="story"]',
            'div[class*="article"]',
            'div[class*="content"]',
            'div[class*="body"]',
            'article',
            'main',
            '.story-content',
            '.article-content',
            '.post-content'
        ]
        
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 200:  # Only consider substantial content
                        content += text + " "
                        break
                if content:
                    break
        
        # Fallback to all paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            content = " ".join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
        
        return content.strip()[:2000]  # Limit to 2000 characters
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def check_new_excel():
    """Check the new_excel.xlsx file and verify content"""
    
    excel_file = r'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/new_excel.xlsx'
    
    if not os.path.exists(excel_file):
        print("❌ new_excel.xlsx file not found!")
        return
    
    print(f"📁 Checking: new_excel.xlsx")
    print("=" * 70)
    
    try:
        df = pd.read_excel(excel_file)
        
        print(f"📊 SUMMARY:")
        print(f"   Total Articles: {len(df)}")
        print(f"   File Size: {os.path.getsize(excel_file)} bytes")
        
        # Check date range
        if 'Published date of News' in df.columns:
            dates = pd.to_datetime(df['Published date of News'])
            min_date = dates.min()
            max_date = dates.max()
            
            print(f"\n📅 DATE ANALYSIS:")
            print(f"   Date Range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
            print(f"   Years: {min_date.year} - {max_date.year}")
            
            # Check if all dates are in 2000-2020 range
            years = dates.dt.year
            valid_years = years.between(2000, 2020)
            valid_count = valid_years.sum()
            invalid_count = len(years) - valid_count
            
            print(f"   Valid dates (2000-2020): {valid_count}")
            print(f"   Invalid dates: {invalid_count}")
            
            if invalid_count == 0:
                print("   ✅ All dates are within 2000-2020 range!")
            else:
                print("   ❌ Some dates are outside 2000-2020 range!")
        
        # Check title-content matching
        print(f"\n🔍 TITLE-CONTENT MATCHING ANALYSIS:")
        print("-" * 50)
        
        mismatched_articles = []
        
        for i, row in df.iterrows():
            title = row['Headline of News Article']
            content = row['Content in detail of News article']
            url = row['Enter URL or Link of News']
            
            if not check_title_content_match(title, content):
                mismatched_articles.append({
                    'index': i,
                    'title': title,
                    'content': content[:100] + "...",
                    'url': url
                })
        
        print(f"   Total articles checked: {len(df)}")
        print(f"   Mismatched articles: {len(mismatched_articles)}")
        print(f"   Match rate: {((len(df) - len(mismatched_articles)) / len(df) * 100):.1f}%")
        
        if mismatched_articles:
            print(f"\n❌ MISMATCHED ARTICLES (showing first 5):")
            for i, article in enumerate(mismatched_articles[:5]):
                print(f"\n{i+1}. Row {article['index'] + 1}:")
                print(f"   Title: {article['title'][:60]}...")
                print(f"   Content: {article['content']}")
                print(f"   URL: {article['url'][:60]}...")
                
                # Try to extract better content
                print("   🔄 Attempting to extract better content...")
                better_content = extract_full_content(article['url'])
                if better_content:
                    print(f"   ✅ New content: {better_content[:150]}...")
                    # Update the dataframe
                    df.at[article['index'], 'Content in detail of News article'] = better_content
                else:
                    print("   ❌ Could not extract better content")
                
                time.sleep(1)  # Be respectful to servers
        
        # Save updated dataframe if we made improvements
        if mismatched_articles:
            print(f"\n💾 Saving updated content to Excel...")
            df.to_excel(excel_file, index=False)
            print("   ✅ Excel file updated with improved content!")
        
        # Show sample articles with dates
        print(f"\n📋 SAMPLE ARTICLES WITH DATES:")
        print("-" * 70)
        for i, row in df.head(5).iterrows():
            print(f"{i+1}. [{row['Published date of News']}] {row['Headline of News Article'][:50]}...")
            print(f"   Source: {row['Name of Newspaper']} | Category: {row['Category']}")
            print(f"   Content: {str(row['Content in detail of News article'])[:100]}...")
            print()
        
        print("=" * 70)
        print("✅ Excel file check and content verification completed!")
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_new_excel()