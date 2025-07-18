#!/usr/bin/env python3
"""
Check Current Excel State
"""

import pandas as pd
import os

def check_excel():
    if os.path.exists("new_excel.xlsx"):
        try:
            df = pd.read_excel("new_excel.xlsx")
            print(f"📊 Current Excel Status:")
            print(f"   Articles: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            print(f"   File size: {os.path.getsize('new_excel.xlsx')/1024:.1f} KB")
            
            if len(df) > 0:
                print(f"\n📝 Recent articles:")
                for i in range(min(3, len(df))):
                    row = df.iloc[i]
                    print(f"   {i+1}. {row.get('Name of Newspaper', 'N/A')} | {row.get('Headline of News Article', 'N/A')[:50]}...")
            
            return len(df)
        except Exception as e:
            print(f"❌ Error: {e}")
            return 0
    else:
        print("❌ new_excel.xlsx not found")
        return 0

if __name__ == "__main__":
    check_excel()