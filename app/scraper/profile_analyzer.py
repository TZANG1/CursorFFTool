"""
Profile Analyzer for Future Founder Finder
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from config import Config

class ProfileAnalyzer:
    def __init__(self):
        """Initialize profile analyzer"""
        self.config = Config()
        
        # Title level mapping for career progression analysis
        self.title_levels = {
            'intern': 1,
            'associate': 2,
            'analyst': 2,
            'specialist': 2,
            'coordinator': 2,
            'manager': 3,
            'senior': 4,
            'lead': 4,
            'principal': 5,
            'director': 6,
            'head': 6,
            'vp': 7,
            'vice president': 7,
            'c-level': 8,
            'ceo': 8,
            'cto': 8,
            'cfo': 8,
            'founder': 10,
            'co-founder': 10,
            'entrepreneur': 10
        }
        
        # Technical expertise indicators
        self.technical_indicators = {
            'github': {
                'repos': 0.3,      # Weight for number of repos
                'followers': 0.2,   # Weight for followers
                'stars': 0.5       # Weight for total stars
            },
            'patents': {
                'filed': 0.6,      # Weight for filed patents
                'granted': 0.4     # Weight for granted patents
            },
            'publications': {
                'technical': 0.4,  # Weight for technical blog posts
                'research': 0.6    # Weight for research papers
            },
            'speaking': {
                'conference': 0.7,  # Weight for conference talks
                'meetup': 0.3      # Weight for meetup talks
            }
        }
    
    def calculate_future_founder_score(self, profile: Dict[str, Any]) -> float:
        """Calculate a score indicating potential as a future founder"""
        score = 0.0
        weights = self.config.SCORING_WEIGHTS
        
        # Age score (0-1)
        age_score = self._calculate_age_score(profile.get('age'))
        score += age_score * weights['age']
        
        # Career progression score (0-1)
        career_score = self._calculate_career_progression_score(profile)
        score += career_score * weights['career_progression']
        
        # Technical expertise score (0-1)
        technical_score = self._calculate_technical_expertise_score(profile)
        score += technical_score * weights.get('technical_expertise', 0.15)
        
        # Innovation score (0-1)
        innovation_score = self._calculate_innovation_score(profile)
        score += innovation_score * weights.get('innovation', 0.15)
        
        # Leadership score (0-1)
        leadership_score = self._calculate_leadership_score(profile)
        score += leadership_score * weights.get('leadership', 0.15)
        
        # Education score (0-1)
        education_score = self._calculate_education_score(profile.get('education'))
        score += education_score * weights['education']
        
        return round(score, 3)
    
    def _calculate_technical_expertise_score(self, profile: Dict[str, Any]) -> float:
        """Calculate technical expertise score based on GitHub, patents, and publications"""
        score = 0.0
        weights = self.technical_indicators
        
        # GitHub activity
        if profile.get('source') == 'github':
            github_score = (
                min(profile.get('public_repos', 0) / 20, 1) * weights['github']['repos'] +
                min(profile.get('followers', 0) / 500, 1) * weights['github']['followers']
            )
            score += github_score
        
        # Patents
        if profile.get('source') == 'patents':
            patents_score = 1.0  # Having patents is a strong signal
            score += patents_score
        
        # Technical publications
        if profile.get('source') in ['medium', 'devto']:
            pub_score = 0.7  # Technical writing shows expertise
            score += pub_score
        
        # Research papers
        if profile.get('source') == 'research_papers':
            research_score = 0.8  # Academic research is valuable
            score += research_score
        
        return min(score, 1.0)  # Normalize to 0-1
    
    def _calculate_innovation_score(self, profile: Dict[str, Any]) -> float:
        """Calculate innovation score based on patents, projects, and contributions"""
        score = 0.0
        
        # Patent activity
        if profile.get('source') == 'patents':
            score += 0.8  # Patents are a strong innovation signal
        
        # GitHub projects
        if profile.get('source') == 'github':
            repos = profile.get('public_repos', 0)
            if repos > 0:
                score += min(repos / 20, 0.5)  # Cap at 0.5 for repos
        
        # Technical blog posts
        if profile.get('source') in ['medium', 'devto']:
            score += 0.3  # Writing about technical topics shows innovation
        
        # Conference speaking
        if profile.get('source') == 'conference':
            score += 0.4  # Speaking shows thought leadership
        
        return min(score, 1.0)
    
    def _calculate_leadership_score(self, profile: Dict[str, Any]) -> float:
        """Calculate leadership score based on roles and activities"""
        score = 0.0
        
        # Current role level
        title = profile.get('title', '').lower()
        level = self._get_title_level(title)
        score += level / 10  # Normalize to 0-1
        
        # Conference speaking
        if profile.get('source') == 'conference':
            score += 0.3  # Speaking shows leadership
        
        # GitHub followers
        if profile.get('source') == 'github':
            followers = profile.get('followers', 0)
            score += min(followers / 1000, 0.3)  # Cap at 0.3 for followers
        
        # Technical writing
        if profile.get('source') in ['medium', 'devto']:
            score += 0.2  # Writing shows thought leadership
        
        return min(score, 1.0)
    
    def _calculate_age_score(self, age: Optional[int]) -> float:
        """Calculate age-based score"""
        if not age:
            return 0.5  # Neutral score if age unknown
        
        if self.config.IDEAL_AGE_MIN <= age <= self.config.IDEAL_AGE_MAX:
            return 1.0  # Perfect score for ideal age range
        elif self.config.TARGET_AGE_MIN <= age <= self.config.TARGET_AGE_MAX:
            return 0.7  # Good score for acceptable age range
        elif age < self.config.TARGET_AGE_MIN:
            return 0.3  # Lower score for too young
        else:
            return 0.1  # Very low score for too old
    
    def _calculate_career_progression_score(self, profile: Dict[str, Any]) -> float:
        """Calculate career progression score"""
        career_progression = profile.get('career_progression', [])
        experience_years = profile.get('experience_years', 0)
        
        if not career_progression or experience_years == 0:
            return 0.5  # Neutral score if no data
        
        # Calculate average title level progression
        title_levels = []
        for position in career_progression:
            title = position.get('title', '').lower()
            level = self._get_title_level(title)
            title_levels.append(level)
        
        if len(title_levels) < 2:
            return 0.5  # Need at least 2 positions to assess progression
        
        # Calculate progression rate
        current_level = max(title_levels)
        starting_level = min(title_levels)
        level_increase = current_level - starting_level
        
        # Ideal: 2+ level increase in 3-5 years
        if experience_years >= 3 and level_increase >= 2:
            return 1.0
        elif experience_years >= 2 and level_increase >= 1:
            return 0.8
        elif level_increase > 0:
            return 0.6
        else:
            return 0.3
    
    def _calculate_education_score(self, education: Optional[List[Dict[str, Any]]]) -> float:
        """Calculate education score"""
        if not education:
            return 0.5
        
        max_score = 0.0
        for edu in education:
            school = edu.get('school', '').lower()
            field = edu.get('field', '').lower()
            degree = edu.get('degree', '').lower()
            
            score = 0.0
            
            # Top tier schools
            top_schools = ['stanford', 'harvard', 'mit', 'berkeley', 'princeton', 'yale']
            if any(school_name in school for school_name in top_schools):
                score = max(score, 1.0)
            
            # Good schools
            good_schools = ['columbia', 'upenn', 'cornell', 'dartmouth', 'brown', 'duke']
            if any(school_name in school for school_name in good_schools):
                score = max(score, 0.9)
            
            # Technical degrees
            tech_degrees = ['computer science', 'engineering', 'mathematics', 'physics']
            if any(tech_degree in field for tech_degree in tech_degrees):
                score = max(score, 0.8)
            
            # Business degrees
            business_degrees = ['business', 'economics', 'finance', 'mba']
            if any(bus_degree in field for bus_degree in business_degrees) or 'mba' in degree:
                score = max(score, 0.7)
            
            # Advanced degrees bonus
            if degree in ['phd', 'doctorate', 'ms', 'master']:
                score = min(score + 0.1, 1.0)
            
            max_score = max(max_score, score)
        
        return max_score if max_score > 0 else 0.5  # Default score
    
    def _get_title_level(self, title: str) -> int:
        """Get numeric level for a job title"""
        title_lower = title.lower()
        
        for keyword, level in self.title_levels.items():
            if keyword in title_lower:
                return level
        
        return 2  # Default to associate level
    
    def extract_age_from_profile(self, profile_data: Dict[str, Any]) -> Optional[int]:
        """Extract age from profile data using various methods"""
        # Method 1: Direct age field
        if profile_data.get('age'):
            return profile_data['age']
        
        # Method 2: Extract from education graduation year
        education = profile_data.get('education', '')
        if education:
            graduation_year = self._extract_graduation_year(education)
            if graduation_year:
                current_year = datetime.now().year
                estimated_age = current_year - graduation_year + 22  # Assume graduation at 22
                return max(18, min(100, estimated_age))  # Clamp to reasonable range
        
        # Method 3: Extract from experience years
        experience_years = profile_data.get('experience_years', 0)
        if experience_years:
            estimated_age = 22 + experience_years  # Assume starting career at 22
            return max(18, min(100, estimated_age))
        
        return None
    
    def _extract_graduation_year(self, education: str) -> Optional[int]:
        """Extract graduation year from education string"""
        # Look for 4-digit years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, education)
        
        if years:
            # Return the most recent year (assuming it's graduation year)
            return max(int(year) for year in years)
        
        return None
    
    def analyze_career_progression(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze career progression from position history"""
        if not positions or len(positions) < 2:
            return {'progression_rate': 0, 'promotions': 0, 'growth_trajectory': 'stable'}
        
        # Sort positions by date (assuming they have date fields)
        sorted_positions = sorted(positions, key=lambda x: x.get('start_date', ''))
        
        # Calculate progression metrics
        title_levels = []
        promotions = 0
        
        for i, position in enumerate(sorted_positions):
            title = position.get('title', '').lower()
            level = self._get_title_level(title)
            title_levels.append(level)
            
            if i > 0 and level > title_levels[i-1]:
                promotions += 1
        
        # Calculate progression rate
        if len(title_levels) >= 2:
            total_increase = max(title_levels) - min(title_levels)
            years_span = len(title_levels)  # Rough estimate
            progression_rate = total_increase / max(years_span, 1)
        else:
            progression_rate = 0
        
        # Determine growth trajectory
        if progression_rate >= 1.5:
            trajectory = 'rapid'
        elif progression_rate >= 0.5:
            trajectory = 'steady'
        else:
            trajectory = 'stable'
        
        return {
            'progression_rate': round(progression_rate, 2),
            'promotions': promotions,
            'growth_trajectory': trajectory,
            'title_levels': title_levels
        } 