import streamlit as st
from transformers import pipeline
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.genai.errors import ClientError
import re
import time
from datetime import datetime
import pandas as pd

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="SafeGuard AI - Cyberbullying Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== PROFESSIONAL CSS ==================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }
    
    /* Hero Section */
    .hero-section {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 3rem 2.5rem;
        border-radius: 20px;
        margin-bottom: 2.5rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 15s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        color: white;
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        line-height: 1.2;
    }
    
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.25rem;
        margin-top: 1rem;
        font-weight: 400;
    }
    
    .hero-features {
        display: flex;
        gap: 2rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    
    .feature-badge {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        padding: 0.75rem 1.5rem;
        border-radius: 50px;
        color: white;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Dashboard Cards */
    .dashboard-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .dashboard-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .card-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a202c;
        margin: 0;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stat-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: translateX(-100%);
    }
    
    .stat-box:hover::before {
        animation: shimmer 1.5s ease-in-out;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stat-label {
        font-size: 0.95rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-box.danger {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }
    
    .stat-box.success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
    }
    
    .stat-box.warning {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        box-shadow: 0 4px 15px rgba(254, 225, 64, 0.4);
    }
    
    /* Result Cards */
    .result-item {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .result-item:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        transform: translateX(4px);
    }
    
    .result-item.threat {
        border-left-color: #dc2626;
        background: linear-gradient(to right, #fef2f2 0%, white 100%);
    }
    
    .result-item.negative {
        border-left-color: #f97316;
        background: linear-gradient(to right, #fff7ed 0%, white 100%);
    }
    
    .result-item.positive {
        border-left-color: #10b981;
        background: linear-gradient(to right, #f0fdf4 0%, white 100%);
    }
    
    .result-item.neutral {
        border-left-color: #6b7280;
        background: linear-gradient(to right, #f9fafb 0%, white 100%);
    }
    
    .comment-content {
        font-size: 1.05rem;
        color: #1f2937;
        line-height: 1.7;
        margin-bottom: 1rem;
    }
    
    .translation-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%);
        border-left: 3px solid #0284c7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .translation-header {
        font-size: 0.85rem;
        color: #0369a1;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .translation-text {
        color: #0c4a6e;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Tags */
    .tag-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .tag {
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .tag-threat {
        background: #dc2626;
        color: white;
    }
    
    .tag-negative {
        background: #f97316;
        color: white;
    }
    
    .tag-positive {
        background: #10b981;
        color: white;
    }
    
    .tag-neutral {
        background: #6b7280;
        color: white;
    }
    
    .tag-info {
        background: #f3f4f6;
        color: #374151;
        border: 1px solid #d1d5db;
    }
    
    /* Input Styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .sidebar-content {
        padding: 1rem;
    }
    
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid rgba(255,255,255,0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #6b7280;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    /* Report Section */
    .report-card {
        background: linear-gradient(135deg, #fef2f2 0%, white 100%);
        border: 2px solid #fca5a5;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .report-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .report-timestamp {
        color: #991b1b;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: #6b7280;
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""", unsafe_allow_html=True)

# ================== API CONFIGURATION ==================
GEMINI_API_KEY = "AIzaSyCJU2Tb-jDwQQPhgSIBYqntOh4En0EGf0U"
YOUTUBE_API_KEY = "AIzaSyDtn_KClWO6QZQp4loBvzJ6VbnGyxO63IM"

# ================== LOAD MODELS ==================
@st.cache_resource
def load_models():
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-xlm-roberta-base-sentiment"
    )
    return gemini_model, youtube, sentiment_pipeline

gemini_model, youtube, sentiment_pipeline = load_models()

# ================== KEYWORDS DATABASE ==================
ABUSE_KEYWORDS = {
    "HATE_SPEECH": [
        "kill", "die", "death", "murdered", "execute", "slaughter", "eliminate",
        "kms", "kys", "hang yourself", "shoot yourself", "jump off",
        "terrorist", "nazi", "supremacist", "subhuman", "vermin", "scum",
        "racist", "sexist", "homophobe", "bigot", "hatred",
        "konnu", "kolai", "savu", "sethu", "kollanum",
        "maro", "maar dalo", "khatam karo", "nafrat"
    ],
    "VULGAR": [
        "fuck", "fucking", "fucked", "fucker", "motherfucker", "mf",
        "shit", "shitty", "bullshit", "crap", "damn", "bitch", "bastard",
        "asshole", "ass", "dickhead", "dick", "cock", "pussy", "cunt",
        "whore", "slut", "hoe", "prostitute", "pimp",
        "punda", "punde", "pundai", "oombu", "otha", "oothu",
        "thevdiya", "thevidiya", "lavuda", "lavde", "koodhi", "koothhi",
        "sunni", "soothu", "olu", "poolu", "pundamavan",
        "kena", "kenna", "poda", "podi", "loosu koodhi",
        "chutiya", "chut", "loda", "lund", "bhosdi", "bhosad",
        "behen chod", "maa chod", "gandu", "madarchod", "mc", "bc",
        "randi", "kutti", "kamina", "harami", "saala", "kutte"
    ],
    "ABUSIVE": [
        "idiot", "stupid", "dumb", "dumbass", "moron", "imbecile",
        "retard", "retarded", "mental", "braindead", "brainless",
        "ignorant", "fool", "foolish", "pathetic", "worthless",
        "ugly", "hideous", "disgusting", "gross", "fat", "fatso",
        "pig", "animal", "monkey", "dog", "donkey",
        "loosu", "lusu", "paithiyam", "mayiru", "panni",
        "naaye", "kutta", "eruma", "madayan", "muttaal",
        "vedippu", "mokka", "waste", "useless",
        "pagal", "bewakoof", "ullu", "gadha", "kutta",
        "suar", "janwar", "nalayak", "nikamma", "faltu"
    ],
    "THREAT": [
        "shoot", "stab", "bomb", "attack", "assault", "beat",
        "murder", "kill you", "hurt you", "harm you", "destroy you",
        "rape", "molest", "kidnap", "torture", "burn",
        "watch out", "i'll get you", "you're dead", "i'll find you",
        "smash", "crush", "break your", "bash", "punch", "kick",
        "adippan", "adippen", "vekkaren", "kolrean", "kuthuren"
    ],
    "HARASSMENT": [
        "loser", "nobody", "failure", "reject", "waste of space",
        "go away", "get lost", "disappear", "no one likes you",
        "everyone hates you", "kill yourself",
        "unwanted", "not welcome", "freak", "weirdo", "creep",
        "veliya po", "theva illa", "shut up", "get cancer"
    ],
    "TOXIC": [
        "whatever", "who cares", "stfu", "gtfo",
        "nobody asked", "didn't ask", "don't care",
        "cringe", "trash", "garbage", "terrible",
        "ez", "noob", "git gud", "cope", "stay mad"
    ]
}

SEVERITY_WEIGHTS = {
    "HATE_SPEECH": 10,
    "THREAT": 9,
    "HARASSMENT": 7,
    "VULGAR": 6,
    "ABUSIVE": 5,
    "TOXIC": 3
}

# ================== SESSION STATE ==================
if 'results' not in st.session_state:
    st.session_state.results = []
if 'reported_comments' not in st.session_state:
    st.session_state.reported_comments = set()
if 'reports' not in st.session_state:
    st.session_state.reports = []

# ================== HELPER FUNCTIONS ==================
def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    return text.strip()

def normalize_text(text):
    text = text.lower().strip()
    replacements = {
        '@': 'a', '4': 'a', '3': 'e', '1': 'i', '!': 'i',
        '0': 'o', '$': 's', '7': 't', '+': 't', '5': 's'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)
    return text

def extract_video_id(url):
    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?&]+)",
        r"youtube\.com/shorts/([^?&]+)"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def get_youtube_comments(video_id, max_results=20):
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            textFormat="plainText"
        ).execute()
        return [item["snippet"]["topLevelComment"]["snippet"]["textDisplay"] 
                for item in response.get("items", [])]
    except HttpError as e:
        st.error(f"YouTube API Error: {str(e)}")
        return []

def detect_and_translate(text):
    try:
        has_non_ascii = any(ord(char) > 127 for char in text)
        tamil_patterns = ['pa', 'da', 'la', 'nga', 'tha', 'poda', 'loosu', 'nalla', 'enna', 'illa']
        has_tamil = any(p in text.lower() for p in tamil_patterns)
        
        if has_non_ascii or has_tamil:
            prompt = f"""Detect language and translate to English:
Text: "{text}"

Format:
LANGUAGE: [language name]
TRANSLATION: [English translation]"""
            
            response = gemini_model.generate_content(prompt)
            result = response.text.strip()
            
            language = "Unknown"
            translation = text
            
            for line in result.split('\n'):
                if 'LANGUAGE:' in line:
                    language = line.split('LANGUAGE:')[1].strip()
                elif 'TRANSLATION:' in line:
                    translation = line.split('TRANSLATION:')[1].strip()
            
            return True, translation, language
        return False, text, "English"
    except:
        return False, text, "English"

def keyword_classify(text):
    text_norm = normalize_text(text)
    for category in ["HATE_SPEECH", "THREAT", "HARASSMENT", "VULGAR", "ABUSIVE", "TOXIC"]:
        if category in ABUSE_KEYWORDS:
            for keyword in ABUSE_KEYWORDS[category]:
                if normalize_text(keyword) in text_norm:
                    severity = SEVERITY_WEIGHTS.get(category, 0)
                    return f"Negative - {category.replace('_', ' ').title()}", keyword, severity
    return "UNKNOWN", None, 0

def gemini_classify(text):
    try:
        response = gemini_model.generate_content(
            f"""Classify into ONE category: Positive, Neutral, Negative - Hate Speech, Negative - Vulgar, Negative - Abusive, Negative - Threat, Negative - Harassment, Negative - Toxic

Comment: "{text}"

Category:"""
        )
        return response.text.strip()
    except:
        return "Neutral"

def hybrid_classify(text):
    cleaned = clean_text(text)
    is_translated, translated, language = detect_and_translate(cleaned)
    category, keyword, severity = keyword_classify(cleaned)
    
    if category == "UNKNOWN" and is_translated:
        category, keyword, severity = keyword_classify(translated)
    
    result = {
        "original_text": text,
        "is_translated": is_translated,
        "translated_text": translated if is_translated else None,
        "detected_language": language,
        "category": category,
        "matched_keyword": keyword,
        "severity_score": severity,
        "confidence": 0.0,
        "method": "keyword"
    }
    
    if category != "UNKNOWN" and severity >= 7:
        result["confidence"] = 0.95
        return result
    
    try:
        analyze_text = translated if is_translated else cleaned
        ml_result = sentiment_pipeline(analyze_text[:512])[0]
        
        if ml_result["label"] == "POSITIVE" and ml_result["score"] > 0.8:
            result["category"] = "Positive"
            result["confidence"] = ml_result["score"]
            result["method"] = "ml"
            return result
        
        if ml_result["label"] == "NEGATIVE" and ml_result["score"] > 0.75:
            if category != "UNKNOWN":
                result["confidence"] = ml_result["score"]
                result["method"] = "hybrid"
            else:
                result["category"] = "Negative - Abusive"
                result["confidence"] = ml_result["score"]
                result["method"] = "ml"
            return result
    except:
        pass
    
    if category == "UNKNOWN":
        result["category"] = gemini_classify(translated if is_translated else cleaned)
        result["confidence"] = 0.7
        result["method"] = "ai"
    
    return result

def report_comment(comment_id, comment_text, category, reason):
    if comment_id not in st.session_state.reported_comments:
        st.session_state.reported_comments.add(comment_id)
        st.session_state.reports.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comment": comment_text,
            "category": category,
            "reason": reason
        })
        return True
    return False

# ================== MAIN APP ==================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-content">
            <div class="sidebar-title">🛡️ SafeGuard AI</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚙️ Settings")
        st.markdown("---")
        
        st.markdown("**Analysis Mode**")
        analysis_mode = st.radio(
            "mode",
            ["Standard", "Deep Analysis", "Quick Scan"],
            label_visibility="collapsed"
        )
        
        st.markdown("**Language Support**")
        st.checkbox("Auto-detect language", value=True)
        st.checkbox("Enable translation", value=True)
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.info("SafeGuard AI uses advanced ML and AI to detect cyberbullying in real-time across multiple languages.")
        
        st.markdown("---")
        st.caption("© 2026 SafeGuard AI")
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">SafeGuard AI</h1>
            <p class="hero-subtitle">Advanced Cyberbullying Detection & Prevention Platform</p>
            <div class="hero-features">
                <div class="feature-badge">🤖 AI-Powered Analysis</div>
                <div class="feature-badge">🌍 Multi-Language Support</div>
                <div class="feature-badge">⚡ Real-time Detection</div>
                <div class="feature-badge">📊 Advanced Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Tabs
    tab1, tab2, tab3 = st.tabs(["📺 YouTube Analysis", "📝 Text Analysis", "📋 Reports & Insights"])
    
    # ========== TAB 1: YOUTUBE ==========
    with tab1:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-header">
                <div class="card-icon">📺</div>
                <h2 class="card-title">YouTube Video Analysis</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            youtube_url = st.text_input(
                "YouTube Video URL",
                placeholder="https://youtube.com/watch?v=... or https://youtu.be/...",
                label_visibility="collapsed"
            )
        with col2:
            max_comments = st.number_input(
                "Max Comments",
                min_value=5,
                max_value=100,
                value=20,
                label_visibility="collapsed"
            )
        
        if st.button("🔍 Analyze Comments", type="primary", use_container_width=True):
            if youtube_url:
                video_id = extract_video_id(youtube_url)
                if video_id:
                    with st.spinner("🔄 Fetching and analyzing comments..."):
                        comments = get_youtube_comments(video_id, max_comments)
                    
                    if comments:
                        st.success(f"✅ Successfully fetched {len(comments)} comments")
                        results = []
                        progress = st.progress(0)
                        status_text = st.empty()
                        
                        for i, comment in enumerate(comments):
                            status_text.text(f"Analyzing comment {i+1} of {len(comments)}...")
                            result = hybrid_classify(comment)
                            result["comment_id"] = f"yt_{i}"
                            results.append(result)
                            progress.progress((i + 1) / len(comments))
                        
                        st.session_state.results = results
                        progress.empty()
                        status_text.empty()
                        st.balloons()
                    else:
                        st.warning("⚠️ No comments found for this video")
                else:
                    st.error("❌ Invalid YouTube URL. Please check and try again.")
            else:
                st.warning("⚠️ Please enter a YouTube URL")
    
    # ========== TAB 2: TEXT ==========
    with tab2:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-header">
                <div class="card-icon">📝</div>
                <h2 class="card-title">Text Analysis</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        user_text = st.text_area(
            "Enter text to analyze",
            height=150,
            placeholder="Type or paste any comment here... Supports English, Tamil, Hindi, and more languages...",
            label_visibility="collapsed"
        )
        
        if st.button("🔍 Analyze Text", type="primary", use_container_width=True):
            if user_text.strip():
                with st.spinner("🔄 Analyzing..."):
                    result = hybrid_classify(user_text)
                    result["comment_id"] = "text_0"
                    st.session_state.results = [result]
                st.success("✅ Analysis complete!")
            else:
                st.warning("⚠️ Please enter some text to analyze")
    
    # ========== TAB 3: REPORTS ==========
    with tab3:
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-header">
                <div class="card-icon">📋</div>
                <h2 class="card-title">Reports & Insights</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.reports:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.metric("Total Reports", len(st.session_state.reports))
            with col3:
                if st.button("📥 Download CSV", use_container_width=True):
                    df = pd.DataFrame(st.session_state.reports)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "⬇️ Download Report",
                        csv,
                        f"cyberbully_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        "text/csv",
                        use_container_width=True
                    )
            
            st.markdown("---")
            
            for report in reversed(st.session_state.reports):
                st.markdown(f"""
                <div class="report-card">
                    <div class="report-header">
                        <span class="tag tag-threat">{report['category']}</span>
                        <span class="report-timestamp">📅 {report['timestamp']}</span>
                    </div>
                    <div class="comment-content">{report['comment']}</div>
                    <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #fca5a5;">
                        <strong style="color: #991b1b;">Reason:</strong> {report['reason']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <h3>No Reports Yet</h3>
                <p>Reported comments will appear here</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ========== DISPLAY RESULTS ==========
    if st.session_state.results:
        st.markdown("---")
        
        # Statistics
        total = len(st.session_state.results)
        negative = sum(1 for r in st.session_state.results if "Negative" in r["category"])
        positive = sum(1 for r in st.session_state.results if r["category"] == "Positive")
        neutral = sum(1 for r in st.session_state.results if r["category"] == "Neutral")
        translated = sum(1 for r in st.session_state.results if r.get("is_translated"))
        threats = sum(1 for r in st.session_state.results if "Threat" in r["category"] or "Hate Speech" in r["category"])
        
        st.markdown("""
        <div class="dashboard-card">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <h2 class="card-title">Analysis Dashboard</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{total}</div>
                <div class="stat-label">Total Comments</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-box danger">
                <div class="stat-number">{negative}</div>
                <div class="stat-label">Negative</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-box success">
                <div class="stat-number">{positive}</div>
                <div class="stat-label">Positive</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stat-box warning">
                <div class="stat-number">{neutral}</div>
                <div class="stat-label">Neutral</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="stat-box">
                <div class="stat-number">{translated}</div>
                <div class="stat-label">Translated</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Filter Section
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            filter_option = st.selectbox(
                "🔍 Filter Results",
                ["All Comments", "Negative Only", "Positive Only", "Neutral Only", "Translated Only", "High Severity (Threats & Hate Speech)"]
            )
        with col2:
            if st.button("🔄 Clear Results"):
                st.session_state.results = []
                st.rerun()
        
        st.markdown("---")
        
        # Display results
        filtered_count = 0
        for idx, result in enumerate(st.session_state.results):
            # Apply filter
            if filter_option == "Negative Only" and "Negative" not in result["category"]:
                continue
            if filter_option == "Positive Only" and result["category"] != "Positive":
                continue
            if filter_option == "Neutral Only" and result["category"] != "Neutral":
                continue
            if filter_option == "Translated Only" and not result.get("is_translated"):
                continue
            if filter_option == "High Severity (Threats & Hate Speech)" and not ("Threat" in result["category"] or "Hate Speech" in result["category"]):
                continue
            
            filtered_count += 1
            
            # Determine card class
            if "Threat" in result["category"] or "Hate Speech" in result["category"]:
                card_class = "threat"
                tag_class = "tag-threat"
            elif "Negative" in result["category"]:
                card_class = "negative"
                tag_class = "tag-negative"
            elif result["category"] == "Positive":
                card_class = "positive"
                tag_class = "tag-positive"
            else:
                card_class = "neutral"
                tag_class = "tag-neutral"
            
            # Build result card
            st.markdown(f"""
            <div class="result-item {card_class}">
                <div class="comment-content">"{result["original_text"]}"</div>
            """, unsafe_allow_html=True)
            
            # Translation box
            if result.get("is_translated"):
                st.markdown(f"""
                <div class="translation-box">
                    <div class="translation-header">🌐 {result["detected_language"]} → English</div>
                    <div class="translation-text">"{result["translated_text"]}"</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Tags
            st.markdown('<div class="tag-container">', unsafe_allow_html=True)
            st.markdown(f'<span class="tag {tag_class}">{result["category"]}</span>', unsafe_allow_html=True)
            
            if result.get("severity_score"):
                severity_emoji = "🔴" if result["severity_score"] >= 8 else "🟡" if result["severity_score"] >= 5 else "🟢"
                st.markdown(f'<span class="tag tag-info">{severity_emoji} Severity: {result["severity_score"]}/10</span>', unsafe_allow_html=True)
            
            if result.get("matched_keyword"):
                st.markdown(f'<span class="tag tag-info">🎯 Keyword: "{result["matched_keyword"]}"</span>', unsafe_allow_html=True)
            
            if result.get("confidence"):
                st.markdown(f'<span class="tag tag-info">📈 Confidence: {result["confidence"]:.0%}</span>', unsafe_allow_html=True)
            
            st.markdown(f'<span class="tag tag-info">🔧 Method: {result.get("method", "N/A").upper()}</span>', unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Report button for negative comments
            if "Negative" in result["category"]:
                is_reported = result.get("comment_id") in st.session_state.reported_comments
                
                if not is_reported:
                    with st.expander("🚨 Report this comment"):
                        reason = st.text_input(
                            "Why are you reporting this comment?",
                            key=f"reason_{idx}",
                            placeholder="Enter your reason..."
                        )
                        
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if st.button("Submit Report", key=f"submit_{idx}", type="primary"):
                                if reason.strip():
                                    if report_comment(
                                        result.get("comment_id"),
                                        result["original_text"],
                                        result["category"],
                                        reason
                                    ):
                                        st.success("✅ Report submitted successfully!")
                                        time.sleep(1)
                                        st.rerun()
                                else:
                                    st.warning("⚠️ Please provide a reason for reporting")
                else:
                    st.markdown("✅ **Already Reported**")
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        if filtered_count == 0:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-icon">🔍</div>
                <h3>No Results Found</h3>
                <p>No comments match your current filter</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: white; padding: 2rem;">
        <p style="font-size: 0.9rem; opacity: 0.8;">
            © 2026 SafeGuard AI - Cyberbullying Detection & Prevention Platform<br>
            Powered by Google Gemini AI, Transformers ML, and YouTube Data API
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()