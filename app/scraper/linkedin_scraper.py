"""
LinkedIn Scraper for Future Founder Finder
"""

import time
import random
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config
from loguru import logger
from .stealth import (
    create_stealth_driver,
    human_like_typing,
    random_scroll,
    add_random_delays,
    simulate_human_behavior
)

class LinkedInScraper:
    def __init__(self):
        """Initialize LinkedIn scraper"""
        self.config = Config()
        self.driver = None
        self.is_authenticated = False
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Selenium WebDriver with stealth settings"""
        try:
            self.driver = create_stealth_driver()
            if self.driver:
                logger.info("Selenium WebDriver initialized successfully")
                return True
            else:
                logger.error("Failed to create stealth driver")
                return False
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            self.driver = None
            return False
    
    def search_profiles(self, company: str = '', title: str = '', location: str = '', 
                       max_results: int = 50) -> List[Dict[str, Any]]:
        """Search LinkedIn profiles based on criteria"""
        profiles = []
        
        try:
            # Add random initial delay
            time.sleep(add_random_delays())
            
            # Build search URL
            search_url = self._build_search_url(company, title, location)
            logger.info(f"Searching LinkedIn with URL: {search_url}")
            
            if self.driver:
                # Navigate to search URL
                self.driver.get(search_url)
                
                # Simulate human behavior before searching
                simulate_human_behavior(self.driver)
                
                # Random delay before scrolling
                time.sleep(add_random_delays())
                
                # Scroll like a human
                random_scroll(self.driver, 1000)  # Scroll down 1000px initially
                
                # Wait for results with human-like patience
                try:
                    WebDriverWait(self.driver, random.uniform(15, 25)).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "search-result"))
                    )
                except Exception as e:
                    logger.warning(f"Timeout waiting for results: {e}")
                    return []
                
                # Extract profile cards with random delays
                profile_cards = self.driver.find_elements(By.CLASS_NAME, "search-result")
                
                for card in profile_cards[:max_results]:
                    try:
                        # Simulate human behavior between profile extractions
                        simulate_human_behavior(self.driver)
                        
                        profile = self._extract_profile_from_card(card)
                        if profile:
                            profiles.append(profile)
                            
                        # Add random delay between extractions
                        time.sleep(random.uniform(1.5, 3.5))
                        
                    except Exception as e:
                        logger.warning(f"Error extracting profile from card: {e}")
                        continue
            
            logger.info(f"Found {len(profiles)} profiles")
            return profiles
            
        except Exception as e:
            logger.error(f"Error searching profiles: {e}")
            return []
    
    def _build_search_url(self, company: str, title: str, location: str) -> str:
        """Build LinkedIn search URL"""
        base_url = "https://www.linkedin.com/search/results/people/"
        params = []
        
        if company:
            params.append(f"company={company}")
        if title:
            params.append(f"title={title}")
        if location:
            params.append(f"location={location}")
        
        # Add filters for age range and experience
        params.append("facetAgeRange=25-35")
        params.append("facetExperienceLevel=entry_level,mid_senior_level")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        return base_url
    
    def _extract_profile_from_card(self, card) -> Optional[Dict[str, Any]]:
        """Extract profile data from Selenium element"""
        try:
            if not self.driver:
                return None
                
            # Scroll element into view naturally
            self.driver.execute_script("""
                arguments[0].scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            """, card)
            
            # Small delay after scrolling
            time.sleep(random.uniform(0.5, 1.5))
            
            # Extract basic info
            name_elem = card.find_element(By.CSS_SELECTOR, ".name")
            name = name_elem.text.strip() if name_elem else ""
            
            title_elem = card.find_element(By.CSS_SELECTOR, ".title")
            title = title_elem.text.strip() if title_elem else ""
            
            company_elem = card.find_element(By.CSS_SELECTOR, ".company")
            company = company_elem.text.strip() if company_elem else ""
            
            location_elem = card.find_element(By.CSS_SELECTOR, ".location")
            location = location_elem.text.strip() if location_elem else ""
            
            # Extract LinkedIn URL
            profile_link = card.find_element(By.CSS_SELECTOR, "a[href*='/in/']")
            linkedin_url = profile_link.get_attribute('href') if profile_link else ""
            
            return {
                'name': name,
                'title': title,
                'company': company,
                'location': location,
                'linkedin_url': linkedin_url,
                'source': 'linkedin'
            }
            
        except Exception as e:
            logger.warning(f"Error extracting profile from card: {e}")
            return None
    
    def _extract_profile_from_soup(self, card) -> Optional[Dict[str, Any]]:
        """Extract profile data from BeautifulSoup element"""
        try:
            # Extract basic info
            name_elem = card.find('span', class_='name')
            name = name_elem.text.strip() if name_elem else ""
            
            title_elem = card.find('span', class_='title')
            title = title_elem.text.strip() if title_elem else ""
            
            company_elem = card.find('span', class_='company')
            company = company_elem.text.strip() if company_elem else ""
            
            location_elem = card.find('span', class_='location')
            location = location_elem.text.strip() if location_elem else ""
            
            # Extract LinkedIn URL
            profile_link = card.find('a', href=lambda x: x and '/in/' in x)
            linkedin_url = profile_link['href'] if profile_link else ""
            
            return {
                'name': name,
                'title': title,
                'company': company,
                'location': location,
                'linkedin_url': linkedin_url,
                'age': None,  # Will be estimated later
                'source': 'linkedin'
            }
            
        except Exception as e:
            logger.warning(f"Error extracting profile from soup: {e}")
            return None
    
    def _estimate_age_from_profile(self, card) -> Optional[int]:
        """Estimate age from profile information"""
        try:
            # Look for education information
            education_elem = card.find_element(By.CSS_SELECTOR, ".education")
            if education_elem:
                education_text = education_elem.text.lower()
                
                # Look for graduation years
                import re
                years = re.findall(r'\b(19|20)\d{2}\b', education_text)
                if years:
                    graduation_year = max(int(year) for year in years)
                    current_year = time.localtime().tm_year
                    estimated_age = current_year - graduation_year + 22  # Assume graduation at 22
                    return max(18, min(100, estimated_age))
            
            # Look for experience information
            experience_elem = card.find_element(By.CSS_SELECTOR, ".experience")
            if experience_elem:
                experience_text = experience_elem.text.lower()
                
                # Look for "X years of experience"
                experience_match = re.search(r'(\d+)\s*years?\s*of\s*experience', experience_text)
                if experience_match:
                    experience_years = int(experience_match.group(1))
                    estimated_age = 22 + experience_years  # Assume starting career at 22
                    return max(18, min(100, estimated_age))
            
        except Exception as e:
            logger.debug(f"Error estimating age: {e}")
        
        return None
    
    def get_profile_details(self, linkedin_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile information"""
        try:
            if not self.driver:
                logger.warning("Selenium driver not available for detailed profile scraping")
                return None
            
            self.driver.get(linkedin_url)
            time.sleep(random.uniform(2, 4))
            
            # Extract detailed information
            profile_data = {
                'linkedin_url': linkedin_url,
                'name': self._get_text_by_selector('.profile-name'),
                'title': self._get_text_by_selector('.profile-title'),
                'company': self._get_text_by_selector('.profile-company'),
                'location': self._get_text_by_selector('.profile-location'),
                'education': self._get_text_by_selector('.profile-education'),
                'experience': self._extract_experience_section(),
                'skills': self._extract_skills_section(),
                'achievements': self._extract_achievements_section()
            }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error getting profile details: {e}")
            return None
    
    def _get_text_by_selector(self, selector: str, element: Any = None) -> str:
        """Get text content by CSS selector"""
        if not self.driver:
            return ""
        try:
            if element:
                return element.find_element(By.CSS_SELECTOR, selector).text.strip()
            else:
                return self.driver.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return ""
    
    def _extract_experience_section(self) -> List[Dict[str, str]]:
        """Extract work experience from profile"""
        if not self.driver:
            return []
            
        experience = []
        try:
            experience_elements = self.driver.find_elements(By.CSS_SELECTOR, '.experience-item')
            
            for elem in experience_elements:
                exp = {
                    'title': self._get_text_by_selector('.title'),
                    'company': self._get_text_by_selector('.company'),
                    'duration': self._get_text_by_selector('.duration'),
                    'description': self._get_text_by_selector('.description')
                }
                experience.append(exp)
                
        except Exception as e:
            logger.debug(f"Error extracting experience: {e}")
        
        return experience
    
    def _extract_skills_section(self) -> List[str]:
        """Extract skills from profile"""
        if not self.driver:
            return []
            
        skills = []
        try:
            skill_elements = self.driver.find_elements(By.CSS_SELECTOR, '.skill-item')
            skills = [elem.text.strip() for elem in skill_elements if elem.text.strip()]
        except Exception as e:
            logger.debug(f"Error extracting skills: {e}")
        
        return skills
    
    def _extract_achievements_section(self) -> List[str]:
        """Extract achievements from profile"""
        if not self.driver:
            return []
            
        achievements = []
        try:
            achievement_elements = self.driver.find_elements(By.CSS_SELECTOR, '.achievement-item')
            achievements = [elem.text.strip() for elem in achievement_elements if elem.text.strip()]
        except Exception as e:
            logger.debug(f"Error extracting achievements: {e}")
        
        return achievements
    
    def close(self):
        """Close the scraper and cleanup resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 