"""
Add sample test profiles to the database
"""

from app.database.db_manager import DatabaseManager
from app.scraper.profile_analyzer import ProfileAnalyzer
from datetime import datetime, timedelta

def generate_dates(start_year, num_positions):
    dates = []
    current_date = datetime(start_year, 1, 1)
    for _ in range(num_positions):
        dates.append(current_date.strftime('%Y-%m'))
        current_date += timedelta(days=365 * 2)  # Roughly 2 years between positions
    return dates

def add_sample_profiles():
    db = DatabaseManager()
    analyzer = ProfileAnalyzer()
    
    sample_profiles = [
        {
            'name': '[TEST] John Smith',
            'title': 'Senior Software Engineer',
            'company': 'Google',
            'location': 'San Francisco, CA',
            'linkedin_url': 'https://linkedin.com/in/test-john-smith',
            'source': 'sample_data',
            'experience': [
                {
                    'title': 'Software Engineer',
                    'company': 'Microsoft',
                    'start_date': '2019-01',
                    'end_date': '2020-12',
                    'description': 'Full-stack development'
                },
                {
                    'title': 'Senior Software Engineer',
                    'company': 'Google',
                    'start_date': '2021-01',
                    'end_date': 'present',
                    'description': 'Leading backend team'
                }
            ],
            'education': [
                {
                    'school': 'Stanford University',
                    'degree': 'BS',
                    'field': 'Computer Science',
                    'start_date': '2015-09',
                    'end_date': '2019-06'
                }
            ],
            'skills': ['Python', 'JavaScript', 'System Design']
        },
        {
            'name': '[TEST] Emily Zhang',
            'title': 'Founder & CEO',
            'company': 'TechStartup Inc',
            'location': 'New York, NY',
            'linkedin_url': 'https://linkedin.com/in/test-emily-zhang',
            'source': 'sample_data',
            'experience': [
                {
                    'title': 'Product Manager',
                    'company': 'Amazon',
                    'start_date': '2018-06',
                    'end_date': '2021-12',
                    'description': 'Led product development'
                },
                {
                    'title': 'Founder & CEO',
                    'company': 'TechStartup Inc',
                    'start_date': '2022-01',
                    'end_date': 'present',
                    'description': 'Founded AI startup'
                }
            ],
            'education': [
                {
                    'school': 'MIT',
                    'degree': 'MS',
                    'field': 'Computer Science',
                    'start_date': '2016-09',
                    'end_date': '2018-05'
                }
            ],
            'skills': ['Leadership', 'AI/ML', 'Product Strategy']
        },
        {
            'name': '[TEST] David Kim',
            'title': 'Serial Entrepreneur',
            'company': 'Self-Employed',
            'location': 'Austin, TX',
            'linkedin_url': 'https://linkedin.com/in/test-david-kim',
            'source': 'sample_data',
            'experience': [
                {
                    'title': 'Software Engineer',
                    'company': 'Facebook',
                    'start_date': '2017-01',
                    'end_date': '2019-12',
                    'description': 'Mobile development'
                },
                {
                    'title': 'Co-Founder',
                    'company': 'Tech Venture 1',
                    'start_date': '2020-01',
                    'end_date': '2021-12',
                    'description': 'Founded and sold startup'
                },
                {
                    'title': 'Founder',
                    'company': 'Tech Venture 2',
                    'start_date': '2022-01',
                    'end_date': 'present',
                    'description': 'Building new startup'
                }
            ],
            'education': [
                {
                    'school': 'UC Berkeley',
                    'degree': 'BS',
                    'field': 'Computer Science',
                    'start_date': '2013-09',
                    'end_date': '2017-05'
                }
            ],
            'skills': ['Entrepreneurship', 'Mobile Development', 'Fundraising']
        }
    ]
    
    # Calculate scores and store profiles
    for profile in sample_profiles:
        # Add test data indicators
        profile['is_test_data'] = True
        profile['name'] = f"[TEST] {profile['name']}" if not profile['name'].startswith('[TEST]') else profile['name']
        profile['company'] = f"[TEST] {profile['company']}" if not profile['company'].startswith('[TEST]') else profile['company']
        
        # Calculate scores
        profile['founder_score'] = analyzer.calculate_future_founder_score(profile)
        profile['technical_score'] = analyzer._calculate_technical_expertise_score(profile)
        profile['innovation_score'] = analyzer._calculate_innovation_score(profile)
        profile['leadership_score'] = analyzer._calculate_leadership_score(profile)
        
        # Store in database
        db.store_profiles([profile])

if __name__ == "__main__":
    add_sample_profiles() 