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

def create_tables():
    print("Creating tables...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create QB stats table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS qb_stats (
            playername VARCHAR(100),
            playerid VARCHAR(20) PRIMARY KEY,
            team VARCHAR(5),
            passingyards INTEGER,
            passingtds INTEGER,
            interceptions INTEGER,
            rushingyards INTEGER,
            rushingtds INTEGER,
            totalpoints NUMERIC,
            rank INTEGER
        )
    """)
    print("Created QB stats table")

    # Create RB stats table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rb_stats (
            playername VARCHAR(100),
            playerid VARCHAR(20) PRIMARY KEY,
            team VARCHAR(5),
            rushingyards INTEGER,
            rushingtds INTEGER,
            receptions INTEGER,
            receivingyards INTEGER,
            receivingtds INTEGER,
            totalpoints NUMERIC,
            rank INTEGER
        )
    """)
    print("Created RB stats table")

    # Create WR stats table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wr_stats (
            playername VARCHAR(100),
            playerid VARCHAR(20) PRIMARY KEY,
            team VARCHAR(5),
            receptions INTEGER,
            targets INTEGER,
            receivingyards INTEGER,
            receivingtds INTEGER,
            totalpoints NUMERIC,
            rank INTEGER
        )
    """)
    print("Created WR stats table")

    # Create TE stats table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS te_stats (
            playername VARCHAR(100),
            playerid VARCHAR(20) PRIMARY KEY,
            team VARCHAR(5),
            receptions INTEGER,
            targets INTEGER,
            receivingyards INTEGER,
            receivingtds INTEGER,
            totalpoints NUMERIC,
            rank INTEGER
        )
    """)
    print("Created TE stats table")

    # Create K stats table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS k_stats (
            playername VARCHAR(100),
            playerid VARCHAR(20) PRIMARY KEY,
            team VARCHAR(5),
            fieldgoals INTEGER,
            fieldgoalattempts INTEGER,
            extrapoints INTEGER,
            extrapointattempts INTEGER,
            totalpoints NUMERIC,
            rank INTEGER
        )
    """)
    print("Created K stats table")

    # Create defensive player tables (LB, DL, DB)
    defensive_tables = ['lb_stats', 'dl_stats', 'db_stats']
    for table in defensive_tables:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                playername VARCHAR(100),
                playerid VARCHAR(20) PRIMARY KEY,
                team VARCHAR(5),
                tackles INTEGER,
                sacks NUMERIC,
                interceptions INTEGER,
                totalpoints NUMERIC,
                rank INTEGER
            )
        """)
        print(f"Created {table.upper()} table")
    
    conn.commit()
    cur.close()
    conn.close()
    print("All tables created successfully!")

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

def load_json_data(position, filename):
    print(f"\nLoading {position} data from {filename}...")
    # Get the absolute path of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    print(f"Looking for file at: {file_path}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Directory contents: {os.listdir(os.getcwd())}")
            return
            
        with open(file_path, 'r') as file:
            data = json.load(file)
            print(f"Found {len(data)} {position} players to load")
            
            for player in data:
                if position == 'QB':
                    cur.execute("""
                        INSERT INTO qb_stats (playername, playerid, team, 
                            passingyards, passingtds, interceptions,
                            rushingyards, rushingtds, totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        player['PlayerName'], player['PlayerId'], player['Team'],
                        int(player['PassingYDS']) if player['PassingYDS'] else 0,
                        int(player['PassingTD']) if player['PassingTD'] else 0,
                        int(player['PassingInt']) if player['PassingInt'] else 0,
                        int(player['RushingYDS']) if player['RushingYDS'] else 0,
                        int(player['RushingTD']) if player['RushingTD'] else 0,
                        float(player['TotalPoints']) if player['TotalPoints'] else 0,
                        int(player['Rank']) if player['Rank'] else 0
                    ))
                elif position == 'RB':
                    cur.execute("""
                        INSERT INTO rb_stats (playername, playerid, team,
                            rushingyards, rushingtds, receptions,
                            receivingyards, receivingtds, totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        player['PlayerName'], player['PlayerId'], player['Team'],
                        int(player['RushingYDS']) if player['RushingYDS'] else 0,
                        int(player['RushingTD']) if player['RushingTD'] else 0,
                        int(player['ReceivingRec']) if player['ReceivingRec'] else 0,
                        int(player['ReceivingYDS']) if player['ReceivingYDS'] else 0,
                        int(player['ReceivingTD']) if player['ReceivingTD'] else 0,
                        float(player['TotalPoints']) if player['TotalPoints'] else 0,
                        int(player['Rank']) if player['Rank'] else 0
                    ))
                elif position in ['WR', 'TE']:
                    cur.execute(f"""
                        INSERT INTO {position.lower()}_stats (playername, playerid, team,
                            receptions, targets, receivingyards,
                            receivingtds, totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        player['PlayerName'], player['PlayerId'], player['Team'],
                        int(player['ReceivingRec']) if player['ReceivingRec'] else 0,
                        int(player['Targets']) if player['Targets'] else 0,
                        int(player['ReceivingYDS']) if player['ReceivingYDS'] else 0,
                        int(player['ReceivingTD']) if player['ReceivingTD'] else 0,
                        float(player['TotalPoints']) if player['TotalPoints'] else 0,
                        int(player['Rank']) if player['Rank'] else 0
                    ))
                elif position == 'K':
                    cur.execute("""
                        INSERT INTO k_stats (playername, playerid, team,
                            fieldgoals, fieldgoalattempts,
                            extrapoints, extrapointattempts,
                            totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        player['PlayerName'], player['PlayerId'], player['Team'],
                        int(player['FieldGoals']) if player.get('FieldGoals') else 0,
                        int(player['FieldGoalAttempts']) if player.get('FieldGoalAttempts') else 0,
                        int(player['ExtraPoints']) if player.get('ExtraPoints') else 0,
                        int(player['ExtraPointAttempts']) if player.get('ExtraPointAttempts') else 0,
                        float(player['TotalPoints']) if player['TotalPoints'] else 0,
                        int(player['Rank']) if player['Rank'] else 0
                    ))
                elif position in ['LB', 'DL', 'DB']:
                    cur.execute(f"""
                        INSERT INTO {position.lower()}_stats (playername, playerid, team,
                            tackles, sacks, interceptions,
                            totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        player['PlayerName'], player['PlayerId'], player['Team'],
                        int(player['Tackles']) if player.get('Tackles') else 0,
                        float(player['Sacks']) if player.get('Sacks') else 0,
                        int(player['Interceptions']) if player.get('Interceptions') else 0,
                        float(player['TotalPoints']) if player['TotalPoints'] else 0,
                        int(player['Rank']) if player['Rank'] else 0
                    ))
                print(f"Loaded player: {player['PlayerName']}")
        
        conn.commit()
        print(f"Successfully loaded all {position} players!")
    except Exception as e:
        print(f"Error loading {position} data: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir(os.getcwd())}")
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
    
    for position, filename in position_files.items():
        if os.path.exists(filename):
            print(f"\nProcessing {position} data from {filename}")
            load_json_data(position, filename)
        else:
            print(f"Warning: File {filename} not found in {os.getcwd()}") 