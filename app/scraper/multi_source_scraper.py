"""
Multi-source profile scraper for Future Founder Finder
"""

import asyncio
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from loguru import logger
import aiohttp
from bs4 import BeautifulSoup
import certifi
import ssl
import json
import time
from config import Config
import os

class MultiSourceScraper:
    def __init__(self):
        """Initialize the multi-source scraper"""
        self.config = Config()
        self.session = None
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/vnd.github.v3+json'  # Explicitly request GitHub API v3
        }
        
        # API keys and endpoints
        self.github_token = os.getenv('GITHUB_TOKEN', '').strip()  # Get directly from environment
        if not self.github_token:
            self.github_token = getattr(self.config, 'GITHUB_TOKEN', '').strip()  # Fallback to config
            
        # Validate GitHub token
        if self.github_token:
            if not self.github_token.startswith('ghp_'):
                logger.error("Invalid GitHub token format: Token must start with 'ghp_'")
                self.github_token = ''
            elif len(self.github_token) != 44:  # GitHub tokens are 40 characters plus 'ghp_' prefix
                logger.error(f"Invalid GitHub token length: Expected 44 characters (including 'ghp_'), got {len(self.github_token)}")
                self.github_token = ''
            elif ' ' in self.github_token or '#' in self.github_token:
                logger.error("Invalid GitHub token format: Token contains spaces or comments")
                self.github_token = ''
            else:
                logger.info("GitHub token format appears valid")
        else:
            logger.error("No GitHub token found")
        
        self.github_api = getattr(self.config, 'GITHUB_API', 'https://api.github.com')
        
        # Rate limiting - GitHub allows 5000 requests/hour with auth
        self.rate_limits = {
            'github': {'calls': 0, 'reset_time': time.time(), 'limit': 4500}  # Keep buffer of 500
        }
    
    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
            logger.info("HTTP session initialized")

    async def _check_rate_limit(self, source: str) -> None:
        """Check and handle rate limiting for a source"""
        if source not in self.rate_limits:
            return
            
        rate_info = self.rate_limits[source]
        current_time = time.time()
        
        # Reset counter if an hour has passed
        if current_time - rate_info['reset_time'] >= 3600:  # GitHub resets hourly
            rate_info['calls'] = 0
            rate_info['reset_time'] = current_time
        
        # Wait if we've hit the limit
        if rate_info['calls'] >= rate_info['limit']:
            wait_time = 3600 - (current_time - rate_info['reset_time'])
            if wait_time > 0:
                logger.info(f"Rate limit hit for {source}, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                rate_info['calls'] = 0
                rate_info['reset_time'] = time.time()
        
        rate_info['calls'] += 1

    async def _make_request(self, source: str, url: str, headers: Optional[Dict[str, str]] = None, 
                          params: Optional[Dict[str, str]] = None, retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make a rate-limited request with retries"""
        if not self.session:
            await self.init_session()
            if not self.session:
                logger.error("Failed to initialize HTTP session")
                return None
                
        await self._check_rate_limit(source)
        
        # Ensure headers dictionary exists
        if headers is None:
            headers = {}
        
        # Add GitHub token if making a GitHub API request
        if source == 'github' and self.github_token:
            # GitHub API requires token in Authorization header
            headers['Authorization'] = f'token {self.github_token.strip()}'
            logger.debug(f"Using GitHub token: {bool(self.github_token)}")
        
        # Add default headers
        headers.update(self.headers)
        
        # Log request details for debugging
        logger.debug(f"Making request to {url}")
        logger.debug(f"Headers: {headers}")
        
        for attempt in range(retries):
            try:
                async with self.session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Too Many Requests
                        retry_after = 3600  # Default to 1 hour for GitHub
                        try:
                            if 'Retry-After' in response.headers:
                                retry_after = int(response.headers['Retry-After'])
                        except (ValueError, TypeError):
                            pass  # Keep default if header value is invalid
                        logger.warning(f"{source} rate limited, waiting {retry_after} seconds")
                        await asyncio.sleep(retry_after)
                    elif response.status == 401:  # Unauthorized
                        error_body = await response.text()
                        logger.error(f"{source} API error: Unauthorized. Token: {bool(self.github_token)}")
                        logger.error(f"Response body: {error_body}")
                        return None
                    elif response.status == 403:  # Forbidden
                        error_body = await response.text()
                        logger.error(f"{source} API error: Forbidden. Check your API permissions.")
                        logger.error(f"Response body: {error_body}")
                        return None
                    else:
                        error_body = await response.text()
                        logger.error(f"{source} API error: {response.status}")
                        logger.error(f"Response body: {error_body}")
                        if attempt < retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                logger.error(f"Error making request to {source}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None

    async def search_professional_profiles(self, name: str, company: str, role: str) -> List[Dict[str, Any]]:
        """Search for professional profiles across platforms"""
        if not self.session:
            await self.init_session()
        
        query = f"{name} {company} {role}".strip()
        
        # Search GitHub profiles
        profiles = await self._search_github(query)
        
        return self._deduplicate_results(profiles)

    async def _search_github(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub for user profiles"""
        try:
            headers = {'Authorization': f'token {self.github_token}'} if self.github_token else {}
            data = await self._make_request('github', f'{self.github_api}/search/users',
                                          headers=headers,
                                          params={'q': query})
            
            if not data or not isinstance(data, dict) or 'items' not in data:
                return []
                
            profiles = []
            for item in data['items']:
                # Get detailed user info
                user_data = await self._make_request('github', item['url'], headers=headers)
                if user_data:
                    # Get repository data for assessment
                    repos_data = await self._make_request('github', f"{item['url']}/repos", headers=headers)
                    repos = repos_data if isinstance(repos_data, list) else []
                    
                    # Get contribution data
                    contributions = await self._get_contribution_stats(item['url'], headers)
                    
                    # Calculate scores
                    scores = self._calculate_technical_score(user_data, repos, contributions)
                    
                    # Calculate account age and estimate actual age
                    age_info = self._calculate_age_info(user_data, repos)
                    
                    profile = {
                        'name': user_data.get('name', ''),
                        'company': user_data.get('company', ''),
                        'location': user_data.get('location', ''),
                        'bio': user_data.get('bio', ''),
                        'github_url': user_data.get('html_url', ''),
                        'public_repos': user_data.get('public_repos', 0),
                        'followers': user_data.get('followers', 0),
                        'following': user_data.get('following', 0),
                        'account_age': age_info['account_age'],
                        'estimated_age': age_info['estimated_age'],
                        'early_achievements': age_info['early_achievements'],
                        'technical_score': scores['technical_score'],
                        'innovation_score': scores['innovation_score'],
                        'collaboration_score': scores['collaboration_score'],
                        'age_score': scores['age_score'],
                        'founder_potential': scores['founder_potential'],
                        'languages': self._extract_languages(repos),
                        'top_repos': self._get_top_repos(repos),
                        'contribution_frequency': contributions['frequency'],
                        'source': 'github'
                    }
                    profiles.append(profile)
            
            # Sort by founder potential
            return sorted(profiles, key=lambda x: x['founder_potential'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
            return []

    async def _get_contribution_stats(self, user_url: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get user's contribution statistics"""
        try:
            # Get contribution activity
            events_url = f"{user_url}/events/public"
            events_data = await self._make_request('github', events_url, headers=headers)
            
            if not events_data or not isinstance(events_data, list):
                return {'frequency': 'low'}
            
            # Calculate contribution frequency
            now = datetime.now(timezone.utc)  # Use UTC timezone
            recent_count = 0
            
            for event in events_data:
                try:
                    created_at_str = event.get('created_at') if isinstance(event, dict) else None
                    if created_at_str:
                        # Parse GitHub timestamp to UTC
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        if (now - created_at).days <= 90:
                            recent_count += 1
                except (ValueError, KeyError, TypeError, AttributeError) as e:
                    logger.debug(f"Error processing event date: {e}")
                    continue
            
            if recent_count > 100:
                frequency = 'very_high'
            elif recent_count > 50:
                frequency = 'high'
            elif recent_count > 20:
                frequency = 'medium'
            else:
                frequency = 'low'
                
            return {'frequency': frequency}
            
        except Exception as e:
            logger.error(f"Error getting contribution stats: {e}")
            return {'frequency': 'low'}

    def _calculate_technical_score(self, user_data: Dict[str, Any], repos: List[Dict[str, Any]], 
                                 contributions: Dict[str, Any]) -> Dict[str, float]:
        """Calculate technical expertise and other scores"""
        # Base scores
        technical_score = 0.0
        innovation_score = 0.0
        collaboration_score = 0.0
        
        # Technical score components
        if repos:
            # Repository quality
            total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
            total_forks = sum(repo.get('forks_count', 0) for repo in repos)
            
            # Language diversity
            languages = set()
        for repo in repos:
            if repo.get('language'):
                    languages.add(repo.get('language'))
            
            # Calculate technical score
            technical_score = min(1.0, (
                (total_stars * 0.3) / 100 +  # Stars weight
                (total_forks * 0.2) / 50 +   # Forks weight
                (len(languages) * 0.2) / 5 +  # Language diversity
                (len(repos) * 0.3) / 20       # Number of repos
            ))
            
            # Innovation score based on original projects
            innovation_score = min(1.0, (
                (total_stars * 0.4) / 100 +
                (total_forks * 0.3) / 50 +
                (0.3 if contributions['frequency'] in ['high', 'very_high'] else 0.1)
            ))
            
            # Collaboration score
            collaboration_score = min(1.0, (
                (user_data.get('followers', 0) * 0.4) / 500 +
                (user_data.get('following', 0) * 0.2) / 200 +
                (0.4 if contributions['frequency'] in ['high', 'very_high'] else 0.2)
            ))
        
        # Calculate founder potential
        founder_potential = (
            technical_score * 0.4 +
            innovation_score * 0.3 +
            collaboration_score * 0.3
        )
        
        return {
            'technical_score': technical_score * 10,  # Scale to 0-10
            'innovation_score': innovation_score * 10,
            'collaboration_score': collaboration_score * 10,
            'age_score': self._calculate_age_score(user_data),
            'founder_potential': founder_potential * 10
        }

    def _calculate_age_info(self, user_data: Dict[str, Any], repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate age-related information"""
        try:
            created_at = datetime.fromisoformat(user_data.get('created_at', '').replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            account_years = (now - created_at).days / 365.25
            
            # Early achievements analysis
            early_achievements = []
            if repos:
                # Sort repos by stars
                top_repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)
                for repo in top_repos[:3]:
                    repo_created = datetime.fromisoformat(repo.get('created_at', '').replace('Z', '+00:00'))
                    repo_age = (repo_created - created_at).days / 365.25
                    if repo_age <= 2 and repo.get('stargazers_count', 0) >= 50:
                        early_achievements.append({
                            'name': repo.get('name', ''),
                            'stars': repo.get('stargazers_count', 0),
                            'created_after_years': round(repo_age, 1)
                        })
            
            # Estimate actual age
            estimated_age = None
            bio = user_data.get('bio', '').lower()
            
            # Look for age indicators in bio
            grad_year_match = re.search(r'class of (20\d{2})', bio)
            if grad_year_match:
                grad_year = int(grad_year_match.group(1))
                estimated_age = datetime.now(timezone.utc).year - grad_year + 22
            
            # If no direct age indicators, estimate from account age
            if not estimated_age:
                # Assume they were at least 16 when creating the account
                estimated_age = max(16 + account_years, 16)
            
            return {
                'account_age': f"{account_years:.1f} years",
                'estimated_age': int(estimated_age),
                'early_achievements': early_achievements
            }
            
        except Exception as e:
            logger.error(f"Error calculating age info: {e}")
            return {
                'account_age': "N/A",
                'estimated_age': None,
                'early_achievements': []
            }

    def _get_top_repos(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get user's top repositories by stars"""
        if not repos:
            return []
            
        # Sort repos by stars
        sorted_repos = sorted(repos, key=lambda x: x.get('stargazers_count', 0), reverse=True)
        
        # Return top 3 repos with relevant info
        top_repos = []
        for repo in sorted_repos[:3]:
            repo_info = {
                'name': repo.get('name', ''),
                'description': repo.get('description', ''),
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language', ''),
                'created_at': repo.get('created_at', '')
            }
            top_repos.append(repo_info)
        return top_repos

    def _calculate_age_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate age-based score (favoring younger profiles)"""
        try:
            created_at = datetime.fromisoformat(user_data.get('created_at', '').replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            account_age = (now - created_at).days / 365.25
            
            # Assume they were at least 16 when creating the account
            estimated_age = 16 + account_age
            
            # Score peaks at age 25, gradually decreases until 35
            if estimated_age < 25:
                score = 0.7 + (estimated_age - 16) * 0.03  # Gradually increase from 0.7 to 1.0
            elif estimated_age <= 35:
                score = 1.0 - (estimated_age - 25) * 0.03  # Gradually decrease from 1.0 to 0.7
            else:
                score = 0.7 - (estimated_age - 35) * 0.02  # Continue decreasing after 35
                
            return max(0, min(score * 10, 10))  # Scale to 0-10 and clamp
            
        except Exception as e:
            logger.error(f"Error calculating age score: {e}")
            return 5.0  # Default to middle score on error

    def _extract_languages(self, repos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Extract programming languages from repositories"""
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        return languages

    def _deduplicate_results(self, profiles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate profiles based on name and company"""
        seen = set()
        unique_profiles = []
        
        for profile in profiles:
            key = f"{profile.get('name', '')}-{profile.get('company', '')}"
            if key not in seen:
                seen.add(key)
                unique_profiles.append(profile)
        
        return unique_profiles

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("HTTP session closed") 