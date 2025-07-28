"""
Social Media Scraper for career advancement posts
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from loguru import logger
import re

class SocialMediaScraper:
    def __init__(self):
        """Initialize social media scraper"""
        self.browser = None
        self.context = None
        
    async def init(self):
        """Initialize browser and context"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            
            # Context configuration
            context_config = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': self._get_random_user_agent(),
                'locale': 'en-US'
            }
            
            self.context = await self.browser.new_context(**context_config)
            logger.info("Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string"""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
        ]
        return random.choice(user_agents)
    
    async def search_career_posts(self, role: str = '', industry: str = '', 
                                experience_level: str = '', max_results: int = 50,
                                field: str = '', location: str = '', grad_year: Optional[int] = None,
                                grad_year_range: int = 2) -> List[Dict[str, Any]]:
        """
        Search for career advancement posts with additional filters
        
        Args:
            role: Job role (e.g., "Software Engineer")
            industry: Industry sector (e.g., "Tech", "Finance")
            experience_level: Level of experience (e.g., "Entry", "Senior")
            max_results: Maximum number of results to return
            field: Field of study/major (e.g., "Computer Science", "Business")
            location: Geographic location (e.g., "San Francisco", "New York")
            grad_year: Graduation year to filter by
            grad_year_range: Range of years around grad_year to include (±)
        """
        if not self.context or not self.browser:
            if not await self.init():
                return []
        
        posts = []
        try:
            # Build search keywords including new filters
            keywords = self._build_search_keywords(
                role=role,
                industry=industry,
                experience_level=experience_level,
                field=field,
                location=location,
                grad_year=grad_year
            )
            
            # Search different platforms
            twitter_posts = await self._search_twitter(keywords, max_results)
            posts.extend(twitter_posts)
            
            reddit_posts = await self._search_reddit(keywords, max_results)
            posts.extend(reddit_posts)
            
            hn_posts = await self._search_hackernews(keywords, max_results)
            posts.extend(hn_posts)
            
            # Filter and sort posts by relevance with new criteria
            filtered_posts = self._filter_relevant_posts(
                posts=posts,
                role=role,
                industry=industry,
                experience_level=experience_level,
                field=field,
                location=location,
                grad_year=grad_year,
                grad_year_range=grad_year_range
            )
            return filtered_posts[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching career posts: {e}")
            return []
    
    def _build_search_keywords(self, role: str, industry: str, experience_level: str,
                             field: str, location: str, grad_year: Optional[int] = None) -> List[str]:
        """Build search keywords from all filters"""
        keywords = [
            "career growth",
            "job promotion",
            "career advancement",
            role if role else "",
            industry if industry else "",
            experience_level if experience_level else "",
            field if field else "",
            location if location else ""
        ]
        
        # Add graduation year related terms if specified
        if grad_year is not None:
            keywords.extend([
                f"class of {grad_year}",
                f"graduated {grad_year}",
                "alumni",
                "graduate"
            ])
        
        # Filter out empty strings and join with spaces
        return [kw for kw in keywords if kw.strip()]
    
    async def _search_twitter(self, keywords: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search Twitter for career posts"""
        if not self.context:
            logger.error("Browser context not available")
            return []
            
        posts = []
        page = None
        try:
            page = await self.context.new_page()
            if not page:
                logger.error("Failed to create new page")
                return []
            
            # Join keywords for search query
            search_query = " ".join(keywords)
            
            # Use Twitter's advanced search
            search_url = f"https://twitter.com/search?q={search_query}%20-filter%3Areplies&f=live"
            await page.goto(search_url, wait_until='networkidle')
            
            # Wait for tweets to load
            await page.wait_for_selector('article[data-testid="tweet"]', timeout=30000)
            
            # Extract tweets
            tweets = await page.query_selector_all('article[data-testid="tweet"]')
            for tweet in tweets[:max_results]:
                try:
                    post = await self._extract_tweet(tweet)
                    if post:
                        post['source'] = 'twitter'
                        posts.append(post)
                except Exception as e:
                    logger.warning(f"Error extracting tweet: {e}")
                    continue
                
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Error searching Twitter: {e}")
        finally:
            if page:
                await page.close()
        
        return posts
    
    async def _search_reddit(self, keywords: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search Reddit for career posts"""
        if not self.context:
            logger.error("Browser context not available")
            return []
            
        posts = []
        page = None
        try:
            page = await self.context.new_page()
            if not page:
                logger.error("Failed to create new page")
                return []
            
            # Search relevant subreddits
            subreddits = [
                "cscareerquestions",
                "careerguidance",
                "jobs",
                "careeradvice",
                "gradschool",  # Added for education-related posts
                "college"      # Added for education-related posts
            ]
            
            for subreddit in subreddits:
                # Join keywords for search query
                search_query = " ".join(keywords)
                
                search_url = f"https://www.reddit.com/r/{subreddit}/search/?q={search_query}&sort=new"
                await page.goto(search_url, wait_until='networkidle')
                
                # Wait for posts to load
                await page.wait_for_selector('[data-testid="post-container"]', timeout=30000)
                
                # Extract posts
                reddit_posts = await page.query_selector_all('[data-testid="post-container"]')
                for post in reddit_posts[:max_results // len(subreddits)]:
                    try:
                        post_data = await self._extract_reddit_post(post)
                        if post_data:
                            post_data['source'] = 'reddit'
                            post_data['subreddit'] = subreddit
                            posts.append(post_data)
                    except Exception as e:
                        logger.warning(f"Error extracting Reddit post: {e}")
                        continue
                    
                    await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Error searching Reddit: {e}")
        finally:
            if page:
                await page.close()
        
        return posts
    
    async def _search_hackernews(self, keywords: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search HackerNews for career posts"""
        if not self.context:
            logger.error("Browser context not available")
            return []
            
        posts = []
        page = None
        try:
            page = await self.context.new_page()
            if not page:
                logger.error("Failed to create new page")
                return []
            
            # Join keywords for search query
            search_query = " ".join(keywords)
            
            # Use HN Search API
            search_url = f"https://hn.algolia.com/?q={search_query}"
            await page.goto(search_url, wait_until='networkidle')
            
            # Wait for results
            await page.wait_for_selector('.Story', timeout=30000)
            
            # Extract posts
            hn_posts = await page.query_selector_all('.Story')
            for post in hn_posts[:max_results]:
                try:
                    post_data = await self._extract_hn_post(post)
                    if post_data:
                        post_data['source'] = 'hackernews'
                        posts.append(post_data)
                except Exception as e:
                    logger.warning(f"Error extracting HN post: {e}")
                    continue
                
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Error searching HackerNews: {e}")
        finally:
            if page:
                await page.close()
        
        return posts
    
    async def _extract_tweet(self, tweet) -> Optional[Dict[str, Any]]:
        """Extract data from a tweet"""
        try:
            # Extract tweet text
            text_elem = await tweet.query_selector('[data-testid="tweetText"]')
            text = await text_elem.text_content() if text_elem else ""
            
            # Extract user info
            user_elem = await tweet.query_selector('[data-testid="User-Name"]')
            username = await user_elem.text_content() if user_elem else ""
            
            # Extract timestamp
            time_elem = await tweet.query_selector('time')
            timestamp = await time_elem.get_attribute('datetime') if time_elem else ""
            
            return {
                'content': text,
                'author': username,
                'timestamp': timestamp,
                'type': 'tweet'
            }
        except Exception:
            return None
    
    async def _extract_reddit_post(self, post) -> Optional[Dict[str, Any]]:
        """Extract data from a Reddit post"""
        try:
            # Extract title
            title_elem = await post.query_selector('h3')
            title = await title_elem.text_content() if title_elem else ""
            
            # Extract post content
            content_elem = await post.query_selector('[data-click-id="text"]')
            content = await content_elem.text_content() if content_elem else ""
            
            # Extract author
            author_elem = await post.query_selector('[data-click-id="user"]')
            author = await author_elem.text_content() if author_elem else ""
            
            return {
                'title': title,
                'content': content,
                'author': author,
                'type': 'reddit_post'
            }
        except Exception:
            return None
    
    async def _extract_hn_post(self, post) -> Optional[Dict[str, Any]]:
        """Extract data from a HackerNews post"""
        try:
            # Extract title
            title_elem = await post.query_selector('.Story_title')
            title = await title_elem.text_content() if title_elem else ""
            
            # Extract URL
            url_elem = await post.query_selector('.Story_link')
            url = await url_elem.get_attribute('href') if url_elem else ""
            
            # Extract author
            author_elem = await post.query_selector('.Story_by')
            author = await author_elem.text_content() if author_elem else ""
            
            return {
                'title': title,
                'url': url,
                'author': author,
                'type': 'hn_post'
            }
        except Exception:
            return None
    
    def _filter_relevant_posts(self, posts: List[Dict[str, Any]], role: str, 
                             industry: str, experience_level: str, field: str,
                             location: str, grad_year: Optional[int] = None,
                             grad_year_range: int = 2) -> List[Dict[str, Any]]:
        """Filter posts by relevance to all search criteria"""
        relevant_posts = []
        
        # Compile search patterns
        patterns = {
            'role': re.compile(role, re.IGNORECASE) if role else None,
            'industry': re.compile(industry, re.IGNORECASE) if industry else None,
            'experience': re.compile(experience_level, re.IGNORECASE) if experience_level else None,
            'field': re.compile(field, re.IGNORECASE) if field else None,
            'location': re.compile(location, re.IGNORECASE) if location else None,
            'career': re.compile(r'promotion|career|advancement|growth|transition', re.IGNORECASE),
            'education': re.compile(r'graduated|graduate|alumni|class of|studied|major', re.IGNORECASE)
        }
        
        # Graduation year pattern
        grad_years = []
        if grad_year is not None:
            grad_years = range(grad_year - grad_year_range, grad_year + grad_year_range + 1)
            grad_pattern = '|'.join(map(str, grad_years))
            patterns['grad_year'] = re.compile(grad_pattern)
        
        for post in posts:
            score = 0
            content = post.get('content', '') or post.get('title', '')
            
            # Basic career-related score
            if patterns['career'].search(content):
                score += 1
            
            # Role match
            if patterns['role'] and patterns['role'].search(content):
                score += 2
            
            # Industry match
            if patterns['industry'] and patterns['industry'].search(content):
                score += 2
            
            # Experience level match
            if patterns['experience'] and patterns['experience'].search(content):
                score += 2
            
            # Field of study match
            if patterns['field'] and patterns['field'].search(content):
                score += 2
            
            # Location match
            if patterns['location'] and patterns['location'].search(content):
                score += 2
            
            # Education/graduation info
            if patterns['education'].search(content):
                score += 1
                
                # Graduation year match
                if grad_year is not None and 'grad_year' in patterns and patterns['grad_year'].search(content):
                    score += 3  # Higher weight for exact grad year match
            
            # Add post if it's relevant enough (adjusted threshold)
            if score >= 3:  # Increased threshold due to more criteria
                post['relevance_score'] = score
                relevant_posts.append(post)
        
        # Sort by relevance score
        return sorted(relevant_posts, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    async def close(self):
        """Close browser and cleanup resources"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed") 