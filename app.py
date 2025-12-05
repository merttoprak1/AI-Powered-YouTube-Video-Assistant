import streamlit as st
import google.generativeai as genai
import yt_dlp
from dotenv import load_dotenv
import os
import re
import time
import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import requests
import random
import urllib.parse
from xml.etree import ElementTree

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file!")
    st.info("💡 Please create a .env file with your Google API key:\n```\nGOOGLE_API_KEY=your_key_here\n```")
    st.stop()

try:
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"❌ Failed to configure Gemini API: {str(e)}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="TubeMind - AI YouTube Assistant",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional modern UI
st.markdown("""
    <style>
    /* Main header styling - sleek gradient */
    .main-header {
        font-size: 3.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0 0.3rem 0;
        margin-bottom: 0;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        text-align: center;
        color: #a1a1aa;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Summary box - clean professional design */
    .summary-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 1.8rem;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 1.2rem 0;
        color: #334155;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
    }
    
    .summary-box strong {
        font-size: 1.2rem;
        color: #5b21b6;
        display: block;
        margin-bottom: 0.8rem;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Video styling */
    .stVideo > iframe {
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Feature cards */
    .feature-card {
        text-align: center;
        padding: 2rem 1.5rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 16px;
        height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
    }
    
    h3.feature-title {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: #667eea !important;
    }
    
    .feature-desc {
        color: #64748b;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #94a3b8;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        border-top: 1px solid #e2e8f0;
        padding-top: 1rem;
        margin-top: 0;
    }
    
    /* Section headers - lighter for dark mode compatibility */
    h3:not(.feature-title), .stSubheader {
        color: #e2e8f0 !important;
        font-weight: 600;
    }
    
    /* Sidebar text */
    .css-1d391kg, [data-testid="stSidebar"] {
        color: #e2e8f0;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] li {
        color: #cbd5e1 !important;
    }
    
    [data-testid="stSidebar"] strong {
        color: #f1f5f9 !important;
    }
    </style>
""", unsafe_allow_html=True)


def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_transcript_method1(video_id):
    """Method 1: Use youtube-transcript-api with retry and delay"""
    try:
        st.info("📋 Method 1: Trying youtube-transcript-api...")
        
        # Add random delay to avoid detection
        time.sleep(random.uniform(1, 3))
        
        # Try to get English transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        
        # Combine all text
        transcript_text = ' '.join([entry['text'] for entry in transcript_list])
        
        # Clean up
        transcript_text = transcript_text.replace('\n', ' ')
        transcript_text = ' '.join(transcript_text.split())
        
        if transcript_text and len(transcript_text) >= 50:
            st.success("✅ Method 1 successful!")
            return transcript_text
        
        return None
        
    except TranscriptsDisabled:
        st.warning("⚠️ Method 1: Transcripts are disabled for this video")
        return None
    except NoTranscriptFound:
        st.warning("⚠️ Method 1: No English transcript found")
        return None
    except VideoUnavailable:
        st.warning("⚠️ Method 1: Video unavailable")
        return None
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "Too Many" in error_str:
            st.warning("⚠️ Method 1: Rate limited")
        else:
            st.warning(f"⚠️ Method 1 failed: {error_str[:100]}")
        return None


