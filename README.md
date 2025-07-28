# Future Founder Finder

A web scraper and analysis tool designed to identify professionals who fit the profile of ideal "Future Founders" - young professionals (25-30, max 35) with evidence of rapid career progression.

## Features

- **Intelligent Web Scraping**: Scrapes LinkedIn, company websites, and professional platforms
- **Profile Analysis**: Analyzes career progression, age indicators, and professional achievements
- **Modern Web UI**: Beautiful, responsive interface for viewing and managing results
- **Data Storage**: SQLite database for storing and querying candidate profiles
- **Export Capabilities**: Export results to CSV, JSON, or PDF formats

## Project Structure

```
future-founder-finder/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask application
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── linkedin_scraper.py
│   │   ├── company_scraper.py
│   │   └── profile_analyzer.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── profile.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_manager.py
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── templates/
│   ├── index.html
│   ├── results.html
│   └── profile.html
├── data/
│   └── profiles.db
├── requirements.txt
├── config.py
└── run.py
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd future-founder-finder
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python -c "from app.database.db_manager import init_db; init_db()"
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

## Usage

1. Open your browser and navigate to `http://localhost:5000`
2. Use the search interface to find potential future founders
3. View detailed profiles and analysis results
4. Export data as needed

## Configuration

Edit `config.py` to customize:
- Target companies and industries
- Age range preferences
- Career progression criteria
- Scraping parameters

## Legal Notice

This tool is for educational and research purposes. Please respect:
- Website terms of service
- Rate limiting guidelines
- Privacy policies
- Robots.txt files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details 