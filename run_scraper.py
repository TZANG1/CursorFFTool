#!/usr/bin/env python3

import asyncio
from app.scraper.multi_source_scraper import MultiSourceScraper
import json
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def main():
    """Run the GitHub profile scraper"""
    scraper = MultiSourceScraper()
    try:
        # Example search - you can modify these parameters
        profiles = await scraper.search_professional_profiles(
            name="",  # Leave empty to be more general
            company="startup",  # Looking for startup employees
            role="founder OR cto OR engineer"  # Common founder backgrounds
        )
        
        # Print results in a readable format
        print("\nFound Profiles:")
        print("==============")
        for profile in profiles:
            print(f"\nName: {profile.get('name', 'N/A')}")
            print(f"Company: {profile.get('company', 'N/A')}")
            print(f"Location: {profile.get('location', 'N/A')}")
            print(f"Bio: {profile.get('bio', 'N/A')}")
            print(f"GitHub URL: {profile.get('github_url', 'N/A')}")
            print(f"Account Age: {profile.get('account_age', 'N/A')}")
            print(f"Public Repos: {profile.get('public_repos', 0)}")
            print(f"Followers: {profile.get('followers', 0)}")
            
            # Print scores
            print("\nScores:")
            print(f"Technical Score: {profile.get('technical_score', 0):.2f}/10")
            print(f"Innovation Score: {profile.get('innovation_score', 0):.2f}/10")
            print(f"Collaboration Score: {profile.get('collaboration_score', 0):.2f}/10")
            print(f"Age Score: {profile.get('age_score', 0):.2f}/10")
            print(f"Overall Founder Potential: {profile.get('founder_potential', 0):.2f}/10")
            
            # Print languages
            print("\nLanguages:")
            languages = profile.get('languages', {})
            if languages:
                for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    print(f"- {lang}: {count} repos")
            else:
                print("No language data available")
            
            print("-" * 80)
        
        print(f"\nTotal profiles found: {len(profiles)}")
        
    except Exception as e:
        logger.error(f"Error running scraper: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main()) 