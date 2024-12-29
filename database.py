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
        # Create teams table first
        cur.execute("""
            DROP TABLE IF EXISTS teams CASCADE;
            CREATE TABLE teams (
                team_code VARCHAR(5) PRIMARY KEY,
                team_name VARCHAR(100) NOT NULL,
                division VARCHAR(50)
            )
        """)
        print("Created teams table")

        # Create QB stats table with foreign key
        cur.execute("""
            DROP TABLE IF EXISTS qb_stats CASCADE;
            CREATE TABLE qb_stats (
                playerid VARCHAR(20) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(5) REFERENCES teams(team_code) NULL,
                passingyards INTEGER,
                passingtds INTEGER,
                interceptions INTEGER,
                rushingyards INTEGER,
                rushingtds INTEGER,
                totalpoints NUMERIC,
                rank INTEGER CHECK (rank > 0),
                CONSTRAINT unique_qb_rank UNIQUE (rank)
            )
        """)
        print("Created QB stats table")

        # Create RB stats table with foreign key
        cur.execute("""
            DROP TABLE IF EXISTS rb_stats CASCADE;
            CREATE TABLE rb_stats (
                playerid VARCHAR(20) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(5) REFERENCES teams(team_code) NULL,
                rushingyards INTEGER,
                rushingtds INTEGER,
                receptions INTEGER,
                receivingyards INTEGER,
                receivingtds INTEGER,
                totalpoints NUMERIC,
                rank INTEGER CHECK (rank > 0),
                CONSTRAINT unique_rb_rank UNIQUE (rank)
            )
        """)
        print("Created RB stats table")

        # Create WR/TE stats tables with foreign key
        for pos in ['wr', 'te']:
            cur.execute(f"""
                DROP TABLE IF EXISTS {pos}_stats CASCADE;
                CREATE TABLE {pos}_stats (
                    playerid VARCHAR(20) PRIMARY KEY,
                    playername VARCHAR(100) NOT NULL,
                    team VARCHAR(5) REFERENCES teams(team_code) NULL,
                    receptions INTEGER,
                    targets INTEGER,
                    receivingyards INTEGER,
                    receivingtds INTEGER,
                    totalpoints NUMERIC,
                    rank INTEGER CHECK (rank > 0),
                    CONSTRAINT unique_{pos}_rank UNIQUE (rank)
                )
            """)
            print(f"Created {pos.upper()} stats table")

        # Create defensive player tables (LB, DL, DB) with foreign keys
        defensive_tables = ['lb_stats', 'dl_stats', 'db_stats']
        for table in defensive_tables:
            cur.execute(f"""
                DROP TABLE IF EXISTS {table} CASCADE;
                CREATE TABLE {table} (
                    playerid VARCHAR(20) PRIMARY KEY,
                    playername VARCHAR(100) NOT NULL,
                    team VARCHAR(5) REFERENCES teams(team_code) NULL,
                    tackles INTEGER,
                    sacks NUMERIC,
                    interceptions INTEGER,
                    totalpoints NUMERIC,
                    rank INTEGER CHECK (rank > 0),
                    CONSTRAINT unique_{table.split('_')[0]}_rank UNIQUE (rank)
                )
            """)
            print(f"Created {table.upper()} table")

        # Create K stats table with foreign key
        cur.execute("""
            DROP TABLE IF EXISTS k_stats CASCADE;
            CREATE TABLE k_stats (
                playerid VARCHAR(20) PRIMARY KEY,
                playername VARCHAR(100) NOT NULL,
                team VARCHAR(5) REFERENCES teams(team_code) NULL,
                fieldgoals INTEGER,
                fieldgoalattempts INTEGER,
                extrapoints INTEGER,
                extrapointattempts INTEGER,
                totalpoints NUMERIC,
                rank INTEGER CHECK (rank > 0),
                CONSTRAINT unique_k_rank UNIQUE (rank)
            )
        """)
        print("Created K stats table")

        # Create trigger function for rank validation
        cur.execute("""
        CREATE OR REPLACE FUNCTION validate_rank() RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.rank <= 0 THEN
                RAISE EXCEPTION 'Rank must be greater than 0';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """)

        # Create triggers for each table
        for table in ['qb_stats', 'rb_stats', 'wr_stats', 'te_stats', 'lb_stats', 'dl_stats', 'db_stats', 'k_stats']:
            cur.execute(f"""
            DROP TRIGGER IF EXISTS validate_{table}_rank ON {table};
            CREATE TRIGGER validate_{table}_rank
                BEFORE INSERT OR UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION validate_rank();
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
        conn.close()

def load_json_data():
    print("Loading data...")
    conn = connect_to_db()
    cur = conn.cursor()
    
    try:
        # Load teams data first
        with open('teams.json', 'r') as f:
            teams_data = json.load(f)
            for team in teams_data:
                cur.execute("""
                    INSERT INTO teams (team_code, team_name, division)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (team_code) DO UPDATE 
                    SET team_name = EXCLUDED.team_name,
                        division = EXCLUDED.division
                """, (team['team_code'], team['team_name'], team.get('division')))
        print("Loaded teams data")

        # Load QB stats
        with open('QB_season.json', 'r') as f:
            qb_data = json.load(f)
            for player in qb_data:
                try:
                    cur.execute("""
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
                    """, (
                        player['PlayerId'], player['PlayerName'], player.get('Team'),
                        player.get('PassingYards', 0), player.get('PassingTouchdowns', 0),
                        player.get('PassingInterceptions', 0), player.get('RushingYards', 0),
                        player.get('RushingTouchdowns', 0), player.get('TotalPoints', 0),
                        player.get('Rank', 999)
                    ))
                    print(f"Loaded player: {player['PlayerName']}")
                except Exception as e:
                    print(f"Error loading player {player['PlayerName']}: {str(e)}")

        # Load RB stats
        with open('RB_season.json', 'r') as f:
            rb_data = json.load(f)
            for player in rb_data:
                try:
                    cur.execute("""
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
                    """, (
                        player['PlayerId'], player['PlayerName'], player.get('Team'),
                        player.get('RushingAttempts', 0), player.get('RushingYards', 0),
                        player.get('RushingTouchdowns', 0), player.get('TotalPoints', 0),
                        player.get('Rank', 999)
                    ))
                    print(f"Loaded player: {player['PlayerName']}")
                except Exception as e:
                    print(f"Error loading player {player['PlayerName']}: {str(e)}")

        # Load WR/TE stats
        for pos in ['WR', 'TE']:
            with open(f'{pos}_season.json', 'r') as f:
                wr_data = json.load(f)
                for player in wr_data:
                    try:
                        cur.execute(f"""
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
                        """, (
                            player['PlayerId'], player['PlayerName'], player.get('Team'),
                            player.get('Receptions', 0), player.get('Targets', 0),
                            player.get('ReceivingYards', 0), player.get('ReceivingTouchdowns', 0),
                            player.get('TotalPoints', 0), player.get('Rank', 999)
                        ))
                        print(f"Loaded player: {player['PlayerName']}")
                    except Exception as e:
                        print(f"Error loading player {player['PlayerName']}: {str(e)}")

        # Load defensive player stats (LB, DL, DB)
        for pos in ['LB', 'DL', 'DB']:
            with open(f'{pos}_season.json', 'r') as f:
                def_data = json.load(f)
                for player in def_data:
                    try:
                        cur.execute(f"""
                            INSERT INTO {pos.lower()}_stats (playerid, playername, team, tackles, sacks, interceptions, totalpoints, rank)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (playerid) DO UPDATE 
                            SET playername = EXCLUDED.playername,
                                team = EXCLUDED.team,
                                tackles = EXCLUDED.tackles,
                                sacks = EXCLUDED.sacks,
                                interceptions = EXCLUDED.interceptions,
                                totalpoints = EXCLUDED.totalpoints,
                                rank = EXCLUDED.rank
                        """, (
                            player['PlayerId'], player['PlayerName'], player.get('Team'),
                            float(player.get('TacklesTot', 0)), float(player.get('TacklesSck', 0)),
                            float(player.get('TurnoverInt', 0)), float(player.get('TotalPoints', 0)),
                            int(player.get('Rank', 999))
                        ))
                        print(f"Loaded player: {player['PlayerName']}")
                    except Exception as e:
                        print(f"Error loading player {player['PlayerName']}: {str(e)}")

        # Load K stats
        with open('K_season.json', 'r') as f:
            k_data = json.load(f)
            for player in k_data:
                try:
                    cur.execute("""
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
                    """, (
                        player['PlayerId'], player['PlayerName'], player.get('Team'),
                        player.get('FieldGoals', 0), player.get('FieldGoalAttempts', 0),
                        player.get('ExtraPoints', 0), player.get('ExtraPointAttempts', 0),
                        player.get('TotalPoints', 0), player.get('Rank', 999)
                    ))
                    print(f"Loaded player: {player['PlayerName']}")
                except Exception as e:
                    print(f"Error loading player {player['PlayerName']}: {str(e)}")

        conn.commit()
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
    
    conn = connect_to_db()
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
    create_tables()
    load_teams_data()
    load_json_data()

if __name__ == '__main__':
    main() 