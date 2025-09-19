import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import requests
import time

# Import existing modules
from models import BlogPost, get_db, create_tables
from blog_monitor import BlogMonitor
from ai_summarizer import AISummarizer
from content_intelligence import ContentIntelligence
from config import BLOG_URLS, AI_KEYWORDS

# Initialize services
@st.cache_resource
def init_services():
    return {
        'blog_monitor': BlogMonitor(),
        'ai_summarizer': AISummarizer(),
        'content_intelligence': ContentIntelligence()
    }

# Initialize session state
if 'fresh_posts' not in st.session_state:
    st.session_state.fresh_posts = []
if 'editing_posts' not in st.session_state:
    st.session_state.editing_posts = set()
if 'copied_posts' not in st.session_state:
    st.session_state.copied_posts = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Page config
st.set_page_config(
    page_title="AI LinkedIn Post Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS styling with enhanced visual design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .main {
        background: transparent;
    }
    
    /* Typography */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #2c3e50 !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Hero header text override */
    .hero-container * {
        color: white !important;
    }
    
    .hero-container p {
        color: white !important;
    }
    
    .hero-container .stMarkdown p {
        color: white !important;
    }
    
    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #667eea 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .hero-title {
        color: white !important;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        color: white !important;
        font-size: 1.2rem;
        margin: 1rem 0 0 0;
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle * {
        color: white !important;
    }
    
    .hero-stats {
        display: flex;
        gap: 2rem;
        margin-top: 2rem;
        position: relative;
        z-index: 1;
    }
    
    .hero-stat {
        text-align: center;
        color: white !important;
    }
    
    .hero-stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        display: block;
        color: white !important;
    }
    
    .hero-stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
        color: white !important;
    }
    
    .hero-container .hero-stat-label {
        color: white !important;
    }
    
    .hero-container .hero-stat-number {
        color: white !important;
    }
    
    /* Navigation */
    .nav-pills {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 0.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Enhanced Cards */
    .glass-card {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
        border-radius: 20px 20px 0 0;
    }
    
    .glass-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    }
    
    .card-title {
        color: #2c3e50 !important;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-content {
        color: #5a6c7d !important;
        line-height: 1.7;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        font-weight: 600;
    }
    
    /* LinkedIn Post Styling */
    .linkedin-post {
        background: linear-gradient(135deg, #f8faff 0%, #e8f2ff 100%);
        border: 2px solid #e3f2fd;
        border-left: 6px solid #0077b5;
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
        line-height: 1.8;
        color: #2c3e50 !important;
        box-shadow: 0 4px 20px rgba(0,119,181,0.1);
        position: relative;
    }
    
    .linkedin-post::before {
        content: '💼';
        position: absolute;
        top: 1rem;
        right: 1.5rem;
        font-size: 1.5rem;
        opacity: 0.3;
    }
    
    /* Enhanced Metrics */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102,126,234,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        transform: rotate(45deg);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 40px rgba(102,126,234,0.4);
    }
    
    .metric-card:hover::before {
        transform: rotate(45deg) translate(20px, 20px);
    }
    
    .metric-number {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        font-family: 'Inter', sans-serif;
        color: white !important;
        position: relative;
        z-index: 1;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.95;
        font-family: 'Inter', sans-serif;
        color: white !important;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    /* Enhanced Buttons */
    .stButton > button {
        border-radius: 12px;
        border: none;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.95rem;
        padding: 0.75rem 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
        color: white !important;
        border: 2px solid #ff6b6b !important;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ff5252 0%, #d63031 100%) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6) !important;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .status-approved {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724 !important;
        border: 1px solid #c3e6cb;
    }
    
    .status-posted {
        background: linear-gradient(135deg, #cce7ff 0%, #b3d9ff 100%);
        color: #004085 !important;
        border: 1px solid #b3d9ff;
    }
    
    /* Copy Container */
    .copy-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 2px solid #dee2e6;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    .copy-text {
        background: white;
        border: 1px solid #ced4da;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        color: #2c3e50 !important;
        white-space: pre-wrap;
        word-wrap: break-word;
        max-height: 250px;
        overflow-y: auto;
        line-height: 1.6;
    }
    
    /* Loading Animation */
    .loading-pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2rem;
        }
        
        .hero-subtitle {
            font-size: 1rem;
        }
        
        .glass-card {
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        .metric-number {
            font-size: 2rem;
        }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
</style>
""", unsafe_allow_html=True)

# Initialize database and services
create_tables()
services = init_services()

# Hero Header with Stats
db = next(get_db())
total_posts = db.query(BlogPost).count()
approved_count = db.query(BlogPost).filter(BlogPost.is_approved == True).count()
posted_count = db.query(BlogPost).filter(BlogPost.is_posted == True).count()
db.close()

st.markdown(f"""
<div class="hero-container">
    <h1 class="hero-title">🚀 AI LinkedIn Post Generator</h1>
    <p class="hero-subtitle">Transform AI/ML content into engaging LinkedIn posts</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-number">{total_posts}</span>
            <span class="hero-stat-label">Total Posts</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">{approved_count}</span>
            <span class="hero-stat-label">Approved</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">{posted_count}</span>
            <span class="hero-stat-label">Published</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">{len(BLOG_URLS)}</span>
            <span class="hero-stat-label">Sources</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Feature boxes below hero header
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 1rem; border-radius: 12px; text-align: center; margin: 0.5rem 0;">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem; color: white !important;">⚡</div>
        <div style="font-size: 0.9rem; color: white !important;">AI Powered</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 1rem; border-radius: 12px; text-align: center; margin: 0.5rem 0;">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem; color: white !important;">🎯</div>
        <div style="font-size: 0.9rem; color: white !important;">Smart Filtering</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 12px; text-align: center; margin: 0.5rem 0;">
        <div style="font-size: 1.5rem; margin-bottom: 0.3rem;">🚀</div>
        <div style="font-size: 0.9rem;">Ready to Post</div>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Navigation Menu
st.markdown("""
<div class="nav-pills">
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    if st.button("📊 Dashboard", use_container_width=True, type="primary" if st.session_state.current_page == "Dashboard" else "secondary"):
        st.session_state.current_page = "Dashboard"
        st.rerun()

with col2:
    if st.button("⚡ Quick Generate", use_container_width=True, type="primary" if st.session_state.current_page == "Quick" else "secondary"):
        st.session_state.current_page = "Quick"
        st.rerun()

with col3:
    if st.button("✅ Approved Posts", use_container_width=True, type="primary" if st.session_state.current_page == "Approved" else "secondary"):
        st.session_state.current_page = "Approved"
        st.rerun()

with col4:
    if st.button("📈 Analytics", use_container_width=True, type="primary" if st.session_state.current_page == "Analytics" else "secondary"):
        st.session_state.current_page = "Analytics"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Page Content Based on Navigation
if st.session_state.current_page == "Dashboard":
    # Dashboard Header with Action Button
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔄 Scan Blogs Now", type="primary", use_container_width=True):
            with st.spinner("Scanning blogs..."):
                try:
                    posts = services['blog_monitor'].fetch_blog_posts(BLOG_URLS)
                    
                    processed_posts = []
                    # Group posts by source to ensure diversity
                    source_posts = {}
                    for post_data in posts:
                        source = post_data['source_blog']
                        if source not in source_posts:
                            source_posts[source] = []
                        source_posts[source].append(post_data)
                    
                    # Process up to 2 posts per source for diversity
                    for source, source_post_list in source_posts.items():
                        for post_data in source_post_list[:2]:  # Max 2 per source
                            try:
                                full_content = services['blog_monitor'].get_full_content(post_data['url'])
                                keywords = services['blog_monitor'].is_ai_related(post_data['title'], full_content)
                                if keywords:
                                    summary = services['ai_summarizer'].summarize_content(post_data['title'], full_content)
                                    linkedin_post = services['ai_summarizer'].generate_linkedin_post(
                                        post_data['title'], summary, post_data['url'], keywords
                                    )
                                    processed_posts.append({
                                        'title': post_data['title'],
                                        'url': post_data['url'],
                                        'summary': summary,
                                        'linkedin_post': linkedin_post,
                                        'source_blog': post_data['source_blog'],
                                        'keywords': ', '.join(keywords)
                                    })
                            except Exception as e:
                                print(f"Error processing post from {source}: {e}")
                                continue
                    
                    st.session_state.fresh_posts = processed_posts
                    st.success(f"✅ Found {len(processed_posts)} AI/ML posts!")
                    
                except Exception as e:
                    st.error(f"Error scanning blogs: {str(e)}")
    

    
    # Display fresh posts
    if st.session_state.fresh_posts:
        st.markdown("""
        <div class="glass-card">
            <h2 class="card-title">🆕 Fresh AI/ML Content</h2>
            <p class="card-content">Latest posts discovered from monitored blogs - AI-filtered and ready for LinkedIn</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, post in enumerate(st.session_state.fresh_posts):
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <h3 class="card-title">📰 {post['title']}</h3>
                    <div class="card-content">
                        <p><strong>🏷️ Keywords:</strong> <span style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600;">{post['keywords']}</span></p>
                        <p><strong>🌐 Source:</strong> {post['source_blog']}</p>
                        <p><strong>📝 Summary:</strong> {post['summary']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**📱 LinkedIn Post Preview:**")
                st.markdown(f"""
                <div class="linkedin-post">
                    {post['linkedin_post'].replace(chr(10), '<br>')}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"✅ Approve & Save", key=f"approve_fresh_{i}_{hash(post['url'])}", use_container_width=True):
                        try:
                            db = next(get_db())
                            existing = db.query(BlogPost).filter(BlogPost.url == post['url']).first()
                            if not existing:
                                new_post = BlogPost(
                                    title=post['title'],
                                    url=post['url'],
                                    summary=post['summary'],
                                    linkedin_post=post['linkedin_post'],
                                    source_blog=post['source_blog'],
                                    keywords_matched=post['keywords'],
                                    is_approved=True
                                )
                                db.add(new_post)
                                db.commit()
                                st.success("✅ Post approved and saved!")
                            else:
                                st.warning("Post already exists in database")
                            db.close()
                        except Exception as e:
                            st.error(f"Error saving post: {str(e)}")
                
                with col2:
                    st.link_button("🔗 View Original", post['url'], use_container_width=True)

    # Date Search Controls
    col_date, col_range, col_search = st.columns([2, 1, 1])
    
    with col_date:
        selected_date = st.date_input("End Date (search backwards from):", value=datetime.now().date())
    
    with col_range:
        range_days = st.number_input("Days to search back:", min_value=1, max_value=365, value=7, step=1)
    
    with col_search:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Search Posts", use_container_width=True, type="primary"):
            with st.spinner("Searching posts by date..."):
                try:
                    target_datetime = datetime.combine(selected_date, datetime.min.time())
                    posts = services['blog_monitor'].fetch_posts_by_date(BLOG_URLS, target_datetime, range_days)
                    
                    processed_posts = []
                    source_posts = {}
                    for post_data in posts:
                        source = post_data['source_blog']
                        if source not in source_posts:
                            source_posts[source] = []
                        source_posts[source].append(post_data)
                    
                    for source, source_post_list in source_posts.items():
                        for post_data in source_post_list[:2]:
                            try:
                                full_content = services['blog_monitor'].get_full_content(post_data['url'])
                                keywords = services['blog_monitor'].is_ai_related(post_data['title'], full_content)
                                if keywords:
                                    summary = services['ai_summarizer'].summarize_content(post_data['title'], full_content)
                                    linkedin_post = services['ai_summarizer'].generate_linkedin_post(
                                        post_data['title'], summary, post_data['url'], keywords
                                    )
                                    processed_posts.append({
                                        'title': post_data['title'],
                                        'url': post_data['url'],
                                        'summary': summary,
                                        'linkedin_post': linkedin_post,
                                        'source_blog': post_data['source_blog'],
                                        'keywords': ', '.join(keywords)
                                    })
                            except Exception as e:
                                print(f"Error processing post from {source}: {e}")
                                continue
                    
                    st.session_state.fresh_posts = processed_posts
                    if processed_posts:
                        st.success(f"✅ Found {len(processed_posts)} AI/ML posts for {selected_date}!")
                        st.rerun()
                    else:
                        st.warning(f"⚠️ No AI/ML content found for {selected_date}. Try a different date or range.")
                        
                except Exception as e:
                    st.error(f"❌ Search Error: {str(e)}")
                    st.info("💡 Try adjusting your date range or check your internet connection")

elif st.session_state.current_page == "Quick":
    st.markdown("""
    <div class="glass-card">
        <h2 class="card-title">⚡ Quick LinkedIn Post Generator</h2>
        <p class="card-content">Instantly transform any article or content into a professional LinkedIn post using advanced AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        content_input = st.text_area(
            "📝 Paste URL or Content:", 
            height=150, 
            placeholder="Paste article URL or any content here...",
            key="quick_content_input"
        )
        
        if st.button("🪄 Generate LinkedIn Post", type="primary", use_container_width=True):
            if content_input.strip():
                # Enhanced loading for quick generation
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                with st.spinner("🤖 AI is crafting your professional LinkedIn post..."):
                    try:
                        # Process content
                        status_text.text("🔍 Analyzing your content...")
                        progress_bar.progress(25)
                        
                        if content_input.startswith(('http://', 'https://')):
                            full_content = services['blog_monitor'].get_full_content(content_input)
                            title = content_input.split('/')[-1] or "Article"
                            content_to_process = full_content[:3000]
                        else:
                            title = "Custom Content"
                            content_to_process = content_input[:3000]
                        
                        # Generate content
                        status_text.text("🏷️ Detecting keywords and themes...")
                        progress_bar.progress(50)
                        keywords = services['blog_monitor'].is_ai_related(title, content_to_process) or ['ai', 'technology']
                        
                        status_text.text("📝 Creating summary...")
                        progress_bar.progress(75)
                        summary = services['ai_summarizer'].summarize_content(title, content_to_process)
                        
                        status_text.text("✨ Generating LinkedIn post...")
                        progress_bar.progress(90)
                        linkedin_post = services['ai_summarizer'].generate_linkedin_post(
                            title, summary, content_input if content_input.startswith('http') else '', keywords
                        )
                        
                        progress_bar.progress(100)
                        status_text.empty()
                        progress_bar.empty()
                        
                        st.success("✅ ✨ LinkedIn Post Generated Successfully!")
                        st.balloons()  # Celebration animation
                        
                        # Display generated post
                        st.markdown("""
                        <div class="glass-card">
                            <h3 class="card-title">📝 ✨ Generated LinkedIn Post</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="linkedin-post">
                            {linkedin_post.replace(chr(10), '<br>')}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons
                        col_copy, col_save = st.columns(2)
                        with col_copy:
                            if st.button("📋 Copy to Clipboard", use_container_width=True):
                                st.markdown("""
                                <div class="copy-container">
                                    <p style="color: #28a745; font-weight: bold; margin-bottom: 0.5rem;">✅ Select and copy the text below:</p>
                                    <div class="copy-text">{}</div>
                                </div>
                                """.format(linkedin_post.replace('\n', '<br>')), unsafe_allow_html=True)
                        
                        with col_save:
                            if st.button("💾 Save to Approved", use_container_width=True):
                                try:
                                    db = next(get_db())
                                    new_post = BlogPost(
                                        title=title,
                                        url=content_input if content_input.startswith('http') else '',
                                        summary=summary,
                                        linkedin_post=linkedin_post,
                                        source_blog='Quick Generator',
                                        keywords_matched=', '.join(keywords),
                                        is_approved=True
                                    )
                                    db.add(new_post)
                                    db.commit()
                                    db.close()
                                    st.success("✅ Post saved to approved posts!")
                                except Exception as e:
                                    st.error(f"Error saving: {str(e)}")
                        
                    except Exception as e:
                        st.error(f"❌ Error generating post: {str(e)}")
            else:
                st.warning("⚠️ Please paste some content or URL to generate a post")
    
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3 class="card-title">💡 Pro Tips for Best Results</h3>
            <div class="card-content">
                <div style="background: linear-gradient(135deg, #f8f9ff 0%, #e8f2ff 100%); padding: 1.5rem; border-radius: 12px; margin: 1rem 0;">
                    <p style="margin: 0.5rem 0;"><strong>🔗 URLs:</strong> Paste any article URL for automatic content extraction</p>
                    <p style="margin: 0.5rem 0;"><strong>📝 Text:</strong> Paste article text, research papers, or any content</p>
                    <p style="margin: 0.5rem 0;"><strong>📄 Length:</strong> Longer content provides better context for generation</p>
                    <p style="margin: 0.5rem 0;"><strong>🤖 AI Focus:</strong> AI/ML content gets enhanced keyword detection</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        db = next(get_db())
        quick_posts = db.query(BlogPost).filter(BlogPost.source_blog == 'Quick Generator').count()
        db.close()
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{quick_posts}</div>
            <div class="metric-label">Quick Posts Generated</div>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "Approved":
    st.markdown("""
    <div class="glass-card">
        <h2 class="card-title">✅ Approved Posts Management</h2>
        <p class="card-content">Review, edit, and manage your approved LinkedIn posts with advanced controls</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get approved posts
    db = next(get_db())
    approved_posts = db.query(BlogPost).filter(BlogPost.is_approved == True).order_by(BlogPost.created_at.desc()).all()
    db.close()
    
    if approved_posts:
        for post in approved_posts:
            post_id = post.id
            is_editing = post_id in st.session_state.editing_posts
            
            with st.container():
                status_badge = "<span class='status-badge status-posted'>✅ Posted</span>" if post.is_posted else "<span class='status-badge status-approved'>📝 Approved</span>"
                
                st.markdown(f"""
                <div class="glass-card">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                        <h3 class="card-title" style="margin: 0;">📰 {post.title}</h3>
                        {status_badge}
                    </div>
                    <div class="card-content">
                        <p><strong>🏷️ Keywords:</strong> <span style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600;">{post.keywords_matched or 'N/A'}</span></p>
                        <p><strong>🌐 Source:</strong> {post.source_blog}</p>
                        <p><strong>📅 Created:</strong> {post.created_at.strftime('%Y-%m-%d %H:%M')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if not is_editing:
                    st.markdown("**📱 LinkedIn Post:**")
                    st.markdown(f"""
                    <div class="linkedin-post">
                        {post.linkedin_post.replace(chr(10), '<br>')}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.link_button("🔗 Original", post.url, use_container_width=True)
                    
                    with col2:
                        if st.button("📋 Copy", key=f"copy_{post_id}", use_container_width=True):
                            st.session_state.copied_posts[post_id] = post.linkedin_post
                            st.markdown("""
                            <div class="copy-container">
                                <p style="color: #28a745; font-weight: bold; margin-bottom: 0.5rem;">✅ Select and copy the text below:</p>
                                <div class="copy-text">{}</div>
                            </div>
                            """.format(post.linkedin_post.replace('\n', '<br>')), unsafe_allow_html=True)
                    
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_{post_id}", use_container_width=True):
                            st.session_state.editing_posts.add(post_id)
                            st.rerun()
                    
                    with col4:
                        if not post.is_posted:
                            if st.button("🚀 Mark Posted", key=f"posted_{post_id}", use_container_width=True):
                                try:
                                    db = next(get_db())
                                    db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
                                    if db_post:
                                        db_post.is_posted = True
                                        db.commit()
                                        st.success("✅ Marked as posted!")
                                    db.close()
                                    time.sleep(0.5)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        else:
                            st.markdown("<div style='text-align: center; color: #28a745; font-weight: bold;'>✅ Posted</div>", unsafe_allow_html=True)
                    
                    with col5:
                        if st.button("🗑️ Remove", key=f"remove_{post_id}", use_container_width=True):
                            try:
                                db = next(get_db())
                                db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
                                if db_post:
                                    db.delete(db_post)
                                    db.commit()
                                    st.success("✅ Post removed!")
                                db.close()
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                
                else:
                    # Edit mode
                    st.markdown("**Edit LinkedIn Post:**")
                    edited_content = st.text_area(
                        "Edit content:", 
                        value=post.linkedin_post, 
                        height=150, 
                        key=f"edit_area_{post_id}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Save Changes", key=f"save_{post_id}", type="primary", use_container_width=True):
                            try:
                                db = next(get_db())
                                db_post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
                                if db_post:
                                    db_post.linkedin_post = edited_content
                                    db.commit()
                                    st.success("✅ Post updated!")
                                db.close()
                                st.session_state.editing_posts.discard(post_id)
                                time.sleep(0.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
                    
                    with col_cancel:
                        if st.button("❌ Cancel", key=f"cancel_{post_id}", use_container_width=True):
                            st.session_state.editing_posts.discard(post_id)
                            st.rerun()
    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 4rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🚀</div>
            <h3 class="card-title">Ready to Create Amazing Content?</h3>
            <p class="card-content">Start by scanning blogs or using the Quick Generator to create your first professional LinkedIn post!</p>
            <div style="margin-top: 2rem;">
                <p style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 600; font-size: 1.1rem;">Your AI-powered content journey begins here</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show copied content
    if st.session_state.copied_posts:
        st.markdown("""
        <div class="glass-card">
            <h3 class="card-title">📋 Recently Copied Posts</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for post_id, content in list(st.session_state.copied_posts.items()):
            with st.expander(f"📄 Post {post_id} - Click to expand and copy", expanded=False):
                st.markdown("""
                <div class="copy-container">
                    <p style="color: #0066cc; font-weight: bold; margin-bottom: 0.5rem;">Select and copy the text below:</p>
                    <div class="copy-text">{}</div>
                </div>
                """.format(content.replace('\n', '<br>')), unsafe_allow_html=True)
                if st.button("🗑️ Clear", key=f"clear_copy_{post_id}"):
                    del st.session_state.copied_posts[post_id]
                    st.rerun()

elif st.session_state.current_page == "Analytics":
    st.markdown("""
    <div class="glass-card">
        <h2 class="card-title">📈 Analytics & Insights</h2>
        <p class="card-content">Track your content performance and discover trending patterns with advanced analytics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get analytics data
    db = next(get_db())
    all_posts = db.query(BlogPost).all()
    approved_posts = db.query(BlogPost).filter(BlogPost.is_approved == True).all()
    posted_posts = db.query(BlogPost).filter(BlogPost.is_posted == True).all()
    db.close()
    
    # Enhanced Metrics Dashboard
    st.markdown("""
    <div class="glass-card">
        <h2 class="card-title">📊 Performance Overview</h2>
        <p class="card-content">Real-time insights into your content generation and approval metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(all_posts)}</div>
            <div class="metric-label">Total Posts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(approved_posts)}</div>
            <div class="metric-label">Approved Posts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{len(posted_posts)}</div>
            <div class="metric-label">Posted to LinkedIn</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        approval_rate = (len(approved_posts) / len(all_posts) * 100) if all_posts else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{approval_rate:.1f}%</div>
            <div class="metric-label">Approval Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced Analytics
    if approved_posts:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="glass-card">
                <h3 class="card-title">📊 Top Performing Sources</h3>
            </div>
            """, unsafe_allow_html=True)
            
            source_counts = {}
            for post in approved_posts:
                source = post.source_blog
                source_counts[source] = source_counts.get(source, 0) + 1
            
            source_df = pd.DataFrame(list(source_counts.items()), columns=['Source', 'Posts'])
            st.bar_chart(source_df.set_index('Source'))
        
        with col2:
            st.markdown("""
            <div class="glass-card">
                <h3 class="card-title">🏷️ Trending Keywords</h3>
            </div>
            """, unsafe_allow_html=True)
            
            keyword_counts = {}
            for post in approved_posts:
                if post.keywords_matched:
                    keywords = [k.strip() for k in post.keywords_matched.split(',')]
                    for keyword in keywords:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            if keyword_counts:
                keyword_df = pd.DataFrame(list(keyword_counts.items()), columns=['Keyword', 'Count'])
                keyword_df = keyword_df.sort_values('Count', ascending=False).head(10)
                st.bar_chart(keyword_df.set_index('Keyword'))
            else:
                st.info("No keyword data available yet")





