#!/usr/bin/env python3
"""Setup and run the chatbot locally"""
import subprocess
import sys
import os
#runs on server
#os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Make sure we're in the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Working directory: {os.getcwd()}")

print("="*60)
print("CHATBOT SETUP")
print("="*60)

# Step 1: Install packages
print("\n[1/4] Installing Python packages...")
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "flask", "nltk", "numpy", "scikit-learn"], check=True)

# Step 2: Download NLTK data
print("[2/4] Downloading NLTK data...")
subprocess.run([sys.executable, "-m", "nltk.downloader", "-q", "punkt_tab", "wordnet"], check=False)

# Step 3: Delete old model to force retraining
print("[3/4] Preparing fresh model...")
for f in ['chatbot_model.pkl', 'vectorizer.pkl', 'words.pkl', 'classes.pkl']:
    if os.path.exists(f):
        os.remove(f)

# Step 4: Run the app
print("[4/4] Starting chatbot...")
print("\n" + "="*60)
print("Flask is running! Open your browser to:")
print("  http://localhost:5000")
print("="*60 + "\n")

subprocess.run([sys.executable, "chatbot_backend.py"], check=False)
