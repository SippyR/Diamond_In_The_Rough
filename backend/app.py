import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

# --- DATABASE CONNECTION ---
# Check if we are on Render (using DATABASE_URL) or local (using .env)
database_url = os.environ.get("DATABASE_URL")

try:
    if database_url:
        # Connect using the single Neon string provided by Render Environment Variables
        conn = psycopg2.connect(database_url)
    else:
        # Fallback for your local development setup
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
except Exception as e:
    print(f"Database connection failed: {e}")

def validate_guess(name, season, position, category, subcategory):
    # 1. Grab all player columns
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        query = """
            SELECT * 
            FROM player_stats 
            WHERE LOWER(name_ascii) = LOWER(%s) 
              AND season = %s 
              AND primary_position = %s;
        """
        cursor.execute(query, (name.strip(), int(season), position.strip().upper()))
        player = cursor.fetchone()

    if not player:
        return {
            "valid": False, 
            "message": f"No record of {name} playing {position.upper()} in {season}."
        }

    # --- 2. Category: Team ---
    if category == "Team":
        player_teams = player['team'].split('/') if player['team'] else []
        target_team = str(subcategory).strip().upper()

        if target_team not in player_teams and target_team != player['team']:
            return {"valid": False, "message": f"{player['name_ascii']} did not play for {target_team} in {season}."}
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT MAX(war) as max_war FROM player_stats 
                WHERE primary_position = %s AND team ILIKE %s;
            """, (position.strip().upper(), f"%{target_team}%"))
            highest_war = float(cursor.fetchone()['max_war'] or 0.0)

        player_war = float(player['war'] or 0.0)
        is_highest = round(player_war, 2) >= round(highest_war, 2)
        percent_of_max = int(round((player_war / highest_war) * 100)) if highest_war > 0 else 100

        return {
            "valid": True,
            "war": round(player_war, 2),
            "mlbam_id": player.get('mlbam_id'),
            "is_highest_war": is_highest,
            "percent_of_max": percent_of_max,
            "message": f"Correct! {player['name_ascii']} played for {target_team} in {season}."
        }

    # --- 3. Category: Statistics ---
    else:
        # Map the DB column and enforce the correct data type for clean text formatting
        stat_map = {
            "HR": {"col": "hr", "type": int},
            "RBI": {"col": "rbi", "type": int},
            "H": {"col": "h", "type": int},
            "SB": {"col": "sb", "type": int},
            "R": {"col": "r", "type": int},
            "2B": {"col": "2b", "type": int},
            "W": {"col": "w", "type": int},
            "SV": {"col": "sv", "type": int},
            "SO_P": {"col": "so.1", "type": int},
            "wRC+": {"col": "wRC+", "type": int}, 
            "WAR": {"col": "war", "type": float},
            "IP": {"col": "ip", "type": float}
        }
        
        stat_config = stat_map.get(category)
        
        if not stat_config:
            return {"valid": False, "message": f"Unknown category: {category}"}

        db_column = stat_config["col"]
        cast_type = stat_config["type"]

        # Parse the required stat according to its type
        required_stat = cast_type(subcategory)
        
        # Safely convert the player's stat (casting to float first handles edge cases 
        # where the DB passes '150.0' strings to an int conversion)
        raw_val = player[db_column] or 0
        if cast_type == float:
            player_stat = round(float(raw_val), 1) if category != "WAR" else round(float(raw_val), 2)
        else:
            player_stat = int(float(raw_val))

        if player_stat < required_stat:
            return {"valid": False, "message": f"{player['name_ascii']} only had {player_stat} {category} in {season} (needed {required_stat}+)."}
        
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"""
                SELECT MAX(war) as max_war FROM player_stats 
                WHERE primary_position = %s AND "{db_column}" >= %s;
            """, (position.strip().upper(), required_stat))
            highest_war = float(cursor.fetchone()['max_war'] or 0.0)

        player_war = float(player['war'] or 0.0)
        is_highest = round(player_war, 2) >= round(highest_war, 2)
        percent_of_max = int(round((player_war / highest_war) * 100)) if highest_war > 0 else 100

        return {
            "valid": True,
            "war": round(player_war, 2),
            "mlbam_id": player.get('mlbam_id'),
            "is_highest_war": is_highest,
            "percent_of_max": percent_of_max,
            "message": f"Correct! {player['name_ascii']} had {player_stat} {category} in {season}."
        }

app = Flask(__name__)
CORS(app) # Allows your frontend to talk to this backend

@app.route('/api/validate', methods=['POST'])
def validate():
    # 1. Parse the incoming JSON from the frontend
    data = request.get_json()
    
    # 2. Extract variables
    name = data.get('name')
    season = data.get('season')
    position = data.get('position')
    category = data.get('category')
    subcategory = data.get('subcategory')
    
    # 3. Run your database validation
    result = validate_guess(name, season, position, category, subcategory)
    
    # 4. Send the result back to the frontend as JSON
    return jsonify(result)

@app.route('/api/optimal', methods=['POST'])
def get_optimal_lineup():
    game_config = request.json
    optimal_lineup = {}
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            for pos, req in game_config.items():
                cat = req['cat']
                sub = req['sub']
                
                if cat == "Team":
                    # Using NULLS LAST prevents empty WAR rows from accidentally floating to the top
                    cursor.execute("""
                        SELECT name_ascii, war, season FROM player_stats 
                        WHERE primary_position = %s AND team ILIKE %s
                        ORDER BY CAST(NULLIF(CAST(war AS TEXT), '') AS FLOAT) DESC NULLS LAST LIMIT 1;
                    """, (pos.strip().upper(), f"%{str(sub).strip().upper()}%"))
                else:
                    stat_map = {"HR": "hr", "RBI": "rbi", "H": "h", "SB": "sb", "R": "r", "2B": "2b", "W": "w", "SV": "sv", "SO_P": "so.1", "wRC+": "wRC+", "WAR": "war", "IP": "ip"}
                    db_column = stat_map.get(cat)
                    
                    # Safely cast the column to TEXT, convert empty strings to NULL, and then cast to FLOAT
                    cursor.execute(f"""
                        SELECT name_ascii, war, season FROM player_stats 
                        WHERE primary_position = %s 
                          AND CAST(NULLIF(CAST("{db_column}" AS TEXT), '') AS FLOAT) >= %s
                        ORDER BY CAST(NULLIF(CAST(war AS TEXT), '') AS FLOAT) DESC NULLS LAST LIMIT 1;
                    """, (pos.strip().upper(), float(sub)))
                
                best = cursor.fetchone()
                if best:
                    # Format WAR neatly to 2 decimal places
                    safe_war = round(float(best['war'] or 0.0), 2)
                    optimal_lineup[pos] = f"{best['name_ascii']} ('{str(best['season'])[2:]}) - {safe_war} WAR"
                else:
                    optimal_lineup[pos] = "No player found"
                    
        # Commit the transaction so the connection stays clean
        conn.commit()
        return jsonify(optimal_lineup)
        
    except Exception as e:
        # If it fails again, roll back the connection to prevent a lockup and print the exact error to your terminal
        conn.rollback()
        print(f"Optimal Lineup Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/autocomplete', methods=['GET'])
def autocomplete():
    query = request.args.get('q', '')
    
    # Only search if they've typed at least 2 characters to save database load
    if len(query) < 2:
        return jsonify({"players": []})
        
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            # SELECT DISTINCT ensures we don't get 20 rows of "Albert Pujols" for his 20 seasons
            cursor.execute("""
                SELECT DISTINCT name_ascii 
                FROM player_stats 
                WHERE name_ascii ILIKE %s 
                ORDER BY name_ascii 
                LIMIT 8;
            """, (f"%{query}%",))
            
            results = cursor.fetchall()
            players = [row['name_ascii'] for row in results]
            
        return jsonify({"players": players})
        
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Starts the local server on port 5000
    app.run(debug=True, port=5000)