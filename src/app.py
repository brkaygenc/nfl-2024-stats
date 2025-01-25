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
                    playerid,
                    'QB' as position,
                    team,
                    passingyards as passing_yards,
                    passingtds as passing_touchdowns,
                    interceptions,
                    rushingyards as rushing_yards,
                    rushingtds as rushing_touchdowns,
                    totalpoints as total_points
                FROM qb_stats
                ORDER BY totalpoints DESC
            """
        elif position == 'RB':
            query = """
                SELECT 
                    playername as name,
                    playerid,
                    'RB' as position,
                    team,
                    rushingyards as rushing_yards,
                    rushingtds as rushing_touchdowns,
                    receptions,
                    receivingyards as receiving_yards,
                    receivingtds as receiving_touchdowns,
                    totalpoints as total_points
                FROM rb_stats
                ORDER BY totalpoints DESC
            """
        elif position in ['WR', 'TE']:
            query = f"""
                SELECT 
                    playername as name,
                    playerid,
                    '{position}' as position,
                    team,
                    receivingyards as receiving_yards,
                    receptions,
                    targets,
                    receivingtds as receiving_touchdowns,
                    totalpoints as total_points
                FROM {position.lower()}_stats
                ORDER BY totalpoints DESC
            """
        elif position == 'K':
            query = """
                SELECT 
                    playername as name,
                    playerid,
                    'K' as position,
                    team,
                    fieldgoals as field_goals,
                    fieldgoalattempts as field_goals_attempted,
                    extrapoints as extra_points,
                    extrapointattempts as extra_points_attempted,
                    totalpoints as total_points
                FROM k_stats
                ORDER BY totalpoints DESC
            """
        elif position in ['LB', 'DL', 'DB']:
            query = f"""
                SELECT 
                    playername as name,
                    playerid,
                    '{position}' as position,
                    team,
                    tackles,
                    sacks,
                    interceptions,
                    passes_defended,
                    forced_fumbles,
                    tackles_tfl as tackles_for_loss,
                    totalpoints as total_points
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

