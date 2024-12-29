import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connect_to_db():
    try:
        print("Connecting to database...")
        # Get database URL from environment variable, default to local database if not set
        database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/nfl_stats')
        
        # If using local database, don't require SSL
        if 'localhost' in database_url:
            conn = psycopg2.connect(database_url)
        else:
            conn = psycopg2.connect(database_url, sslmode='require')
        
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e

def create_tables():
    print("Creating tables...")
    conn = connect_to_db()
    cur = conn.cursor()
    
    try:
        # Create QB stats table
        cur.execute("""
            DROP TABLE IF EXISTS qb_stats CASCADE;
            CREATE TABLE qb_stats (
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
            DROP TABLE IF EXISTS rb_stats CASCADE;
            CREATE TABLE rb_stats (
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
            DROP TABLE IF EXISTS wr_stats CASCADE;
            CREATE TABLE wr_stats (
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
            DROP TABLE IF EXISTS te_stats CASCADE;
            CREATE TABLE te_stats (
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
            DROP TABLE IF EXISTS k_stats CASCADE;
            CREATE TABLE k_stats (
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
                DROP TABLE IF EXISTS {table} CASCADE;
                CREATE TABLE {table} (
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
        print("All tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def load_json_data(position, filename):
    print(f"\nLoading {position} data from {filename}...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    print(f"Looking for file at: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Directory contents: {os.listdir(os.getcwd())}")
        return
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print(f"Successfully loaded JSON data with {len(data)} {position} players")
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return
    
    conn = connect_to_db()
    cur = conn.cursor()
    
    try:
        for player in data:
            try:
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
                    # Calculate total field goals and attempts
                    fg_made = sum([
                        int(player.get('FgMade_0-19', 0) or 0),
                        int(player.get('FgMade_20-29', 0) or 0),
                        int(player.get('FgMade_30-39', 0) or 0),
                        int(player.get('FgMade_40-49', 0) or 0),
                        int(player.get('FgMade_50', 0) or 0)
                    ])
                    fg_attempts = fg_made + sum([
                        int(player.get('FgMiss_0-19', 0) or 0),
                        int(player.get('FgMiss_20-29', 0) or 0),
                        int(player.get('FgMiss_30-39', 0) or 0),
                        int(player.get('FgMiss_40-49', 0) or 0),
                        int(player.get('FgMiss_50', 0) or 0)
                    ])
                    pat_made = int(player.get('PatMade', 0) or 0)
                    pat_attempts = pat_made + int(player.get('PatMissed', 0) or 0)
                    
                    cur.execute("""
                        INSERT INTO k_stats (playername, playerid, team,
                            fieldgoals, fieldgoalattempts,
                            extrapoints, extrapointattempts,
                            totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        player['PlayerName'], player['PlayerId'], player['Team'],
                        fg_made, fg_attempts,
                        pat_made, pat_attempts,
                        float(player['TotalPoints']) if player['TotalPoints'] else 0,
                        int(player['Rank']) if player['Rank'] else 0
                    ))
                elif position in ['LB', 'DL', 'DB']:
                    # Get defensive stats from the correct fields
                    tackles = int(player.get('TacklesTot', 0) or 0)
                    sacks = float(player.get('TacklesSck', 0) or 0)
                    interceptions = int(player.get('TurnoverInt', 0) or 0)
                    
                    cur.execute(f"""
                        INSERT INTO {position.lower()}_stats (playername, playerid, team,
                            tackles, sacks, interceptions, totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        player['PlayerName'], player['PlayerId'], player['Team'],
                        tackles, sacks, interceptions,
                        float(player['TotalPoints']) if player['TotalPoints'] else 0,
                        int(player['Rank']) if player['Rank'] else 0
                    ))
                print(f"Loaded player: {player['PlayerName']}")
            except Exception as e:
                print(f"Error loading player {player.get('PlayerName', 'Unknown')}: {str(e)}")
                conn.rollback()
                continue
        
        conn.commit()
        print(f"Successfully loaded all {position} players!")
    except Exception as e:
        print(f"Error in database operations: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Starting database initialization...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Directory contents: {os.listdir(os.getcwd())}")
    
    try:
        # Create tables (this will also drop existing tables)
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
        
        print("\nDatabase initialization complete!")
    except Exception as e:
        print(f"Error in main process: {str(e)}") 