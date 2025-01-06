import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection

def test_procedures():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("\n1. Testing get_team_player_stats for KC Chiefs:")
        print("---------------------------------------------")
        cur.execute("SELECT * FROM get_team_player_stats('KC')")
        results = cur.fetchall()
        for row in results:
            print(f"Player: {row[0]}, Position: {row[1]}, Team: {row[2]}, Points: {row[3]}")

        print("\n2. Testing QB Points Calculation Trigger:")
        print("---------------------------------------------")
        # Try to update Mahomes stats to see trigger in action
        cur.execute("""
            UPDATE qb_stats 
            SET passingyards = 5000, passingtds = 40, interceptions = 10
            WHERE playername = 'Patrick Mahomes'
            RETURNING playername, totalpoints;
        """)
        result = cur.fetchone()
        if result:
            print(f"Updated {result[0]}'s points to: {result[1]}")

        print("\n3. Testing Rank Validation Trigger:")
        print("---------------------------------------------")
        try:
            cur.execute("""
                UPDATE qb_stats 
                SET rank = -1
                WHERE playername = 'Patrick Mahomes';
            """)
        except Exception as e:
            print(f"Rank validation worked! Error: {str(e)}")

        conn.commit()
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Error in tests: {str(e)}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    test_procedures() 