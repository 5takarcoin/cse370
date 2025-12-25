from flask import Flask
from flask import request, redirect, url_for, session
from flask import render_template
from markupsafe import escape

from db import get_db_connection

app = Flask(__name__)
app.secret_key = '123'

@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        if 'id' in session:
            player_id = session['id']

            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = f'''
            SELECT username 
            FROM players 
            WHERE player_id="{player_id}";
            '''

            cursor.execute(query)
            player = cursor.fetchone()

            cursor.close()
            conn.close()

            username = player['username']
            return render_template('home.html', username=username)
        else:
            return redirect(url_for('login'))
    else:
        if "logout" in request.form:
            session.pop('id', None)
            return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = escape(request.form.get('username'))
        password = escape(request.form.get('password'))

        conn = get_db_connection()
        cursor = conn.cursor()        

        query = f'SELECT player_id, password FROM players WHERE username="{username}";'
        cursor.execute(query)
        player = cursor.fetchone()

        if player and player['password'] == password:
            session['id'] = player['player_id']
            return redirect(url_for('home'))
        else:
            return "Invalid"
        cursor.close()
        conn.close()
    else:
        session.pop('id', None)
        return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = escape(request.form.get('first_name'))
        lname = escape(request.form.get('last_name'))
        uname = escape(request.form.get('username'))
        email = escape(request.form.get('email'))
        dob = escape(request.form.get('dob'))
        password = escape(request.form.get('password'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
        INSERT INTO players (first_name, last_name, username, email, password, date_of_birth)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        print("Dekho", fname, uname, dob, password)
        cursor.execute(sql, (fname, lname, uname, email, password, dob))
        
        conn.commit()        
        cursor.close()
        conn.close()

        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route("/friends", methods=['GET', 'POST'])
def friends():
    player_id = session['id']

    conn = get_db_connection()
    cursor = conn.cursor()
    match = None
    is_self = False

    if request.method == 'POST':
        if 'friend_id' in request.form:
            receiver_id = session['id']
            sender_id = request.form["friend_id"]

            insertion_query = f'''
            INSERT INTO friendships(befriender_id, befriended_id)
            VALUES({sender_id}, {receiver_id})'''
            cursor.execute(insertion_query)

            deletion_query = f'''
            DELETE FROM friend_requests 
            WHERE sender_id = {sender_id} AND receiver_id = {receiver_id}
            '''
            cursor.execute(deletion_query)
            conn.commit()
            cursor.close()
            conn.close()

            return redirect(url_for('friends'))
        else:
            # Check if user is in database
            username = request.form['username']
            sql = f"SELECT player_id, username FROM players WHERE username = '{username}';"
            cursor.execute(sql)
            matches = cursor.fetchone()
            if matches:
                match = True
                receiver_id = matches['player_id']
                if receiver_id == player_id:
                    is_self = True
                else:
                    sql = f"INSERT INTO friend_requests (sender_id, receiver_id) VALUES ({player_id}, {receiver_id});"
                    cursor.execute(sql)
                    conn.commit()
            else:
                match = False

    friendship_query = f'''
    SELECT CONCAT(p.first_name, " ", p.last_name) AS name, p.username
    FROM (
        SELECT befriended_id AS friend_id
        FROM friendships
        WHERE befriender_id = "{player_id}"
        
        UNION

        SELECT befriender_id AS friend_id
        FROM friendships
        WHERE befriended_id = "{player_id}"
    ) AS t

    INNER JOIN players p 
    ON p.player_id = t.friend_id
    ORDER BY p.personal_balance DESC;
    '''
    cursor.execute(friendship_query)
    friends = cursor.fetchall()
    
    frq_query = f'''
    SELECT CONCAT(p.first_name, ' ', p.last_name) as name, p.username, p.player_id
    FROM players p
    INNER JOIN friend_requests frq ON frq.sender_id = p.player_id
    WHERE frq.receiver_id = {player_id}
    '''
    cursor.execute(frq_query)
    requests = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template("friends.html", match=match, is_self=is_self, frn=friends, frq=requests)

@app.route("/player/<username>")
def player_profile(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    profile_query = f'''
    SELECT CONCAT(first_name, " ", last_name) AS name, TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) AS age, personal_balance 
    FROM players 
    WHERE username="{username}";
    '''
    cursor.execute(profile_query)
    profile_details = cursor.fetchone()

    friendship_query = f'''
    SELECT CONCAT(p.first_name, " ", p.last_name) AS name, p.username
    FROM (SELECT befriended_id AS friend_id
    FROM friendships
    WHERE befriender_id = (SELECT player_id FROM players WHERE username = "{username}")
    
    UNION

    SELECT befriender_id AS friend_id
    FROM friendships
    WHERE befriended_id = (SELECT player_id FROM players WHERE username = "{username}")) 
    AS t

    INNER JOIN players p 
    ON p.player_id = t.friend_id
    ORDER BY p.personal_balance DESC;
    '''
    cursor.execute(friendship_query)
    friends = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('player_profile.html', user=username, details=profile_details, friends=friends)

if __name__ == "__main__":
    app.run(debug=True)
