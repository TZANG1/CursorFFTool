"""
Database Manager for Future Founder Finder
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import os
from config import Config
from loguru import logger
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self):
        """Initialize database manager"""
        self.config = Config()
        self._setup_database()
    
    @contextmanager
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.config.DATABASE_PATH)
        try:
            yield conn
        finally:
            conn.close()
    
    @contextmanager
    def get_cursor(self):
        """Get a database cursor"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
    
    def _setup_database(self):
        """Setup database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Create profiles table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        title TEXT,
                        company TEXT,
                        location TEXT,
                        linkedin_url TEXT UNIQUE,
                        github_url TEXT,
                        twitter_url TEXT,
                        medium_url TEXT,
                        devto_url TEXT,
                        conference_url TEXT,
                        patent_url TEXT,
                        research_url TEXT,
                        source TEXT,
                        is_test_data BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create experience table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS experience (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_id INTEGER,
                        title TEXT,
                        company TEXT,
                        location TEXT,
                        start_date TEXT,
                        end_date TEXT,
                        description TEXT,
                        FOREIGN KEY (profile_id) REFERENCES profiles (id)
                    )
                """)
                
                # Create education table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS education (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_id INTEGER,
                        school TEXT,
                        degree TEXT,
                        field TEXT,
                        start_date TEXT,
                        end_date TEXT,
                        FOREIGN KEY (profile_id) REFERENCES profiles (id)
                    )
                """)
                
                # Create skills table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS skills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_id INTEGER,
                        name TEXT,
                        category TEXT,
                        FOREIGN KEY (profile_id) REFERENCES profiles (id)
                    )
                """)
                
                conn.commit()
                logger.info("Database setup complete")
                
        except Exception as e:
            logger.error(f"Error setting up database: {e}")
            raise
    
    def store_profiles(self, profiles: List[Dict[str, Any]]):
        """Store multiple profiles in the database"""
        try:
            with self.get_cursor() as cursor:
                for profile in profiles:
                    self._store_single_profile(cursor, profile)
        except Exception as e:
            logger.error(f"Error storing profiles: {e}")
            # The original code had self.conn.rollback(), but self.conn is not defined
            # This line is removed as per the new_code, as the context manager handles commit/rollback
    
    def _store_single_profile(self, cursor, profile: Dict[str, Any]):
        """Store a single profile in the database"""
        try:
            # Check if profile already exists
            cursor.execute("""
                SELECT id FROM profiles 
                WHERE (linkedin_url = ? AND linkedin_url IS NOT NULL)
                OR (github_url = ? AND github_url IS NOT NULL)
                OR (twitter_url = ? AND twitter_url IS NOT NULL)
                OR (medium_url = ? AND medium_url IS NOT NULL)
                OR (devto_url = ? AND devto_url IS NOT NULL)
            """, (
                profile.get('linkedin_url'),
                profile.get('github_url'),
                profile.get('twitter_url'),
                profile.get('medium_url'),
                profile.get('devto_url')
            ))
            
            existing_id = cursor.fetchone()
            
            if existing_id:
                # Update existing profile
                self._update_profile(cursor, existing_id[0], profile)
            else:
                # Insert new profile
                self._insert_profile(cursor, profile)
                
        except Exception as e:
            logger.error(f"Error storing profile: {e}")
            raise
    
    def _insert_profile(self, cursor, profile: Dict[str, Any]):
        """Insert a new profile"""
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT INTO profiles (
                name, title, company, location,
                linkedin_url, github_url, twitter_url, medium_url, devto_url,
                source, founder_score, technical_score, innovation_score,
                leadership_score, career_score, education_score,
                raw_data, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.get('name'),
            profile.get('title'),
            profile.get('company'),
            profile.get('location'),
            profile.get('linkedin_url'),
            profile.get('github_url'),
            profile.get('twitter_url'),
            profile.get('medium_url'),
            profile.get('devto_url'),
            profile.get('source'),
            profile.get('founder_score'),
            profile.get('technical_score'),
            profile.get('innovation_score'),
            profile.get('leadership_score'),
            profile.get('career_score'),
            profile.get('education_score'),
            str(profile),  # Store raw data as string
            now,
            now
        ))
        
        profile_id = cursor.lastrowid
        
        # Store related data
        self._store_experience(cursor, profile_id, profile.get('experience', []))
        self._store_education(cursor, profile_id, profile.get('education', []))
        self._store_skills(cursor, profile_id, profile.get('skills', []))
    
    def _update_profile(self, cursor, profile_id: int, profile: Dict[str, Any]):
        """Update an existing profile"""
        now = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE profiles SET
                name = ?,
                title = ?,
                company = ?,
                location = ?,
                linkedin_url = ?,
                github_url = ?,
                twitter_url = ?,
                medium_url = ?,
                devto_url = ?,
                source = ?,
                founder_score = ?,
                technical_score = ?,
                innovation_score = ?,
                leadership_score = ?,
                career_score = ?,
                education_score = ?,
                raw_data = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            profile.get('name'),
            profile.get('title'),
            profile.get('company'),
            profile.get('location'),
            profile.get('linkedin_url'),
            profile.get('github_url'),
            profile.get('twitter_url'),
            profile.get('medium_url'),
            profile.get('devto_url'),
            profile.get('source'),
            profile.get('founder_score'),
            profile.get('technical_score'),
            profile.get('innovation_score'),
            profile.get('leadership_score'),
            profile.get('career_score'),
            profile.get('education_score'),
            str(profile),
            now,
            profile_id
        ))
        
        # Update related data
        self._store_experience(cursor, profile_id, profile.get('experience', []))
        self._store_education(cursor, profile_id, profile.get('education', []))
        self._store_skills(cursor, profile_id, profile.get('skills', []))
    
    def _store_experience(self, cursor, profile_id: int, experience: List[Dict[str, Any]]):
        """Store experience entries for a profile"""
        # Clear existing experience
        cursor.execute("DELETE FROM experience WHERE profile_id = ?", (profile_id,))
        
        # Insert new experience
        for exp in experience:
            cursor.execute("""
                INSERT INTO experience (
                    profile_id, title, company,
                    start_date, end_date, description
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                exp.get('title'),
                exp.get('company'),
                exp.get('start_date'),
                exp.get('end_date'),
                exp.get('description')
            ))
    
    def _store_education(self, cursor, profile_id: int, education: List[Dict[str, Any]]):
        """Store education entries for a profile"""
        # Clear existing education
        cursor.execute("DELETE FROM education WHERE profile_id = ?", (profile_id,))
        
        # Insert new education
        for edu in education:
            cursor.execute("""
                INSERT INTO education (
                    profile_id, school, degree,
                    field, start_date, end_date
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                edu.get('school'),
                edu.get('degree'),
                edu.get('field'),
                edu.get('start_date'),
                edu.get('end_date')
            ))
    
    def _store_skills(self, cursor, profile_id: int, skills: List[Dict[str, Any]]):
        """Store skills for a profile"""
        # Clear existing skills
        cursor.execute("DELETE FROM skills WHERE profile_id = ?", (profile_id,))
        
        # Insert new skills
        for skill in skills:
            cursor.execute("""
                INSERT INTO skills (
                    profile_id, name, category
                ) VALUES (?, ?, ?)
            """, (
                profile_id,
                skill.get('name'),
                skill.get('category')
            ))
    
    def get_profiles(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get profiles from database"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM profiles
                    ORDER BY founder_score DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                columns = [description[0] for description in cursor.description]
                profiles = []
                
                for row in cursor.fetchall():
                    profile = dict(zip(columns, row))
                    
                    # Get related data
                    profile['experience'] = self._get_experience(cursor, profile['id'])
                    profile['education'] = self._get_education(cursor, profile['id'])
                    profile['skills'] = self._get_skills(cursor, profile['id'])
                    
                    profiles.append(profile)
                
                return profiles
                
        except Exception as e:
            logger.error(f"Error getting profiles: {e}")
            return []
    
    def get_total_profiles(self) -> int:
        """Get total number of profiles in database"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM profiles")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting total profiles: {e}")
            return 0
    
    def _get_experience(self, cursor, profile_id: int) -> List[Dict[str, Any]]:
        """Get experience entries for a profile"""
        cursor.execute("""
            SELECT * FROM experience
            WHERE profile_id = ?
            ORDER BY start_date DESC
        """, (profile_id,))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _get_education(self, cursor, profile_id: int) -> List[Dict[str, Any]]:
        """Get education entries for a profile"""
        cursor.execute("""
            SELECT * FROM education
            WHERE profile_id = ?
            ORDER BY start_date DESC
        """, (profile_id,))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _get_skills(self, cursor, profile_id: int) -> List[Dict[str, Any]]:
        """Get skills for a profile"""
        cursor.execute("""
            SELECT * FROM skills
            WHERE profile_id = ?
        """, (profile_id,))
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        # The original code had self.conn.close(), but self.conn is not defined
        # This line is removed as per the new_code, as the context manager handles commit/rollback
        logger.info("Database connection closed") 