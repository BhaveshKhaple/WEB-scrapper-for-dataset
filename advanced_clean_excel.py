#!/usr/bin/env python3
"""
Advanced Excel data cleaning with comprehensive pattern matching
"""

import pandas as pd
import re
import os
from datetime import datetime

def advanced_clean_content(content):
    """
    Advanced cleaning function with comprehensive pattern matching
    """
    if pd.isna(content) or content == '':
        return content
    
    content = str(content)
    original_content = content
    
    # Step 1: Remove bylines and agency names
    content = re.sub(r'^By:\s*[A-Z]+\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^Written by[^|]*\|', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^[A-Z]{2,4}\s*\|', '', content)  # Remove "PTI |", "ANI |", etc.
    
    # Step 2: Remove location and timestamp patterns
    # Pattern: "Location |Date Time IST"
    content = re.sub(r'^[A-Za-z\s,]+\s*\|\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content)
    # Pattern: "Location |Updated: Date Time IST"
    content = re.sub(r'^[A-Za-z\s,]+\s*\|\s*Updated:\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content)
    # Pattern: Just "Updated: Date Time IST"
    content = re.sub(r'^Updated:\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content)
    
    # Step 3: Remove reading time and print indicators
    content = re.sub(r'\d+\s*min\s*read\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'PRINT\s*', '', content, flags=re.IGNORECASE)
    
    # Step 4: Remove photo/image references
    content = re.sub(r'\([^)]*Photo\)\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\([^)]*Image\)\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\(File\s+[^)]*\)\s*', '', content, flags=re.IGNORECASE)
    
    # Step 5: Remove advertisement text
    content = re.sub(r'Story continues below this ad\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Advertisement\s*', '', content, flags=re.IGNORECASE)
    
    # Step 6: Clean up any remaining location|date patterns in the middle
    content = re.sub(r'\s*[A-Za-z\s,]+\s*\|\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', ' ', content)
    
    # Step 7: Remove standalone agency names that might be left
    content = re.sub(r'^\s*[A-Z]{2,4}\s+', '', content)
    
    # Step 8: Clean up formatting
    content = re.sub(r'^\s*\|\s*', '', content)  # Remove leading pipes
    content = re.sub(r'\s*\|\s*$', '', content)  # Remove trailing pipes
    content = re.sub(r'\s+', ' ', content)  # Multiple spaces to single space
    content = content.strip()
    
    # Step 9: If content became too short or empty, return original
    if len(content) < 50 and len(original_content) > 100:
        print(f"Warning: Content became too short, keeping original")
        return original_content
    
    return content

def test_cleaning_patterns():
    """
    Test the cleaning patterns on sample data
    """
    test_cases = [
        "By:PTINew Delhi |January 2, 2020 22:27 IST4 min readPRINT\"If you see Pakistan's statement...",
        "By:PTIChennai |Updated: January 2, 2020  22:27 IST3 min readPRINTKoneru Humpy (File Photo)India's newest world champion...",
        "Written byAgenciesPanaji |July 8, 2010 19:07 IST2 min readPRINTSome news content here...",
        "Prime Minister announced a 21-day nationwide lockdown to combat the spread of COVID-19..."
    ]
    
    print("=== TESTING CLEANING PATTERNS ===")
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("BEFORE:", test_case[:100] + "...")
        cleaned = advanced_clean_content(test_case)
        print("AFTER: ", cleaned[:100] + "...")
        print("-" * 80)

def clean_excel_advanced():
    """
    Clean Excel data with advanced patterns
    """
    # Use the backup file to avoid overwriting cleaned data
    backup_files = [f for f in os.listdir("c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/") if f.startswith("new_excel_backup_")]
    
    if backup_files:
        backup_file = sorted(backup_files)[-1]  # Get the latest backup
        excel_path = f"c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/{backup_file}"
        print(f"Using backup file: {excel_path}")
    else:
        excel_path = "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/new_excel.xlsx"
        print(f"Using original file: {excel_path}")
    
    if not os.path.exists(excel_path):
        print("Excel file not found!")
        return
    
    print(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    
    print(f"Shape: {df.shape}")
    
    content_col = 'Content in detail of News article'
    
    if content_col not in df.columns:
        print(f"Column '{content_col}' not found!")
        return
    
    print(f"Cleaning content in column: '{content_col}'")
    
    # Test patterns first
    test_cleaning_patterns()
    
    # Show some before examples
    print("\n=== BEFORE ADVANCED CLEANING (First 3 samples) ===")
    for i in range(min(3, len(df))):
        original = str(df[content_col].iloc[i])
        print(f"\nRow {i+1}:")
        print("-" * 50)
        print(original[:400] + "..." if len(original) > 400 else original)
    
    # Clean the content
    df[content_col] = df[content_col].apply(advanced_clean_content)
    
    # Show some after examples
    print("\n=== AFTER ADVANCED CLEANING (First 3 samples) ===")
    for i in range(min(3, len(df))):
        cleaned = str(df[content_col].iloc[i])
        print(f"\nRow {i+1}:")
        print("-" * 50)
        print(cleaned[:400] + "..." if len(cleaned) > 400 else cleaned)
    
    # Save cleaned data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleaned_path = f"c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/advanced_cleaned_excel_{timestamp}.xlsx"
    
    print(f"\nSaving advanced cleaned data to: {cleaned_path}")
    df.to_excel(cleaned_path, index=False)
    
    # Update the main file
    main_path = "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/new_excel.xlsx"
    print(f"Updating main file: {main_path}")
    df.to_excel(main_path, index=False)
    
    print("\n✅ Advanced data cleaning completed!")
    print(f"- Advanced cleaned file saved to: {cleaned_path}")
    print(f"- Main file updated with advanced cleaned data")

if __name__ == "__main__":
    clean_excel_advanced()