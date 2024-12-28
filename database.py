import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL is None:
        raise ValueError("No DATABASE_URL environment variable set")
    
    # Add SSL mode for Heroku
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    return conn

def drop_all_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Drop the players table if it exists
    cur.execute("""
        DROP TABLE IF EXISTS players CASCADE;
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("All tables dropped successfully")

def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS players (
            id SERIAL PRIMARY KEY,
            position VARCHAR(5),
            player_name VARCHAR(100),
            team VARCHAR(50),
            season_data JSONB
        )
        """,
    )
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    for command in commands:
        cur.execute(command)
    
    cur.close()
    conn.commit()
    conn.close()

def load_json_data(position, filename):
    conn = get_db_connection()
    cur = conn.cursor()
    
    with open(filename, 'r') as file:
        data = json.load(file)
        for player_data in data:
            cur.execute(
                """
                INSERT INTO players (position, player_name, team, season_data)
                VALUES (%s, %s, %s, %s)
                """,
                (position, player_data.get('name'), player_data.get('team'), json.dumps(player_data))
            )
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    # First drop all existing tables
    drop_all_tables()
    
    # Create tables
    create_tables()
    
    # Load data for each position
    position_files = {
        'QB': 'QB_season.json',
        'RB': 'RB_season.json',
        'WR': 'WR_season.json',
        'TE': 'TE_season.json',
        'K': 'K_season.json',
        'LB': 'LB_season.json',
        'DL': 'DL_season.json',
        'DB': 'DB_season.json'
    }
    
    for position, filename in position_files.items():
        if os.path.exists(filename):
            print(f"Loading {position} data from {filename}")
            load_json_data(position, filename) 