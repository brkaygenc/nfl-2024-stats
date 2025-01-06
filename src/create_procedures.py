import psycopg2
from database import get_db_connection

def create_procedures_and_triggers():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create get_team_player_stats function (this is used in the UI)
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
                        te.playername::VARCHAR,
                        'TE'::VARCHAR,
                        t.team_name::VARCHAR,
                        te.totalpoints::NUMERIC
                    FROM te_stats te
                    JOIN teams t ON t.team_code = te.team
                    WHERE te.team = team_code_param
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
        
        # Create rank validation trigger
        cur.execute("""
            CREATE OR REPLACE FUNCTION validate_rank()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.rank <= 0 THEN
                    RAISE EXCEPTION 'Rank must be positive: %', NEW.rank;
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # Apply rank validation trigger to all stats tables
        for table in ['qb_stats', 'rb_stats', 'wr_stats', 'te_stats', 'lb_stats', 'dl_stats', 'db_stats', 'k_stats']:
            cur.execute(f"""
                DROP TRIGGER IF EXISTS validate_{table}_rank ON {table};
                CREATE TRIGGER validate_{table}_rank
                    BEFORE INSERT OR UPDATE ON {table}
                    FOR EACH ROW
                    EXECUTE FUNCTION validate_rank();
            """)
        
        # Create points calculation triggers for each position
        # QB Points
        cur.execute("""
            CREATE OR REPLACE FUNCTION calculate_qb_points()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.totalpoints = (
                    COALESCE(NEW.passingyards, 0) * 0.04 +
                    COALESCE(NEW.passingtds, 0) * 4 +
                    COALESCE(NEW.interceptions, 0) * -2 +
                    COALESCE(NEW.rushingyards, 0) * 0.1 +
                    COALESCE(NEW.rushingtds, 0) * 6
                );
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            
            DROP TRIGGER IF EXISTS calculate_qb_points_trigger ON qb_stats;
            CREATE TRIGGER calculate_qb_points_trigger
                BEFORE INSERT OR UPDATE ON qb_stats
                FOR EACH ROW
                EXECUTE FUNCTION calculate_qb_points();
        """)

        # RB Points
        cur.execute("""
            CREATE OR REPLACE FUNCTION calculate_rb_points()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.totalpoints = (
                    COALESCE(NEW.rushingyards, 0) * 0.1 +
                    COALESCE(NEW.rushingtds, 0) * 6 +
                    COALESCE(NEW.receptions, 0) * 1 +
                    COALESCE(NEW.receivingyards, 0) * 0.1 +
                    COALESCE(NEW.receivingtds, 0) * 6
                );
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            
            DROP TRIGGER IF EXISTS calculate_rb_points_trigger ON rb_stats;
            CREATE TRIGGER calculate_rb_points_trigger
                BEFORE INSERT OR UPDATE ON rb_stats
                FOR EACH ROW
                EXECUTE FUNCTION calculate_rb_points();
        """)

        # Create update_player_stats procedure
        cur.execute("""
            CREATE OR REPLACE PROCEDURE update_player_stats(
                p_playerid VARCHAR,
                p_playername VARCHAR,
                p_team VARCHAR,
                p_stats JSON
            )
            LANGUAGE plpgsql
            AS $$
            BEGIN
                -- Update QB stats if player is QB
                IF EXISTS (SELECT 1 FROM qb_stats WHERE playerid = p_playerid) THEN
                    UPDATE qb_stats
                    SET playername = p_playername,
                        team = p_team,
                        passingyards = COALESCE((p_stats->>'passingyards')::INTEGER, passingyards),
                        passingtds = COALESCE((p_stats->>'passingtds')::INTEGER, passingtds),
                        interceptions = COALESCE((p_stats->>'interceptions')::INTEGER, interceptions),
                        rushingyards = COALESCE((p_stats->>'rushingyards')::INTEGER, rushingyards),
                        rushingtds = COALESCE((p_stats->>'rushingtds')::INTEGER, rushingtds)
                    WHERE playerid = p_playerid;
                -- Update RB stats if player is RB
                ELSIF EXISTS (SELECT 1 FROM rb_stats WHERE playerid = p_playerid) THEN
                    UPDATE rb_stats
                    SET playername = p_playername,
                        team = p_team,
                        rushingyards = COALESCE((p_stats->>'rushingyards')::INTEGER, rushingyards),
                        rushingtds = COALESCE((p_stats->>'rushingtds')::INTEGER, rushingtds),
                        receptions = COALESCE((p_stats->>'receptions')::INTEGER, receptions),
                        receivingyards = COALESCE((p_stats->>'receivingyards')::INTEGER, receivingyards),
                        receivingtds = COALESCE((p_stats->>'receivingtds')::INTEGER, receivingtds)
                    WHERE playerid = p_playerid;
                END IF;
                
                COMMIT;
            END;
            $$;
        """)
        
        conn.commit()
        print("Successfully created all procedures and triggers!")
        
    except Exception as e:
        print(f"Error creating procedures and triggers: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    create_procedures_and_triggers() 