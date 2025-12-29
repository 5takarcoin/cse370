from flask import Blueprint, render_template
from db import get_db_connection

games = Blueprint("games", __name__, static_folder="static", template_folder="templates")

def normalize_game_name(str):
    return str.lower().replace(" ", "_").replace("-", "_").replace("'", "_")

@games.route("/", methods=['GET'])
def games_home():
    conn = get_db_connection()
    cursor = conn.cursor()        

    query = "SELECT * from games;"

    cursor.execute(query)
    games = cursor.fetchall()
    cursor.close()
    conn.close()

    for game in games:
        normalized = normalize_game_name(game["game_name"])
        game["normalized_name"] = normalized

    print("Meow", games)

    return render_template('games_home.html', games=games)

@games.route("/coin_toss")
def coin_toss():
    return render_template("coin_toss.html")

@games.route("/rock_paper_scissors")
def rock_paper_scissors():
    return render_template("rock_paper_scissors.html")
