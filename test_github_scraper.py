#!/usr/bin/env python3

import asyncio
import os
from dotenv import load_dotenv
from app.scraper.multi_source_scraper import MultiSourceScraper
from loguru import logger

async def main():
    """Test the GitHub profile scraper"""
    # Load environment variables
    load_dotenv()
    
    # Check if GitHub token is configured
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        logger.error("No GitHub token found. Set GITHUB_TOKEN in your .env file.")
        return
    else:
        logger.info(f"GitHub token found: {github_token[:4]}...{github_token[-4:]}")
    
    # Initialize scraper
    scraper = MultiSourceScraper()
    
    # Debug: Check if token is set in scraper
    logger.info(f"Scraper GitHub token: {scraper.github_token[:4]}...{scraper.github_token[-4:] if scraper.github_token else 'None'}")
    
    try:
        # Example search for young technical founders
        profiles = await scraper.search_professional_profiles(
            name="",  # Leave empty to be more general
            company="startup OR founder",  # Looking for startup people
            role="engineer OR developer"  # Technical roles
        )
        
        # Print results
        print("\nFound Profiles:")
        print("==============")
        
        for profile in profiles:
            print(f"\nName: {profile.get('name', 'N/A')}")
            print(f"Company: {profile.get('company', 'N/A')}")
            print(f"Location: {profile.get('location', 'N/A')}")
            print(f"Bio: {profile.get('bio', 'N/A')}")
            print(f"GitHub URL: {profile.get('github_url', 'N/A')}")
            print(f"Account Age: {profile.get('account_age', 'N/A')}")
            print(f"Estimated Age: {profile.get('estimated_age', 'N/A')}")
            
            # Print scores
            print("\nScores:")
            print(f"Technical Score: {profile.get('technical_score', 0):.2f}/10")
            print(f"Innovation Score: {profile.get('innovation_score', 0):.2f}/10")
            print(f"Collaboration Score: {profile.get('collaboration_score', 0):.2f}/10")
            print(f"Age Score: {profile.get('age_score', 0):.2f}/10")
            print(f"Founder Potential: {profile.get('founder_potential', 0):.2f}/10")
            
            # Print contribution frequency
            print(f"\nContribution Frequency: {profile.get('contribution_frequency', 'N/A')}")
            
            # Print early achievements
            achievements = profile.get('early_achievements', [])
            if achievements:
                print("\nEarly Achievements:")
                for achievement in achievements:
                    print(f"- {achievement['name']}: {achievement['stars']} stars "
                          f"(created {achievement['created_after_years']} years after joining)")
            
            # Print top repositories
            top_repos = profile.get('top_repos', [])
            if top_repos:
                print("\nTop Repositories:")
                for repo in top_repos:
                    print(f"- {repo['name']}: {repo['stars']} stars, {repo['forks']} forks "
                          f"({repo['language'] or 'Unknown language'})")
            
            # Print languages
            languages = profile.get('languages', {})
            if languages:
                print("\nLanguages:")
                for lang, count in languages.items():
                    print(f"- {lang}: {count} repos")
            
            print("\n" + "="*50)
    
    except Exception as e:
        logger.error(f"Error running scraper: {e}")
    
    finally:
        # Clean up
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main()) 