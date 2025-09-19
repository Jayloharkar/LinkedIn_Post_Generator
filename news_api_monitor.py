import requests
from datetime import datetime, timedelta
from typing import List, Dict
from config import NEWS_API_KEY, NEWS_SOURCES, AI_KEYWORDS

class NewsAPIMonitor:
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2"
        
    def fetch_ai_news(self, days_back: int = 7) -> List[Dict]:
        """Fetch AI-related news from NewsAPI"""
        if not self.api_key:
            return []
            
        all_articles = []
        
        # Create search query from AI keywords
        query = " OR ".join([f'"{keyword}"' for keyword in AI_KEYWORDS[:10]])  # Limit to avoid long URLs
        
        # Calculate date range
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        try:
            # Search everything endpoint
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 50,
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for article in data.get('articles', []):
                    # Filter out articles without proper content
                    if (article.get('title') and 
                        article.get('description') and 
                        article.get('url') and
                        len(article.get('description', '')) > 50):
                        
                        all_articles.append({
                            'title': article['title'],
                            'url': article['url'],
                            'content': article.get('description', ''),
                            'published': article.get('publishedAt'),
                            'source_blog': f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}"
                        })
            
            print(f"NewsAPI: Found {len(all_articles)} AI articles")
            return all_articles[:20]  # Limit to 20 articles
            
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []
    
    def fetch_from_sources(self, days_back: int = 7) -> List[Dict]:
        """Fetch from specific tech news sources"""
        if not self.api_key:
            return []
            
        all_articles = []
        
        # Create AI-focused query
        query = "artificial intelligence OR machine learning OR AI OR deep learning"
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        try:
            url = f"{self.base_url}/everything"
            params = {
                'q': query,
                'sources': ','.join(NEWS_SOURCES),
                'from': from_date,
                'sortBy': 'publishedAt',
                'language': 'en',
                'pageSize': 30,
                'apiKey': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for article in data.get('articles', []):
                    if (article.get('title') and 
                        article.get('description') and 
                        article.get('url')):
                        
                        all_articles.append({
                            'title': article['title'],
                            'url': article['url'],
                            'content': article.get('description', ''),
                            'published': article.get('publishedAt'),
                            'source_blog': f"NewsAPI - {article.get('source', {}).get('name', 'Tech News')}"
                        })
            
            print(f"NewsAPI Sources: Found {len(all_articles)} articles")
            return all_articles[:15]  # Limit to 15 articles
            
        except Exception as e:
            print(f"NewsAPI sources error: {e}")
            return []