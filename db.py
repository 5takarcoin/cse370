import pymysql

def get_db_connection():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="money_game",
        port=3306
        cursorclass=pymysql.cursors.DictCursor
    )