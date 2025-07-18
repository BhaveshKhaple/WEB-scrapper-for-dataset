#!/usr/bin/env python3
"""
Examine the Excel data to understand impurities
"""

import pandas as pd
import os

def examine_excel_data():
    excel_path = "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/new_excel.xlsx"
    
    if not os.path.exists(excel_path):
        print("Excel file not found, checking other files...")
        # Check other Excel files
        excel_files = [
            "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/continuous_news.xlsx",
            "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/Final_Indian_News_Archive_20250718_032134.xlsx",
            "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/Final_Indian_News_Archive_20250718_032134_raw_data.xlsx"
        ]
        
        for file_path in excel_files:
            if os.path.exists(file_path):
                excel_path = file_path
                print(f"Using file: {file_path}")
                break
    
    try:
        df = pd.read_excel(excel_path)
        print(f"Excel file loaded: {excel_path}")
        print(f"Shape: {df.shape}")
        print(f"Columns: {df.columns.tolist()}")
        
        # Look for content column
        content_col = None
        for col in df.columns:
            if 'content' in col.lower() or 'detail' in col.lower() or 'news' in col.lower():
                content_col = col
                break
        
        # Check the specific content column mentioned by user
        target_col = 'Content in detail of News article'
        if target_col in df.columns:
            print(f"\nFound target column: '{target_col}'")
            print("\nFirst few content samples:")
            for i in range(min(3, len(df))):
                print(f"\nRow {i+1}:")
                print("-" * 50)
                content_str = str(df[target_col].iloc[i])
                if len(content_str) > 800:
                    print(content_str[:800] + "...")
                else:
                    print(content_str)
        else:
            print(f"\nTarget column '{target_col}' not found.")
            print("\nAvailable columns:")
            for col in df.columns:
                print(f"- {col}")
                
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    examine_excel_data()