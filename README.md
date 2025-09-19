# 🤖 AI LinkedIn Post Generator (Streamlit Version)

Automatically monitor 8 curated AI/ML blogs, generate engaging summaries, and create professional LinkedIn posts using Cerebras AI with a modern Streamlit interface.

## ✨ Features

- **🔍 Smart Blog Monitoring**: Scans 8 top AI/ML blogs (Google AI, OpenAI, Meta AI, etc.)
- **🎯 AI Content Detection**: Filters posts using 25+ AI/ML keywords for relevance
- **🧠 AI-Powered Generation**: Uses Cerebras Llama 3.1-8B for summaries and LinkedIn posts
- **💼 Professional LinkedIn Posts**: Creates engaging content with hooks, technical insights, and discussion questions
- **🎨 Modern Streamlit UI**: Beautiful, responsive interface with real-time updates
- **📅 Date-Based Search**: Search posts by specific dates with customizable ranges
- **📊 Enhanced Analytics**: Visual insights with charts and metrics
- **⚡ Quick Summarizer**: Paste any URL or content to generate LinkedIn posts instantly

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
Add your Cerebras API key to `.env`:
```env
CEREBRAS_API_KEY=your_api_key_here
```

### 3. Run Streamlit Application
```bash
streamlit run streamlit_app.py
```

### 4. Access Dashboard
Open **http://localhost:8501** in your browser

## 📖 Usage Guide

### Dashboard Operations
1. **🔄 Scan Blogs**: Click "Scan Blogs Now" for immediate content discovery
2. **📅 Date Search**: Select specific dates and ranges in sidebar
3. **📝 Review Content**: View AI-generated summaries and LinkedIn posts
4. **✅ Approve Posts**: Save high-quality posts to database
5. **📋 Copy & Share**: Copy approved posts to LinkedIn

### Quick Summarizer
1. **📝 Paste Content**: Add any URL or text content in sidebar
2. **🪄 Generate**: Click "Generate LinkedIn Post"
3. **📋 Copy**: Copy generated post directly to LinkedIn

### Analytics Dashboard
- **📊 Visual Metrics**: Total, approved, and posted post counts
- **📈 Source Analysis**: Bar charts showing top performing sources
- **🏷️ Keyword Trends**: Popular AI/ML keywords analysis
- **📉 Approval Rates**: Performance tracking over time

## 🛠️ Technical Stack

- **Frontend**: Streamlit (Python)
- **AI Model**: Cerebras Llama 3.1-8B
- **Database**: SQLite
- **Scraping**: BeautifulSoup4 + Feedparser
- **Analytics**: Pandas + Plotly
- **Intelligence**: Custom ML-powered content filtering

## 📁 Project Structure

```
LinkedIn_Post_Generator/
├── streamlit_app.py        # Main Streamlit application
├── blog_monitor.py         # Web scraping and RSS monitoring
├── ai_summarizer.py        # Cerebras AI integration
├── content_intelligence.py # ML-powered content filtering
├── models.py              # SQLite database models
├── config.py              # Blog URLs and settings
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this)
└── blog_posts.db         # SQLite database (auto-created)
```

## ⚙️ Configuration

### Blog Sources (8 curated sources)
Edit `config.py` to modify blog URLs:
- Google AI Blog
- DeepMind Blog
- Microsoft Research
- OpenAI Research
- Meta AI Blog
- Anthropic News
- NVIDIA Developer Blog
- Amazon Science Blog

### AI Keywords (25+ keywords)
Customize AI detection keywords in `config.py`:
```python
AI_KEYWORDS = [
    'artificial intelligence', 'ai', 'machine learning', 'ml',
    'deep learning', 'neural network', 'llm', 'gpt', 'transformer',
    'generative ai', 'computer vision', 'nlp', 'multimodal',
    # ... and more
]
```

### Date Search Settings
```python
DATE_RANGE_DAYS = 7        # Default search range
MAX_SEARCH_DAYS = 30       # Maximum allowed range
DEFAULT_POSTS_LIMIT = 20   # Posts per scan
```

## 🔧 Advanced Features

### Content Intelligence
- **🔍 Duplicate Detection**: Automatically removes similar content
- **📊 Relevance Scoring**: Ranks content by trending topics
- **🎯 Engagement Prediction**: AI predicts post performance
- **🧠 Personalization**: Learns from your approval patterns

### Date-Based Search
- **📅 Calendar Picker**: Select any specific date
- **⏰ Range Selection**: 1, 3, 7, 14, or 30-day ranges
- **🔍 Smart Filtering**: Find posts from conferences, events, announcements

### Quick Summarizer
- **🔗 URL Processing**: Automatically extracts content from any article URL
- **📝 Text Processing**: Paste any content directly
- **⚡ Instant Generation**: Creates LinkedIn posts in seconds
- **📋 One-Click Copy**: Copy to clipboard functionality

## 🚨 Requirements

- **Python 3.8+**
- **Cerebras API Key** (for AI generation)
- **Internet Connection** (for blog monitoring)
- **2GB RAM** (for local processing)

## 📊 Content Flow

```
Blog Sources → RSS/Scraping → AI Filtering → Content Generation → Quality Review → LinkedIn Ready
     ↓              ↓             ↓              ↓               ↓            ↓
  8 Blogs    →  All Posts    → AI Keywords → Cerebras AI → User Approval → Copy & Post
```

## 🎯 Perfect For

- **Content Creators** who need AI/ML content
- **LinkedIn Influencers** in tech space  
- **AI Professionals** sharing industry insights
- **Marketing Teams** covering AI trends
- **Developers** building personal brand

## 📈 Benefits

- **Save 5+ hours/week** on content research
- **Stay updated** with latest AI developments
- **Professional content** with technical depth
- **Visual analytics** for performance tracking
- **Higher engagement** with AI-optimized posts

## 🎨 Streamlit Advantages

- **📱 Responsive Design**: Works on all devices
- **⚡ Real-time Updates**: Instant feedback on actions
- **📊 Built-in Charts**: Native analytics visualization
- **🎛️ Interactive Widgets**: Intuitive controls
- **🔄 Auto-refresh**: Live data updates

---

**Built with ❤️ using Streamlit & Cerebras AI • Ready to transform your LinkedIn presence**