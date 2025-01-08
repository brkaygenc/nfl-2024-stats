from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_db_connection
import psycopg2
from functools import wraps
import time
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Rate limiting configuration
RATE_LIMIT = 100  # requests per minute
rate_limit_data = {}

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP
        client_ip = request.remote_addr
        current_time = time.time()
        
        # Initialize or clean up old rate limit data
        if client_ip not in rate_limit_data:
            rate_limit_data[client_ip] = []
        rate_limit_data[client_ip] = [t for t in rate_limit_data[client_ip] if current_time - t < 60]
        
        # Check rate limit
        if len(rate_limit_data[client_ip]) >= RATE_LIMIT:
            return jsonify({
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "status": 429
            }), 429
        
        # Add request timestamp
        rate_limit_data[client_ip].append(current_time)
        return f(*args, **kwargs)
    return decorated_function

# Root endpoint to verify API is working
@app.route('/')
def index():
    return jsonify({
        "message": "Welcome to NFL Stats API",
        "endpoints": {
            "/api/players/{position}": "Get players by position (QB, RB, WR, TE, K, DEF)",
        },
        "status": "operational"
    })

# Validate position parameter
VALID_POSITIONS = {'QB', 'RB', 'WR', 'TE', 'K', 'DEF'}

def get_table_name(position):
    if position == 'DEF':
        return ['lb_stats', 'dl_stats', 'db_stats']
    return f"{position.lower()}_stats"

@app.route('/api/players/<position>', methods=['GET'])
@rate_limit
def get_players_by_position(position):
    if position not in VALID_POSITIONS:
        return jsonify({
            "error": "Invalid position",
            "message": f"Position must be one of: {', '.join(VALID_POSITIONS)}",
            "status": 400
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if position == 'DEF':
            # Combine defensive players
            query = """
                SELECT 
                    playername,
                    playerid,
                    team,
                    COALESCE(tackles, 0) as tackles,
                    COALESCE(tackles_ast, 0) as tackles_ast,
                    COALESCE(sacks, 0) as sacks,
                    COALESCE(tackles_tfl, 0) as tackles_tfl,
                    COALESCE(interceptions, 0) as interceptions,
                    COALESCE(forced_fumbles, 0) as forced_fumbles,
                    COALESCE(fumble_recoveries, 0) as fumble_recoveries,
                    COALESCE(passes_defended, 0) as passes_defended,
                    COALESCE(qb_hits, 0) as qb_hits,
                    COALESCE(totalpoints, 0) as totalpoints,
                    rank
                FROM (
                    SELECT * FROM lb_stats
                    UNION ALL
                    SELECT * FROM dl_stats
                    UNION ALL
                    SELECT * FROM db_stats
                ) as def_stats
                ORDER BY totalpoints DESC
            """
        elif position == 'QB':
            query = """
                SELECT 
                    playername,
                    playerid,
                    team,
                    COALESCE(passingyards, 0) as passingyards,
                    COALESCE(passingtds, 0) as passingtds,
                    COALESCE(interceptions, 0) as interceptions,
                    COALESCE(rushingyards, 0) as rushingyards,
                    COALESCE(rushingtds, 0) as rushingtds,
                    COALESCE(totalpoints, 0) as totalpoints,
                    rank
                FROM qb_stats
                ORDER BY totalpoints DESC
            """
        elif position in ['WR', 'TE']:
            query = """
                SELECT 
                    playername,
                    playerid,
                    team,
                    COALESCE(receptions, 0) as receptions,
                    COALESCE(targets, 0) as targets,
                    COALESCE(receivingyards, 0) as receivingyards,
                    COALESCE(receivingtds, 0) as receivingtds,
                    COALESCE(totalpoints, 0) as totalpoints,
                    rank
                FROM {}
                ORDER BY totalpoints DESC
            """.format(get_table_name(position))
        elif position == 'RB':
            query = """
                SELECT 
                    playername,
                    playerid,
                    team,
                    COALESCE(rushingyards, 0) as rushingyards,
                    COALESCE(rushingtds, 0) as rushingtds,
                    COALESCE(receptions, 0) as receptions,
                    COALESCE(receivingyards, 0) as receivingyards,
                    COALESCE(receivingtds, 0) as receivingtds,
                    COALESCE(totalpoints, 0) as totalpoints,
                    rank
                FROM rb_stats
                ORDER BY totalpoints DESC
            """
        else:  # K
            query = """
                SELECT 
                    playername,
                    playerid,
                    team,
                    COALESCE(fieldgoals, 0) as fieldgoals,
                    COALESCE(fieldgoalattempts, 0) as fieldgoalattempts,
                    COALESCE(extrapoints, 0) as extrapoints,
                    COALESCE(extrapointattempts, 0) as extrapointattempts,
                    COALESCE(totalpoints, 0) as totalpoints,
                    rank
                FROM k_stats
                ORDER BY totalpoints DESC
            """

        cur.execute(query)
        results = cur.fetchall()
        
        if not results:
            return jsonify({
                "error": "Not Found",
                "message": f"No players found for position: {position}",
                "status": 404
            }), 404

        # Get column names from cursor description
        columns = [desc[0] for desc in cur.description]
        
        # Convert results to list of dictionaries
        players = []
        for row in results:
            player_dict = {}
            for i, value in enumerate(row):
                # Convert numeric strings to appropriate types
                if isinstance(value, str) and value.isdigit():
                    player_dict[columns[i]] = int(value)
                elif isinstance(value, (int, float)):
                    player_dict[columns[i]] = value
                else:
                    player_dict[columns[i]] = value
            players.append(player_dict)

        return jsonify({
            "success": True,
            "data": players,
            "count": len(players),
            "position": position
        }), 200

    except Exception as e:
        return jsonify({
            "error": "Server Error",
            "message": str(e),
            "status": 500
        }), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 