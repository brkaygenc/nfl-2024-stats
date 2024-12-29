from flask import Flask, jsonify, request
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db_connection
import psycopg2
from functools import wraps

app = Flask(__name__)

def handle_db_error(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except psycopg2.Error as e:
            return jsonify({
                "error": "Database error",
                "message": str(e)
            }), 500
        except Exception as e:
            return jsonify({
                "error": "Server error",
                "message": str(e)
            }), 500
    return decorated_function

@app.route('/')
@handle_db_error
def index():
    # Test database connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1")
    cur.close()
    conn.close()
    
    return jsonify({
        "message": "Welcome to NFL Stats API",
        "status": "Database connection successful",
        "endpoints": {
            "/players/<position>": "Get all players by position (QB, RB, WR, etc.)",
            "/players/team/<team>": "Get all players by team",
            "/players/search": "Search players by name (use ?name= parameter)",
            "/stats/position/<position>": "Get aggregated stats for a position",
            "/teams": "Get list of all teams"
        }
    })

@app.route('/players/<position>')
def get_players_by_position(position):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT player_name, team, season_data FROM players WHERE position = %s", (position.upper(),))
    players = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([{
        "name": player[0],
        "team": player[1],
        "stats": player[2]
    } for player in players])

@app.route('/players/team/<team>')
def get_players_by_team(team):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT position, player_name, season_data FROM players WHERE team ILIKE %s", (f"%{team}%",))
    players = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([{
        "position": player[0],
        "name": player[1],
        "stats": player[2]
    } for player in players])

@app.route('/players/search')
def search_players():
    name = request.args.get('name', '')
    if not name:
        return jsonify({"error": "Name parameter is required"}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT position, player_name, team, season_data 
        FROM players 
        WHERE player_name ILIKE %s
    """, (f"%{name}%",))
    players = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([{
        "position": player[0],
        "name": player[1],
        "team": player[2],
        "stats": player[3]
    } for player in players])

@app.route('/teams')
def get_teams():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT team FROM players WHERE team IS NOT NULL ORDER BY team")
    teams = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify([team[0] for team in teams])

@app.route('/stats/position/<position>')
def get_position_stats(position):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT COUNT(*) as player_count,
               array_agg(DISTINCT team) as teams
        FROM players 
        WHERE position = %s
    """, (position.upper(),))
    stats = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return jsonify({
        "position": position.upper(),
        "total_players": stats[0],
        "teams_represented": stats[1]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 