import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL is None:
        raise ValueError("No DATABASE_URL environment variable set")
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("Database connection successful!")
    return conn

def drop_all_tables():
    print("Dropping existing tables...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        DROP TABLE IF EXISTS players CASCADE;
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("All tables dropped successfully")

def create_tables():
    print("Creating tables...")
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
        print("Table creation SQL executed successfully")
    
    cur.close()
    conn.commit()
    conn.close()
    print("Tables created successfully!")

def load_json_data(position, filename):
    print(f"\nLoading {position} data from {filename}...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            print(f"Found {len(data)} {position} players to load")
            for player_data in data:
                cur.execute(
                    """
                    INSERT INTO players (position, player_name, team, season_data)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (position, player_data.get('name'), player_data.get('team'), json.dumps(player_data))
                )
                print(f"Loaded player: {player_data.get('name')}")
        
        conn.commit()
        print(f"Successfully loaded all {position} players!")
    except Exception as e:
        print(f"Error loading {position} data: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Starting database initialization...")
    
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
    
    print("\nStarting data loading...")
    for position, filename in position_files.items():
        if os.path.exists(filename):
            print(f"\nProcessing {position} data from {filename}")
            load_json_data(position, filename)
        else:
            print(f"Warning: File {filename} not found")
    
    print("\nDatabase initialization complete!") 