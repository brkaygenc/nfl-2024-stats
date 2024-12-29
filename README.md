# NFL Stats 2024

A comprehensive NFL statistics database and visualization project that provides player statistics across different positions with both API and web interface access.

## Live Demo

- Web Interface: [https://nfl-website-db-8d1f1be10618.herokuapp.com/](https://nfl-website-db-8d1f1be10618.herokuapp.com/)
- API Endpoint: [https://nfl-website-db-8d1f1be10618.herokuapp.com/api](https://nfl-website-db-8d1f1be10618.herokuapp.com/api)

## Project Structure

```
nfl-stats-2024/
├── src/                    # Source code
│   ├── app.py             # Flask API application
│   ├── database.py        # Database operations and models
│   ├── streamlit_app.py   # Streamlit web interface
│   └── create_procedures.py# Database stored procedures
│
├── data/                   # Data files
│   ├── teams.json         # Team information
│   ├── QB_season.json     # Quarterback statistics
│   ├── RB_season.json     # Running back statistics
│   ├── WR_season.json     # Wide receiver statistics
│   ├── TE_season.json     # Tight end statistics
│   ├── K_season.json      # Kicker statistics
│   ├── DB_season.json     # Defensive back statistics
│   ├── DL_season.json     # Defensive line statistics
│   └── LB_season.json     # Linebacker statistics
│
├── config/                 # Configuration files
│   ├── .env               # Environment variables
│   └── setup.sh           # Setup script for Heroku
│
├── scripts/               # Utility scripts
│   └── check_db.py       # Database connection checker
│
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python runtime specification
├── Procfile             # Heroku process file
├── Procfile.streamlit   # Streamlit process file
└── README.md            # Project documentation
```

## Features

- Complete NFL player statistics database for the 2024 season
- REST API for programmatic data access
- Interactive web interface built with Streamlit featuring:
  - Position-based player statistics
  - Team roster views
  - Custom SQL query interface
  - Data visualization and analytics
- Stored procedures for complex database operations
- Support for multiple player positions (QB, RB, WR, TE, K, DB, DL, LB)
- Comprehensive team statistics

## Web Interface

The Streamlit web interface offers two main modes:

1. **Stats View**
   - Filter players by position groups (Offense, Defense, Special Teams)
   - View detailed statistics for each position
   - See top players rankings
   - Access summary statistics

2. **SQL Query Mode**
   - Write and execute custom SQL queries
   - View query results in tabular format
   - Access example queries
   - See available tables and their structure

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/brkaygenc/nfl-2024-stats.git
cd nfl-2024-stats
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database and configure environment variables:
```bash
# Create a .env file in the config directory with:
DATABASE_URL=postgresql://username:password@localhost/nfl_stats
```

5. Initialize the database:
```bash
python src/database.py
```

6. Create stored procedures:
```bash
python src/create_procedures.py
```

7. Run the applications:
```bash
# For Flask API (in one terminal)
python src/app.py

# For Streamlit interface (in another terminal)
streamlit run src/streamlit_app.py
```

## API Endpoints

- `GET /api/teams` - List all teams
- `GET /api/players/<position>` - Get players by position (QB, RB, WR, TE, K, DB, DL, LB)
- `GET /api/players/team/<team>` - Get all players for a specific team
- `GET /api/stats/<position>` - Get detailed statistics for a position
- `GET /api/team/points/<team>` - Get total points for a team

## Database Features

- Optimized PostgreSQL database schema
- Stored procedures for complex queries:
  - `get_team_player_stats(team_code)` - Get all players and their stats for a team
  - `calculate_team_points(team_code)` - Calculate total points for a team
  - `get_top_position_players(position, limit)` - Get top players for a position
- Efficient data loading and updates
- SSL-secured database connections

## Deployment

The application is deployed on Heroku with:
- PostgreSQL database for data storage
- Automatic SSL database connections
- Separate processes for API and Streamlit interface
- Environment variable configuration

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests. 