@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = """
            SELECT team_code, team_name, division
            FROM teams
            ORDER BY division, team_name
        """
        
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        teams = []
        for row in results:
            team = {}
            for i, value in enumerate(row):
                team[columns[i]] = value
            teams.append(team)
            
        return jsonify(teams), 200
        
    except Exception as e:
        logger.error(f"Error fetching teams: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/api/team/<team_code>/players', methods=['GET'])
def get_team_players(team_code):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get all players from all position tables for the given team
        query = """
            SELECT playername as name, 'QB' as position, totalpoints as total_points
            FROM qb_stats WHERE team = %s
            UNION ALL
            SELECT playername as name, 'RB' as position, totalpoints as total_points
            FROM rb_stats WHERE team = %s
            UNION ALL
            SELECT playername as name, 'WR' as position, totalpoints as total_points
            FROM wr_stats WHERE team = %s
            UNION ALL
            SELECT playername as name, 'TE' as position, totalpoints as total_points
            FROM te_stats WHERE team = %s
            UNION ALL
            SELECT playername as name, 'K' as position, totalpoints as total_points
            FROM k_stats WHERE team = %s
            UNION ALL
            SELECT playername as name, 'LB' as position, totalpoints as total_points
            FROM lb_stats WHERE team = %s
            UNION ALL
            SELECT playername as name, 'DL' as position, totalpoints as total_points
            FROM dl_stats WHERE team = %s
            UNION ALL
            SELECT playername as name, 'DB' as position, totalpoints as total_points
            FROM db_stats WHERE team = %s
            ORDER BY total_points DESC
        """
        
        cur.execute(query, [team_code] * 8)  # Pass team_code 8 times for each UNION
        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        players = []
        for row in results:
            player = {}
            for i, value in enumerate(row):
                if isinstance(value, Decimal):
                    player[columns[i]] = float(value)
                else:
                    player[columns[i]] = value
            players.append(player)
            
        return jsonify(players), 200
        
    except Exception as e:
        logger.error(f"Error fetching players for team {team_code}: {str(e)}")
        return jsonify({
            'error': 'Database error',
            'message': str(e)
        }), 500
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

@app.route('/api/search', methods=['GET'])
def search_players():
    try:
        name = request.args.get('name', '').strip().lower()
        position = request.args.get('position', '').strip().upper()
        
        if not name:
            return jsonify({
                'error': 'Missing parameter',
                'message': 'Name parameter is required'
            }), 400

        valid_positions = {'QB', 'RB', 'WR', 'TE', 'K', 'LB', 'DL', 'DB'}
        if position and position not in valid_positions:
            return jsonify({
                'error': 'Invalid position',
                'message': f"Position must be one of: {', '.join(sorted(valid_positions))}",
                'provided': position
            }), 400
            
        conn = get_db_connection()
        cur = conn.cursor()
        
        # If no position specified, search across all positions
        if not position:
            query = """
                WITH all_players AS (
                    SELECT 
                        playername as name,
                        playerid,
                        'QB' as position,
                        team,
                        passingyards as passing_yards,
                        passingtds as passing_touchdowns,
                        interceptions,
                        rushingyards as rushing_yards,
                        rushingtds as rushing_touchdowns,
                        totalpoints as total_points
                    FROM qb_stats
                    WHERE LOWER(playername) LIKE %s
                    UNION ALL
                    SELECT 
                        playername as name,
                        playerid,
                        'RB' as position,
                        team,
                        rushingyards as rushing_yards,
                        rushingtds as rushing_touchdowns,
                        receptions,
                        receivingyards as receiving_yards,
                        receivingtds as receiving_touchdowns,
                        totalpoints as total_points
                    FROM rb_stats
                    WHERE LOWER(playername) LIKE %s
                    UNION ALL
                    SELECT 
                        playername as name,
                        playerid,
                        'WR' as position,
                        team,
                        receivingyards as receiving_yards,
                        receptions,
                        targets,
                        receivingtds as receiving_touchdowns,
                        NULL as other_stats,
                        totalpoints as total_points
                    FROM wr_stats
                    WHERE LOWER(playername) LIKE %s
                    UNION ALL
                    SELECT 
                        playername as name,
                        playerid,
                        'TE' as position,
                        team,
                        receivingyards as receiving_yards,
                        receptions,
                        targets,
                        receivingtds as receiving_touchdowns,
                        NULL as other_stats,
                        totalpoints as total_points
                    FROM te_stats
                    WHERE LOWER(playername) LIKE %s
                    UNION ALL
                    SELECT 
                        playername as name,
                        playerid,
                        'K' as position,
                        team,
                        fieldgoals as field_goals,
                        fieldgoalattempts as field_goals_attempted,
                        extrapoints as extra_points,
                        extrapointattempts as extra_points_attempted,
                        NULL as other_stats,
                        totalpoints as total_points
                    FROM k_stats
                    WHERE LOWER(playername) LIKE %s
                    UNION ALL
                    SELECT 
                        playername as name,
                        playerid,
                        pos.position,
                        team,
                        tackles,
                        sacks,
                        interceptions,
                        passes_defended,
                        forced_fumbles,
                        totalpoints as total_points
                    FROM (
                        SELECT 'LB' as position, * FROM lb_stats
                        UNION ALL
                        SELECT 'DL' as position, * FROM dl_stats
                        UNION ALL
                        SELECT 'DB' as position, * FROM db_stats
                    ) pos
                    WHERE LOWER(playername) LIKE %s
                )
                SELECT * FROM all_players
                ORDER BY total_points DESC
            """
            search_pattern = f"%{name}%"
            cur.execute(query, [search_pattern] * 6)
        else:
            # Position-specific queries (existing implementation)
            if position == 'QB':
                query = """
                    SELECT 
                        playername as name,
                        playerid,
                        'QB' as position,
                        team,
                        passingyards as passing_yards,
                        passingtds as passing_touchdowns,
                        interceptions,
                        rushingyards as rushing_yards,
                        rushingtds as rushing_touchdowns,
                        totalpoints as total_points
                    FROM qb_stats
                    WHERE LOWER(playername) LIKE %s
                    ORDER BY totalpoints DESC
                """
            elif position == 'RB':
                query = """
                    SELECT 
                        playername as name,
                        playerid,
                        'RB' as position,
                        team,
                        rushingyards as rushing_yards,
                        rushingtds as rushing_touchdowns,
                        receptions,
                        receivingyards as receiving_yards,
                        receivingtds as receiving_touchdowns,
                        totalpoints as total_points
                    FROM rb_stats
                    WHERE LOWER(playername) LIKE %s
                    ORDER BY totalpoints DESC
                """
            elif position in ['WR', 'TE']:
                query = f"""
                    SELECT 
                        playername as name,
                        playerid,
                        '{position}' as position,
                        team,
                        receivingyards as receiving_yards,
                        receptions,
                        targets,
                        receivingtds as receiving_touchdowns,
                        totalpoints as total_points
                    FROM {position.lower()}_stats
                    WHERE LOWER(playername) LIKE %s
                    ORDER BY totalpoints DESC
                """
            elif position == 'K':
                query = """
                    SELECT 
                        playername as name,
                        playerid,
                        'K' as position,
                        team,
                        fieldgoals as field_goals,
                        fieldgoalattempts as field_goals_attempted,
                        extrapoints as extra_points,
                        extrapointattempts as extra_points_attempted,
                        totalpoints as total_points
                    FROM k_stats
                    WHERE LOWER(playername) LIKE %s
                    ORDER BY totalpoints DESC
                """
            elif position in ['LB', 'DL', 'DB']:
                query = f"""
                    SELECT 
                        playername as name,
                        playerid,
                        '{position}' as position,
                        team,
                        tackles,
                        sacks,
                        interceptions,
                        passes_defended,
                        forced_fumbles,
                        tackles_tfl as tackles_for_loss,
                        totalpoints as total_points
                    FROM {position.lower()}_stats
                    WHERE LOWER(playername) LIKE %s
                    ORDER BY totalpoints DESC
                """
            search_pattern = f"%{name}%"
            cur.execute(query, (search_pattern,))

        columns = [desc[0] for desc in cur.description]
        results = cur.fetchall()
        
        # Convert to list of dictionaries with proper types
        players = []
        for row in results:
            player = {}
            for i, value in enumerate(row):
                if isinstance(value, (int, float, Decimal)):
                    player[columns[i]] = float(value) if isinstance(value, Decimal) else value
                else:
                    player[columns[i]] = value
            players.append(player)
            
        return jsonify(players), 200
        
    except Exception as e:
        logger.error(f"Error searching players: {str(e)}")
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