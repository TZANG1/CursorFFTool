"""
Script to scrape social media for potential founder signals
"""

import asyncio
from app.scraper.social_media_scraper import SocialMediaScraper
from app.scraper.profile_analyzer import ProfileAnalyzer
from app.database.db_manager import DatabaseManager
from config import Config
from loguru import logger

async def main():
    """Main scraping function"""
    config = Config()
    scraper = SocialMediaScraper()
    analyzer = ProfileAnalyzer()
    db = DatabaseManager()
    
    # Initialize scraper
    if not await scraper.init():
        logger.error("Failed to initialize scraper")
        return
    
    try:
        # Search for each role and industry combination
        for role in config.SEARCH_CRITERIA['roles']:
            for industry in config.SEARCH_CRITERIA['industries']:
                for exp_level in config.SEARCH_CRITERIA['experience_levels']:
                    logger.info(f"Searching for {exp_level} {role} in {industry}")
                    
                    # Search for posts
                    posts = await scraper.search_career_posts(
                        role=role,
                        industry=industry,
                        experience_level=exp_level,
                        max_results=20  # Limit per combination to avoid rate limits
                    )
                    
                    # Process and store profiles
                    for post in posts:
                        # Extract profile data from post
                        profile_data = {
                            'name': post.get('author_name', 'Unknown'),
                            'title': post.get('current_role', ''),
                            'company': post.get('company', ''),
                            'location': post.get('location', ''),
                            'experience_years': post.get('experience_years', 0),
                            'education': post.get('education', ''),
                            'skills': post.get('skills', []),
                            'achievements': post.get('achievements', []),
                            'source_url': post.get('url', ''),
                            'source_platform': post.get('source', ''),
                            'post_content': post.get('content', ''),
                            'post_date': post.get('date', '')
                        }
                        
                        # Calculate founder potential score
                        score = analyzer.calculate_future_founder_score(profile_data)
                        profile_data['score'] = score
                        
                        # Store in database
                        db.add_profile(profile_data)
                        
                        logger.info(f"Added profile for {profile_data['name']} with score {score}")
                    
                    # Delay between searches
                    await asyncio.sleep(config.SEARCH_DELAY)
    
    finally:
        # Cleanup
        await scraper.close()

if __name__ == '__main__':
    asyncio.run(main()) 