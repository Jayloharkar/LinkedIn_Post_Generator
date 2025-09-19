import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from typing import List, Dict
from news_api_monitor import NewsAPIMonitor
from config import NEWS_API_ENABLED

class BlogMonitor:
    def __init__(self):
        self.ai_keywords = [
            'artificial intelligence', 'ai', 'machine learning', 'ml', 
            'deep learning', 'neural network', 'generative ai', 'gen ai',
            'autogen', 'llm', 'large language model', 'chatgpt', 'gpt',
            'transformer', 'nlp', 'computer vision', 'data science'
        ]
        
    def extract_rss_feed(self, blog_url: str) -> str:
        """Try to find RSS feed URL from blog"""
        # Specific RSS feeds for known blogs (only working ones)
        rss_mapping = {
            'microsoft.com/en-us/research': 'https://www.microsoft.com/en-us/research/feed/',
            'developer.nvidia.com': 'https://developer.nvidia.com/blog/feed/'
        }
        
        # Check if we have a specific RSS feed for this blog
        for domain, rss_url in rss_mapping.items():
            if domain in blog_url:
                return rss_url
        
        # Fallback to common RSS paths
        common_rss_paths = ['/feed', '/rss', '/feed.xml', '/rss.xml', '/atom.xml']
        for path in common_rss_paths:
            try:
                rss_url = blog_url.rstrip('/') + path
                response = requests.get(rss_url, timeout=10)
                if response.status_code == 200:
                    return rss_url
            except:
                continue
        return blog_url
    
    def fetch_blog_posts(self, blog_urls: List[str]) -> List[Dict]:
        """Fetch recent posts from blog URLs and NewsAPI"""
        all_posts = []
        
        # Fetch from blog URLs
        for blog_url in blog_urls:
            try:
                print(f"Fetching from: {blog_url}")
                # Try RSS first
                rss_url = self.extract_rss_feed(blog_url)
                print(f"Using RSS: {rss_url}")
                feed = feedparser.parse(rss_url)
                
                if feed.entries:
                    print(f"Found {len(feed.entries)} entries from {blog_url}")
                    for entry in feed.entries[:3]:  # Limit to 3 posts per blog
                        post_data = {
                            'title': entry.get('title', ''),
                            'url': entry.get('link', ''),
                            'content': entry.get('summary', ''),
                            'published': entry.get('published_parsed'),
                            'source_blog': self.get_blog_name(blog_url)
                        }
                        
                        # Check if post is recent (last 30 days for better coverage)
                        if self.is_recent_post(post_data['published'], days=30):
                            all_posts.append(post_data)
                else:
                    print(f"No RSS entries found for {blog_url}, trying web scraping")
                    # Fallback to web scraping
                    posts = self.scrape_blog_posts(blog_url)
                    if posts:
                        print(f"Scraped {len(posts)} posts from {blog_url}")
                        all_posts.extend(posts[:2])  # Limit scraped posts to 2 per blog
                    
            except Exception as e:
                print(f"Error fetching from {blog_url}: {e}")
        
        # Add NewsAPI content if enabled
        if NEWS_API_ENABLED:
            try:
                news_monitor = NewsAPIMonitor()
                news_articles = news_monitor.fetch_ai_news(days_back=7)
                if news_articles:
                    all_posts.extend(news_articles)
                    print(f"Added {len(news_articles)} NewsAPI articles")
            except Exception as e:
                print(f"NewsAPI integration error: {e}")
                
        print(f"Total posts fetched: {len(all_posts)}")
        return all_posts
    
    def scrape_blog_posts(self, blog_url: str) -> List[Dict]:
        """Fallback web scraping for blogs without RSS"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(blog_url, timeout=15, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            posts = []
            
            # Blog-specific selectors
            if 'ai.googleblog.com' in blog_url:
                # Try multiple selectors for Google AI Blog
                selectors = ['.post h3 a', '.post h2 a', 'article h2 a', 'h2 a', 'h3 a']
                for selector in selectors:
                    links = soup.select(selector)[:3]
                    if links:
                        for link in links:
                            title = link.get_text().strip()
                            url = link.get('href')
                            if title and url and len(title) > 5:
                                posts.append({
                                    'title': title,
                                    'url': url,
                                    'content': '',
                                    'source_blog': self.get_blog_name(blog_url)
                                })
                        break
            
            elif 'deepmind.google' in blog_url:
                selectors = ['article h2 a', 'article h3 a', 'h2 a', 'h3 a', 'a[href*="/discover/"]']
                for selector in selectors:
                    links = soup.select(selector)[:3]
                    if links:
                        for link in links:
                            title = link.get_text().strip()
                            url = link.get('href')
                            if title and url and len(title) > 5:
                                if not url.startswith('http'):
                                    url = 'https://deepmind.google' + url
                                posts.append({
                                    'title': title,
                                    'url': url,
                                    'content': '',
                                    'source_blog': self.get_blog_name(blog_url)
                                })
                        break
            
            elif 'ai.meta.com' in blog_url:
                selectors = ['.blog-post h2 a', '.blog-post h3 a', 'article h2 a', 'h2 a', 'h3 a']
                for selector in selectors:
                    links = soup.select(selector)[:3]
                    if links:
                        for link in links:
                            title = link.get_text().strip()
                            url = link.get('href')
                            if title and url and len(title) > 5:
                                posts.append({
                                    'title': title,
                                    'url': url,
                                    'content': '',
                                    'source_blog': self.get_blog_name(blog_url)
                                })
                        break
            
            elif 'anthropic.com' in blog_url:
                selectors = ['article h2 a', 'article h3 a', 'h2 a', 'h3 a', 'a[href*="/news/"]']
                for selector in selectors:
                    links = soup.select(selector)[:3]
                    if links:
                        for link in links:
                            title = link.get_text().strip()
                            url = link.get('href')
                            if title and url and len(title) > 5:
                                if not url.startswith('http'):
                                    url = 'https://www.anthropic.com' + url
                                posts.append({
                                    'title': title,
                                    'url': url,
                                    'content': '',
                                    'source_blog': self.get_blog_name(blog_url)
                                })
                        break
            
            elif 'amazon.science' in blog_url:
                selectors = ['.blog-post h2 a', '.blog-post h3 a', 'article h2 a', 'h2 a', 'h3 a']
                for selector in selectors:
                    links = soup.select(selector)[:3]
                    if links:
                        for link in links:
                            title = link.get_text().strip()
                            url = link.get('href')
                            if title and url and len(title) > 5:
                                posts.append({
                                    'title': title,
                                    'url': url,
                                    'content': '',
                                    'source_blog': self.get_blog_name(blog_url)
                                })
                        break
            
            # Generic fallback for other blogs
            if not posts:
                selectors = ['article h2 a', 'article h3 a', '.post-title a', 'h2 a', 'h3 a']
                for selector in selectors:
                    links = soup.select(selector)[:3]
                    for link in links:
                        title = link.get_text().strip()
                        url = link.get('href')
                        
                        if title and url and len(title) > 10:
                            if not url.startswith('http'):
                                url = blog_url.rstrip('/') + '/' + url.lstrip('/')
                            
                            posts.append({
                                'title': title,
                                'url': url,
                                'content': '',
                                'source_blog': self.get_blog_name(blog_url)
                            })
                    
                    if posts:
                        break
            
            if posts:
                print(f"Scraped {len(posts)} posts from {blog_url}")
                return posts[:3]
            else:
                print(f"No posts found via scraping for {blog_url}")
                return []
            
        except Exception as e:
            print(f"Error scraping {blog_url}: {e}")
            return []
    
    def is_recent_post(self, published_time, days=7) -> bool:
        """Check if post is from last N days"""
        if not published_time:
            return True  # Assume recent if no date
        
        post_date = datetime(*published_time[:6])
        return (datetime.now() - post_date).days <= days
    
    def get_blog_name(self, blog_url: str) -> str:
        """Get friendly blog name from URL"""
        blog_names = {
            'deepmind.google': 'DeepMind Blog',
            'microsoft.com/en-us/research': 'Microsoft Research',
            'anthropic.com/news': 'Anthropic News',
            'developer.nvidia.com': 'NVIDIA Developer Blog',
            'venturebeat.com': 'VentureBeat AI',
            'technologyreview.com': 'MIT Technology Review',
            'techcrunch.com': 'TechCrunch AI',
            'theverge.com': 'The Verge AI',
            'wired.com': 'Wired AI',
            'distill.pub': 'Distill Research',
            'blog.research.google': 'Google Research',
            'huggingface.co': 'Hugging Face Blog',
            'pytorch.org': 'PyTorch Blog',
            'blog.tensorflow.org': 'TensorFlow Blog'
        }
        
        for domain, name in blog_names.items():
            if domain in blog_url:
                return name
        return blog_url
    
    def filter_posts_by_date(self, posts: List[Dict], target_date: datetime, days_range: int = 1) -> List[Dict]:
        """Filter posts by date range - searches BEFORE the target date
        
        Args:
            target_date: The end date (e.g., 2025-01-09)
            days_range: Number of days to search backwards (e.g., 7 = search 7 days before target_date)
        
        Example: target_date=2025-01-09, days_range=7 → searches from 2025-01-02 to 2025-01-09
        """
        filtered_posts = []
        
        # Calculate date range: from (target_date - days_range + 1) to target_date
        start_date = target_date - timedelta(days=days_range - 1)
        end_date = target_date
        
        print(f"Searching posts from {start_date.date()} to {end_date.date()}")
        
        for post in posts:
            published_time = post.get('published')
            if not published_time:
                # If no date, include recent posts (assume they're within range)
                filtered_posts.append(post)
                continue
            
            try:
                # Handle different date formats
                if isinstance(published_time, str):
                    # Skip string dates for now, include the post
                    filtered_posts.append(post)
                    continue
                elif isinstance(published_time, tuple) and len(published_time) >= 6:
                    post_date = datetime(*published_time[:6])
                else:
                    # Unknown format, include the post
                    filtered_posts.append(post)
                    continue
                
                # Check if post is within the date range (start_date <= post_date <= end_date)
                if start_date.date() <= post_date.date() <= end_date.date():
                    post['published_date'] = post_date
                    filtered_posts.append(post)
                    print(f"✓ Included post from {post_date.date()}: {post.get('title', '')[:50]}...")
                    
            except Exception as e:
                # If date parsing fails, include the post anyway
                print(f"Date parsing error for post: {e}")
                filtered_posts.append(post)
        
        print(f"Found {len(filtered_posts)} posts in date range")
        return filtered_posts
    
    def fetch_posts_by_date(self, blog_urls: List[str], target_date: datetime, days_range: int = 1) -> List[Dict]:
        """Fetch posts from specific date across all blogs"""
        all_posts = self.fetch_blog_posts(blog_urls)
        return self.filter_posts_by_date(all_posts, target_date, days_range)
    
    def is_ai_related(self, title: str, content: str) -> List[str]:
        """Check if post content matches AI keywords"""
        text = (title + ' ' + content).lower()
        matched_keywords = []
        
        for keyword in self.ai_keywords:
            if keyword.lower() in text:
                matched_keywords.append(keyword)
                
        return matched_keywords
    
    def get_full_content(self, url: str) -> str:
        """Extract full article content from URL"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Try to find main content
            content_selectors = [
                'article', '.content', '.post-content', '.entry-content',
                '.article-content', 'main', '.main-content'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    return content_elem.get_text().strip()
            
            # Fallback to body text
            return soup.get_text().strip()
            
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return ""