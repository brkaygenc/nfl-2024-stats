from flask import Flask, jsonify, request
from flask_cors import CORS
from src.database import get_db_connection
import psycopg2
from functools import wraps
import time
import os
import logging

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
    if position not in {'QB', 'RB', 'WR', 'TE', 'K', 'DEF'}:
        return jsonify({
            'error': 'Invalid position',
            'message': f"Position must be one of: QB, RB, WR, TE, K, DEF",
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
        else:  # DEF
            query = """
                SELECT 
                    playername as name,
                    'DEF' as position,
                    team,
                    0 as passing_yards,
                    0 as rushing_yards,
                    0 as touchdowns,
                    interceptions
                FROM (
                    SELECT * FROM lb_stats
                    UNION ALL
                    SELECT * FROM dl_stats
                    UNION ALL
                    SELECT * FROM db_stats
                ) as def_stats
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
                if columns[i] in ['passing_yards', 'rushing_yards', 'touchdowns', 'interceptions']:
                    player[columns[i]] = int(value) if value is not None else 0
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