def get_transcript_method3(video_id):
    """Method 3: Direct YouTube Timedtext API access"""
    try:
        st.info("📋 Method 3: Trying direct timedtext API...")
        
        # First, get caption tracks
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.youtube.com/',
            'DNT': '1',
        }
        
        # Random delay
        time.sleep(random.uniform(2, 4))
        
        # Get video page
        response = requests.get(video_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            st.warning(f"⚠️ Method 3: HTTP {response.status_code}")
            return None
        
        # Look for caption tracks in the page
        page_content = response.text
        
        # Find captionTracks in the ytInitialPlayerResponse
        import re as regex
        pattern = r'"captionTracks":\s*(\[.*?\])'
        match = regex.search(pattern, page_content)
        
        if not match:
            st.warning("⚠️ Method 3: No caption tracks found")
            return None
        
        # Parse the caption tracks JSON
        caption_tracks_str = match.group(1)
        caption_tracks = json.loads(caption_tracks_str)
        
        # Find English caption
        caption_url = None
        for track in caption_tracks:
            if track.get('languageCode', '').startswith('en'):
                caption_url = track.get('baseUrl')
                break
        
        if not caption_url:
            st.warning("⚠️ Method 3: No English captions")
            return None
        
        # Fetch the caption
        time.sleep(random.uniform(1, 2))
        caption_response = requests.get(caption_url, headers=headers, timeout=15)
        
        if caption_response.status_code != 200:
            st.warning(f"⚠️ Method 3: Caption fetch failed ({caption_response.status_code})")
            return None
        
        # Parse XML captions
        root = ElementTree.fromstring(caption_response.content)
        text_parts = []
        
        for text_elem in root.findall('.//text'):
            text = text_elem.text
            if text:
                text_parts.append(text)
        
        result = ' '.join(text_parts).strip()
        result = result.replace('\n', ' ')
        result = ' '.join(result.split())
        
        if result and len(result) >= 50:
            st.success("✅ Method 3 successful!")
            return result
        
        return None
        
    except Exception as e:
        st.warning(f"⚠️ Method 3 failed: {str(e)[:100]}")
        return None


def get_transcript_method2(video_id):
    """Method 2: Use yt-dlp (most reliable and maintained)"""
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        # Random user agents to avoid detection
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        ]
        
        import tempfile
        import os as os_module
        
        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitlesformat': 'json3',
                'subtitleslangs': ['en', 'en-US', 'en-GB'],
                'outtmpl': os_module.path.join(temp_dir, '%(id)s.%(ext)s'),
                'quiet': False,  # Show output for debugging
                'no_warnings': False,
                'headers': {
                    'User-Agent': random.choice(user_agents),
                    'Accept-Language': 'en-US,en;q=0.9',
                },
            }
            
            # Add delay to avoid rate limiting
            time.sleep(random.uniform(1, 2))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if not info:
                    st.error("Failed to get video info")
                    return None
                
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                subtitle_url = None
                subtitle_type = None
                
                # Priority 1: Manual subtitles
                for lang in ['en', 'en-US', 'en-GB']:
                    if lang in subtitles:
                        st.info(f"📝 Found manual subtitles ({lang})")
                        for fmt in subtitles[lang]:
                            if fmt.get('ext') == 'json3':
                                subtitle_url = fmt['url']
                                subtitle_type = "manual"
                                break
                    if subtitle_url:
                        break
                
                # Priority 2: Auto-generated
                if not subtitle_url:
                    for lang in ['en', 'en-US', 'en-GB']:
                        if lang in automatic_captions:
                            st.info(f"📝 Found auto-generated subtitles ({lang})")
                            for fmt in automatic_captions[lang]:
                                if fmt.get('ext') == 'json3':
                                    subtitle_url = fmt['url']
                                    subtitle_type = "auto"
                                    break
                        if subtitle_url:
                            break
                
                if not subtitle_url:
                    st.warning("⚠️ No English subtitles found for this video")
                    return None
                
                # Download and parse subtitle
                st.info(f"⬇️ Downloading {subtitle_type} subtitles...")
                headers = {
                    'User-Agent': random.choice(user_agents),
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.youtube.com/',
                }
                
                time.sleep(random.uniform(1, 2))
                
                try:
                    response = requests.get(subtitle_url, headers=headers, timeout=30)
                    
                    if response.status_code == 429:
                        st.error("⚠️ Rate limited. Please wait 30 minutes and try again.")
                        return None
                    
                    if response.status_code != 200:
                        st.error(f"HTTP {response.status_code} error")
                        return None
                    
                    subtitle_data = response.json()
                    text_parts = []
                    
                    if 'events' in subtitle_data:
                        for event in subtitle_data['events']:
                            if 'segs' in event:
                                for seg in event['segs']:
                                    if 'utf8' in seg:
                                        text_parts.append(seg['utf8'])
                    
                    result = ' '.join(text_parts).strip()
                    result = result.replace('\n', ' ')
                    result = ' '.join(result.split())
                    
                    if result and len(result) >= 50:
                        st.success(f"✅ Successfully fetched transcript! ({subtitle_type}, {len(result)} chars)")
                        return result
                    else:
                        st.warning(f"⚠️ Transcript too short: {len(result)} characters")
                        return None
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"⚠️ Network error: {str(e)[:100]}")
                    return None
        
        return None
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            st.error("⚠️ Rate limited by YouTube")
        else:
            st.error(f"⚠️ Error: {error_msg[:150]}")
        return None


