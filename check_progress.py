#!/usr/bin/env python3
"""
Check summarization progress
"""

import pandas as pd

def check_progress():
    """Check the current summarization progress"""
    
    files = [
        'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/continuous_news.xlsx',
        'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/new_excel.xlsx'
    ]
    
    for file_path in files:
        try:
            df = pd.read_excel(file_path)
            filename = file_path.split('/')[-1]
            
            print(f"\n📊 {filename}")
            print("=" * 50)
            
            # Summary status counts
            if 'Summary Status' in df.columns:
                status_counts = df['Summary Status'].value_counts()
                print("Summary Status:")
                for status, count in status_counts.items():
                    print(f"  {status}: {count}")
                
                # Show progress percentage
                total = len(df)
                summarized = status_counts.get('SUMMARIZED', 0)
                progress = (summarized / total) * 100
                print(f"\nProgress: {summarized}/{total} ({progress:.1f}%)")
                
                # Show latest summaries
                if summarized > 0:
                    summarized_df = df[df['Summary Status'] == 'SUMMARIZED']
                    print(f"\nLatest summary:")
                    latest = summarized_df.iloc[-1]
                    print(f"  Headline: {latest['Headline of News Article'][:60]}...")
                    print(f"  Summary: {latest['Human Summary For Article News'][:150]}...")
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

if __name__ == "__main__":
    check_progress()