# Configuration file for blog URLs and settings

# Curated AI/ML Blog URLs (verified working sources)
BLOG_URLS = [
    # Big Tech & Research Labs
    "https://deepmind.google/discover/blog",
    "https://www.microsoft.com/en-us/research/blog/",
    "https://www.anthropic.com/news",
    "https://developer.nvidia.com/blog/",
    
    # AI/ML News & Research Sites
    "https://venturebeat.com/ai/",
    "https://www.technologyreview.com/topic/artificial-intelligence/",
    "https://techcrunch.com/category/artificial-intelligence/",
    "https://www.theverge.com/ai-artificial-intelligence",
    "https://www.wired.com/tag/artificial-intelligence/",
    
    # Academic & Research
    
    "https://blog.research.google/",
    "https://huggingface.co/blog",
    "https://pytorch.org/blog/",
    
]

# AI/ML Keywords to monitor
AI_KEYWORDS = [
    'artificial intelligence', 'ai', 'machine learning', 'ml', 
    'deep learning', 'neural network', 'generative ai', 'gen ai',
    'autogen', 'llm', 'large language model', 'chatgpt', 'gpt',
    'transformer', 'nlp', 'computer vision', 'data science',
    'pytorch', 'tensorflow', 'hugging face', 'langchain',
    'vector database', 'embedding', 'rag', 'fine-tuning',
    'multimodal', 'diffusion', 'stable diffusion', 
    'multi agent', 'ai tools','midjourney'
]

# News API Integration (alternative source)
NEWS_API_ENABLED = True
NEWS_API_KEY = "20c3104c99644e628aa9b20509b745ba"  # NewsAPI key for broader coverage
NEWS_SOURCES = [
    "techcrunch", "the-verge", "wired", "ars-technica", 
    "engadget", "venturebeat", "mit-technology-review"
]

# Monitoring settings
MONITORING_INTERVAL_HOURS = 6
DATE_BASED_SEARCH = True  # Enable date-based content search
MAX_SEARCH_DAYS = 30  # Maximum days to search back from selected date
DATE_RANGE_DAYS = 7  # Search within 7-day range from selected date
DEFAULT_POSTS_LIMIT = 20  # Default limit when no date specified