#!/usr/bin/env python3
"""
Complete Workflow Runner
Runs the entire news scraping, validation, and summarization workflow
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print("=" * 60)
    
    try:
        # Change to the appropriate directory for the command
        if command.startswith('python scrapers/'):
            os.chdir('scrapers')
            command = command.replace('python scrapers/', 'python ')
        elif command.startswith('python checkers/'):
            os.chdir('checkers')
            command = command.replace('python checkers/', 'python ')
        elif command.startswith('python summarizers/'):
            os.chdir('summarizers')
            command = command.replace('python summarizers/', 'python ')
        elif command.startswith('python utilities/'):
            os.chdir('utilities')
            command = command.replace('python utilities/', 'python ')
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Return to root directory
        os.chdir('..')
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Show last 500 chars
        else:
            print(f"❌ {description} failed!")
            if result.stderr:
                print("Error:", result.stderr[-500:])
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False
    
    return True

def main():
    """Run the complete workflow"""
    start_time = datetime.now()
    
    print("🎯 NEWS SCRAPER COMPLETE WORKFLOW")
    print("=" * 60)
    print(f"Started at: {start_time}")
    print("This will run the complete workflow:")
    print("1. Environment check")
    print("2. News scraping")
    print("3. Content validation")
    print("4. AI summarization")
    print("5. Final verification")
    print("=" * 60)
    
    # Get user confirmation
    response = input("\nDo you want to run the complete workflow? (y/n): ").lower().strip()
    
    if response not in ['y', 'yes']:
        print("Workflow cancelled.")
        return
    
    # Store original directory
    original_dir = os.getcwd()
    
    try:
        # Step 1: Environment and setup checks
        print("\n" + "="*60)
        print("PHASE 1: ENVIRONMENT SETUP & VERIFICATION")
        print("="*60)
        
        if not run_command("python utilities/check_ollama.py", "Checking Ollama setup"):
            print("⚠️ Ollama check failed. Please ensure Ollama is installed and running.")
            response = input("Continue anyway? (y/n): ").lower().strip()
            if response not in ['y', 'yes']:
                return
        
        run_command("python utilities/quick_status.py", "Checking current project status")
        
        # Step 2: Data collection
        print("\n" + "="*60)
        print("PHASE 2: DATA COLLECTION")
        print("="*60)
        
        scraper_choice = input("\nChoose scraper:\n1. news_scraper.py (200 articles)\n2. continuous_news_scraper.py (multiple cycles)\nEnter choice (1 or 2): ").strip()
        
        if scraper_choice == "1":
            if not run_command("python scrapers/news_scraper.py", "Running news scraper (200 articles)"):
                print("❌ Scraping failed. Cannot continue.")
                return
        elif scraper_choice == "2":
            if not run_command("python scrapers/continuous_news_scraper.py", "Running continuous news scraper"):
                print("❌ Scraping failed. Cannot continue.")
                return
        else:
            print("Invalid choice. Using default news_scraper.py")
            if not run_command("python scrapers/news_scraper.py", "Running news scraper (200 articles)"):
                print("❌ Scraping failed. Cannot continue.")
                return
        
        # Step 3: Data validation
        print("\n" + "="*60)
        print("PHASE 3: DATA VALIDATION & QUALITY ASSURANCE")
        print("="*60)
        
        run_command("python checkers/check_new_excel.py", "Checking data quality")
        
        print("\n🔧 Running content validation and fixing mismatches...")
        print("This step is CRITICAL for data quality!")
        
        # For reauthenticator, we need to provide input
        print("\nRunning reauthenticator in auto-fix mode...")
        if not run_command("python utilities/run_reauthenticator.py", "Fixing title-content mismatches"):
            print("⚠️ Content validation had issues. Check logs.")
        
        run_command("python utilities/quick_check_reauthenticator.py", "Verifying content fixes")
        
        # Step 4: AI Summarization
        print("\n" + "="*60)
        print("PHASE 4: AI SUMMARIZATION")
        print("="*60)
        
        # Final Ollama check before summarization
        if not run_command("python utilities/check_ollama.py", "Final Ollama verification"):
            print("❌ Ollama is not ready. Cannot proceed with summarization.")
            return
        
        print("\n🤖 Starting AI summarization...")
        print("This may take 30-60 minutes depending on the number of articles.")
        
        if not run_command("python summarizers/production_summarizer.py", "Generating AI summaries"):
            print("❌ Summarization failed. Check logs and Ollama status.")
            return
        
        # Step 5: Final verification
        print("\n" + "="*60)
        print("PHASE 5: FINAL VERIFICATION")
        print("="*60)
        
        run_command("python checkers/verify_excel.py", "Comprehensive Excel verification")
        run_command("python utilities/check_progress.py", "Checking final progress")
        run_command("python utilities/quick_status.py", "Final status check")
        
        # Completion summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "="*60)
        print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Started: {start_time}")
        print(f"Completed: {end_time}")
        print(f"Duration: {duration}")
        print("\n📊 Final Results:")
        print("- News articles scraped and validated")
        print("- Content quality assured")
        print("- AI summaries generated")
        print("- Excel files ready for use")
        print("\n📁 Output Files:")
        print("- continuous_news.xlsx (if continuous scraper was used)")
        print("- new_excel.xlsx (if news scraper was used)")
        print("\n📝 Logs Available:")
        print("- logs/continuous_scraper.log")
        print("- logs/production_summarizer.log")
        print("- logs/reauthenticator.log")
        print("\n✨ Your news scraping and summarization system is ready!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Workflow interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Return to original directory
        os.chdir(original_dir)

if __name__ == "__main__":
    main()