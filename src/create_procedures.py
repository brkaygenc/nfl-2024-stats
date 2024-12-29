import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection

def create_stored_procedures():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Drop existing procedures/functions
        cur.execute("""
            DROP FUNCTION IF EXISTS get_team_player_stats(VARCHAR) CASCADE;
            DROP FUNCTION IF EXISTS calculate_team_points(VARCHAR) CASCADE;
            DROP FUNCTION IF EXISTS get_top_position_players(VARCHAR, INTEGER) CASCADE;
        """)
        print("Dropped existing functions")

        # Function 1: Get player stats by team
        cur.execute("""
            CREATE OR REPLACE FUNCTION get_team_player_stats(team_code_param VARCHAR)
            RETURNS TABLE (
                playername VARCHAR,
                pos VARCHAR,
                team_name VARCHAR,
                points NUMERIC
            ) AS $$
            BEGIN
                RETURN QUERY
                WITH team_stats AS (
                    SELECT 
                        q.playername::VARCHAR,
                        'QB'::VARCHAR as pos,
                        t.team_name::VARCHAR as team_name,
                        q.totalpoints::NUMERIC as points
                    FROM qb_stats q
                    JOIN teams t ON t.team_code = q.team
                    WHERE q.team = team_code_param
                    UNION ALL
                    SELECT 
                        r.playername::VARCHAR,
                        'RB'::VARCHAR,
                        t.team_name::VARCHAR,
                        r.totalpoints::NUMERIC
                    FROM rb_stats r
                    JOIN teams t ON t.team_code = r.team
                    WHERE r.team = team_code_param
                    UNION ALL
                    SELECT 
                        w.playername::VARCHAR,
                        'WR'::VARCHAR,
                        t.team_name::VARCHAR,
                        w.totalpoints::NUMERIC
                    FROM wr_stats w
                    JOIN teams t ON t.team_code = w.team
                    WHERE w.team = team_code_param
                    UNION ALL
                    SELECT 
                        t.playername::VARCHAR,
                        'TE'::VARCHAR,
                        tm.team_name::VARCHAR,
                        t.totalpoints::NUMERIC
                    FROM te_stats t
                    JOIN teams tm ON tm.team_code = t.team
                    WHERE t.team = team_code_param
                    UNION ALL
                    SELECT 
                        k.playername::VARCHAR,
                        'K'::VARCHAR,
                        t.team_name::VARCHAR,
                        k.totalpoints::NUMERIC
                    FROM k_stats k
                    JOIN teams t ON t.team_code = k.team
                    WHERE k.team = team_code_param
                )
                SELECT * FROM team_stats ORDER BY points DESC;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("Created get_team_player_stats function")

        # Function 2: Calculate team total points
        cur.execute("""
            CREATE OR REPLACE FUNCTION calculate_team_points(team_code_param VARCHAR)
            RETURNS TABLE (
                team VARCHAR,
                points NUMERIC,
                players INTEGER
            ) AS $$
            BEGIN
                RETURN QUERY
                WITH team_points AS (
                    SELECT totalpoints FROM qb_stats q WHERE q.team = team_code_param
                    UNION ALL
                    SELECT totalpoints FROM rb_stats r WHERE r.team = team_code_param
                    UNION ALL
                    SELECT totalpoints FROM wr_stats w WHERE w.team = team_code_param
                    UNION ALL
                    SELECT totalpoints FROM te_stats t WHERE t.team = team_code_param
                    UNION ALL
                    SELECT totalpoints FROM k_stats k WHERE k.team = team_code_param
                )
                SELECT 
                    team_code_param::VARCHAR,
                    COALESCE(SUM(totalpoints), 0)::NUMERIC,
                    COUNT(*)::INTEGER
                FROM team_points;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("Created calculate_team_points function")

        # Function 3: Get top players by position
        cur.execute("""
            CREATE OR REPLACE FUNCTION get_top_position_players(pos VARCHAR, limit_count INTEGER)
            RETURNS TABLE (
                playername VARCHAR,
                team VARCHAR,
                points NUMERIC
            ) AS $$
            BEGIN
                CASE pos
                    WHEN 'QB' THEN
                        RETURN QUERY
                        SELECT q.playername::VARCHAR, q.team::VARCHAR, q.totalpoints::NUMERIC
                        FROM qb_stats q
                        ORDER BY q.totalpoints DESC
                        LIMIT limit_count;
                    WHEN 'RB' THEN
                        RETURN QUERY
                        SELECT r.playername::VARCHAR, r.team::VARCHAR, r.totalpoints::NUMERIC
                        FROM rb_stats r
                        ORDER BY r.totalpoints DESC
                        LIMIT limit_count;
                    WHEN 'WR' THEN
                        RETURN QUERY
                        SELECT w.playername::VARCHAR, w.team::VARCHAR, w.totalpoints::NUMERIC
                        FROM wr_stats w
                        ORDER BY w.totalpoints DESC
                        LIMIT limit_count;
                    WHEN 'TE' THEN
                        RETURN QUERY
                        SELECT t.playername::VARCHAR, t.team::VARCHAR, t.totalpoints::NUMERIC
                        FROM te_stats t
                        ORDER BY t.totalpoints DESC
                        LIMIT limit_count;
                    WHEN 'K' THEN
                        RETURN QUERY
                        SELECT k.playername::VARCHAR, k.team::VARCHAR, k.totalpoints::NUMERIC
                        FROM k_stats k
                        ORDER BY k.totalpoints DESC
                        LIMIT limit_count;
                    ELSE
                        RAISE EXCEPTION 'Invalid position: %', pos;
                END CASE;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("Created get_top_position_players function")

        conn.commit()
        print("Successfully created all stored functions!")
    except Exception as e:
        print(f"Error creating stored functions: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_stored_procedures() 