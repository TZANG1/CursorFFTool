from app.scraper.linkedin_scraper import LinkedInScraper
from app.scraper.profile_sources import AngelListSource, CrunchbaseSource, GithubSource
from loguru import logger

def test_scrapers():
    try:
        # Initialize scrapers
        linkedin = LinkedInScraper()
        angellist = AngelListSource(linkedin.driver)  # Reuse the same driver
        crunchbase = CrunchbaseSource(linkedin.driver)
        github = GithubSource(linkedin.driver)
        
        search_params = {
            'company': "Google",
            'title': "Software Engineer",
            'location': "San Francisco Bay Area",
            'max_results': 5
        }
        
        # Search using each source
        all_profiles = []
        
        # LinkedIn search
        logger.info("Searching LinkedIn...")
        linkedin_profiles = linkedin.search_profiles(**search_params)
        all_profiles.extend(linkedin_profiles)
        
        # AngelList search
        logger.info("Searching AngelList...")
        angellist_profiles = angellist.search_profiles(**search_params)
        all_profiles.extend(angellist_profiles)
        
        # Crunchbase search
        logger.info("Searching Crunchbase...")
        crunchbase_profiles = crunchbase.search_profiles(**search_params)
        all_profiles.extend(crunchbase_profiles)
        
        # GitHub search
        logger.info("Searching GitHub...")
        github_profiles = github.search_profiles(**search_params)
        all_profiles.extend(github_profiles)
        
        # Print results
        logger.info(f"Found {len(all_profiles)} total profiles")
        for profile in all_profiles:
            logger.info(f"Profile from {profile.get('source', 'unknown')}: {profile}")
            
    except Exception as e:
        logger.error(f"Error running scrapers: {e}")
    finally:
        # Clean up
        linkedin.close()

if __name__ == "__main__":
    test_scrapers() 