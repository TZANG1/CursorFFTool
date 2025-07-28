"""
Playwright-based scraper for professional profiles
"""

import asyncio
import random
import time
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from loguru import logger

class PlaywrightScraper:
    def __init__(self):
        """Initialize Playwright scraper"""
        self.browser = None
        self.context = None
        
    async def init(self):
        """Initialize browser and context"""
        try:
            playwright = await async_playwright().start()
            
            self.browser = await playwright.chromium.launch(headless=True)
            
            # Context configuration with stealth settings
            context_config = {
                'viewport': {
                    'width': random.choice([1280, 1366, 1920]),
                    'height': random.choice([800, 768, 1080])
                },
                'user_agent': self._get_random_user_agent(),
                'locale': 'en-US',
                'timezone_id': 'America/Los_Angeles',
                'permissions': ['geolocation'],
                'geolocation': {'latitude': 37.7749, 'longitude': -122.4194},  # San Francisco
                'color_scheme': 'light',
                'device_scale_factor': 1,
                'is_mobile': False,
                'has_touch': False
            }
            
            self.context = await self.browser.new_context(**context_config)
            
            # Add stealth scripts
            await self._add_stealth_scripts()
            
            logger.info("Playwright browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
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
    
    async def _add_stealth_scripts(self):
        """Add scripts to avoid detection"""
        if not self.context:
            return
            
        # Override webdriver property
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        # Add plugins
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    }
                ]
            });
        """)
        
        # Add other browser-specific properties
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: async (param) => ({
                        state: param.name === 'notifications' ? 'prompt' : 'granted'
                    })
                })
            });
        """)
    
    async def search_profiles(self, company: str = '', title: str = '', location: str = '',
                            max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for professional profiles"""
        if not self.context or not self.browser:
            if not await self.init():
                logger.error("Failed to initialize browser context")
                return []
            
        if not self.context:
            logger.error("Browser context is not available")
            return []
        
        page = None
        profiles = []
        try:
            # Create new page
            page = await self.context.new_page()
            if not page:
                logger.error("Failed to create new page")
                return []
            
            # Add random delays and mouse movements
            await self._add_human_behavior(page)
            
            # Search on different platforms
            linkedin_profiles = await self._search_linkedin(page, company, title, location, max_results)
            profiles.extend(linkedin_profiles)
            
            github_profiles = await self._search_github(page, company, title, location, max_results)
            profiles.extend(github_profiles)
            
            return profiles[:max_results]
            
        except Exception as e:
            logger.error(f"Error searching profiles: {e}")
            return []
        finally:
            if page:
                await page.close()
    
    async def _add_human_behavior(self, page: Page):
        """Add random human-like behavior"""
        # Random mouse movements
        await page.mouse.move(
            random.randint(0, 500),
            random.randint(0, 500)
        )
        
        # Random scrolling
        await page.evaluate("""
            window.scrollTo({
                top: Math.random() * 100,
                behavior: 'smooth'
            });
        """)
        
        # Random delay
        await asyncio.sleep(random.uniform(1, 3))
    
    async def _search_linkedin(self, page: Page, company: str, title: str, location: str,
                             max_results: int) -> List[Dict[str, Any]]:
        """Search LinkedIn profiles"""
        profiles = []
        try:
            # Build search URL
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={title}"
            if company:
                search_url += f"+{company}"
            if location:
                search_url += f"+{location}"
            
            # Navigate to search page
            await page.goto(search_url, wait_until='networkidle')
            await self._add_human_behavior(page)
            
            # Wait for results
            await page.wait_for_selector('.search-result', timeout=30000)
            
            # Extract profiles
            elements = await page.query_selector_all('.search-result')
            for element in elements[:max_results]:
                try:
                    profile = await self._extract_linkedin_profile(element)
                    if profile:
                        profile['source'] = 'linkedin'
                        profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Error extracting LinkedIn profile: {e}")
                    continue
                
                # Add random delay between extractions
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {e}")
        
        return profiles
    
    async def _search_github(self, page: Page, company: str, title: str, location: str,
                           max_results: int) -> List[Dict[str, Any]]:
        """Search GitHub profiles"""
        profiles = []
        try:
            # Build search query
            query = f"type:user"
            if company:
                query += f"+company:{company}"
            if location:
                query += f"+location:{location}"
            if title:
                query += f"+{title}"
            
            search_url = f"https://github.com/search?q={query}&type=users"
            
            # Navigate to search page
            await page.goto(search_url, wait_until='networkidle')
            await self._add_human_behavior(page)
            
            # Wait for results
            await page.wait_for_selector('.user-list-item', timeout=30000)
            
            # Extract profiles
            elements = await page.query_selector_all('.user-list-item')
            for element in elements[:max_results]:
                try:
                    profile = await self._extract_github_profile(element)
                    if profile:
                        profile['source'] = 'github'
                        profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Error extracting GitHub profile: {e}")
                    continue
                
                # Add random delay between extractions
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.error(f"Error searching GitHub: {e}")
        
        return profiles
    
    async def _extract_linkedin_profile(self, element) -> Optional[Dict[str, Any]]:
        """Extract profile data from LinkedIn search result"""
        try:
            name = await element.query_selector('.name')
            title = await element.query_selector('.title')
            company = await element.query_selector('.company')
            location = await element.query_selector('.location')
            
            return {
                'name': await name.text_content() if name else "",
                'title': await title.text_content() if title else "",
                'company': await company.text_content() if company else "",
                'location': await location.text_content() if location else "",
                'profile_url': await element.get_attribute('href')
            }
        except Exception:
            return None
    
    async def _extract_github_profile(self, element) -> Optional[Dict[str, Any]]:
        """Extract profile data from GitHub search result"""
        try:
            name = await element.query_selector('.name')
            bio = await element.query_selector('.bio')
            location = await element.query_selector('.location')
            
            profile_link = await element.query_selector('a.name')
            profile_url = await profile_link.get_attribute('href') if profile_link else None
            
            return {
                'name': await name.text_content() if name else "",
                'title': await bio.text_content() if bio else "",
                'location': await location.text_content() if location else "",
                'profile_url': f"https://github.com{profile_url}" if profile_url else None
            }
        except Exception:
            return None
    
    async def close(self):
        """Close browser and cleanup resources"""
        if self.browser:
            await self.browser.close()
            logger.info("Playwright browser closed") 