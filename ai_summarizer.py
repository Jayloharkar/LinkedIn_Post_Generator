import requests
import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

class AISummarizer:
    def __init__(self):
        self.api_key = os.getenv("CEREBRAS_API_KEY")
        self.base_url = "https://api.cerebras.ai/v1/chat/completions"
        
    def summarize_content(self, title: str, content: str) -> str:
        """Generate summary of blog post content"""
        try:
            prompt = f"""
            Create a precise, factual summary of this content for LinkedIn (2-3 sentences):
            
            Title: {title}
            Content: {content[:3000]}
            
            CRITICAL REQUIREMENTS:
            - Use ONLY information explicitly stated in the source content
            - Do NOT add tools, frameworks, or technologies not mentioned in the original
            - Maintain exact technical details, numbers, and terminology from the source
            - If the content mentions specific ranges or scales, preserve them accurately
            - Focus on the author's main argument or key findings
            - Avoid inferring or adding industry context not present in the original
            
            Be factually precise and stay faithful to the source material.
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
                    "max_tokens": 150,
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                result = response.json()["choices"][0]["message"]["content"].strip()
                # Basic validation to ensure content relevance
                if len(result) > 20 and not result.startswith("I cannot"):
                    return result
                else:
                    return f"Key insights from {title}. Read the full article for detailed information."
            else:
                print(f"Cerebras API error: {response.status_code}")
                return f"Interesting insights about {title}. Check out the full article for more details."
            
        except Exception as e:
            print(f"Error summarizing content: {e}")
            return f"Interesting insights about {title}. Check out the full article for more details."
    
    def generate_linkedin_post(self, title: str, summary: str, url: str, keywords: List[str]) -> str:
        """Generate LinkedIn post from summary"""
        try:
            hashtags = self.generate_hashtags(keywords)
            
            prompt = f"""
            Create a professional LinkedIn post based on this summary:
            
            Title: {title}
            Summary: {summary}
            
            STRICT REQUIREMENTS:
            - Use ONLY facts and details from the provided summary
            - Do NOT add tools, technologies, or frameworks not mentioned in the summary
            - Preserve exact numbers, ranges, and technical terminology from the source
            - Start with an engaging hook or thought-provoking question
            - Include 2-3 key insights directly from the summary
            - End with a discussion question that reflects the main theme
            - Stay under 1300 characters
            - Do NOT include hashtags (added separately)
            - Maintain factual accuracy - no embellishments or assumptions
            
            Style: Authoritative but conversational, faithful to source content
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
                    "max_tokens": 200,
                    "temperature": 0.8
                }
            )
            
            if response.status_code == 200:
                post_content = response.json()["choices"][0]["message"]["content"].strip()
                # Validate generated content quality
                if len(post_content) > 50 and not post_content.startswith("I cannot"):
                    final_post = f"{post_content}\n\nRead more: {url}\n\n{hashtags}"
                    return final_post
                else:
                    # Fallback to summary-based post
                    return f"{summary}\n\nRead more: {url}\n\n{hashtags}"
            else:
                print(f"Cerebras API error: {response.status_code}")
                return f"{summary}\n\nRead more: {url}\n\n#AI #MachineLearning #Technology"
            
        except Exception as e:
            print(f"Error generating LinkedIn post: {e}")
            return f"{summary}\n\nRead more: {url}\n\n#AI #MachineLearning #Technology"
    
    def generate_hashtags(self, keywords: List[str]) -> str:
        """Generate relevant hashtags from keywords"""
        hashtag_map = {
            'artificial intelligence': '#ArtificialIntelligence',
            'ai': '#AI',
            'machine learning': '#MachineLearning',
            'ml': '#ML',
            'deep learning': '#DeepLearning',
            'neural network': '#NeuralNetworks',
            'generative ai': '#GenerativeAI',
            'gen ai': '#GenAI',
            'autogen': '#AutoGen',
            'llm': '#LLM',
            'large language model': '#LargeLanguageModels',
            'chatgpt': '#ChatGPT',
            'gpt': '#GPT',
            'transformer': '#Transformers',
            'nlp': '#NLP',
            'computer vision': '#ComputerVision',
            'data science': '#DataScience'
        }
        
        hashtags = set()
        for keyword in keywords[:5]:  # Limit to 5 hashtags
            if keyword.lower() in hashtag_map:
                hashtags.add(hashtag_map[keyword.lower()])
        
        # Add default hashtags if none found
        if not hashtags:
            hashtags = {'#AI', '#Technology', '#Innovation'}
        
        return ' '.join(sorted(hashtags))