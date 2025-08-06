#!/usr/bin/env python3
"""
AI Resume Analyzer - Installation Script
This script installs all required dependencies for the AI Resume Analyzer project.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def download_spacy_model():
    """Download the spaCy English model"""
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("✅ Successfully downloaded spaCy English model")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to download spaCy English model")
        return False

def main():
    print("🤖 AI Resume Analyzer - Installation Script")
    print("=" * 50)
    
    # List of required packages
    packages = [
        "streamlit>=1.43.0",
        "pandas>=1.3.0",
        "plotly>=5.0.0",
        "spacy>=3.8.0",
        "nltk>=3.7",
        "pdfminer.six>=20220524",
        "docx2txt>=0.8",
        "python-dateutil>=2.8.0",
        "geocoder>=1.38.0",
        "geopy>=2.2.0"
    ]
    
    print("📦 Installing required packages...")
    print("-" * 30)
    
    failed_packages = []
    
    for package in packages:
        if not install_package(package):
            failed_packages.append(package)
    
    print("\n🔧 Downloading spaCy model...")
    print("-" * 30)
    
    if not download_spacy_model():
        failed_packages.append("en_core_web_sm")
    
    print("\n📋 Installation Summary")
    print("=" * 30)
    
    if failed_packages:
        print(f"❌ Failed to install: {', '.join(failed_packages)}")
        print("\n🔧 Manual installation commands:")
        for package in failed_packages:
            if package == "en_core_web_sm":
                print(f"   python -m spacy download en_core_web_sm")
            else:
                print(f"   pip install {package}")
    else:
        print("✅ All packages installed successfully!")
    
    print("\n🚀 To run the application:")
    print("   cd App")
    print("   streamlit run App.py")
    print("\n🌐 The app will open in your browser at http://localhost:8501")
    
    print("\n📚 For more information, see ENHANCED_README.md")

if __name__ == "__main__":
    main()
