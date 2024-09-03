import mysql.connector


mydb = mysql.connector.connect(
    user="root",
    passwd = "password123",
    host="127.0.0.1",
    port=3306,
    auth_plugin='mysql_native_password',
)

my_cursor = mydb.cursor(buffered=True)

#my_cursor.execute("CREATE DATABASE our_users")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)