def get_transcript(video_id):
    """Fetch transcript using yt-dlp (most reliable method)"""
    
    st.info(f"🎬 Video ID: `{video_id}`")
    st.info("🔄 Fetching transcript using yt-dlp...")
    
    # Try yt-dlp method (most reliable)
    try:
        transcript = get_transcript_method2(video_id)
        if transcript:
            return transcript
    except Exception as e:
        st.warning(f"⚠️ yt-dlp error: {str(e)[:100]}")
    
    # Fallback: Try direct timedtext API
    try:
        st.info("🔄 Trying alternative method...")
        time.sleep(2)
        transcript = get_transcript_method3(video_id)
        if transcript:
            return transcript
    except Exception as e:
        st.warning(f"⚠️ Alternative method error: {str(e)[:100]}")
    
    # If all methods failed
    st.error("❌ **Failed to fetch transcript**")
    st.info("""
    💡 **Possible Issues:**
    
    1. **No Captions Available** 🚫
       - Check if the video has captions (CC button on YouTube)
       - Not all videos have subtitles enabled
    
    2. **Rate Limited** ⏰
       - If you tried multiple videos quickly, wait 15-30 minutes
       - Use mobile hotspot to test with different IP
    
    3. **Video Restrictions** 🔒
       - Video might be private, age-restricted, or deleted
       - Regional restrictions may apply
    
    4. **Try These Solutions:**
       - Wait 30 minutes and try again
       - Try a different popular video with confirmed captions
       - Check the video on YouTube directly
    """)
    
    return None


def download_and_parse_subtitle(subtitle_url, max_retries=3):
    """Download and parse subtitle from URL with retry logic"""
    import urllib.request
    import urllib.error
    
    for attempt in range(max_retries):
        try:
            # Add a small delay before each attempt (except the first)
            if attempt > 0:
                wait_time = (2 ** attempt) * 2  # Exponential backoff: 4s, 8s, 16s
                st.info(f"⏳ Waiting {wait_time} seconds before retry... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            
            # Download subtitle data with timeout and proper headers
            request = urllib.request.Request(
                subtitle_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'application/json',
                    'Accept-Language': 'en-US,en;q=0.9',
                }
            )
            
            with urllib.request.urlopen(request, timeout=20) as response:
                data = response.read().decode('utf-8')
                subtitle_data = json.loads(data)
            
            # Extract text from JSON3 format
            text_parts = []
            
            # Parse events structure
            if 'events' in subtitle_data:
                for event in subtitle_data['events']:
                    if 'segs' in event:
                        # Segments contain the actual text
                        for seg in event['segs']:
                            if 'utf8' in seg:
                                text_parts.append(seg['utf8'])
            
            # Join all text parts
            result = ' '.join(text_parts).strip()
            
            # Clean up common subtitle artifacts
            result = result.replace('\n', ' ')
            result = ' '.join(result.split())  # Remove extra whitespace
            
            # Only return if we got meaningful text (at least 50 characters)
            if result and len(result) >= 50:
                return result
            else:
                st.warning(f"⚠️ Subtitle text too short: {len(result) if result else 0} characters")
                return None
                
        except json.JSONDecodeError as e:
            st.error(f"❌ Failed to parse subtitle JSON: {str(e)[:100]}")
            return None
            
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Too Many Requests
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ Rate limited by YouTube (HTTP 429). Retrying with exponential backoff...")
                    continue
                else:
                    st.error("❌ **YouTube Rate Limit Exceeded**")
                    st.info("💡 **Please wait 5-10 minutes before trying again.**\n\n"
                           "YouTube limits how many subtitle requests can be made in a short time. "
                           "This is temporary and will reset automatically.")
                    return None
            else:
                st.error(f"❌ HTTP Error {e.code}: {str(e)[:100]}")
                return None
                
        except urllib.error.URLError as e:
            st.error(f"❌ Failed to download subtitle: {str(e)[:100]}")
            return None
            
        except Exception as e:
            st.error(f"❌ Subtitle extraction error: {str(e)[:100]}")
            return None
    
    return None


