# Advanced Content Intelligence - ML-powered filtering and predictions
import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter, defaultdict
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class ContentIntelligence:
    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        self.base_url = "https://api.cerebras.ai/v1/chat/completions"
        self.user_preferences = defaultdict(int)  # Track user approval patterns
        self.trending_keywords = Counter()  # Track trending topics
        
    def calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two pieces of content (0-1 score)"""
        # Simple word-based similarity
        words1 = set(re.findall(r'\w+', content1.lower()))
        words2 = set(re.findall(r'\w+', content2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def detect_duplicates(self, posts: List[Dict], similarity_threshold: float = 0.7) -> List[Dict]:
        """Remove duplicate/similar content"""
        unique_posts = []
        seen_hashes = set()
        
        for post in posts:
            # Create content hash for exact duplicates
            content_hash = hashlib.md5(post['title'].encode()).hexdigest()
            if content_hash in seen_hashes:
                continue
                
            # Check similarity with existing posts
            is_duplicate = False
            for existing_post in unique_posts:
                similarity = self.calculate_content_similarity(
                    post['title'] + ' ' + post.get('summary', ''),
                    existing_post['title'] + ' ' + existing_post.get('summary', '')
                )
                if similarity > similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_posts.append(post)
                seen_hashes.add(content_hash)
                
        return unique_posts
    
    def calculate_relevance_score(self, post: Dict) -> float:
        """Calculate relevance score based on keywords and trends (0-1 score)"""
        title = post.get('title', '').lower()
        content = post.get('summary', '').lower()
        text = title + ' ' + content
        
        # Trending keywords get higher scores
        trending_score = 0
        for keyword, count in self.trending_keywords.most_common(10):
            if keyword in text:
                trending_score += count / max(self.trending_keywords.values())
        
        # Recent posts get higher scores
        recency_score = 1.0  # Default for posts without dates
        if 'created_at' in post and post['created_at']:
            days_old = (datetime.utcnow() - post['created_at']).days
            recency_score = max(0, 1 - (days_old / 7))  # Decay over 7 days
        
        # Keyword density score
        keyword_score = len(post.get('keywords_matched', '').split(',')) / 10
        
        return min(1.0, (trending_score * 0.4 + recency_score * 0.3 + keyword_score * 0.3))
    
    def predict_engagement(self, post: Dict) -> Dict:
        """Predict engagement potential using AI"""
        try:
            prompt = f"""
            Analyze this LinkedIn post for engagement potential:
            
            Title: {post.get('title', '')}
            Content: {post.get('linkedin_post', '')[:500]}
            
            Rate 1-10 for:
            1. Engagement potential (likes/comments)
            2. Shareability 
            3. Professional relevance
            4. Trending topic alignment
            
            Respond with: "Engagement: X, Shareability: Y, Relevance: Z, Trending: W, Overall: A"
            """
            
            response = requests.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama3.1-8b",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 100,
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"].strip()
                scores = self._parse_engagement_scores(result)
                return scores
            else:
                return {"engagement": 5, "shareability": 5, "relevance": 5, "trending": 5, "overall": 5}
                
        except Exception as e:
            print(f"Error predicting engagement: {e}")
            return {"engagement": 5, "shareability": 5, "relevance": 5, "trending": 5, "overall": 5}
    
    def _parse_engagement_scores(self, ai_response: str) -> Dict:
        """Parse AI response into engagement scores"""
        scores = {"engagement": 5, "shareability": 5, "relevance": 5, "trending": 5, "overall": 5}
        
        # Extract numbers from AI response
        import re
        numbers = re.findall(r'\d+', ai_response)
        if len(numbers) >= 5:
            scores["engagement"] = min(10, max(1, int(numbers[0])))
            scores["shareability"] = min(10, max(1, int(numbers[1])))
            scores["relevance"] = min(10, max(1, int(numbers[2])))
            scores["trending"] = min(10, max(1, int(numbers[3])))
            scores["overall"] = min(10, max(1, int(numbers[4])))
        
        return scores
    
    def learn_user_preferences(self, approved_posts: List[Dict]):
        """Learn from user's approval patterns"""
        for post in approved_posts:
            # Track preferred keywords
            keywords = post.get('keywords_matched', '').split(',')
            for keyword in keywords:
                keyword = keyword.strip().lower()
                if keyword:
                    self.user_preferences[keyword] += 1
            
            # Track preferred sources
            source = post.get('source_blog', '')
            if source:
                self.user_preferences[f"source:{source}"] += 1
    
    def get_personalized_score(self, post: Dict) -> float:
        """Calculate personalized score based on learned preferences"""
        score = 0.0
        
        # Check keyword preferences
        keywords = post.get('keywords_matched', '').split(',')
        for keyword in keywords:
            keyword = keyword.strip().lower()
            if keyword in self.user_preferences:
                score += self.user_preferences[keyword] / 10
        
        # Check source preferences
        source = post.get('source_blog', '')
        source_key = f"source:{source}"
        if source_key in self.user_preferences:
            score += self.user_preferences[source_key] / 5
        
        return min(1.0, score)
    
    def identify_trending_topics(self, posts: List[Dict]) -> List[Tuple[str, int]]:
        """Identify trending topics from recent posts"""
        recent_keywords = Counter()
        
        # Count keywords from recent posts (last 3 days)
        cutoff_date = datetime.utcnow() - timedelta(days=3)
        
        for post in posts:
            post_date = post.get('created_at', datetime.utcnow())
            if isinstance(post_date, str):
                continue
                
            if post_date > cutoff_date:
                keywords = post.get('keywords_matched', '').split(',')
                for keyword in keywords:
                    keyword = keyword.strip().lower()
                    if keyword:
                        recent_keywords[keyword] += 1
        
        # Update global trending keywords
        self.trending_keywords.update(recent_keywords)
        
        return recent_keywords.most_common(10)
    
    def rank_posts_by_intelligence(self, posts: List[Dict]) -> List[Dict]:
        """Rank posts using all intelligence features"""
        # Remove duplicates
        unique_posts = self.detect_duplicates(posts)
        
        # Calculate scores for each post
        for post in unique_posts:
            relevance = self.calculate_relevance_score(post)
            personalization = self.get_personalized_score(post)
            engagement_pred = self.predict_engagement(post)
            
            # Combined intelligence score
            post['intelligence_score'] = (
                relevance * 0.3 +
                personalization * 0.3 +
                (engagement_pred['overall'] / 10) * 0.4
            )
            
            post['relevance_score'] = relevance
            post['personalization_score'] = personalization
            post['engagement_prediction'] = engagement_pred
        
        # Sort by intelligence score
        return sorted(unique_posts, key=lambda x: x.get('intelligence_score', 0), reverse=True)