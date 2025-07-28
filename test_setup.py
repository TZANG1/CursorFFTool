#!/usr/bin/env python3
"""
Test script for Future Founder Finder setup
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError:
        print("❌ requests not found - run: pip install requests")
        return False
    
    try:
        import beautifulsoup4
        print("✅ beautifulsoup4 imported successfully")
    except ImportError:
        print("❌ beautifulsoup4 not found - run: pip install beautifulsoup4")
        return False
    
    try:
        import flask
        print("✅ flask imported successfully")
    except ImportError:
        print("❌ flask not found - run: pip install flask")
        return False
    
    try:
        import pandas
        print("✅ pandas imported successfully")
    except ImportError:
        print("❌ pandas not found - run: pip install pandas")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import Config
        config = Config()
        print("✅ Configuration loaded successfully")
        print(f"   - Target age range: {config.TARGET_AGE_MIN}-{config.TARGET_AGE_MAX}")
        print(f"   - Database path: {config.DATABASE_PATH}")
        print(f"   - Target companies: {len(config.TARGET_COMPANIES)} companies")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database():
    """Test database initialization"""
    print("\n🗄️ Testing database...")
    
    try:
        from app.database.db_manager import DatabaseManager
        db_manager = DatabaseManager()
        print("✅ Database manager initialized successfully")
        
        # Test basic operations
        stats = db_manager.get_statistics()
        print(f"   - Current profiles: {stats['total_profiles']}")
        print(f"   - Average score: {stats['average_score']}")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_analyzer():
    """Test profile analyzer"""
    print("\n📊 Testing profile analyzer...")
    
    try:
        from app.scraper.profile_analyzer import ProfileAnalyzer
        analyzer = ProfileAnalyzer()
        print("✅ Profile analyzer initialized successfully")
        
        # Test with sample profile
        sample_profile = {
            'name': 'John Doe',
            'title': 'Senior Product Manager',
            'company': 'Google',
            'age': 28,
            'education': 'Stanford University 2018',
            'career_progression': [
                {'title': 'Product Manager', 'company': 'Google'},
                {'title': 'Associate Product Manager', 'company': 'Google'}
            ],
            'experience_years': 5
        }
        
        score = analyzer.calculate_future_founder_score(sample_profile)
        print(f"   - Sample profile score: {score:.3f}")
        return True
    except Exception as e:
        print(f"❌ Profile analyzer error: {e}")
        return False

def test_directory_structure():
    """Test if required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = ['data', 'logs', 'templates']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
            print(f"❌ Missing directory: {dir_name}")
        else:
            print(f"✅ Directory exists: {dir_name}")
    
    if missing_dirs:
        print(f"\nCreating missing directories: {missing_dirs}")
        for dir_name in missing_dirs:
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
    
    return True

def test_flask_app():
    """Test Flask app creation"""
    print("\n🌐 Testing Flask app...")
    
    try:
        from app import create_app
        app = create_app()
        print("✅ Flask app created successfully")
        
        with app.test_client() as client:
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Home route working")
            else:
                print(f"❌ Home route returned status {response.status_code}")
        
        return True
    except Exception as e:
        print(f"❌ Flask app error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Future Founder Finder - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_analyzer,
        test_directory_structure,
        test_flask_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo run the application:")
        print("1. python run.py")
        print("2. Open http://localhost:5000 in your browser")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\nTo install missing dependencies:")
        print("pip install -r requirements.txt")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 