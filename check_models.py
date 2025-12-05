#!/usr/bin/env python3
"""
Check available Gemini models
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    
    print("="*60)
    print("🔍 Available Gemini Models")
    print("="*60 + "\n")
    
    try:
        models = genai.list_models()
        
        print("📋 Models that support generateContent:\n")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
                print(f"   Display Name: {model.display_name}")
                print(f"   Description: {model.description[:80]}...")
                print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
else:
    print("❌ No API key found")
