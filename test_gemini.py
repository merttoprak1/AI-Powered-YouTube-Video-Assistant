#!/usr/bin/env python3
"""
Test script to verify Google Gemini API is working
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini():
    """Test if Gemini API is configured correctly"""
    print("="*60)
    print("🧪 Google Gemini API Test")
    print("="*60 + "\n")
    
    # Load environment
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    print("📋 Checking API key...")
    if not api_key:
        print("❌ FAILED: GOOGLE_API_KEY not found in .env file!\n")
        print("💡 Create a .env file with:")
        print("   GOOGLE_API_KEY=your_key_here\n")
        print("📝 Get your API key from:")
        print("   https://makersuite.google.com/app/apikey\n")
        return False
    
    print(f"✅ API key found (length: {len(api_key)} chars)")
    print(f"   Starts with: {api_key[:10]}...\n")
    
    # Try to configure
    print("⚙️  Configuring Gemini API...")
    try:
        genai.configure(api_key=api_key)
        print("✅ Configuration successful\n")
    except Exception as e:
        print(f"❌ FAILED to configure: {str(e)}\n")
        return False
    
    # Try to make a simple request
    print("📡 Testing API with a simple request...")
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content("Say 'Hello, the API is working!'")
        
        print("✅ SUCCESS! API is working!\n")
        print(f"📝 Response: {response.text}\n")
        print("✨ Your Gemini API is configured correctly!")
        print("   You can now use the Streamlit app.\n")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ FAILED: {error_msg}\n")
        
        if "API_KEY_INVALID" in error_msg or "invalid" in error_msg.lower():
            print("⚠️  Your API key appears to be invalid.\n")
            print("💡 Solutions:")
            print("   1. Generate a new API key at: https://makersuite.google.com/app/apikey")
            print("   2. Make sure you copied the entire key")
            print("   3. Update your .env file with the new key\n")
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            print("⚠️  API quota exceeded.\n")
            print("💡 Solutions:")
            print("   1. Wait a few minutes and try again")
            print("   2. Check your quota at: https://makersuite.google.com/")
            print("   3. You may need to upgrade your plan\n")
        elif "credentials" in error_msg.lower():
            print("⚠️  Authentication issue.\n")
            print("💡 This might be a library version problem.")
            print("   Try: pip install --upgrade google-generativeai\n")
        else:
            print("💡 Unknown error. Check your internet connection and try again.\n")
        
        return False


if __name__ == "__main__":
    import sys
    success = test_gemini()
    sys.exit(0 if success else 1)
