#!/usr/bin/env python3
"""
Check Progress - Monitor summarization progress across Excel files
"""

import os
import pandas as pd
from datetime import datetime

def check_progress():
    """Check summarization progress across all Excel files"""
    
    print("📊 Summarization Progress Monitor")
    print("=" * 60)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    excel_files = [
        ('continuous_news.xlsx', 'Continuous News'),
        ('new_excel.xlsx', 'New Excel')
    ]
    
    total_articles = 0
    total_summarized = 0
    total_failed = 0
    total_pending = 0
    
    for filename, display_name in excel_files:
        file_path = f'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/{filename}'
        
        if not os.path.exists(file_path):
            print(f"❌ {display_name}: File not found")
            continue
        
        try:
            df = pd.read_excel(file_path)
            
            # Initialize Summary Status column if it doesn't exist
            if 'Summary Status' not in df.columns:
                df['Summary Status'] = 'NOT_SUMMARIZED'
            
            # Count statuses
            status_counts = df['Summary Status'].value_counts()
            
            summarized = status_counts.get('SUMMARIZED', 0)
            failed = status_counts.get('FAILED', 0)
            pending = status_counts.get('NOT_SUMMARIZED', 0)
            total = len(df)
            
            # Update totals
            total_articles += total
            total_summarized += summarized
            total_failed += failed
            total_pending += pending
            
            # Calculate percentages
            summarized_pct = (summarized / total * 100) if total > 0 else 0
            failed_pct = (failed / total * 100) if total > 0 else 0
            pending_pct = (pending / total * 100) if total > 0 else 0
            
            print(f"\n📁 {display_name}:")
            print(f"   Total Articles: {total}")
            print(f"   ✅ Summarized: {summarized} ({summarized_pct:.1f}%)")
            print(f"   ❌ Failed: {failed} ({failed_pct:.1f}%)")
            print(f"   ⏳ Pending: {pending} ({pending_pct:.1f}%)")
            
            # Progress bar
            if total > 0:
                progress = summarized / total
                bar_length = 30
                filled_length = int(bar_length * progress)
                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                print(f"   Progress: [{bar}] {progress*100:.1f}%")
            
        except Exception as e:
            print(f"❌ Error reading {display_name}: {e}")
    
    # Overall summary
    print("\n" + "=" * 60)
    print("📈 OVERALL SUMMARY:")
    print("=" * 60)
    
    if total_articles > 0:
        overall_summarized_pct = (total_summarized / total_articles * 100)
        overall_failed_pct = (total_failed / total_articles * 100)
        overall_pending_pct = (total_pending / total_articles * 100)
        
        print(f"Total Articles: {total_articles}")
        print(f"✅ Summarized: {total_summarized} ({overall_summarized_pct:.1f}%)")
        print(f"❌ Failed: {total_failed} ({overall_failed_pct:.1f}%)")
        print(f"⏳ Pending: {total_pending} ({overall_pending_pct:.1f}%)")
        
        # Overall progress bar
        overall_progress = total_summarized / total_articles
        bar_length = 50
        filled_length = int(bar_length * overall_progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f"\nOverall Progress: [{bar}] {overall_progress*100:.1f}%")
        
        # Estimated time remaining (if we have some data)
        if total_summarized > 0:
            avg_time_per_article = 8  # seconds (estimated)
            remaining_time_seconds = total_pending * avg_time_per_article
            remaining_hours = remaining_time_seconds // 3600
            remaining_minutes = (remaining_time_seconds % 3600) // 60
            
            print(f"\n⏱️  Estimated time remaining: {remaining_hours}h {remaining_minutes}m")
        
        # Status message
        if total_pending == 0:
            print("\n🎉 All articles have been processed!")
        elif total_summarized == 0:
            print("\n🚀 Ready to start summarization!")
        else:
            print(f"\n⚡ {total_pending} articles remaining to process")
    
    else:
        print("No Excel files found or all files are empty.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_progress()