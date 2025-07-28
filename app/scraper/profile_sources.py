"""
Profile Sources for Future Founder Finder
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import random
from loguru import logger

class ProfileSource(ABC):
    """Abstract base class for profile sources"""
    
    @abstractmethod
    def search_profiles(self, company: str = '', title: str = '', location: str = '', 
                       max_results: int = 50) -> List[Dict[str, Any]]:
        """Search for profiles based on criteria"""
        pass

class AngelListSource(ProfileSource):
    """AngelList (Wellfound) profile source"""
    
    def __init__(self, driver: Optional[webdriver.Chrome] = None):
        self.driver = driver
        self.base_url = "https://wellfound.com/candidates/search"
    
    def search_profiles(self, company: str = '', title: str = '', location: str = '', 
                       max_results: int = 50) -> List[Dict[str, Any]]:
        try:
            # Build search URL
            search_url = f"{self.base_url}?role={title}&location={location}"
            if company:
                search_url += f"&company={company}"
                
            logger.info(f"Searching AngelList with URL: {search_url}")
            
            # Use requests for initial fetch
            response = requests.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            profiles = []
            profile_cards = soup.find_all('div', class_='candidate-card')
            
            for card in profile_cards[:max_results]:
                try:
                    profile = self._extract_profile(card)
                    if profile:
                        profile['source'] = 'angellist'
                        profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Error extracting AngelList profile: {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            logger.error(f"Error searching AngelList profiles: {e}")
            return []
    
    def _extract_profile(self, card) -> Optional[Dict[str, Any]]:
        try:
            name = card.find('h3', class_='name').text.strip()
            title = card.find('div', class_='title').text.strip()
            location = card.find('div', class_='location').text.strip()
            
            return {
                'name': name,
                'title': title,
                'location': location,
                'profile_url': None  # AngelList requires login for profile URLs
            }
        except Exception:
            return None

class CrunchbaseSource(ProfileSource):
    """Crunchbase profile source"""
    
    def __init__(self, driver: Optional[webdriver.Chrome] = None):
        self.driver = driver
        self.base_url = "https://www.crunchbase.com/discover/people"
    
    def search_profiles(self, company: str = '', title: str = '', location: str = '', 
                       max_results: int = 50) -> List[Dict[str, Any]]:
        try:
            # Build search URL
            search_url = f"{self.base_url}?q={title}"
            if location:
                search_url += f"+{location}"
            if company:
                search_url += f"+{company}"
                
            logger.info(f"Searching Crunchbase with URL: {search_url}")
            
            profiles = []
            if self.driver:
                self.driver.get(search_url)
                time.sleep(random.uniform(2, 4))
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "person-card"))
                    )
                    
                    profile_cards = self.driver.find_elements(By.CLASS_NAME, "person-card")
                    for card in profile_cards[:max_results]:
                        try:
                            profile = self._extract_profile(card)
                            if profile:
                                profile['source'] = 'crunchbase'
                                profiles.append(profile)
                        except Exception as e:
                            logger.warning(f"Error extracting Crunchbase profile: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Timeout waiting for Crunchbase results: {e}")
            
            return profiles
            
        except Exception as e:
            logger.error(f"Error searching Crunchbase profiles: {e}")
            return []
    
    def _extract_profile(self, card) -> Optional[Dict[str, Any]]:
        try:
            name = card.find_element(By.CSS_SELECTOR, ".name").text.strip()
            title = card.find_element(By.CSS_SELECTOR, ".title").text.strip()
            company = card.find_element(By.CSS_SELECTOR, ".company").text.strip()
            
            return {
                'name': name,
                'title': title,
                'company': company,
                'profile_url': None  # Crunchbase requires login for profile URLs
            }
        except Exception:
            return None

class GithubSource(ProfileSource):
    """GitHub profile source"""
    
    def __init__(self, driver: Optional[webdriver.Chrome] = None):
        self.driver = driver
        self.base_url = "https://github.com/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        })
    
    def search_profiles(self, company: str = '', title: str = '', location: str = '', 
                       max_results: int = 50) -> List[Dict[str, Any]]:
        try:
            # Build search query
            query = f"type:user"
            if company:
                query += f" company:{company}"
            if location:
                query += f" location:{location}"
                
            # Add common tech titles if no specific title is provided
            if not title:
                query += " software OR developer OR engineer"
            else:
                query += f" {title}"
                
            search_url = f"{self.base_url}?q={query}&type=users"
            logger.info(f"Searching GitHub with URL: {search_url}")
            
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            profiles = []
            profile_cards = soup.find_all('div', class_='user-list-item')
            
            for card in profile_cards[:max_results]:
                try:
                    profile = self._extract_profile(card)
                    if profile:
                        profile['source'] = 'github'
                        profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Error extracting GitHub profile: {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            logger.error(f"Error searching GitHub profiles: {e}")
            return []
    
    def _extract_profile(self, card) -> Optional[Dict[str, Any]]:
        try:
            name_elem = card.find('a', class_='name')
            name = name_elem.text.strip()
            profile_url = f"https://github.com{name_elem['href']}"
            
            bio = card.find('p', class_='bio')
            title = bio.text.strip() if bio else ""
            
            location_elem = card.find('li', class_='location')
            location = location_elem.text.strip() if location_elem else ""
            
            return {
                'name': name,
                'title': title,
                'location': location,
                'profile_url': profile_url
            }
        except Exception:
            return None 