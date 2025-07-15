#!/usr/bin/env python3
"""
Real-time monitoring and analytics for the news scraper
Tracks performance, API usage, and adaptive learning progress
"""

import json
import time
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from config import EXCEL_FILENAME, ERROR_LOG_FILENAME

class ScraperMonitor:
    def __init__(self):
        self.excel_file = EXCEL_FILENAME
        self.selector_tracking_file = "selector_success_tracking.json"
        self.api_usage_file = "llm_api_usage.json"
        self.error_log_file = ERROR_LOG_FILENAME
        
    def load_data(self):
        """Load all available data sources"""
        data = {}
        
        # Load Excel data
        try:
            data['articles'] = pd.read_excel(self.excel_file)
            print(f"✅ Loaded {len(data['articles'])} articles from Excel")
        except Exception as e:
            print(f"⚠️ Could not load Excel data: {e}")
            data['articles'] = pd.DataFrame()
        
        # Load selector tracking
        try:
            with open(self.selector_tracking_file, 'r') as f:
                data['selectors'] = json.load(f)
            print("✅ Loaded selector tracking data")
        except Exception as e:
            print(f"⚠️ Could not load selector tracking: {e}")
            data['selectors'] = {}
        
        # Load API usage
        try:
            with open(self.api_usage_file, 'r') as f:
                data['api_usage'] = json.load(f)
            print("✅ Loaded API usage data")
        except Exception as e:
            print(f"⚠️ Could not load API usage: {e}")
            data['api_usage'] = {}
        
        return data
    
    def analyze_collection_progress(self, data):
        """Analyze article collection progress"""
        print("\n📊 COLLECTION PROGRESS ANALYSIS")
        print("="*50)
        
        articles_df = data['articles']
        
        if len(articles_df) == 0:
            print("No articles collected yet.")
            return
        
        # Basic statistics
        total_articles = len(articles_df)
        unique_newspapers = articles_df['Newspaper'].nunique()
        unique_categories = articles_df['News Category'].nunique()
        
        print(f"Total Articles: {total_articles}")
        print(f"Unique Newspapers: {unique_newspapers}")
        print(f"Unique Categories: {unique_categories}")
        
        # Progress toward target
        target_progress = (total_articles / 1100) * 100
        print(f"Target Progress: {target_progress:.1f}%")
        
        # Newspaper distribution
        print("\n🗞️ NEWSPAPER DISTRIBUTION:")
        newspaper_counts = articles_df['Newspaper'].value_counts()
        for newspaper, count in newspaper_counts.head(10).items():
            print(f"  {newspaper}: {count} articles")
        
        # Category distribution
        print("\n🏷️ CATEGORY DISTRIBUTION:")
        category_counts = articles_df['News Category'].value_counts()
        for category, count in category_counts.head(10).items():
            print(f"  {category}: {count} articles")
        
        # Date distribution
        if 'Published Date' in articles_df.columns:
            print("\n📅 DATE DISTRIBUTION:")
            try:
                articles_df['Published Date'] = pd.to_datetime(articles_df['Published Date'])
                date_range = articles_df['Published Date'].agg(['min', 'max'])
                print(f"  Date Range: {date_range['min'].strftime('%Y-%m-%d')} to {date_range['max'].strftime('%Y-%m-%d')}")
                
                # Year distribution
                year_counts = articles_df['Published Date'].dt.year.value_counts().sort_index()
                for year, count in year_counts.items():
                    print(f"  {year}: {count} articles")
                    
            except Exception as e:
                print(f"  Could not analyze dates: {e}")
        
        # Front page analysis
        if 'Front Page News' in articles_df.columns:
            print("\n📰 FRONT PAGE ANALYSIS:")
            front_page_counts = articles_df['Front Page News'].value_counts()
            for category, count in front_page_counts.items():
                print(f"  {category}: {count} articles")
    
    def analyze_adaptive_learning(self, data):
        """Analyze adaptive learning progress"""
        print("\n🧠 ADAPTIVE LEARNING ANALYSIS")
        print("="*50)
        
        selectors_data = data['selectors']
        
        if not selectors_data:
            print("No adaptive learning data available yet.")
            return
        
        # Overall statistics
        total_domains = set()
        total_selectors = 0
        
        for selector_type in ['headline', 'date', 'content']:
            if selector_type in selectors_data:
                domains = selectors_data[selector_type].keys()
                total_domains.update(domains)
                
                for domain, selectors in selectors_data[selector_type].items():
                    total_selectors += len(selectors)
        
        print(f"Total Domains Learned: {len(total_domains)}")
        print(f"Total Selectors Learned: {total_selectors}")
        
        # Per-type analysis
        for selector_type in ['headline', 'date', 'content']:
            if selector_type in selectors_data:
                print(f"\n{selector_type.upper()} SELECTORS:")
                type_data = selectors_data[selector_type]
                
                # Top performing domains
                domain_scores = {}
                for domain, selectors in type_data.items():
                    domain_scores[domain] = sum(selectors.values())
                
                for domain, score in sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"  {domain}: {score} successful extractions")
                    
                    # Top selectors for this domain
                    top_selectors = sorted(type_data[domain].items(), key=lambda x: x[1], reverse=True)[:3]
                    for selector, count in top_selectors:
                        print(f"    {selector}: {count} uses")
    
    def analyze_api_usage(self, data):
        """Analyze LLM API usage patterns"""
        print("\n🤖 LLM API USAGE ANALYSIS")
        print("="*50)
        
        api_data = data['api_usage']
        
        if not api_data:
            print("No API usage data available yet.")
            return
        
        # Basic statistics
        total_requests = api_data.get('total_requests', 0)
        failed_requests = api_data.get('failed_requests', 0)
        rate_limit_hits = api_data.get('rate_limit_hits', 0)
        
        print(f"Total Requests: {total_requests}")
        print(f"Failed Requests: {failed_requests}")
        print(f"Rate Limit Hits: {rate_limit_hits}")
        
        # Success rate
        if total_requests > 0:
            success_rate = ((total_requests - failed_requests) / total_requests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        # Rate limit percentage
        if total_requests > 0:
            rate_limit_percentage = (rate_limit_hits / total_requests) * 100
            print(f"Rate Limit Percentage: {rate_limit_percentage:.1f}%")
        
        # Estimated remaining quota (assuming 1000 requests per day)
        estimated_quota = 1000
        remaining_quota = estimated_quota - total_requests
        print(f"Estimated Remaining Quota: {remaining_quota}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if rate_limit_hits > 0:
            print("  - Consider increasing delays between API calls")
            print("  - Implement more aggressive rate limiting")
        
        if failed_requests > total_requests * 0.1:
            print("  - High failure rate detected, check API key and network")
        
        if remaining_quota < 100:
            print("  - Approaching API quota limit, consider pausing collection")
    
    def analyze_extraction_success(self, data):
        """Analyze extraction success rates"""
        print("\n📈 EXTRACTION SUCCESS ANALYSIS")
        print("="*50)
        
        articles_df = data['articles']
        
        if len(articles_df) == 0:
            print("No articles to analyze.")
            return
        
        # Extraction success rates by newspaper
        if 'Extraction Success Rate' in articles_df.columns:
            print("📊 SUCCESS RATES BY NEWSPAPER:")
            try:
                # Convert success rate strings to floats
                articles_df['Success Rate Numeric'] = articles_df['Extraction Success Rate'].str.replace('%', '').astype(float)
                
                newspaper_success = articles_df.groupby('Newspaper')['Success Rate Numeric'].agg(['mean', 'count']).sort_values('mean', ascending=False)
                
                for newspaper, stats in newspaper_success.head(10).iterrows():
                    print(f"  {newspaper}: {stats['mean']:.1f}% ({stats['count']} articles)")
                    
            except Exception as e:
                print(f"  Could not analyze success rates: {e}")
        
        # API usage status
        if 'API Usage Status' in articles_df.columns:
            print("\n🤖 API USAGE STATUS:")
            api_status_counts = articles_df['API Usage Status'].value_counts()
            for status, count in api_status_counts.items():
                print(f"  {status}: {count} articles")
    
    def generate_recommendations(self, data):
        """Generate recommendations based on analysis"""
        print("\n💡 RECOMMENDATIONS")
        print("="*50)
        
        articles_df = data['articles']
        api_data = data['api_usage']
        
        recommendations = []
        
        # Collection progress recommendations
        if len(articles_df) > 0:
            total_articles = len(articles_df)
            
            if total_articles < 500:
                recommendations.append("🎯 Collection pace is slow. Consider running multiple instances or increasing collection frequency.")
            
            # Newspaper diversity
            newspaper_counts = articles_df['Newspaper'].value_counts()
            if len(newspaper_counts) < 10:
                recommendations.append("📰 Low newspaper diversity. Ensure all configured newspapers are being accessed.")
            
            # Category diversity
            category_counts = articles_df['News Category'].value_counts()
            if len(category_counts) < 8:
                recommendations.append("🏷️ Limited category diversity. Review topic classification accuracy.")
        
        # API usage recommendations
        if api_data:
            total_requests = api_data.get('total_requests', 0)
            rate_limit_hits = api_data.get('rate_limit_hits', 0)
            
            if rate_limit_hits > 0:
                recommendations.append("⚠️ API rate limits hit. Implement longer delays between LLM calls.")
            
            if total_requests > 800:
                recommendations.append("🚨 Approaching API quota limit. Consider reducing LLM processing or upgrading plan.")
        
        # Adaptive learning recommendations
        selectors_data = data['selectors']
        if selectors_data:
            total_domains = set()
            for selector_type in ['headline', 'date', 'content']:
                if selector_type in selectors_data:
                    total_domains.update(selectors_data[selector_type].keys())
            
            if len(total_domains) < 5:
                recommendations.append("🧠 Limited adaptive learning data. Allow more time for selector optimization.")
        
        # Display recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ No immediate recommendations. Scraper is performing well!")
    
    def save_analysis_report(self, data):
        """Save analysis report to file"""
        report_file = f"scraper_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(report_file, 'w') as f:
                f.write("NEWS SCRAPER ANALYSIS REPORT\n")
                f.write("="*50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                articles_df = data['articles']
                
                # Basic statistics
                f.write("BASIC STATISTICS:\n")
                f.write(f"Total Articles: {len(articles_df)}\n")
                if len(articles_df) > 0:
                    f.write(f"Unique Newspapers: {articles_df['Newspaper'].nunique()}\n")
                    f.write(f"Unique Categories: {articles_df['News Category'].nunique()}\n")
                    f.write(f"Target Progress: {(len(articles_df) / 1100) * 100:.1f}%\n")
                
                # API usage
                api_data = data['api_usage']
                if api_data:
                    f.write(f"\nAPI USAGE:\n")
                    f.write(f"Total Requests: {api_data.get('total_requests', 0)}\n")
                    f.write(f"Failed Requests: {api_data.get('failed_requests', 0)}\n")
                    f.write(f"Rate Limit Hits: {api_data.get('rate_limit_hits', 0)}\n")
                
                # Adaptive learning
                selectors_data = data['selectors']
                if selectors_data:
                    f.write(f"\nADAPTIVE LEARNING:\n")
                    total_domains = set()
                    for selector_type in ['headline', 'date', 'content']:
                        if selector_type in selectors_data:
                            total_domains.update(selectors_data[selector_type].keys())
                    f.write(f"Total Domains Learned: {len(total_domains)}\n")
            
            print(f"📄 Analysis report saved: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Could not save analysis report: {e}")
    
    def run_continuous_monitoring(self, interval=60):
        """Run continuous monitoring with specified interval"""
        print(f"🔄 Starting continuous monitoring (update every {interval} seconds)")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')  # Clear screen
                
                print("="*70)
                print("🖥️  NEWS SCRAPER REAL-TIME MONITOR")
                print("="*70)
                print(f"Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                data = self.load_data()
                
                # Quick stats
                articles_df = data['articles']
                if len(articles_df) > 0:
                    print(f"\n📊 Quick Stats:")
                    print(f"   Articles: {len(articles_df)}")
                    print(f"   Progress: {(len(articles_df) / 1100) * 100:.1f}%")
                    print(f"   Newspapers: {articles_df['Newspaper'].nunique()}")
                    
                    # Recent activity
                    print(f"\n🔄 Recent Activity:")
                    recent_articles = articles_df.tail(5)
                    for _, article in recent_articles.iterrows():
                        print(f"   {article['Newspaper']}: {article['Headline'][:50]}...")
                
                # API usage
                api_data = data['api_usage']
                if api_data:
                    total_requests = api_data.get('total_requests', 0)
                    print(f"\n🤖 API Usage: {total_requests} requests")
                    
                    if total_requests > 800:
                        print("   ⚠️ WARNING: Approaching API limit!")
                
                print(f"\n⏰ Next update in {interval} seconds...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
    
    def run_full_analysis(self):
        """Run full analysis"""
        print("="*70)
        print("🔍 NEWS SCRAPER COMPREHENSIVE ANALYSIS")
        print("="*70)
        
        data = self.load_data()
        
        self.analyze_collection_progress(data)
        self.analyze_adaptive_learning(data)
        self.analyze_api_usage(data)
        self.analyze_extraction_success(data)
        self.generate_recommendations(data)
        self.save_analysis_report(data)
        
        print("\n✅ Analysis complete!")

def main():
    """Main function"""
    import sys
    
    monitor = ScraperMonitor()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "monitor":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            monitor.run_continuous_monitoring(interval)
        elif command == "analyze":
            monitor.run_full_analysis()
        else:
            print("Usage: python monitor_scraper.py [monitor|analyze] [interval]")
    else:
        monitor.run_full_analysis()

if __name__ == "__main__":
    main()