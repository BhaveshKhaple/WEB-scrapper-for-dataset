#!/usr/bin/env python3
"""
Final comprehensive Excel data cleaning
"""

import pandas as pd
import re
import os
from datetime import datetime

def final_clean_content(content):
    """
    Final comprehensive cleaning function
    """
    if pd.isna(content) or content == '':
        return content
    
    content = str(content)
    original_content = content
    
    # Step 1: Remove all bylines and agency prefixes
    content = re.sub(r'^By:\s*[A-Z]+\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^Written by[^|]*\|', '', content, flags=re.IGNORECASE)
    content = re.sub(r'^[A-Z]{2,4}\s*\|', '', content)  # Remove "PTI |", "ANI |", etc.
    content = re.sub(r'^[A-Z]{2,4}\s+', '', content)  # Remove standalone "PTI ", "ANI ", etc.
    
    # Step 2: Remove all timestamp patterns (more comprehensive)
    # Pattern: "Location |Date Time IST/GMT/UTC"
    content = re.sub(r'^[A-Za-z\s,.-]+\s*\|\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content)
    # Pattern: "Location |Updated: Date Time IST/GMT/UTC"
    content = re.sub(r'^[A-Za-z\s,.-]+\s*\|\s*Updated:\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content)
    # Pattern: Just "Updated: Date Time IST/GMT/UTC" anywhere
    content = re.sub(r'Updated:\s*[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content, flags=re.IGNORECASE)
    # Pattern: Standalone date-time patterns
    content = re.sub(r'^[A-Za-z]+ \d{1,2}, \d{4}\s+\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content)
    
    # Step 3: Remove reading time and print indicators
    content = re.sub(r'\d+\s*min\s*read\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'PRINT\s*', '', content, flags=re.IGNORECASE)
    
    # Step 4: Remove all photo/image references
    content = re.sub(r'\([^)]*Photo[^)]*\)\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\([^)]*Image[^)]*\)\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\(File[^)]*\)\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'\(Representative[^)]*\)\s*', '', content, flags=re.IGNORECASE)
    
    # Step 5: Remove advertisement and social media text
    content = re.sub(r'Story continues below this ad\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Advertisement\s*', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Follow us on[^.]*\.', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Subscribe to[^.]*\.', '', content, flags=re.IGNORECASE)
    
    # Step 6: Remove any remaining location|date patterns
    content = re.sub(r'\s*[A-Za-z\s,.-]+\s*\|\s*[A-Za-z]+ \d{1,2}, \d{4}[^.]*', ' ', content)
    
    # Step 7: Clean up formatting artifacts
    content = re.sub(r'^\s*\|\s*', '', content)  # Remove leading pipes
    content = re.sub(r'\s*\|\s*$', '', content)  # Remove trailing pipes
    content = re.sub(r'\s*\|\s*', ' ', content)  # Replace remaining pipes with spaces
    content = re.sub(r'\s+', ' ', content)  # Multiple spaces to single space
    content = re.sub(r'^\s*[.,:;-]+\s*', '', content)  # Remove leading punctuation
    content = content.strip()
    
    # Step 8: Remove any remaining standalone timestamps at the beginning
    content = re.sub(r'^[A-Za-z]+ \d{1,2}, \d{4}\s*', '', content)
    content = re.sub(r'^\d{1,2}:\d{2}\s+(IST|GMT|UTC)\s*', '', content)
    
    # Step 9: Final cleanup
    content = content.strip()
    
    # Step 10: Quality check - if content became too short, return original
    if len(content) < 30 and len(original_content) > 100:
        print(f"Warning: Content became too short ({len(content)} chars), keeping original")
        return original_content.strip()
    
    return content

def final_clean_excel():
    """
    Final comprehensive cleaning of Excel data
    """
    excel_path = "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/new_excel.xlsx"
    
    if not os.path.exists(excel_path):
        print("Excel file not found!")
        return
    
    print(f"Loading Excel file for final cleaning: {excel_path}")
    df = pd.read_excel(excel_path)
    
    print(f"Shape: {df.shape}")
    
    content_col = 'Content in detail of News article'
    
    if content_col not in df.columns:
        print(f"Column '{content_col}' not found!")
        return
    
    print(f"Performing final cleaning on column: '{content_col}'")
    
    # Show some before examples
    print("\n=== BEFORE FINAL CLEANING (First 5 samples) ===")
    for i in range(min(5, len(df))):
        original = str(df[content_col].iloc[i])
        print(f"\nRow {i+1}:")
        print("-" * 50)
        print(original[:300] + "..." if len(original) > 300 else original)
    
    # Apply final cleaning
    df[content_col] = df[content_col].apply(final_clean_content)
    
    # Show some after examples
    print("\n=== AFTER FINAL CLEANING (First 5 samples) ===")
    for i in range(min(5, len(df))):
        cleaned = str(df[content_col].iloc[i])
        print(f"\nRow {i+1}:")
        print("-" * 50)
        print(cleaned[:300] + "..." if len(cleaned) > 300 else cleaned)
    
    # Save final cleaned data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create backup of current state
    backup_path = f"c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/pre_final_clean_backup_{timestamp}.xlsx"
    df_backup = pd.read_excel(excel_path)
    df_backup.to_excel(backup_path, index=False)
    
    # Save final cleaned version
    final_cleaned_path = f"c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/final_cleaned_excel_{timestamp}.xlsx"
    df.to_excel(final_cleaned_path, index=False)
    
    # Update main file
    df.to_excel(excel_path, index=False)
    
    print(f"\n✅ FINAL DATA CLEANING COMPLETED!")
    print(f"- Pre-final backup saved to: {backup_path}")
    print(f"- Final cleaned file saved to: {final_cleaned_path}")
    print(f"- Main file updated with final cleaned data")
    
    # Show statistics
    total_rows = len(df)
    non_empty_content = df[content_col].notna().sum()
    avg_content_length = df[content_col].str.len().mean()
    
    print(f"\n📊 CLEANING STATISTICS:")
    print(f"- Total rows: {total_rows}")
    print(f"- Rows with content: {non_empty_content}")
    print(f"- Average content length: {avg_content_length:.1f} characters")

if __name__ == "__main__":
    final_clean_excel()