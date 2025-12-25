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
        connection.close()
    else:
        session.pop('id', None)
        return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form.get('first_name')
        lname = request.form.get('last_name')
        uname = request.form.get('username')
        email = request.form.get('email')
        dob   = request.form.get('dob')
        password = request.form.get('password')
        # password = generate_password_hash(unhashed_password) 

        connection = get_db_connection()
        cursor = connection.cursor()
        
        sql = """
        INSERT INTO players (first_name, last_name, username, email, password, date_of_birth)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        print("Dekho", fname, uname, dob, password)
        cursor.execute(sql, (fname, lname, uname, email, password, dob))
        connection.commit()        
        cursor.close()
        connection.close()

        return redirect('/login')
    return render_template("signup.html")

@app.route("/friends", methods=['GET', 'POST'])
def friends():
    player_id = 1
    conn = get_db_connection()
    cursor = conn.cursor()
    match = None
    is_self = False
    if request.method == 'POST':
        # Check if user is in database
        username = request.form['username']
        sql = f"SELECT player_id, username FROM players WHERE username = '{username}';"
        cursor.execute(sql)
        matches = cursor.fetchall()
        if len(matches) == 1:
            match = True
            receiver_id = matches[0][0]
            if receiver_id == player_id:
                is_self = True
            else:
                sql = f"INSERT INTO friend_requests (sender_id, receiver_id) VALUES ({player_id}, {receiver_id});"
                cursor.execute(sql)
                conn.commit()
        else:
            match = False
    
    # Show friend requests
    sql = f'''
    SELECT CONCAT(p.first_name, ' ', p.last_name) FROM players p
    INNER JOIN friend_requests frq ON frq.sender_id = p.player_id
    WHERE frq.receiver_id = {player_id}
    '''
    cursor.execute(sql)
    incoming_friend_requests = cursor.fetchall()

    
    # # Show friends
    # sql = f'''
    # SELECT CONCAT(p.first_name, ' ', p.last_name) FROM friendships frn
    # INNER JOIN players p1 ON frn.befriender_id = p1.player_id
    # INNER JOIN players p2 ON frn.befriended_id = p2.player_id
    # WHERE frn.befriender_id = {player_id} or frn.befriended_id = {player_id}
    # '''
    cursor.execute(sql)
    # friends = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template("friends.html", match=match, is_self=is_self, incoming_friend_requests = incoming_friend_requests)

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
