from flask import Flask, request, render_template
from db import get_db_connection

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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
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