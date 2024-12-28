# NFL Stats Database

This project provides a PostgreSQL database and API for NFL player statistics.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with:
```
DATABASE_URL=your_postgres_database_url
```

3. Initialize the database and load data:
```bash
python database.py
```

4. Run the application:
```bash
python app.py
```

## API Endpoints

- `GET /`: Welcome message
- `GET /players/<position>`: Get all players by position (QB, RB, WR, etc.)
- `GET /players/team/<team>`: Get all players by team

## Heroku Deployment

1. Create a new Heroku app
2. Add Heroku Postgres addon
3. Deploy using GitHub integration or Heroku CLI
4. Set environment variables in Heroku dashboard

## Database Schema

The database contains a single `players` table with the following columns:
- id (SERIAL PRIMARY KEY)
- position (VARCHAR)
- player_name (VARCHAR)
- team (VARCHAR)
- season_data (JSONB) 