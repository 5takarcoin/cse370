from flask import Flask, render_template
from db import get_db_connection

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello my name is Human!"

@app.route("/users")
def get_users():
    connection = get_db_connection()
    cursor = connection.cursor()

    sql = "show tables"
    cursor.execute(sql)
    users = cursor.fetchall()

    print("================================= ****")
    tablename = users[0]['Tables_in_moneygame']

    
    print("=================================")

    sql = "describe " + tablename;
    cursor.execute(sql)
    users = cursor.fetchall()

    cursor.close()
    connection.close()

    # return jsonify(users)

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



if __name__ == "__main__":
    app.run(debug=True)