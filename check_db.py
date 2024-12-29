import pg8000
import os

# Database connection
DATABASE_URL = "postgres://u4frfq8rphkr89:pb906d5963e4ac1f17db49d71c8ff2cfddd55faa1f12a6f63aa9a1d1ac938b9a9@clhtb6lu92mj2.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d1imqo8lepvt22"

try:
    # Parse the URL
    user = "u4frfq8rphkr89"
    password = "pb906d5963e4ac1f17db49d71c8ff2cfddd55faa1f12a6f63aa9a1d1ac938b9a9"
    host = "clhtb6lu92mj2.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com"
    port = 5432
    database = "d1imqo8lepvt22"
    
    # Connect to database
    conn = pg8000.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    cur = conn.cursor()
    
    # List all tables
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = [r[0] for r in cur.fetchall()]
    print("\nTables in database:", tables)
    
    # Check content of each table
    for table in tables:
        cur.execute(f"SELECT COUNT(*) FROM {table};")
        count = cur.fetchone()[0]
        print(f"\n{table}: {count} rows")
        
        if count > 0:
            cur.execute(f"SELECT * FROM {table} LIMIT 1;")
            sample = cur.fetchone()
            print(f"Sample row: {sample}")
    
except Exception as e:
    print("Error:", str(e))
finally:
    if 'conn' in locals():
        conn.close() 