#!/usr/bin/env python3
"""
Setup script for News Scraper environment
For use in Google Colab or Linux environments
"""

import os
import subprocess
import sys

def run_command(command):
    """Run shell command and return success status"""
    try:
        print(f"🔧 Running: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Success")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def setup_chrome():
    """Install Google Chrome stable version"""
    print("🌐 Setting up Google Chrome...")
    
    # Update package list
    run_command("apt-get update")
    
    # Remove old installations
    run_command("apt-get purge -y google-chrome-stable")
    run_command("apt-get purge -y chromium-browser")
    
    # Install dependencies
    run_command("apt-get install -y wget gnupg")
    
    # Add Google's official GPG key
    run_command("wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -")
    
    # Add Google Chrome repository
    run_command('echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list')
    
    # Update package list again
    run_command("apt-get update")
    
    # Install Google Chrome
    run_command("apt-get install -y google-chrome-stable")
    
    # Verify installation
    result = run_command("google-chrome --version")
    if result:
        print("✅ Chrome installed successfully")
    else:
        print("❌ Chrome installation failed")
        
    return result

def install_python_packages():
    """Install required Python packages"""
    print("🐍 Installing Python packages...")
    
    # Upgrade pip
    run_command("pip install --upgrade pip")
    
    # Install packages from requirements.txt
    if os.path.exists("requirements.txt"):
        run_command("pip install -r requirements.txt")
    else:
        # Install packages individually
        packages = [
            "selenium==4.15.2",
            "webdriver-manager==4.0.1",
            "pandas==2.1.3",
            "openpyxl==3.1.2",
            "cohere==4.37",
            "requests==2.31.0",
            "beautifulsoup4==4.12.2",
            "lxml==4.9.3"
        ]
        
        for package in packages:
            run_command(f"pip install {package}")
    
    print("✅ Python packages installed")

def verify_installation():
    """Verify that all components are properly installed"""
    print("🔍 Verifying installation...")
    
    # Check Chrome
    chrome_ok = run_command("google-chrome --version")
    
    # Check Python packages
    try:
        import selenium
        import pandas
        import cohere
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ All Python packages imported successfully")
        packages_ok = True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        packages_ok = False
    
    if chrome_ok and packages_ok:
        print("🎉 Setup completed successfully!")
        return True
    else:
        print("❌ Setup incomplete. Please check errors above.")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("🔧 NEWS SCRAPER ENVIRONMENT SETUP")
    print("="*60)
    
    # Check if running in Colab
    try:
        import google.colab
        print("📱 Running in Google Colab")
        colab_mode = True
    except ImportError:
        print("🖥️  Running in local environment")
        colab_mode = True  # Assume Linux-like environment
    
    if colab_mode:
        # Setup Chrome
        if not setup_chrome():
            print("❌ Chrome setup failed. Exiting.")
            return
    
    # Install Python packages
    install_python_packages()
    
    # Verify installation
    if verify_installation():
        print("\n🚀 Ready to run news scraper!")
        print("Execute: python news_scraper.py")
    else:
        print("❌ Setup failed. Please check the errors above.")

if __name__ == "__main__":
    main()