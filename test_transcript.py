#!/usr/bin/env python3
"""
Quick test script to check if transcript fetching works
Run this to test without starting the full Streamlit app
"""

import yt_dlp
import requests
import sys
import time
import json

def test_transcript(video_id):
    """Test if we can fetch transcript for a video using yt-dlp"""
    print(f"🧪 Testing transcript fetch for video: {video_id}")
    print(f"📺 URL: https://www.youtube.com/watch?v={video_id}\n")
    
    try:
        print("⏳ Using yt-dlp to fetch video info...")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitlesformat': 'json3',
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            # Check for subtitles
            has_manual = 'en' in subtitles or 'en-US' in subtitles
            has_auto = 'en' in automatic_captions or 'en-US' in automatic_captions
            
            print(f"📝 Manual subtitles: {'✅ Yes' if has_manual else '❌ No'}")
            print(f"📝 Auto-generated: {'✅ Yes' if has_auto else '❌ No'}\n")
            
            if not has_manual and not has_auto:
                print("❌ FAILED: No English subtitles available\n")
                print("💡 This video doesn't have English captions.")
                print("   Try a different video with confirmed captions.\n")
                return False
            
            # Try to get subtitle URL
            subtitle_url = None
            for lang in ['en', 'en-US', 'en-GB']:
                if lang in subtitles:
                    for fmt in subtitles[lang]:
                        if fmt.get('ext') == 'json3':
                            subtitle_url = fmt['url']
                            break
                if subtitle_url:
                    break
            
            if not subtitle_url:
                for lang in ['en', 'en-US', 'en-GB']:
                    if lang in automatic_captions:
                        for fmt in automatic_captions[lang]:
                            if fmt.get('ext') == 'json3':
                                subtitle_url = fmt['url']
                                break
                    if subtitle_url:
                        break
            
            if not subtitle_url:
                print("❌ FAILED: Could not find subtitle URL\n")
                return False
            
            print("⬇️ Downloading subtitle data...")
            time.sleep(1)
            
            response = requests.get(subtitle_url, timeout=20)
            
            if response.status_code == 429:
                print("❌ FAILED: Rate limited (HTTP 429)\n")
                print("⚠️  Still rate limited. Please wait longer.\n")
                print("💡 Tips:")
                print("   - Wait 30-60 minutes")
                print("   - Try using mobile hotspot")
                print("   - Try again with this script\n")
                return False
            
            if response.status_code != 200:
                print(f"❌ FAILED: HTTP {response.status_code}\n")
                return False
            
            subtitle_data = response.json()
            text_parts = []
            
            if 'events' in subtitle_data:
                for event in subtitle_data['events']:
                    if 'segs' in event:
                        for seg in event['segs']:
                            if 'utf8' in seg:
                                text_parts.append(seg['utf8'])
            
            full_text = ' '.join(text_parts).strip()
            
            if len(full_text) >= 50:
                preview = full_text[:200]
                print("✅ SUCCESS! Transcript fetched successfully!\n")
                print(f"📊 Total characters: {len(full_text)}")
                print(f"📝 Preview: {preview}...\n")
                print("✨ The app should work now! You can start Streamlit.\n")
                return True
            else:
                print(f"❌ FAILED: Transcript too short ({len(full_text)} chars)\n")
                return False
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ FAILED: {error_msg}\n")
        
        if "429" in error_msg or "Too Many" in error_msg:
            print("⚠️  Still rate limited. Please wait longer.\n")
            print("💡 Tips:")
            print("   - Wait 30-60 minutes")
            print("   - Try using mobile hotspot")
            print("   - Try again with this script\n")
        else:
            print("💡 Possible issues:")
            print("   - Video might be private or deleted")
            print("   - Network connection problems")
            print("   - Try a different video\n")
        
        return False


if __name__ == "__main__":
    # Default test video (replace with your own)
    default_video = "rNxC16mlO60"
    
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        video_id = default_video
    
    print("="*60)
    print("🎬 YouTube Transcript Test Tool")
    print("="*60 + "\n")
    
    success = test_transcript(video_id)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
