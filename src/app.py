from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from src.database import get_db_connection
import psycopg2
from functools import wraps
import time
import os
import logging
from decimal import Decimal
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a Blueprint for API routes
api = Blueprint('api', __name__, url_prefix='/api')
app = Flask(__name__)
CORS(app)

# Custom JSON encoder to handle Decimal types
class CustomJSONEncoder(Flask.json_encoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

# Error handling middleware
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"An error occurred: {str(error)}")
    logger.error(traceback.format_exc())
    
    status_code = 500
    if hasattr(error, 'code'):
        status_code = error.code
    
    response = {
        'error': str(error.__class__.__name__),
        'message': str(error)
    }
    
    if status_code == 500:
        response = {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.'
        }
    
    return jsonify(response), status_code

# Database connection decorator
def with_db_connection(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        conn = None
        try:
            conn = get_db_connection()
            return f(conn, *args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {f.__name__}: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    return decorated_function

# API Routes - all under /api prefix
@api.route('/health')
@with_db_connection
def health_check(conn):
    try:
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise

@api.route('/players/<position>', methods=['GET'])
@with_db_connection
def get_players_by_position(conn, position):
    valid_positions = {'QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DL', 'DB'}
    if position not in valid_positions:
        return jsonify({
            'error': 'Invalid position',
            'message': f'Position must be one of: {", ".join(valid_positions)}'
        }), 400

    try:
        cur = conn.cursor()
        
        if position == 'QB':
            query = """
                SELECT playerid, playername, team, passingyards, passingtds, 
                       interceptions, rushingyards, rushingtds, totalpoints, rank
                FROM qb_stats
                ORDER BY rank ASC
            """
        elif position == 'RB':
            query = """
                SELECT playerid, playername, team, rushingyards, rushingtds,
                       receptions, receivingyards, receivingtds, totalpoints, rank
                FROM rb_stats
                ORDER BY rank ASC
            """
        elif position in ('WR', 'TE'):
            query = f"""
                SELECT playerid, playername, team, receptions, targets,
                       receivingyards, receivingtds, totalpoints, rank
                FROM {position.lower()}_stats
                ORDER BY rank ASC
            """
        elif position in ('LB', 'DL', 'DB'):
            query = f"""
                SELECT playerid, playername, team, tackles, sacks,
                       tackles_for_loss, forced_fumbles, totalpoints, rank
                FROM {position.lower()}_stats
                ORDER BY rank ASC
            """
        else:  # K
            query = """
                SELECT playerid, playername, team, fieldgoals, fieldgoal_attempts,
                       extrapoints, extrapoint_attempts, totalpoints, rank
                FROM k_stats
                ORDER BY rank ASC
            """
        
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        players = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return jsonify(players)

    except Exception as e:
        logger.error(f"Error fetching {position} players: {str(e)}")
        raise

@api.route('/teams', methods=['GET'])
@with_db_connection
def get_teams(conn):
    try:
        cur = conn.cursor()
        
        query = """
            SELECT team_code, team_name, division
            FROM teams
            ORDER BY division, team_name
        """
        
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        teams = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return jsonify(teams)
        
    except Exception as e:
        logger.error(f"Error fetching teams: {str(e)}")
        raise

@api.route('/teams/<team_code>/players', methods=['GET'])
@with_db_connection
def get_team_players(conn, team_code):
    try:
        cur = conn.cursor()
        
        # Get all players from all position tables for the given team
        query = """
            SELECT 'QB' as position, playerid, playername, team, 
                   passingyards as yards, passingtds as touchdowns, 
                   totalpoints, rank
            FROM qb_stats 
            WHERE team = %s
            UNION ALL
            SELECT 'RB' as position, playerid, playername, team, 
                   rushingyards as yards, rushingtds as touchdowns, 
                   totalpoints, rank
            FROM rb_stats 
            WHERE team = %s
            UNION ALL
            SELECT 'WR' as position, playerid, playername, team, 
                   receivingyards as yards, receivingtds as touchdowns, 
                   totalpoints, rank
            FROM wr_stats 
            WHERE team = %s
            UNION ALL
            SELECT 'TE' as position, playerid, playername, team, 
                   receivingyards as yards, receivingtds as touchdowns, 
                   totalpoints, rank
            FROM te_stats 
            WHERE team = %s
            ORDER BY totalpoints DESC
        """
        
        cur.execute(query, (team_code, team_code, team_code, team_code))
        columns = [desc[0] for desc in cur.description]
        players = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        if not players:
            return jsonify({
                'error': 'Not Found',
                'message': f'No players found for team {team_code}'
            }), 404
        
        return jsonify(players)
        
    except Exception as e:
        logger.error(f"Error fetching players for team {team_code}: {str(e)}")
        raise

@api.route('/search', methods=['GET'])
@with_db_connection
def search_players(conn):
    try:
        name = request.args.get('name', '').strip().lower()
        position = request.args.get('position', '').strip().upper()
        
        if not name:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Name parameter is required'
            }), 400
            
        valid_positions = {'QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DL', 'DB'}
        if position and position not in valid_positions:
            return jsonify({
                'error': 'Bad Request',
                'message': f'Invalid position. Must be one of: {", ".join(valid_positions)}',
                'provided': position
            }), 400
            
        cur = conn.cursor()
        
        # If no position specified, search across all positions
        if not position:
            query = """
                SELECT 'QB' as position, playerid, playername, team, totalpoints, rank
                FROM qb_stats 
                WHERE LOWER(playername) LIKE %s
                UNION ALL
                SELECT 'RB' as position, playerid, playername, team, totalpoints, rank
                FROM rb_stats 
                WHERE LOWER(playername) LIKE %s
                UNION ALL
                SELECT 'WR' as position, playerid, playername, team, totalpoints, rank
                FROM wr_stats 
                WHERE LOWER(playername) LIKE %s
                UNION ALL
                SELECT 'TE' as position, playerid, playername, team, totalpoints, rank
                FROM te_stats 
                WHERE LOWER(playername) LIKE %s
                UNION ALL
                SELECT 'K' as position, playerid, playername, team, totalpoints, rank
                FROM k_stats 
                WHERE LOWER(playername) LIKE %s
                UNION ALL
                SELECT 'LB' as position, playerid, playername, team, totalpoints, rank
                FROM lb_stats 
                WHERE LOWER(playername) LIKE %s
                UNION ALL
                SELECT 'DL' as position, playerid, playername, team, totalpoints, rank
                FROM dl_stats 
                WHERE LOWER(playername) LIKE %s
                UNION ALL
                SELECT 'DB' as position, playerid, playername, team, totalpoints, rank
                FROM db_stats 
                WHERE LOWER(playername) LIKE %s
                ORDER BY totalpoints DESC
            """
            search_pattern = f'%{name}%'
            cur.execute(query, (search_pattern,) * 8)
        else:
            # Search specific position
            table = f"{position.lower()}_stats"
            query = f"""
                SELECT %s as position, playerid, playername, team, totalpoints, rank
                FROM {table}
                WHERE LOWER(playername) LIKE %s
                ORDER BY totalpoints DESC
            """
            search_pattern = f'%{name}%'
            cur.execute(query, (position, search_pattern))
        
        columns = [desc[0] for desc in cur.description]
        players = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        if not players:
            return jsonify({
                'error': 'Not Found',
                'message': f'No players found matching "{name}"'
                + (f' with position {position}' if position else '')
            }), 404
        
        return jsonify(players)
        
    except Exception as e:
        logger.error(f"Error searching players: {str(e)}")
        raise

# Register the API blueprint
app.register_blueprint(api)

# Root route to handle non-API requests
@app.route('/')
def root():
    return jsonify({
        'message': 'NFL Stats API',
        'endpoints': {
            'search': '/api/search?name={player_name}&position={optional_position}',
            'players_by_position': '/api/players/{position}',
            'teams': '/api/teams',
            'team_players': '/api/teams/{team_code}/players'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)