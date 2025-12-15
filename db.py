import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="moneygame",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor
    )