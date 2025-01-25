import os
import json
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import logging

logger = logging.getLogger(__name__)

load_dotenv()

def get_db_connection():
    try:
        logger.info("Connecting to database...")
        # Get database URL from environment variable, default to local database if not set
        database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/nfl_stats')
        
        # Replace postgres:// with postgresql:// for SQLAlchemy
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
        # If using local database, don't require SSL
        if 'localhost' in database_url:
            logger.info("Using local database connection")
            conn = psycopg2.connect(database_url)
        else:
            logger.info("Using remote database connection with SSL")
            conn = psycopg2.connect(database_url, sslmode='require')
        
        # Test the connection
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
            logger.info("Database connection successful")
        
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise Exception(f"Database connection failed: {str(e)}")

def create_tables(conn):
    print("Creating tables...")
    cur = conn.cursor()
    
    try:
        # Drop existing tables and constraints in reverse order of dependencies
        print("Dropping existing tables and constraints...")
        cur.execute("""
            DROP TABLE IF EXISTS qb_stats CASCADE;
            DROP TABLE IF EXISTS rb_stats CASCADE;
            DROP TABLE IF EXISTS wr_stats CASCADE;
            DROP TABLE IF EXISTS te_stats CASCADE;
            DROP TABLE IF EXISTS lb_stats CASCADE;
            DROP TABLE IF EXISTS dl_stats CASCADE;
            DROP TABLE IF EXISTS db_stats CASCADE;
            DROP TABLE IF EXISTS k_stats CASCADE;
            DROP TABLE IF EXISTS teams CASCADE;
        """)
        
        # Drop any existing constraints that might cause issues
        cur.execute("""
            DO $$ 
            BEGIN
                -- Drop constraints if they exist
                BEGIN
                    ALTER TABLE IF EXISTS qb_stats DROP CONSTRAINT IF EXISTS unique_qb_rank;
                    ALTER TABLE IF EXISTS rb_stats DROP CONSTRAINT IF EXISTS unique_rb_rank;
                    ALTER TABLE IF EXISTS wr_stats DROP CONSTRAINT IF EXISTS unique_wr_rank;
                    ALTER TABLE IF EXISTS te_stats DROP CONSTRAINT IF EXISTS unique_te_rank;
                    ALTER TABLE IF EXISTS lb_stats DROP CONSTRAINT IF EXISTS unique_lb_rank;
                    ALTER TABLE IF EXISTS dl_stats DROP CONSTRAINT IF EXISTS unique_dl_rank;
                    ALTER TABLE IF EXISTS db_stats DROP CONSTRAINT IF EXISTS unique_db_rank;
                    ALTER TABLE IF EXISTS k_stats DROP CONSTRAINT IF EXISTS unique_k_rank;
                EXCEPTION 
                    WHEN undefined_table THEN 
                        NULL;
                END;
            END $$;
        """)
        print("Existing tables and constraints dropped")

        # Create teams table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teams (
                team_code VARCHAR(3) PRIMARY KEY,
                team_name VARCHAR(100) NOT NULL,
                division VARCHAR(50)
            )
        """)
        print("Created teams table")

        # Create QB stats table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS qb_stats (
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
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
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
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
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
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
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
                receptions INTEGER,
                targets INTEGER,
                receivingyards INTEGER,
                receivingtds INTEGER,
                totalpoints NUMERIC,
                rank INTEGER
            )
        """)
        print("Created TE stats table")

        # Create LB stats table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS lb_stats (
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
                tackles NUMERIC,
                tackles_ast NUMERIC,
                sacks NUMERIC,
                tackles_tfl NUMERIC,
                interceptions NUMERIC,
                forced_fumbles NUMERIC,
                fumble_recoveries NUMERIC,
                passes_defended NUMERIC,
                qb_hits NUMERIC,
                totalpoints NUMERIC,
                rank INTEGER
            )
        """)
        print("Created LB_STATS table")

        # Create DL stats table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dl_stats (
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
                tackles NUMERIC,
                tackles_ast NUMERIC,
                sacks NUMERIC,
                tackles_tfl NUMERIC,
                interceptions NUMERIC,
                forced_fumbles NUMERIC,
                fumble_recoveries NUMERIC,
                passes_defended NUMERIC,
                qb_hits NUMERIC,
                totalpoints NUMERIC,
                rank INTEGER
            )
        """)
        print("Created DL_STATS table")

        # Create DB stats table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS db_stats (
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
                tackles NUMERIC,
                tackles_ast NUMERIC,
                sacks NUMERIC,
                tackles_tfl NUMERIC,
                interceptions NUMERIC,
                forced_fumbles NUMERIC,
                fumble_recoveries NUMERIC,
                passes_defended NUMERIC,
                qb_hits NUMERIC,
                totalpoints NUMERIC,
                rank INTEGER
            )
        """)
        print("Created DB_STATS table")

        # Create K stats table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS k_stats (
                playerid VARCHAR(10) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(3) REFERENCES teams(team_code),
                fieldgoals INTEGER,
                fieldgoalattempts INTEGER,
                extrapoints INTEGER,
                extrapointattempts INTEGER,
                totalpoints NUMERIC,
                rank INTEGER
            )
        """)
        print("Created K stats table")

        # Create triggers for team code validation
        cur.execute("""
            CREATE OR REPLACE FUNCTION validate_team_code()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.team IS NOT NULL AND NOT EXISTS (SELECT 1 FROM teams WHERE team_code = NEW.team) THEN
                    RAISE EXCEPTION 'Invalid team code: %', NEW.team;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # Create triggers for each stats table
        for table in ['qb_stats', 'rb_stats', 'wr_stats', 'te_stats', 'lb_stats', 'dl_stats', 'db_stats', 'k_stats']:
            cur.execute(f"""
                DROP TRIGGER IF EXISTS validate_{table}_team ON {table};
                CREATE TRIGGER validate_{table}_team
                    BEFORE INSERT OR UPDATE ON {table}
                    FOR EACH ROW
                    EXECUTE FUNCTION validate_team_code();
            """)
        print("Created triggers")

        conn.commit()
        print("All tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def load_json_data(conn):
    print("Loading data...")
    cur = conn.cursor()
    
    try:
        # Check if all required files exist
        required_files = ['teams.json', 'QB_season.json', 'RB_season.json', 'WR_season.json', 
                         'TE_season.json', 'LB_season.json', 'DL_season.json', 'DB_season.json', 
                         'K_season.json']
        
        # Get the data directory path
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(data_dir, f))]
        if missing_files:
            raise FileNotFoundError(f"Missing required files: {', '.join(missing_files)}")

        # Load teams data first
        with open(os.path.join(data_dir, 'teams.json'), 'r') as f:
            teams_data = json.load(f)
            print(f"Loading teams data...")
            loaded_count = 0
            
            # Check if teams are already loaded
            cur.execute("SELECT COUNT(*) FROM teams")
            team_count = cur.fetchone()[0]
            if team_count > 0:
                print("Teams already loaded, skipping...")
            else:
                for team in teams_data:
                    try:
                        cur.execute("""
                            INSERT INTO teams (team_code, team_name, division)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (team_code) DO UPDATE 
                            SET team_name = EXCLUDED.team_name,
                                division = EXCLUDED.division
                        """, (team['team_code'], team['team_name'], team.get('division')))
                        loaded_count += 1
                    except Exception as e:
                        print(f"Error loading team {team.get('team_name')}: {str(e)}")
                        continue
                conn.commit()
                print(f"Successfully loaded {loaded_count} teams!")

        # Load QB stats
        with open(os.path.join(data_dir, 'QB_season.json'), 'r') as f:
            qb_data = json.load(f)
            values = []
            for player in qb_data:
                try:
                    # Fast conversion with minimal validation
                    values.append((
                        player.get('PlayerId'), player.get('PlayerName'), player.get('Team'),
                        int(player.get('PassingYDS', 0) or 0),
                        int(player.get('PassingTD', 0) or 0),
                        int(player.get('PassingInt', 0) or 0),
                        int(player.get('RushingYDS', 0) or 0),
                        int(player.get('RushingTD', 0) or 0),
                        float(player.get('TotalPoints', 0) or 0),
                        int(player.get('Rank', 999) or 999)
                    ))
                except Exception as e:
                    print(f"Skipping QB {player.get('PlayerName', 'Unknown')}")
                    continue

            if values:
                # Batch insert all QBs at once
                cur.executemany("""
                    INSERT INTO qb_stats (playerid, playername, team, passingyards, passingtds, interceptions, rushingyards, rushingtds, totalpoints, rank)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (playerid) DO UPDATE 
                    SET playername = EXCLUDED.playername,
                        team = EXCLUDED.team,
                        passingyards = EXCLUDED.passingyards,
                        passingtds = EXCLUDED.passingtds,
                        interceptions = EXCLUDED.interceptions,
                        rushingyards = EXCLUDED.rushingyards,
                        rushingtds = EXCLUDED.rushingtds,
                        totalpoints = EXCLUDED.totalpoints,
                        rank = EXCLUDED.rank
                """, values)
                conn.commit()
                print(f"Loaded {len(values)} QBs")

        # Load RB stats
        with open(os.path.join(data_dir, 'RB_season.json'), 'r') as f:
            rb_data = json.load(f)
            values = []
            for player in rb_data:
                try:
                    # Fast conversion with minimal validation
                    values.append((
                        player.get('PlayerId'), player.get('PlayerName'), player.get('Team'),
                        int(player.get('RushingYDS', 0) or 0),
                        int(player.get('RushingTD', 0) or 0),
                        int(player.get('ReceivingRec', 0) or 0),
                        int(player.get('ReceivingYDS', 0) or 0),
                        int(player.get('ReceivingTD', 0) or 0),
                        float(player.get('TotalPoints', 0) or 0),
                        int(player.get('Rank', 999) or 999)
                    ))
                except Exception as e:
                    print(f"Skipping RB {player.get('PlayerName', 'Unknown')}")
                    continue

            if values:
                # Batch insert all RBs at once
                cur.executemany("""
                    INSERT INTO rb_stats (playerid, playername, team, rushingyards, rushingtds, receptions, receivingyards, receivingtds, totalpoints, rank)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (playerid) DO UPDATE 
                    SET playername = EXCLUDED.playername,
                        team = EXCLUDED.team,
                        rushingyards = EXCLUDED.rushingyards,
                        rushingtds = EXCLUDED.rushingtds,
                        receptions = EXCLUDED.receptions,
                        receivingyards = EXCLUDED.receivingyards,
                        receivingtds = EXCLUDED.receivingtds,
                        totalpoints = EXCLUDED.totalpoints,
                        rank = EXCLUDED.rank
                """, values)
                conn.commit()
                print(f"Loaded {len(values)} RBs")

        # Load WR/TE stats
        for pos in ['WR', 'TE']:
            with open(os.path.join(data_dir, f'{pos}_season.json'), 'r') as f:
                pos_data = json.load(f)
                values = []
                for player in pos_data:
                    try:
                        # Fast conversion with minimal validation
                        values.append((
                            player.get('PlayerId'), player.get('PlayerName'), player.get('Team'),
                            int(player.get('ReceivingRec', 0) or 0),
                            int(player.get('Targets', 0) or 0),
                            int(player.get('ReceivingYDS', 0) or 0),
                            int(player.get('ReceivingTD', 0) or 0),
                            float(player.get('TotalPoints', 0) or 0),
                            int(player.get('Rank', 999) or 999)
                        ))
                    except Exception as e:
                        print(f"Skipping {pos} {player.get('PlayerName', 'Unknown')}")
                        continue

                if values:
                    # Batch insert all players at once
                    cur.executemany(f"""
                        INSERT INTO {pos.lower()}_stats (playerid, playername, team, receptions, targets, receivingyards, receivingtds, totalpoints, rank)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (playerid) DO UPDATE 
                        SET playername = EXCLUDED.playername,
                            team = EXCLUDED.team,
                            receptions = EXCLUDED.receptions,
                            targets = EXCLUDED.targets,
                            receivingyards = EXCLUDED.receivingyards,
                            receivingtds = EXCLUDED.receivingtds,
                            totalpoints = EXCLUDED.totalpoints,
                            rank = EXCLUDED.rank
                    """, values)
                    conn.commit()
                    print(f"Loaded {len(values)} {pos}s")

        # Load defensive player stats (LB, DL, DB)
        for pos in ['LB', 'DL', 'DB']:
            try:
                if not os.path.exists(os.path.join(data_dir, f'{pos}_season.json')):
                    print(f"Warning: {pos}_season.json not found")
                    continue
                    
                with open(os.path.join(data_dir, f'{pos}_season.json'), 'r') as f:
                    def_data = json.load(f)
                    if not def_data:
                        continue
                        
                    values = []
                    for player in def_data:
                        try:
                            # Fast conversion with minimal validation
                            values.append((
                                player.get('PlayerId'), player.get('PlayerName'), player.get('Team'),
                                float(player.get('TacklesTot', 0) or 0),
                                float(player.get('TacklesAst', 0) or 0),
                                float(player.get('TacklesSck', 0) or 0),
                                float(player.get('TacklesTfl', 0) or 0),
                                float(player.get('TurnoverInt', 0) or 0),
                                float(player.get('TurnoverFrcFum', 0) or 0),
                                float(player.get('TurnoverFumRec', 0) or 0),
                                float(player.get('PDef', 0) or 0),
                                float(player.get('QBHit', 0) or 0),
                                float(player.get('TotalPoints', 0) or 0),
                                int(player.get('Rank', 999) or 999)
                            ))
                        except Exception as e:
                            print(f"Skipping {pos} {player.get('PlayerName', 'Unknown')}")
                            continue

                    if values:
                        # Batch insert all players at once
                        cur.executemany(f"""
                            INSERT INTO {pos.lower()}_stats (
                                playerid, playername, team, 
                                tackles, tackles_ast, sacks, tackles_tfl,
                                interceptions, forced_fumbles, fumble_recoveries,
                                passes_defended, qb_hits, totalpoints, rank
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (playerid) DO UPDATE 
                            SET playername = EXCLUDED.playername,
                                team = EXCLUDED.team,
                                tackles = EXCLUDED.tackles,
                                tackles_ast = EXCLUDED.tackles_ast,
                                sacks = EXCLUDED.sacks,
                                tackles_tfl = EXCLUDED.tackles_tfl,
                                interceptions = EXCLUDED.interceptions,
                                forced_fumbles = EXCLUDED.forced_fumbles,
                                fumble_recoveries = EXCLUDED.fumble_recoveries,
                                passes_defended = EXCLUDED.passes_defended,
                                qb_hits = EXCLUDED.qb_hits,
                                totalpoints = EXCLUDED.totalpoints,
                                rank = EXCLUDED.rank
                        """, values)
                        conn.commit()
                        print(f"Loaded {len(values)} {pos}s")
            except Exception as e:
                print(f"Error processing {pos}_season.json")

        # Load K stats
        with open(os.path.join(data_dir, 'K_season.json'), 'r') as f:
            k_data = json.load(f)
            values = []
            for player in k_data:
                try:
                    # Fast conversion with minimal validation
                    fg_made = sum(int(player.get(f'FgMade_{rng}', 0) or 0) for rng in ['0-19', '20-29', '30-39', '40-49', '50'])
                    fg_miss = sum(int(player.get(f'FgMiss_{rng}', 0) or 0) for rng in ['0-19', '20-29', '30-39'])
                    fg_attempts = fg_made + fg_miss
                    
                    pat_made = int(player.get('PatMade', 0) or 0)
                    pat_missed = int(player.get('PatMissed', 0) or 0)
                    pat_attempts = pat_made + pat_missed
                    
                    total_points = float(player.get('TotalPoints', 0) or 0)
                    rank = int(player.get('Rank', 999) or 999)

                    values.append((
                        player.get('PlayerId'), player.get('PlayerName'), player.get('Team'),
                        fg_made, fg_attempts, pat_made, pat_attempts,
                        total_points, rank
                    ))
                except Exception as e:
                    print(f"Skipping K {player.get('PlayerName', 'Unknown')}")
                    continue

            if values:
                # Batch insert all kickers at once
                cur.executemany("""
                    INSERT INTO k_stats (playerid, playername, team, fieldgoals, fieldgoalattempts, extrapoints, extrapointattempts, totalpoints, rank)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (playerid) DO UPDATE 
                    SET playername = EXCLUDED.playername,
                        team = EXCLUDED.team,
                        fieldgoals = EXCLUDED.fieldgoals,
                        fieldgoalattempts = EXCLUDED.fieldgoalattempts,
                        extrapoints = EXCLUDED.extrapoints,
                        extrapointattempts = EXCLUDED.extrapointattempts,
                        totalpoints = EXCLUDED.totalpoints,
                        rank = EXCLUDED.rank
                """, values)
                conn.commit()
                print(f"Loaded {len(values)} Ks")

        print("Successfully loaded all data!")
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

def load_teams_data():
    print("\nLoading teams data...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'teams.json')
    
    if not os.path.exists(file_path):
        print(f"Error: Teams file not found at {file_path}")
        return
    
    try:
        with open(file_path, 'r') as file:
            teams = json.load(file)
            print(f"Successfully loaded {len(teams)} teams")
    except Exception as e:
        print(f"Error reading teams JSON file: {str(e)}")
        return
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        for team in teams:
            try:
                cur.execute("""
                    INSERT INTO teams (team_code, team_name, division)
                    VALUES (%s, %s, %s)
                """, (
                    team['team_code'],
                    team['team_name'],
                    team['division']
                ))
                print(f"Loaded team: {team['team_name']}")
            except Exception as e:
                print(f"Error loading team {team.get('team_name', 'Unknown')}: {str(e)}")
                conn.rollback()
                continue
        
        conn.commit()
        print("Successfully loaded all teams!")
    except Exception as e:
        print(f"Error in database operations: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    try:
        # Create a single database connection for the entire process
        conn = get_db_connection()
        create_tables(conn)
        load_json_data(conn)  # Pass the connection to load_json_data
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    main() 