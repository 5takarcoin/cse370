from flask import Flask, render_template, request, redirect
from db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

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
        cursor = connection.cursor()        

        sql = "SELECT first_name, password FROM players WHERE username = %s"

        cursor.execute(sql, (user))
        result = cursor.fetchone()
        if result:
            stored_hash = result['password']
            first_name = result['first_name']

            if check_password_hash(stored_hash, pw):
                print(f"Success! Welcome {first_name}")
                return f"Welcome {first_name}!" 
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
        unhashed_password = request.form.get('password')
        password = generate_password_hash(unhashed_password) 

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
    conn = get_db_connection()
    cursor = conn.cursor()
    match = None
    if request.method == 'POST':
        # Check if user is in database
        username = request.form['username']
        sql = f"SELECT username FROM players WHERE username = '{username}'"
        cursor.execute(sql)
        matches = cursor.fetchall()
        if len(matches) == 1:
            match = True
        else:
            match = False
    cursor.close()
    conn.close()
    return render_template("friends.html", match=match)

if __name__ == "__main__":
    app.run(debug=True)
