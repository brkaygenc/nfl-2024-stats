from flask import Flask, jsonify, request
from flask_cors import CORS
from src.database import get_db_connection
import psycopg2
from functools import wraps
import time
import os
import logging
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes with specific settings
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET"],
        "allow_headers": ["Content-Type"]
    }
})

# Custom JSON encoder to handle Decimal types
class CustomJSONEncoder(Flask.json_encoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

@app.route('/api/health')
def health_check():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'environment': {
                'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
                'PORT': os.getenv('PORT', 5000)
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'environment': {
                'DATABASE_URL': bool(os.getenv('DATABASE_URL')),
                'PORT': os.getenv('PORT', 5000)
            }
        }), 500

@app.route('/api/players/<position>', methods=['GET'])
def get_players_by_position(position):
    valid_positions = {'QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DL', 'DB'}
    if position not in valid_positions:
        return jsonify({
            'error': 'Invalid position',
            'message': f"Position must be one of: {', '.join(sorted(valid_positions))}",
            'provided': position
        }), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if position == 'QB':
            query = """
                SELECT 
                    playername as name,
                    'QB' as position,
                    team,
                    passingyards as passing_yards,
                    rushingyards as rushing_yards,
                    passingtds + rushingtds as touchdowns,
                    interceptions
                FROM qb_stats
                ORDER BY totalpoints DESC
            """
        elif position == 'RB':
            query = """
                SELECT 
                    playername as name,
                    'RB' as position,
                    team,
                    0 as passing_yards,
                    rushingyards as rushing_yards,
                    rushingtds + receivingtds as touchdowns,
                    0 as interceptions
                FROM rb_stats
                ORDER BY totalpoints DESC
            """
        elif position in ['WR', 'TE']:
            query = f"""
                SELECT 
                    playername as name,
                    '{position}' as position,
                    team,
                    0 as passing_yards,
                    0 as rushing_yards,
                    receivingtds as touchdowns,
                    0 as interceptions
                FROM {position.lower()}_stats
                ORDER BY totalpoints DESC
            """
        elif position == 'K':
            query = """
                SELECT 
                    playername as name,
                    'K' as position,
                    team,
                    0 as passing_yards,
                    0 as rushing_yards,
                    0 as touchdowns,
                    0 as interceptions
                FROM k_stats
                ORDER BY totalpoints DESC
            """
        elif position in ['LB', 'DL', 'DB']:
            query = f"""
                SELECT 
                    playername as name,
                    '{position}' as position,
                    team,
                    COALESCE(tackles, 0) as tackles,
                    COALESCE(tackles_ast, 0) as assisted_tackles,
                    COALESCE(sacks, 0) as sacks,
                    COALESCE(interceptions, 0) as interceptions,
                    COALESCE(forced_fumbles, 0) as forced_fumbles,
                    COALESCE(fumble_recoveries, 0) as fumble_recoveries,
                    COALESCE(passes_defended, 0) as passes_defended,
                    COALESCE(tackles_tfl, 0) as tackles_for_loss,
                    COALESCE(qb_hits, 0) as qb_hits,
                    COALESCE(totalpoints, 0) as total_points
                FROM {position.lower()}_stats
                ORDER BY totalpoints DESC
            """

        logger.info(f"Executing query for position: {position}")
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()

        # Convert to list of dictionaries with proper types
        players = []
        for row in results:
            player = {}
            for i, value in enumerate(row):
                # Convert numeric values to float/int
                if isinstance(value, (int, float, Decimal)):
                    player[columns[i]] = float(value) if isinstance(value, Decimal) else value
                elif isinstance(value, str) and value.isdigit():
                    player[columns[i]] = int(value)
                else:
                    player[columns[i]] = value
            players.append(player)

        logger.info(f"Found {len(players)} players for position: {position}")
        return jsonify(players), 200

    except Exception as e:
        logger.error(f"Error fetching {position} players: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 