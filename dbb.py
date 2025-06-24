import sqlite3

conn = sqlite3.connect('access_control.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        qr_code TEXT UNIQUE NOT NULL
    )
""")

qr_codes = ["upi://pay?pa=9315220389@pthdfc&pn=RUPIN%20GUPTA"]

for qr in qr_codes:
    try:
        cursor.execute("INSERT INTO users (qr_code) VALUES (?)", (qr,))
    except sqlite3.IntegrityError:
        print(f"QR code '{qr}' already exists, skipping.")

conn.commit()
conn.close()
print("All QR codes added.")
