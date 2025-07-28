#!/usr/bin/env python3
"""
Demo script for Future Founder Finder
Shows the functionality with sample data
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_sample_profiles():
    """Create sample profiles for demonstration"""
    sample_profiles = [
        {
            'name': 'Sarah Chen',
            'title': 'Senior Product Manager',
            'company': 'Google',
            'industry': 'Technology',
            'location': 'San Francisco, CA',
            'age': 28,
            'education': 'Stanford University, Computer Science 2018',
            'experience_years': 6,
            'career_progression': [
                {'title': 'Senior Product Manager', 'company': 'Google', 'duration': '2022-Present'},
                {'title': 'Product Manager', 'company': 'Google', 'duration': '2020-2022'},
                {'title': 'Associate Product Manager', 'company': 'Google', 'duration': '2018-2020'}
            ],
            'skills': ['Product Strategy', 'Data Analysis', 'User Research', 'Agile', 'SQL'],
            'achievements': ['Led team of 15 engineers', 'Increased user engagement by 40%', 'Launched 3 major features'],
            'linkedin_url': 'https://linkedin.com/in/sarah-chen-demo'
        },
        {
            'name': 'Alex Rodriguez',
            'title': 'Engineering Manager',
            'company': 'Meta',
            'industry': 'Technology',
            'location': 'Seattle, WA',
            'age': 30,
            'education': 'MIT, Computer Science 2016',
            'experience_years': 7,
            'career_progression': [
                {'title': 'Engineering Manager', 'company': 'Meta', 'duration': '2021-Present'},
                {'title': 'Senior Software Engineer', 'company': 'Meta', 'duration': '2019-2021'},
                {'title': 'Software Engineer', 'company': 'Meta', 'duration': '2016-2019'}
            ],
            'skills': ['Python', 'JavaScript', 'React', 'System Design', 'Team Leadership'],
            'achievements': ['Managed team of 12 engineers', 'Reduced system latency by 60%', 'Mentored 8 junior developers'],
            'linkedin_url': 'https://linkedin.com/in/alex-rodriguez-demo'
        },
        {
            'name': 'Emily Johnson',
            'title': 'Data Science Lead',
            'company': 'Stripe',
            'industry': 'Fintech',
            'location': 'New York, NY',
            'age': 27,
            'education': 'Harvard University, Statistics 2019',
            'experience_years': 4,
            'career_progression': [
                {'title': 'Data Science Lead', 'company': 'Stripe', 'duration': '2022-Present'},
                {'title': 'Senior Data Scientist', 'company': 'Stripe', 'duration': '2021-2022'},
                {'title': 'Data Scientist', 'company': 'Stripe', 'duration': '2019-2021'}
            ],
            'skills': ['Machine Learning', 'Python', 'SQL', 'Statistics', 'A/B Testing'],
            'achievements': ['Built fraud detection model with 95% accuracy', 'Increased revenue by $2M through ML insights'],
            'linkedin_url': 'https://linkedin.com/in/emily-johnson-demo'
        },
        {
            'name': 'Michael Kim',
            'title': 'Business Development Manager',
            'company': 'Uber',
            'industry': 'Technology',
            'location': 'Los Angeles, CA',
            'age': 29,
            'education': 'UC Berkeley, Business Administration 2017',
            'experience_years': 6,
            'career_progression': [
                {'title': 'Business Development Manager', 'company': 'Uber', 'duration': '2021-Present'},
                {'title': 'Senior Business Development Associate', 'company': 'Uber', 'duration': '2019-2021'},
                {'title': 'Business Development Associate', 'company': 'Uber', 'duration': '2017-2019'}
            ],
            'skills': ['Sales', 'Partnership Development', 'Market Analysis', 'Negotiation', 'Strategy'],
            'achievements': ['Closed $50M partnership deals', 'Expanded to 3 new markets', 'Built partner ecosystem of 200+ companies'],
            'linkedin_url': 'https://linkedin.com/in/michael-kim-demo'
        },
        {
            'name': 'Jessica Wang',
            'title': 'Product Director',
            'company': 'Airbnb',
            'industry': 'E-commerce',
            'location': 'San Francisco, CA',
            'age': 32,
            'education': 'Yale University, Economics 2014',
            'experience_years': 9,
            'career_progression': [
                {'title': 'Product Director', 'company': 'Airbnb', 'duration': '2020-Present'},
                {'title': 'Senior Product Manager', 'company': 'Airbnb', 'duration': '2018-2020'},
                {'title': 'Product Manager', 'company': 'Airbnb', 'duration': '2016-2018'},
                {'title': 'Associate Product Manager', 'company': 'Airbnb', 'duration': '2014-2016'}
            ],
            'skills': ['Product Strategy', 'User Experience', 'Analytics', 'Team Leadership', 'Go-to-Market'],
            'achievements': ['Led product team of 25 people', 'Launched international expansion to 50 countries', 'Increased bookings by 300%'],
            'linkedin_url': 'https://linkedin.com/in/jessica-wang-demo'
        }
    ]
    return sample_profiles

def demo_profile_analysis():
    """Demonstrate profile analysis functionality"""
    print("🔍 Future Founder Profile Analysis Demo")
    print("=" * 50)
    
    try:
        from app.scraper.profile_analyzer import ProfileAnalyzer
        analyzer = ProfileAnalyzer()
        
        sample_profiles = create_sample_profiles()
        
        print(f"Analyzing {len(sample_profiles)} sample profiles...\n")
        
        for i, profile in enumerate(sample_profiles, 1):
            score = analyzer.calculate_future_founder_score(profile)
            
            print(f"Profile {i}: {profile['name']}")
            print(f"  Title: {profile['title']}")
            print(f"  Company: {profile['company']}")
            print(f"  Age: {profile['age']}")
            print(f"  Experience: {profile['experience_years']} years")
            print(f"  Future Founder Score: {score:.3f} ({score*100:.1f}%)")
            
            # Analyze career progression
            progression = analyzer.analyze_career_progression(profile['career_progression'])
            print(f"  Career Progression: {progression['growth_trajectory']} (rate: {progression['progression_rate']})")
            print(f"  Promotions: {progression['promotions']}")
            print()
        
        # Show top candidates
        scored_profiles = [(profile, analyzer.calculate_future_founder_score(profile)) for profile in sample_profiles]
        scored_profiles.sort(key=lambda x: x[1], reverse=True)
        
        print("🏆 Top Future Founder Candidates:")
        print("-" * 30)
        for i, (profile, score) in enumerate(scored_profiles[:3], 1):
            print(f"{i}. {profile['name']} ({profile['company']}) - {score*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in profile analysis demo: {e}")
        return False

def demo_database_operations():
    """Demonstrate database operations"""
    print("\n🗄️ Database Operations Demo")
    print("=" * 50)
    
    try:
        from app.database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        
        # Clear existing data for demo
        print("Setting up demo database...")
        
        # Add sample profiles
        sample_profiles = create_sample_profiles()
        
        print(f"Adding {len(sample_profiles)} sample profiles to database...")
        for profile in sample_profiles:
            profile_id = db_manager.add_profile(profile)
            print(f"  Added profile {profile_id}: {profile['name']}")
        
        # Get statistics
        stats = db_manager.get_statistics()
        print(f"\nDatabase Statistics:")
        print(f"  Total profiles: {stats['total_profiles']}")
        print(f"  Average score: {stats['average_score']:.3f}")
        print(f"  Top companies: {[c['company'] for c in stats['top_companies'][:3]]}")
        
        # Search demo
        print(f"\nSearch Demo:")
        search_results = db_manager.search_profiles(
            company='Google',
            age_min=25,
            age_max=35,
            limit=5
        )
        print(f"  Found {len(search_results)} profiles at Google")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in database demo: {e}")
        return False

def demo_scoring_criteria():
    """Demonstrate scoring criteria"""
    print("\n📊 Scoring Criteria Demo")
    print("=" * 50)
    
    try:
        from app.scraper.profile_analyzer import ProfileAnalyzer
        analyzer = ProfileAnalyzer()
        
        # Test different scenarios
        scenarios = [
            {
                'name': 'Ideal Candidate',
                'profile': {
                    'age': 28,
                    'title': 'Senior Product Manager',
                    'company': 'Google',
                    'education': 'Stanford University',
                    'career_progression': [
                        {'title': 'Senior Product Manager'},
                        {'title': 'Product Manager'},
                        {'title': 'Associate Product Manager'}
                    ],
                    'experience_years': 5
                }
            },
            {
                'name': 'Too Young',
                'profile': {
                    'age': 22,
                    'title': 'Software Engineer',
                    'company': 'Startup',
                    'education': 'University',
                    'career_progression': [
                        {'title': 'Software Engineer'}
                    ],
                    'experience_years': 1
                }
            },
            {
                'name': 'Too Old',
                'profile': {
                    'age': 40,
                    'title': 'Director',
                    'company': 'Large Corp',
                    'education': 'MBA',
                    'career_progression': [
                        {'title': 'Director'},
                        {'title': 'Manager'},
                        {'title': 'Analyst'}
                    ],
                    'experience_years': 15
                }
            }
        ]
        
        for scenario in scenarios:
            score = analyzer.calculate_future_founder_score(scenario['profile'])
            print(f"{scenario['name']}: {score:.3f} ({score*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in scoring demo: {e}")
        return False

def main():
    """Run all demos"""
    print("🚀 Future Founder Finder - Demo")
    print("=" * 60)
    
    demos = [
        demo_profile_analysis,
        demo_database_operations,
        demo_scoring_criteria
    ]
    
    passed = 0
    total = len(demos)
    
    for demo in demos:
        try:
            if demo():
                passed += 1
        except Exception as e:
            print(f"❌ Demo failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Demo Results: {passed}/{total} demos completed")
    
    if passed == total:
        print("🎉 All demos completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the web app: python run.py")
        print("3. Open http://localhost:5000 in your browser")
    else:
        print("⚠️ Some demos failed. Please check the errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 