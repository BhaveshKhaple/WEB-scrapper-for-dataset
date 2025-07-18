#!/usr/bin/env python3
"""
Verify the cleaning results
"""

import pandas as pd
import random

def verify_cleaning():
    excel_path = "c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/data/excel_files/new_excel.xlsx"
    
    df = pd.read_excel(excel_path)
    content_col = 'Content in detail of News article'
    
    print("=== VERIFICATION OF CLEANED DATA ===")
    print(f"Total rows: {len(df)}")
    print(f"Average content length: {df[content_col].str.len().mean():.1f} characters")
    
    print("\nRandom samples from cleaned data:")
    
    # Check random samples
    sample_indices = random.sample(range(len(df)), min(5, len(df)))
    
    for idx, i in enumerate(sample_indices, 1):
        content = str(df[content_col].iloc[i])
        print(f"\nSample {idx} (Row {i+1}):")
        print("-" * 60)
        print(content[:500] + "..." if len(content) > 500 else content)
    
    # Check for remaining impurities
    print("\n=== CHECKING FOR REMAINING IMPURITIES ===")
    
    impurity_patterns = [
        ("By:PTI", r'By:\s*PTI'),
        ("By:ANI", r'By:\s*ANI'),
        ("min read", r'\d+\s*min\s*read'),
        ("PRINT", r'PRINT'),
        ("Updated:", r'Updated:\s*[A-Za-z]+ \d{1,2}, \d{4}'),
        ("File Photo", r'\([^)]*Photo\)'),
        ("Location |", r'[A-Za-z\s]+\s*\|'),
    ]
    
    for pattern_name, pattern in impurity_patterns:
        import re
        matches = df[content_col].str.contains(pattern, case=False, na=False).sum()
        if matches > 0:
            print(f"⚠️  Found {matches} instances of '{pattern_name}'")
        else:
            print(f"✅ No instances of '{pattern_name}' found")

if __name__ == "__main__":
    verify_cleaning()