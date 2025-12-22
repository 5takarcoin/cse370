from flask import Flask, render_template, request, redirect
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello my name is Human!"

@app.route("/users")
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = '''
    SELECT ga.game_name, gr.game_genre
    FROM games ga
    JOIN game_genres gr ON gr.game_id = ga.game_id
    GROUP BY ga.game_name;
    '''
    cursor.execute(sql)
    users = cursor.fetchall()

    
    
    cursor.close()
    conn.close()


    print("=================================")
    print(users)
    print("=================================")

    return "Connecting DB"

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')

        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)        

        sql = "SELECT * FROM players WHERE username = %s"

        cursor.execute(sql, (user))
        result = cursor.fetchone()
        if result:
            first_name = result['first_name']
            stored_hash = result['password']

            


            if stored_hash == pw:
                print(f"Success! Welcome {first_name}")
                return render_template("welcome.html", result=result)
                
            else:
                print("Failed: Wrong password.")
                return render_template("login.html", error="Invalid password")
        else:
            print("Failed: Username not found.")
            return render_template("login.html", error="User does not exist")

        cursor.close()
        connection.close()

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

@app.route('/bank')
def bank():
    player_id = 1
    pass
if __name__ == "__main__":
    app.run(debug=True)
