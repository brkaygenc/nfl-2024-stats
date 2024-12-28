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
    
    tables = [
        'qb_stats', 'rb_stats', 'wr_stats', 'te_stats',
        'k_stats', 'lb_stats', 'dl_stats', 'db_stats'
    ]
    
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        print(f"Dropped table {table}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("All tables dropped successfully")

def create_tables():
    print("Creating tables...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create QB stats table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS qb_stats (
            playername character varying(100),
            playerid bigint PRIMARY KEY,
            pos character varying(5),
            team character varying(5),
            attempts bigint,
            completions bigint,
            completionpct numeric,
            passingyards bigint,
            passingtds bigint,
            interceptions bigint,
            rating numeric,
            rushingyards bigint,
            rushingtds bigint,
            rank bigint,
            totalpoints numeric
        )
    """)
    print("Created QB stats table")
    
    # Create similar tables for other positions...
    # Add more CREATE TABLE statements for other positions
    
    cur.close()
    conn.commit()
    conn.close()
    print("All tables created successfully!")

def load_json_data(position, filename):
    print(f"\nLoading {position} data from {filename}...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    table_name = f"{position.lower()}_stats"
    
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            print(f"Found {len(data)} {position} players to load")
            
            # Get column names from the first record
            if data:
                columns = list(data[0].keys())
                columns_str = ', '.join(columns)
                values_str = ', '.join(['%s'] * len(columns))
                
                # Create INSERT statement
                insert_query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES ({values_str})
                """
                
                # Insert each player's data
                for player_data in data:
                    values = [player_data.get(col) for col in columns]
                    cur.execute(insert_query, values)
                    print(f"Loaded player: {player_data.get('playername')}")
        
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