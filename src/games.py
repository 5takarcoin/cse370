from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from db import get_db_connection

games = Blueprint("games", __name__, static_folder="static", template_folder="templates")

def normalize_game_name(str):
    return str.lower().replace(" ", "_").replace("-", "_").replace("'", "_")

def create_a_session_for_game(game_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    player_id = session['id']

    cursor.execute(
        """
        SELECT MAX(session_no) AS max_session_no
        FROM game_sessions
        WHERE game_id = %s AND player_id = %s
        """,
        (game_id, player_id)
    )

    row = cursor.fetchone()
    next_session_no = (row["max_session_no"] or 0) + 1

    cursor.execute(
        """
        INSERT INTO game_sessions
        (game_id, player_id, session_no, score)
        VALUES (%s, %s, %s, %s)
        """,
        (game_id, player_id, next_session_no, 0)
    )

    query = "SELECT personal_balance FROM players WHERE player_id = %s;"

    cursor.execute(query, (player_id,))
    result = cursor.fetchone()
    
    balance = result['personal_balance'] if result else 0


    conn.commit()
    cursor.close()
    conn.close()

    return next_session_no, balance


@games.route("/", methods=['GET'])
def games_home():
    conn = get_db_connection()
    cursor = conn.cursor()        

    query = """
    SELECT
        g.game_id,
        g.game_name,
        GROUP_CONCAT(gg.game_genre ORDER BY gg.game_genre SEPARATOR ', ') AS genres
    FROM games g
    LEFT JOIN game_genres gg ON g.game_id = gg.game_id
    GROUP BY g.game_id, g.game_name;
"""

    cursor.execute(query)
    games = cursor.fetchall()

    cursor.close()
    conn.close()

    game_session_id = session.get("game_session_id")
    player_id = session.get("id")

    for game in games:
        normalized = normalize_game_name(game["game_name"])
        game["normalized_name"] = normalized

    return render_template('games_home.html', games=games, game_session_id=game_session_id, player_id=player_id)


@games.route("/coin_toss")
def coin_toss():
    session_id, accbalance = create_a_session_for_game(0)
    if accbalance < 0:
        flash("You are out of money :(")
        return redirect(url_for('home'))
    return render_template("coin_toss.html", session_id=session_id, accbalance=accbalance)


@games.route("/rock_paper_scissors")
def rock_paper_scissors():
    session_id, accbalance = create_a_session_for_game(1)
    if accbalance < 0:
        flash("You are out of money :(")
        return redirect(url_for('home'))
    return render_template("rock_paper_scissors.html", session_id=session_id, accbalance=accbalance)


@games.route("/spin_the_wheel")
def spin_the_wheel():
    session_id, accbalance = create_a_session_for_game(2)
    if accbalance < 0:
        flash("You are out of money :(")
        return redirect(url_for('home'))
    return render_template("spin_the_wheel.html", session_id=session_id, accbalance=accbalance)



@games.route("/start_session", methods=["POST"])
def start_session():

    session_query = "SELECT MAX(session_no) AS max_session_no FROM game_sessions"

    insert_session_query = """
    INSERT INTO game_sessions
    (game_id, player_id, session_no, score)
    VALUES (%s, %s, %s, %s)
    """

    conn = get_db_connection()
    cursor = conn.cursor()        
    cursor.execute(session_query)
    
    player_id = session['id']
    session_id = cursor.fetchone()["max_session_no"] + 1
    game_id = 69

    # cursor.execute(query, (game_id, player_id, sid, 0))
    # conn.commit()

    cursor.close()
    conn.close()

    session['game_session_id'] = session_id;

    return redirect('/games')

@games.route("/end_session", methods=["POST"])
def end_session():

    session.pop('game_session_id', None)

    return redirect('/games')

def get_game_id(name):
    conn = get_db_connection()
    cursor = conn.cursor()  

    cursor.execute("SELECT * FROM games")
    games = cursor.fetchall()
    
    cursor.close()
    conn.close()

    game_dict = {normalize_game_name(g['game_name']): (g['game_id'], g['game_name']) for g in games}

    return game_dict.get(name)

@games.route("/<game_name>/leaderboard")
def leaderboard(game_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    game_id, original_name = get_game_id(game_name)

    query = """
        SELECT 
            gs.player_id,
            p.username,
            CONCAT(p.first_name, ' ', p.last_name) AS fullname,
            MAX(gs.score) AS max_score
        FROM game_sessions gs
        INNER JOIN players p ON gs.player_id = p.player_id
        WHERE gs.game_id = %s
        GROUP BY gs.player_id, p.username, p.first_name, p.last_name
        ORDER BY max_score DESC;
    """

    cursor.execute(query, (game_id,))

    top_players = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("leaderboard.html", game_name=original_name, top_players=top_players)

@games.route("/leaderboard")
def leaderboard_all():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''SELECT 
        s.player_id,
        CONCAT(p.first_name, ' ', p.last_name) AS fullname,
        p.username,
        MAX(s.score) AS max_score,
        g.game_name
    FROM game_sessions s
    JOIN games g ON s.game_id = g.game_id
    JOIN players p ON s.player_id = p.player_id
    GROUP BY s.player_id, g.game_name
    ORDER BY max_score DESC;
    '''

    cursor.execute(query)

    top_players = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("leaderboard.html", game_name="All", top_players=top_players)

@games.route("/history/<player>")
def history(player):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''SELECT 
        gs.session_no,
        gs.session_start_time,
        gs.session_end_time,
        gs.score,
        g.game_id,
        g.game_name,
        p.username,
        CONCAT(p.first_name, ' ', p.last_name) AS player_name
    FROM game_sessions gs
    JOIN games g ON gs.game_id = g.game_id
    JOIN players p ON gs.player_id = p.player_id
    WHERE gs.player_id = %s
    ORDER BY gs.session_start_time DESC;
    '''

    cursor.execute(query, (session['id'],))

    sessions = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("history.html", sessions=sessions)

@games.route("/save_score", methods=["POST"])
def save_coin_score():
    session_no = int(request.form['session_id'])
    score = int(request.form['score'])
    game_id = int(request.form['game_id'])
    player_id = session['id']  

    balance = float(request.form['balance'])

    print("balance")

    conn = get_db_connection()
    cursor = conn.cursor()

    update_query = '''
        UPDATE game_sessions
        SET session_end_time = NOW(), score = %s
        WHERE game_id = %s AND player_id = %s AND session_no = %s
    '''

    balance_query = "UPDATE players SET personal_balance = %s WHERE player_id = %s"
    cursor.execute(balance_query, (balance, player_id))
    conn.commit()

    cursor.execute(update_query, (score, game_id, player_id, session_no))
    conn.commit()

    cursor.close()
    conn.close()
    if balance < 0:
        flash("You are out of money :(", "danger")
    else:
        flash("Game session saved successfully!", "success")
    return redirect(url_for('home'))
