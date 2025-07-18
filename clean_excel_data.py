#!/usr/bin/env python3
"""
Clean Excel data by removing impurities from content column
"""

import pandas as pd
import re
import os
from datetime import datetime

def clean_content_text(content):
    """
    Clean the content text by removing common impurities
    """
    if pd.isna(content) or content == '':
        return content
    
    content = str(content)
    
    # Remove common prefixes and metadata
    patterns_to_remove = [
        r'^By:\s*[A-Z]+\s*',  # Remove "By:PTI", "By:ANI", etc.
        r'^Written by\s*[^|]*\|',  # Remove "Written byAgencies..."
        r'^\s*[A-Za-z\s]+\s*\|\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*',  # Remove location and timestamp
        r'^\s*[A-Za-z\s]+\s*\|\s*Updated:\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*',  # Remove updated timestamp
        r'^\s*[A-Za-z\s]+\s*\|\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s*',  # Remove location and date without timezone
        r'Updated:\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*',  # Remove "Updated:" timestamps anywhere
        r'\d+\s*min\s*read\s*',  # Remove "4 min read"
        r'PRINT\s*',  # Remove "PRINT"
        r'Story continues below this ad\s*',  # Remove ad text
        r'\([^)]*Photo\)\s*',  # Remove "(File Photo)" anywhere
        r'\([^)]*Image\)\s*',  # Remove "(File Image)" anywhere
        r'^\s*[A-Za-z\s]+\s*\|\s*',  # Remove any remaining "Location |" patterns at start
        r'Written by[^|]*\|[^|]*\|',  # Remove "Written by...| location |"
        r'Written by[^|]*\|',  # Remove "Written by...|"
        r'^\s*[A-Z]{2,}\s*',  # Remove agency names like "PTI", "ANI" at start
    ]
    
    # Apply all patterns
    for pattern in patterns_to_remove:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove extra whitespace and newlines at the beginning
    content = content.strip()
    
    # Remove multiple consecutive spaces
    content = re.sub(r'\s+', ' ', content)
    
    # Remove standalone location|date patterns that might be in the middle
    content = re.sub(r'\s*[A-Za-z\s]+\s*\|\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', ' ', content)
    
    # Clean up any remaining artifacts
    content = re.sub(r'^\s*\|\s*', '', content)  # Remove leading pipe
    content = re.sub(r'\s*\|\s*$', '', content)  # Remove trailing pipe
    
    return content.strip()

def clean_excel_data():
    """
    Clean the Excel data and save cleaned version
    """
    excel_path = "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/new_excel.xlsx"
    
    if not os.path.exists(excel_path):
        print("Excel file not found!")
        return
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    
    print(f"Original shape: {df.shape}")
    
    # Target column to clean
    content_col = 'Content in detail of News article'
    
    if content_col not in df.columns:
        print(f"Column '{content_col}' not found!")
        return
    
    print(f"Cleaning content in column: '{content_col}'")
    
    # Show some before examples
    print("\n=== BEFORE CLEANING (First 3 samples) ===")
    for i in range(min(3, len(df))):
        original = str(df[content_col].iloc[i])
        print(f"\nRow {i+1} (first 300 chars):")
        print("-" * 50)
        print(original[:300] + "..." if len(original) > 300 else original)
    
    # Clean the content
    df[content_col] = df[content_col].apply(clean_content_text)
    
    # Show some after examples
    print("\n=== AFTER CLEANING (First 3 samples) ===")
    for i in range(min(3, len(df))):
        cleaned = str(df[content_col].iloc[i])
        print(f"\nRow {i+1} (first 300 chars):")
        print("-" * 50)
        print(cleaned[:300] + "..." if len(cleaned) > 300 else cleaned)
    
    # Save cleaned data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleaned_path = f"c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/cleaned_excel_{timestamp}.xlsx"
    
    print(f"\nSaving cleaned data to: {cleaned_path}")
    df.to_excel(cleaned_path, index=False)
    
    # Also update the original file (backup first)
    backup_path = f"c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/new_excel_backup_{timestamp}.xlsx"
    print(f"Creating backup at: {backup_path}")
    
    # Copy original to backup
    import shutil
    shutil.copy2(excel_path, backup_path)
    
    # Update original
    print(f"Updating original file: {excel_path}")
    df.to_excel(excel_path, index=False)
    
    print("\n✅ Data cleaning completed!")
    print(f"- Original file backed up to: {backup_path}")
    print(f"- Cleaned file saved to: {cleaned_path}")
    print(f"- Original file updated with cleaned data")

if __name__ == "__main__":
    clean_excel_data()