def generate_summary(transcript):
    """Generate an executive summary using Gemini"""
    prompt = f"""You are a professional content analyst. Please provide a concise executive summary of the following video transcript.

Focus on:
- Main topic and key points
- Important insights or arguments
- Any actionable takeaways

Transcript:
{transcript[:15000]}  # Limit to avoid token limits

Please provide a summary in 3-5 paragraphs."""
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        
        # Handle new response structure
        if hasattr(response, 'text'):
            return response.text
        elif response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            st.error("❌ Unexpected response format from Gemini API")
            return None
            
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Error generating summary: {error_msg}")
        
        if "credentials" in error_msg.lower() or "authentication" in error_msg.lower():
            st.warning("⚠️ **API Authentication Issue**")
            st.info("""
            Please check:
            1. Your GOOGLE_API_KEY is correctly set in the .env file
            2. The API key is valid and active
            3. Get your API key from: https://makersuite.google.com/app/apikey
            """)
        
        return None


def ask_question(transcript, question, chat_history):
    """Answer questions based on the video transcript"""
    # Build context with chat history
    context = "Previous conversation:\n"
    for msg in chat_history[-5:]:  # Last 5 messages for context
        context += f"{msg['role']}: {msg['content']}\n"
    
    prompt = f"""You are TubeMind, an AI assistant that helps users understand YouTube video content.

Video Transcript:
{transcript[:20000]}  # Limit to avoid token limits

{context}

User Question: {question}

Instructions:
- Answer based ONLY on the information present in the transcript
- Be concise and specific
- If the information is not in the transcript, say so
- Use bullet points for lists when appropriate

Answer:"""
    
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        
        # Handle new response structure
        if hasattr(response, 'text'):
            return response.text
        elif response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            st.error("❌ Unexpected response format from Gemini API")
            return None
            
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Error generating response: {error_msg[:200]}")
        
        if "credentials" in error_msg.lower() or "authentication" in error_msg.lower():
            st.info("⚠️ API authentication issue. Check your GOOGLE_API_KEY in .env file.")
        
        return None


# Initialize session state
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'video_id' not in st.session_state:
    st.session_state.video_id = None
if 'transcript_cache' not in st.session_state:
    st.session_state.transcript_cache = {}  # Cache transcripts by video_id


# Header - clean professional styling
st.markdown('<div class="main-header">TubeMind</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Video Intelligence</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### About TubeMind")
    st.markdown("""
    Transform YouTube videos into interactive learning experiences with AI.
    """)
    
    st.markdown("---")
    
    st.markdown("**How to Use**")
    st.markdown("""
    1. Paste a YouTube URL
    2. Click Process Video
    3. Read the AI summary
    4. Ask questions!
    """)
    
    st.markdown("---")
    
    st.markdown("**Powered By**")
    st.markdown("""
    • Google Gemini AI  
    • yt-dlp  
    • Streamlit
    """)
    
    # Session stats
    if st.session_state.transcript:
        st.markdown("---")
        st.markdown("**Session Stats**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Videos", len(st.session_state.transcript_cache))
        with col2:
            st.metric("Messages", len(st.session_state.chat_history))
    
    st.markdown("---")
    
    if st.button("Clear Session", use_container_width=True):
        st.session_state.transcript = None
        st.session_state.summary = None
        st.session_state.chat_history = []
        st.session_state.video_id = None
        st.session_state.transcript_cache = {}
        st.rerun()

# Main content with better layout
if not st.session_state.video_id:
    st.markdown("### Get Started")
    st.markdown("Enter a YouTube URL to generate AI summaries and chat with your video")
else:
    st.markdown("### Process Another Video")

col1, col2 = st.columns([3, 1])

with col1:
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="visible"
    )

with col2:
    st.write("")  # Spacing for alignment
    st.write("")  # Spacing for alignment
    process_button = st.button("Process Video", use_container_width=True, type="primary")

