# NFL Stats 2024

A comprehensive NFL statistics database and visualization project.

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

- Complete NFL player statistics database
- REST API for data access
- Interactive web interface using Streamlit
- Stored procedures for complex queries
- Team and player statistics visualization
- Position-based player rankings
- Team roster management

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp config/.env.example config/.env
# Edit config/.env with your database credentials
```

4. Initialize the database:
```bash
python src/database.py
```

5. Run the application:
```bash
# For Flask API
python src/app.py

# For Streamlit interface
streamlit run src/streamlit_app.py
```

## API Endpoints

- `/teams` - List all teams
- `/players/<position>` - Get players by position
- `/players/team/<team>` - Get players by team
- `/players/search` - Search players
- `/stats/position/<position>` - Get position-specific stats

## Database Features

- Multiple related tables for different positions
- Stored procedures for complex queries
- Data validation and error handling
- Efficient data loading and updates
- Team and player statistics tracking

## Deployment

The application is deployed on Heroku with a PostgreSQL database.

## Contributing

Feel free to submit issues and enhancement requests! 