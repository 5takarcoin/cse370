import pymysql

def get_db_connection():
    return pymysql.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="cse370",
        port=3306
    )
