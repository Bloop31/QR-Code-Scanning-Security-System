import sqlite3

conn = sqlite3.connect('access_control.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM users")
conn.commit()

print("All data deleted from 'users' table.")

conn.close()