# Welcome message when no video is loaded
if not st.session_state.video_id:
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>⚡</div>
            <h3 class='feature-title'>Lightning Fast</h3>
            <p class='feature-desc'>Get instant AI summaries of any YouTube video</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>🤖</div>
            <h3 class='feature-title'>AI-Powered</h3>
            <p class='feature-desc'>Powered by Google Gemini for intelligent insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='feature-card'>
            <div class='feature-icon'>💬</div>
            <h3 class='feature-title'>Interactive Chat</h3>
            <p class='feature-desc'>Ask questions and get context-aware answers</p>
        </div>
        """, unsafe_allow_html=True)

# Process video when button is clicked
if process_button and youtube_url:
    video_id = extract_video_id(youtube_url)
    
    if video_id:
        # Create a container for processing status
        status_container = st.container()
        
        with status_container:
            # Check cache first
            if video_id in st.session_state.transcript_cache:
                st.info(f"🎬 Video ID: `{video_id}`")
                st.success("⚡ Loading from cache - instant!")
                transcript = st.session_state.transcript_cache[video_id]
            else:
                with st.status("🔄 Processing video...", expanded=True) as status:
                    st.write("📥 Fetching transcript...")
                    transcript = get_transcript(video_id)
                    
                    # Cache the transcript if successful
                    if transcript:
                        st.session_state.transcript_cache[video_id] = transcript
                        st.write("✅ Transcript retrieved!")
                        
                        st.write("🧠 Generating AI summary...")
                        summary = generate_summary(transcript)
                        st.session_state.summary = summary
                        st.write("✅ Summary complete!")
                        
                        status.update(label="✅ Processing complete!", state="complete", expanded=False)
        
        if transcript:
            st.session_state.transcript = transcript
            st.session_state.video_id = video_id
            st.session_state.chat_history = []  # Reset chat on new video
            
            # Only generate summary if not cached
            if video_id not in st.session_state.transcript_cache or not st.session_state.summary:
                with st.spinner("🧠 Generating AI summary..."):
                    summary = generate_summary(transcript)
                    st.session_state.summary = summary
            
            st.balloons()
            st.success("Video ready! Scroll down to see the summary and start chatting.")
            st.rerun()
    else:
        st.error("Invalid YouTube URL. Please check the format and try again.")

# Display video if available
if st.session_state.video_id:
    st.markdown("---")
    
    # Embed YouTube video - medium sized and centered
    st.subheader("Video Preview")
    
    # Use columns to control video size - 50% of width
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.video(f"https://www.youtube.com/watch?v={st.session_state.video_id}")

# Chat interface - shows summary first, then Q&A in order
if st.session_state.transcript:
    st.markdown("---")
    st.subheader("Chat")
    
    # Display executive summary first if available
    if st.session_state.summary:
        st.markdown('<div class="summary-box"><strong>Summary</strong><br><br>{}</div>'.format(st.session_state.summary), unsafe_allow_html=True)
    
    # Display chat history using Streamlit's native chat message components
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
    
    # Chat input at the bottom - uses native Streamlit chat input (NO RERUN NEEDED!)
    user_question = st.chat_input("Ask anything about this video...")
    
    if user_question:
        # Add user question to chat history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_question
        })
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(
                    st.session_state.transcript,
                    user_question,
                    st.session_state.chat_history
                )
            
            if answer:
                st.markdown(answer)
                # Add AI response to chat history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': answer
                })
    
    # Footer inside chat section - appears above chat input
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center; color: #a1a1aa; padding: 1rem 0; font-size: 0.85rem; border-top: 1px solid #3f3f46;'>"
        "Built with ❤️ using <strong style='color: #d4d4d8;'>Streamlit</strong> & <strong style='color: #d4d4d8;'>Google Gemini AI</strong><br>"
        "<span style='color: #a1a1aa; font-size: 0.8rem;'>Developed by Mert Toprak © 2025</span>"
        "</div>",
        unsafe_allow_html=True
    )

# Footer for when no video is loaded
if not st.session_state.video_id:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: center; color: #a1a1aa; padding: 1.5rem 0; font-size: 0.85rem; border-top: 1px solid #3f3f46;'>"
        "Built with ❤️ using <strong style='color: #d4d4d8;'>Streamlit</strong> & <strong style='color: #d4d4d8;'>Google Gemini AI</strong><br>"
        "<span style='color: #a1a1aa; font-size: 0.8rem;'>Developed by Mert Toprak © 2025</span>"
        "</div>",
        unsafe_allow_html=True
    )
