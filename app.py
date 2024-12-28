from flask import Flask, jsonify
from database import get_db_connection

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "Welcome to NFL Stats API"})

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 