#!/usr/bin/env python3
"""
Production News Article Summarizer
Processes all remaining articles in Excel files and generates summaries using Ollama
"""

import os
import pandas as pd
import requests
import json
import time
import logging
from datetime import datetime
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/production_summarizer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ProductionSummarizer:
    def __init__(self):
        """Initialize the Production Summarizer"""
        self.logger = logging.getLogger(__name__)
        self.model_name = "gemma3:4b"
        self.ollama_url = "http://localhost:11434/api/generate"
        self.batch_size = 10  # Process 10 articles at a time
        
        self.excel_files = [
            'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/continuous_news.xlsx',
            'c:/Users/yadne/OneDrive - MIT - Chhatrapati Sambhajinagar/Desktop/scrapper/new_excel.xlsx'
        ]
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful_summaries': 0,
            'failed_summaries': 0,
            'skipped_articles': 0
        }
    
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                if self.model_name in model_names:
                    self.logger.info(f"✅ Ollama is running and {self.model_name} is available")
                    return True
                else:
                    self.logger.error(f"❌ Model {self.model_name} not found. Available models: {model_names}")
                    return False
            else:
                self.logger.error("❌ Ollama is not responding")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Cannot connect to Ollama: {e}")
            return False
    
    def generate_summary(self, article_content: str) -> Optional[str]:
        """
        Generate summary for article content using Ollama
        
        Args:
            article_content: The article content to summarize
            
        Returns:
            Generated summary or None if failed
        """
        if not article_content or pd.isna(article_content) or len(str(article_content).strip()) < 50:
            return None
        
        prompt = f"""Read this news article and write a concise summary in 2-3 sentences. Write only the summary, no introductory phrases:

{str(article_content)[:2000]}"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 150
            }
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get('response', '').strip()
                
                # Clean up the summary
                if summary:
                    # Remove common prefixes and phrases
                    prefixes_to_remove = [
                        "Here's a 2-3 sentence summary:",
                        "Here's a summary:",
                        "Here's a concise summary:",
                        "Here's a 2-sentence summary of the news article:",
                        "Here's a 2-3 sentence summary of the news article:",
                        "Summary:",
                        "The article states that",
                        "According to the article,",
                        "The news article reports that",
                        "This article discusses",
                        "The story covers"
                    ]
                    
                    # Clean the summary
                    summary = summary.strip()
                    
                    # Remove prefixes
                    for prefix in prefixes_to_remove:
                        if summary.lower().startswith(prefix.lower()):
                            summary = summary[len(prefix):].strip()
                            break
                    
                    # Remove any remaining colons at the start
                    if summary.startswith(':'):
                        summary = summary[1:].strip()
                    
                    # Ensure it starts with a capital letter
                    if summary and summary[0].islower():
                        summary = summary[0].upper() + summary[1:]
                    
                    # Limit length
                    if len(summary) > 400:
                        summary = summary[:400] + "..."
                    
                    return summary
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return None
    
    def process_excel_file(self, file_path: str) -> dict:
        """
        Process a single Excel file and generate summaries
        
        Args:
            file_path: Path to the Excel file
            
        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(file_path):
            self.logger.warning(f"File not found: {file_path}")
            return {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
        
        filename = os.path.basename(file_path)
        self.logger.info(f"Processing {filename}...")
        
        try:
            # Read the Excel file
            df = pd.read_excel(file_path)
            
            # Initialize Summary Status column if it doesn't exist
            if 'Summary Status' not in df.columns:
                df['Summary Status'] = 'NOT_SUMMARIZED'
            
            if 'AI Summary' not in df.columns:
                df['AI Summary'] = ''
            
            # Find articles that need summarization
            unsummarized = df[df['Summary Status'] == 'NOT_SUMMARIZED']
            
            self.logger.info(f"Found {len(unsummarized)} articles to summarize in {filename}")
            
            if len(unsummarized) == 0:
                self.logger.info(f"✅ All articles in {filename} are already summarized!")
                return {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': len(df)}
            
            # Process in batches
            results = {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
            
            for batch_start in range(0, len(unsummarized), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(unsummarized))
                batch = unsummarized.iloc[batch_start:batch_end]
                
                self.logger.info(f"Processing batch {batch_start//self.batch_size + 1}: articles {batch_start + 1}-{batch_end}")
                
                for idx, row in batch.iterrows():
                    try:
                        headline = row['Headline of News Article']
                        content = row['Content in detail of News article']
                        
                        self.logger.info(f"Summarizing: {headline[:60]}...")
                        
                        # Generate summary
                        summary = self.generate_summary(content)
                        
                        if summary:
                            # Update the dataframe
                            df.at[idx, 'AI Summary'] = summary
                            df.at[idx, 'Summary Status'] = 'SUMMARIZED'
                            
                            results['successful'] += 1
                            self.stats['successful_summaries'] += 1
                            
                            self.logger.info(f"✅ Summary generated: {summary[:100]}...")
                        else:
                            df.at[idx, 'Summary Status'] = 'FAILED'
                            results['failed'] += 1
                            self.stats['failed_summaries'] += 1
                            
                            self.logger.error(f"❌ Failed to generate summary")
                        
                        results['processed'] += 1
                        self.stats['total_processed'] += 1
                        
                        # Small delay between requests
                        time.sleep(1)
                        
                    except Exception as e:
                        self.logger.error(f"Error processing article: {e}")
                        df.at[idx, 'Summary Status'] = 'FAILED'
                        results['failed'] += 1
                        self.stats['failed_summaries'] += 1
                
                # Save progress after each batch
                try:
                    df.to_excel(file_path, index=False)
                    self.logger.info(f"💾 Saved batch progress to {filename}")
                except Exception as e:
                    self.logger.error(f"Error saving batch progress: {e}")
                
                # Longer delay between batches
                if batch_end < len(unsummarized):
                    self.logger.info("Waiting 5 seconds before next batch...")
                    time.sleep(5)
            
            self.logger.info(f"✅ Completed {filename}: {results['successful']} successful, {results['failed']} failed")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': 0}
    
    def run_production_summarization(self):
        """Run the production summarization process on all Excel files"""
        start_time = datetime.now()
        
        self.logger.info("=" * 60)
        self.logger.info("PRODUCTION NEWS ARTICLE SUMMARIZER")
        self.logger.info(f"Started at: {start_time}")
        self.logger.info(f"Model: {self.model_name}")
        self.logger.info(f"Batch size: {self.batch_size}")
        self.logger.info("Processing order: continuous_news.xlsx first, then new_excel.xlsx")
        self.logger.info("=" * 60)
        
        # Check Ollama connection first
        if not self.check_ollama_connection():
            self.logger.error("Cannot proceed without Ollama connection. Please start Ollama and try again.")
            return
        
        total_processed = 0
        
        for file_path in self.excel_files:
            if os.path.exists(file_path):
                results = self.process_excel_file(file_path)
                total_processed += results['processed']
            else:
                self.logger.warning(f"File not found: {file_path}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Final statistics
        self.logger.info("=" * 60)
        self.logger.info("PRODUCTION SUMMARIZATION COMPLETED")
        self.logger.info(f"Duration: {duration}")
        self.logger.info(f"Total articles processed: {self.stats['total_processed']}")
        self.logger.info(f"Successful summaries: {self.stats['successful_summaries']}")
        self.logger.info(f"Failed summaries: {self.stats['failed_summaries']}")
        
        if self.stats['total_processed'] > 0:
            success_rate = (self.stats['successful_summaries'] / self.stats['total_processed']) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")
        
        self.logger.info("=" * 60)

def main():
    """Main function"""
    print("Production News Article Summarizer")
    print("=" * 50)
    print("This will process ALL remaining articles.")
    print("Processing order:")
    print("  1. continuous_news.xlsx (10 articles per batch)")
    print("  2. new_excel.xlsx (10 articles per batch)")
    print("The process may take several hours to complete.")
    print("Progress will be saved continuously after each batch.")
    print()
    
    response = input("Do you want to start? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        summarizer = ProductionSummarizer()
        summarizer.run_production_summarization()
        
        print("\n✅ Production summarization completed!")
        print("Check ../logs/production_summarizer.log for detailed logs.")
    else:
        print("Process cancelled.")

if __name__ == "__main__":
    main()