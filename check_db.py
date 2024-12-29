import os
import pg8000

print("starting")

try:
    print("connecting")
    conn = pg8000.connect(
        user=os.environ['DATABASE_URL'].split('/')[2].split(':')[0],
        password=os.environ['DATABASE_URL'].split(':')[2].split('@')[0],
        host=os.environ['DATABASE_URL'].split('@')[1].split(':')[0],
        port=int(os.environ['DATABASE_URL'].split(':')[3].split('/')[0]),
        database=os.environ['DATABASE_URL'].split('/')[-1],
        ssl_context=True
    )
    
    cur = conn.cursor()
    
    # Check lb_stats table
    cur.execute("SELECT COUNT(*) FROM lb_stats")
    count = cur.fetchone()[0]
    print(f"Number of rows in lb_stats: {count}")
    
    # Get a sample row
    cur.execute("SELECT * FROM lb_stats LIMIT 1")
    sample = cur.fetchone()
    print(f"Sample row from lb_stats: {sample}")
    
    conn.close()
    print("Database check completed successfully!")
except Exception as e:
    print(f"Error: {e}") 