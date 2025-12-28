from flask import Flask
from flask import request, redirect, url_for
from flask import session, flash, get_flashed_messages
from flask import render_template
from markupsafe import escape

from db import get_db_connection

app = Flask(__name__)
app.secret_key = '123'

@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'GET':
        if 'id' in session:
            first_name = session['fname']
            last_name = session['lname']
            username = session['username']
            return render_template('home.html', username=username, fname=first_name, lname=last_name)
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

        query = f'SELECT player_id, username, first_name, last_name, password FROM players WHERE username="{username}";'
        cursor.execute(query)
        player = cursor.fetchone()

        if player and player['password'] == password:
            session['id'] = player['player_id']
            session['username'] = player['username']
            session['fname'] = player['first_name']
            session['lname'] = player['last_name']
            return redirect(url_for('home'))
        else:
            flash("Username or password is incorrect!")
            return render_template('login.html')
        cursor.close()
        conn.close()
    else:
        session.pop('id', None)
        return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        uname = request.form['username']
        email = request.form['email']
        dob = request.form['dob']
        password = request.form['password']

        valid = True

        validation_query = '''
        SELECT
            EXISTS (
                SELECT 1 FROM players WHERE username = %s 
            ) AS username_taken,
            EXISTS (
                SELECT 1 FROM players WHERE email = %s
            ) AS email_taken;
        '''

        insertion_query = '''
        INSERT INTO players (first_name, last_name, username, email, date_of_birth, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''

        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            cursor.execute(validation_query, (uname, email))
            row = cursor.fetchone()
            username_taken = bool(row['username_taken'])
            email_taken = bool(row['email_taken'])
            if username_taken or email_taken:
                valid = False
            if username_taken:
                flash("Username is taken! Please try a different one.")
            if email_taken:
                flash("Email is associated with an existing account! Please log in.")
        if valid:
            with conn.cursor() as cursor:
                cursor.execute(
                    insertion_query,
                    (fname, lname, uname, email, dob, password)
                )
                flash("Sign up successful! Please log in.")

        conn.commit()
        conn.close()

        if valid: return redirect(url_for('login'))
    return render_template('signup.html')

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
            cursor.close()
            conn.commit()
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

    return render_template(
        'player_profile.html',
        user=username,
        details=profile_details,
        friends=friends
        )

@app.route('/bank')
def bank():
    player_id = session['id']

    conn = get_db_connection()
    cursor = conn.cursor()

    ownership_query = f'''
    SELECT b.account_no, b.account_balance, b.account_type
    FROM bank_accounts b
    INNER JOIN ownership w ON b.account_no = w.account_no
    INNER JOIN players p ON p.player_id = w.player_id
    WHERE p.player_id = {player_id}
    ''' 
    cursor.execute(ownership_query)
    account = cursor.fetchone()

    if not account:
        return redirect(url_for('create_bank_account'))
    else:
        return render_template('bank.html', account=account)

@app.route('/onboarding', methods=["POST", "GET"])
def create_bank_account():
    valid = False
    conn = get_db_connection()
    
    type_query = '''
        SELECT DISTINCT account_type
        FROM bank_accounts;
    '''
    validation_query = '''
        SELECT personal_balance
        FROM players
        WHERE player_id = %s;
    '''
    ba_insertion_query = '''
        INSERT INTO bank_accounts (account_no, account_type, account_balance)
        VALUES (%s, %s, %s);
    '''
    ownership_insertion_query = '''
        INSERT INTO ownership (player_id, account_no)
        VALUES (%s, %s)
    '''
    update_query = '''
        UPDATE players
        SET personal_balance = personal_balance - %s
        WHERE player_id = %s
    '''

    with conn.cursor() as cursor:
        cursor.execute(type_query)
        account_types = cursor.fetchall()

    if request.method == "POST":
        deposit = int(request.form.get('initial_deposit'))
        account_type = request.form.get('account_type')


        with conn.cursor() as cursor:
            player_id = session['id']
            cursor.execute(validation_query, (player_id,))
            row = cursor.fetchone()
            balance = row['personal_balance']
            valid = balance > deposit
    
        if not valid:
            flash("You do not have that much money!")
            return redirect(url_for('create_bank_account'))
        with conn.cursor() as cursor:
            account_no = f'MONEYGAME-{account_type.upper()}-{player_id:05}'
            cursor.execute(ba_insertion_query, (account_no, account_type, deposit))
            cursor.execute(ownership_insertion_query, (player_id, account_no))
            cursor.execute(update_query, (deposit, player_id))
            conn.commit()
            return redirect(url_for('bank'))
    conn.close()
    return render_template('bank_registration.html', account_types=account_types)
if __name__ == "__main__":
    app.run(debug=True)
