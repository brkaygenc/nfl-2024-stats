import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection

def check_database_connection():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Test query
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print("Successfully connected to the database!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Test tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        print("\nAvailable tables:")
        for table in tables:
            print(f"- {table[0]}")
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    check_database_connection() 