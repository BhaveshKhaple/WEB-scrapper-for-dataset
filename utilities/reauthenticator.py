#!/usr/bin/env python3
"""
Reauthenticator - Verifies title-content matching and recollects articles when needed
Uses check_new_excel.py functionality to validate and fix mismatched articles
"""

import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'reauthenticator.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class NewsReauthenticator:
    def __init__(self):
        """Initialize the News Reauthenticator"""
        self.logger = logging.getLogger(__name__)
        
        # Excel files to check
        self.excel_files = [
            'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/continuous_news.xlsx',
            'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/new_excel.xlsx'
        ]
        
        # Request headers for web scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Statistics
        self.stats = {
            'total_checked': 0,
            'mismatched_found': 0,
            'successfully_fixed': 0,
            'failed_to_fix': 0
        }
    
    def check_title_content_match(self, title: str, content: str) -> bool:
        """
        Check if title and content are related
        
        Args:
            title: Article headline
            content: Article content
            
        Returns:
            True if title and content match, False otherwise
        """
        if not title or not content:
            return False
        
        # Simple check - see if key words from title appear in content
        title_words = set(title.lower().split())
        content_words = set(content.lower().split())
        
        # Remove common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
        }
        
        title_words = title_words - common_words
        content_words = content_words - common_words
        
        if len(title_words) == 0:
            return True  # Can't determine, assume match
        
        # Check if at least 30% of title words appear in content
        matching_words = title_words.intersection(content_words)
        match_ratio = len(matching_words) / len(title_words)
        
        return match_ratio >= 0.3
    
    def extract_full_content(self, url: str) -> Optional[str]:
        """
        Extract full content from URL
        
        Args:
            url: URL to extract content from
            
        Returns:
            Extracted content or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
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
                '.post-content',
                '.entry-content',
                '.post-body'
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
            
            # Clean and limit content
            content = content.strip()
            if len(content) > 3000:
                content = content[:3000] + "..."
            
            return content if len(content) > 100 else None
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def process_excel_file(self, file_path: str) -> Dict:
        """
        Process a single Excel file and fix mismatched articles
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"File not found: {file_path}")
            return {'processed': 0, 'fixed': 0, 'failed': 0}
        
        filename = os.path.basename(file_path)
        self.logger.info(f"Processing {filename}...")
        
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            self.logger.info(f"Found {len(df)} articles in {filename}")
            
            mismatched_articles = []
            processed_count = 0
            
            # Check each article for title-content matching
            for i, row in df.iterrows():
                title = row['Headline of News Article']
                content = row['Content in detail of News article']
                url = row['Enter URL or Link of News']
                
                processed_count += 1
                self.stats['total_checked'] += 1
                
                if not self.check_title_content_match(title, content):
                    mismatched_articles.append({
                        'index': i,
                        'title': title,
                        'content': content,
                        'url': url
                    })
                    self.stats['mismatched_found'] += 1
                
                # Progress update every 100 articles
                if processed_count % 100 == 0:
                    self.logger.info(f"Processed {processed_count}/{len(df)} articles...")
            
            self.logger.info(f"Found {len(mismatched_articles)} mismatched articles in {filename}")
            
            if not mismatched_articles:
                self.logger.info(f"✅ All articles in {filename} have matching titles and content!")
                return {'processed': processed_count, 'fixed': 0, 'failed': 0}
            
            # Fix mismatched articles
            fixed_count = 0
            failed_count = 0
            
            self.logger.info(f"Attempting to fix {len(mismatched_articles)} mismatched articles...")
            
            for i, article in enumerate(mismatched_articles):
                try:
                    self.logger.info(f"Fixing article {i+1}/{len(mismatched_articles)}: {article['title'][:60]}...")
                    
                    # Try to extract better content
                    better_content = self.extract_full_content(article['url'])
                    
                    if better_content:
                        # Check if the new content matches better
                        if self.check_title_content_match(article['title'], better_content):
                            # Update the dataframe
                            df.at[article['index'], 'Content in detail of News article'] = better_content
                            fixed_count += 1
                            self.stats['successfully_fixed'] += 1
                            self.logger.info(f"✅ Successfully fixed article {i+1}")
                        else:
                            self.logger.warning(f"⚠️ New content still doesn't match title for article {i+1}")
                            failed_count += 1
                            self.stats['failed_to_fix'] += 1
                    else:
                        self.logger.error(f"❌ Could not extract content for article {i+1}")
                        failed_count += 1
                        self.stats['failed_to_fix'] += 1
                    
                    # Be respectful to servers
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing article {i+1}: {e}")
                    failed_count += 1
                    self.stats['failed_to_fix'] += 1
            
            # Save the updated file if we made fixes
            if fixed_count > 0:
                try:
                    df.to_excel(file_path, index=False)
                    self.logger.info(f"💾 Saved {fixed_count} fixes to {filename}")
                except Exception as e:
                    self.logger.error(f"Error saving file {filename}: {e}")
            
            self.logger.info(f"✅ Completed {filename}: {fixed_count} fixed, {failed_count} failed")
            
            return {'processed': processed_count, 'fixed': fixed_count, 'failed': failed_count}
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return {'processed': 0, 'fixed': 0, 'failed': 0}
    
    def run_reauthentication(self):
        """Run the reauthentication process on all Excel files"""
        start_time = datetime.now()
        
        self.logger.info("=" * 60)
        self.logger.info("NEWS ARTICLE REAUTHENTICATOR")
        self.logger.info(f"Started at: {start_time}")
        self.logger.info("Checking title-content matching and fixing mismatches...")
        self.logger.info("=" * 60)
        
        total_results = {'processed': 0, 'fixed': 0, 'failed': 0}
        
        for file_path in self.excel_files:
            if os.path.exists(file_path):
                results = self.process_excel_file(file_path)
                
                # Update totals
                for key in total_results:
                    total_results[key] += results[key]
            else:
                self.logger.warning(f"File not found: {file_path}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Final statistics
        self.logger.info("=" * 60)
        self.logger.info("REAUTHENTICATION COMPLETED")
        self.logger.info(f"Duration: {duration}")
        self.logger.info(f"Total articles checked: {self.stats['total_checked']}")
        self.logger.info(f"Mismatched articles found: {self.stats['mismatched_found']}")
        self.logger.info(f"Successfully fixed: {self.stats['successfully_fixed']}")
        self.logger.info(f"Failed to fix: {self.stats['failed_to_fix']}")
        
        if self.stats['mismatched_found'] > 0:
            fix_rate = (self.stats['successfully_fixed'] / self.stats['mismatched_found']) * 100
            self.logger.info(f"Fix success rate: {fix_rate:.1f}%")
        
        self.logger.info("=" * 60)
        
        return total_results
    
    def comprehensive_check(self):
        """Comprehensive check of ALL articles with detailed analysis"""
        self.logger.info("=" * 70)
        self.logger.info("COMPREHENSIVE ARTICLE ANALYSIS - ALL ARTICLES")
        self.logger.info("=" * 70)
        
        total_articles = 0
        total_mismatched = 0
        total_empty_content = 0
        total_empty_titles = 0
        total_short_content = 0
        
        for file_path in self.excel_files:
            if not os.path.exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                continue
                
            filename = os.path.basename(file_path)
            self.logger.info(f"\n📁 Analyzing {filename}...")
            self.logger.info("-" * 50)
            
            try:
                df = pd.read_excel(file_path)
                
                file_mismatched = 0
                file_empty_content = 0
                file_empty_titles = 0
                file_short_content = 0
                problematic_articles = []
                
                # Check every single article
                for i, row in df.iterrows():
                    title = str(row['Headline of News Article']) if pd.notna(row['Headline of News Article']) else ""
                    content = str(row['Content in detail of News article']) if pd.notna(row['Content in detail of News article']) else ""
                    url = str(row['Enter URL or Link of News']) if pd.notna(row['Enter URL or Link of News']) else ""
                    
                    # Check for various issues
                    issues = []
                    
                    # Empty title check
                    if not title.strip():
                        issues.append("EMPTY_TITLE")
                        file_empty_titles += 1
                    
                    # Empty content check
                    if not content.strip():
                        issues.append("EMPTY_CONTENT")
                        file_empty_content += 1
                    
                    # Short content check (less than 100 characters)
                    elif len(content.strip()) < 100:
                        issues.append("SHORT_CONTENT")
                        file_short_content += 1
                    
                    # Title-content mismatch check
                    if title.strip() and content.strip():
                        if not self.check_title_content_match(title, content):
                            issues.append("TITLE_CONTENT_MISMATCH")
                            file_mismatched += 1
                    
                    # Store problematic articles
                    if issues:
                        problematic_articles.append({
                            'row': i + 1,
                            'title': title[:60] + "..." if len(title) > 60 else title,
                            'content_length': len(content.strip()),
                            'url': url[:50] + "..." if len(url) > 50 else url,
                            'issues': issues
                        })
                
                # Update totals
                total_articles += len(df)
                total_mismatched += file_mismatched
                total_empty_content += file_empty_content
                total_empty_titles += file_empty_titles
                total_short_content += file_short_content
                
                # File summary
                self.logger.info(f"📊 {filename} Summary:")
                self.logger.info(f"   Total articles: {len(df)}")
                self.logger.info(f"   ❌ Title-content mismatches: {file_mismatched}")
                self.logger.info(f"   📝 Empty titles: {file_empty_titles}")
                self.logger.info(f"   📄 Empty content: {file_empty_content}")
                self.logger.info(f"   ⚠️  Short content (<100 chars): {file_short_content}")
                
                # Calculate health score
                healthy_articles = len(df) - len(problematic_articles)
                health_score = (healthy_articles / len(df)) * 100 if len(df) > 0 else 0
                self.logger.info(f"   💚 Health score: {health_score:.1f}%")
                
                # Show problematic articles (first 10)
                if problematic_articles:
                    self.logger.info(f"\n🚨 Problematic Articles in {filename} (showing first 10):")
                    for i, article in enumerate(problematic_articles[:10]):
                        self.logger.info(f"   {i+1}. Row {article['row']}: {', '.join(article['issues'])}")
                        self.logger.info(f"      Title: {article['title']}")
                        self.logger.info(f"      Content length: {article['content_length']} chars")
                        if len(problematic_articles) > 10 and i == 9:
                            self.logger.info(f"      ... and {len(problematic_articles) - 10} more issues")
                
            except Exception as e:
                self.logger.error(f"Error analyzing {filename}: {e}")
        
        # Overall summary
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📈 OVERALL ANALYSIS SUMMARY")
        self.logger.info("=" * 70)
        
        if total_articles > 0:
            self.logger.info(f"Total articles analyzed: {total_articles}")
            self.logger.info(f"❌ Title-content mismatches: {total_mismatched} ({(total_mismatched/total_articles)*100:.1f}%)")
            self.logger.info(f"📝 Empty titles: {total_empty_titles} ({(total_empty_titles/total_articles)*100:.1f}%)")
            self.logger.info(f"📄 Empty content: {total_empty_content} ({(total_empty_content/total_articles)*100:.1f}%)")
            self.logger.info(f"⚠️  Short content: {total_short_content} ({(total_short_content/total_articles)*100:.1f}%)")
            
            total_issues = total_mismatched + total_empty_content + total_empty_titles + total_short_content
            overall_health = ((total_articles - total_issues) / total_articles) * 100
            self.logger.info(f"💚 Overall health score: {overall_health:.1f}%")
            
            # Recommendations
            self.logger.info(f"\n💡 RECOMMENDATIONS:")
            if total_mismatched > 0:
                self.logger.info(f"   • Run full reauthentication to fix {total_mismatched} mismatched articles")
            if total_empty_content > 0:
                self.logger.info(f"   • {total_empty_content} articles have empty content - may need manual review")
            if total_empty_titles > 0:
                self.logger.info(f"   • {total_empty_titles} articles have empty titles - may need manual review")
            if total_short_content > 0:
                self.logger.info(f"   • {total_short_content} articles have very short content - may need content extraction")
            
            if total_issues == 0:
                self.logger.info("   🎉 All articles are in good condition!")
        else:
            self.logger.info("No articles found in any Excel files.")
        
        self.logger.info("=" * 70)
    
    def quick_check(self):
        """Quick check to show current mismatch statistics without fixing"""
        self.logger.info("=" * 60)
        self.logger.info("QUICK TITLE-CONTENT MATCH CHECK")
        self.logger.info("=" * 60)
        
        for file_path in self.excel_files:
            if not os.path.exists(file_path):
                continue
                
            filename = os.path.basename(file_path)
            self.logger.info(f"Checking {filename}...")
            
            try:
                df = pd.read_excel(file_path)
                mismatched_count = 0
                
                for i, row in df.iterrows():
                    title = row['Headline of News Article']
                    content = row['Content in detail of News article']
                    
                    if not self.check_title_content_match(title, content):
                        mismatched_count += 1
                
                match_rate = ((len(df) - mismatched_count) / len(df)) * 100
                
                self.logger.info(f"  Total articles: {len(df)}")
                self.logger.info(f"  Mismatched: {mismatched_count}")
                self.logger.info(f"  Match rate: {match_rate:.1f}%")
                
            except Exception as e:
                self.logger.error(f"Error checking {filename}: {e}")
        
        self.logger.info("=" * 60)

def main():
    """Main function"""
    print("News Article Reauthenticator")
    print("=" * 50)
    print("This tool will:")
    print("1. Check title-content matching in both Excel files")
    print("2. Recollect content for mismatched articles")
    print("3. Update the Excel files with corrected content")
    print("4. Comprehensive analysis of ALL articles")
    print()
    
    reauthenticator = NewsReauthenticator()
    
    print("Choose an option:")
    print("1. Quick check (show basic statistics)")
    print("2. Comprehensive check (detailed analysis of ALL articles)")
    print("3. Full reauthentication (check and fix mismatches)")
    print()
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        print("\n🔍 Running quick check...")
        reauthenticator.quick_check()
    elif choice == "2":
        print("\n🔍 Running comprehensive analysis of ALL articles...")
        print("This will analyze every single article for various issues.")
        reauthenticator.comprehensive_check()
    elif choice == "3":
        print("\n🔧 Starting full reauthentication process...")
        print("This may take some time depending on the number of mismatched articles.")
        print("The process will:")
        print("• Check ALL articles for title-content matching")
        print("• Attempt to fix mismatched articles by re-extracting content")
        print("• Update Excel files with corrected content")
        print()
        
        confirm = input("Do you want to proceed? (y/n): ").lower().strip()
        
        if confirm in ['y', 'yes']:
            results = reauthenticator.run_reauthentication()
            
            print(f"\n✅ Reauthentication completed!")
            print(f"Articles processed: {results['processed']}")
            print(f"Articles fixed: {results['fixed']}")
            print(f"Failed to fix: {results['failed']}")
            print(f"\nCheck logs/reauthenticator.log for detailed logs.")
        else:
            print("Process cancelled.")
    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()