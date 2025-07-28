"""
Future Founder Finder - Mapin Flask Blueprint
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from app.database.db_manager import DatabaseManager
from app.scraper.profile_analyzer import ProfileAnalyzer
import json

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@bp.route('/search', methods=['POST'])
def search_profiles():
    """Search for potential future founders"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        company = data.get('company', '')
        industry = data.get('industry', '')
        title = data.get('title', '')
        age_min = data.get('age_min', 25)
        age_max = data.get('age_max', 35)
        
        # Initialize database manager
        db_manager = DatabaseManager()
        
        # Search profiles
        profiles = db_manager.search_profiles(
            company=company,
            industry=industry,
            title=title,
            age_min=age_min,
            age_max=age_max
        )
        
        # Analyze and score profiles
        analyzer = ProfileAnalyzer()
        scored_profiles = []
        
        for profile in profiles:
            score = analyzer.calculate_future_founder_score(profile)
            profile['score'] = score
            scored_profiles.append(profile)
        
        # Sort by score (highest first)
        scored_profiles.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'success': True,
            'profiles': scored_profiles,
            'count': len(scored_profiles)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in search_profiles: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/scrape', methods=['POST'])
def start_scraping():
    """Start scraping for new profiles"""
    try:
        data = request.get_json()
        
        # Extract scraping parameters
        companies = data.get('companies', [])
        industries = data.get('industries', [])
        max_profiles = data.get('max_profiles', 100)
        
        # This would typically be run as a background task
        # For now, we'll return a mock response
        return jsonify({
            'success': True,
            'message': f'Scraping started for {len(companies)} companies',
            'task_id': 'mock_task_123'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in start_scraping: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/profiles')
def list_profiles():
    """List all stored profiles"""
    try:
        db_manager = DatabaseManager()
        profiles = db_manager.get_all_profiles()
        
        return render_template('results.html', profiles=profiles)
        
    except Exception as e:
        current_app.logger.error(f"Error in list_profiles: {str(e)}")
        return render_template('error.html', error=str(e))

@bp.route('/profile/<int:profile_id>')
def view_profile(profile_id):
    """View detailed profile information"""
    try:
        db_manager = DatabaseManager()
        profile = db_manager.get_profile_by_id(profile_id)
        
        if not profile:
            return render_template('error.html', error='Profile not found'), 404
        
        return render_template('profile.html', profile=profile)
        
    except Exception as e:
        current_app.logger.error(f"Error in view_profile: {str(e)}")
        return render_template('error.html', error=str(e))

@bp.route('/export', methods=['POST'])
def export_profiles():
    """Export profiles to various formats"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'csv')
        profile_ids = data.get('profile_ids', [])
        
        db_manager = DatabaseManager()
        
        if profile_ids:
            profiles = db_manager.get_profiles_by_ids(profile_ids)
        else:
            profiles = db_manager.get_all_profiles()
        
        # Export logic would go here
        # For now, return a mock response
        return jsonify({
            'success': True,
            'message': f'Exported {len(profiles)} profiles to {format_type}',
            'download_url': f'/downloads/export_{format_type}_{len(profiles)}.csv'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in export_profiles: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/stats')
def get_stats():
    """Get application statistics"""
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_statistics()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in get_stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 