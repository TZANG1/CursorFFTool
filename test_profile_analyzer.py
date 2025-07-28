from app.scraper.profile_analyzer import ProfileAnalyzer
from config import Config

def main():
    # Initialize the analyzer
    analyzer = ProfileAnalyzer()
    
    # Test profile data
    test_profile = {
        'age': 28,
        'title': 'Senior Software Engineer',
        'company': 'Google',
        'education': 'Stanford University - Computer Science',
        'career_progression': [
            {'title': 'Software Engineer', 'start_date': '2018-01'},
            {'title': 'Senior Software Engineer', 'start_date': '2020-01'}
        ]
    }
    
    # Calculate score
    score = analyzer.calculate_future_founder_score(test_profile)
    print(f"Future Founder Score: {score}")

if __name__ == "__main__":
    main() 