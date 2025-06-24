import cv2
import numpy as np
import pyzbar.pyzbar as pyzbar
import urllib.request
import serial
import sqlite3
import time
import threading

ESP32_URL = 'http://192.168.113.65/'
arduino = serial.Serial('COM6', 9600, timeout=1)
time.sleep(2)

conn = sqlite3.connect("access_control.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, qr_code TEXT UNIQUE)''')
conn.commit()

cv2.namedWindow("QR Scanner", cv2.WINDOW_AUTOSIZE)
font = cv2.FONT_HERSHEY_PLAIN

prev_qr = ""
last_scan_time = 0
cooldown = 3
update_mode = False

def input_listener():
    global update_mode
    while True:
        cmd = input().strip().lower()
        if cmd == "update":
            print(">> Update mode activated. Scan a new QR code.")
            update_mode = True
            arduino.write(b"UPDATING\n")

threading.Thread(target=input_listener, daemon=True).start()

def check_access(qr_data):
    cursor.execute("SELECT * FROM users WHERE qr_code=?", (qr_data,))
    return cursor.fetchone() is not None

while True:
    try:
        img_resp = urllib.request.urlopen(ESP32_URL + 'cam-hi.jpg', timeout=2)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgnp, -1)
    except Exception as e:
        print(f"Camera error: {e}")
        continue

    decoded_objects = pyzbar.decode(frame)
    current_time = time.time()

    for obj in decoded_objects:
        qr_code = obj.data.decode("utf-8")

        if qr_code != prev_qr and (current_time - last_scan_time) > cooldown:
            prev_qr = qr_code
            last_scan_time = current_time
            print(f"QR Code Detected: {qr_code}")

            if update_mode:
                try:
                    cursor.execute("INSERT OR IGNORE INTO users (qr_code) VALUES (?)", (qr_code,))
                    conn.commit()
                    print(">> QR code added to database.")
                    arduino.write(b"GRANTED\n")
                except Exception as e:
                    print(f"Database update failed: {e}")
                update_mode = False
            else:
                if check_access(qr_code):
                    print("Access Granted")
                    arduino.write(b"GRANTED\n")
                else:
                    print("Access Denied")
                    arduino.write(b"DENIED\n")

        cv2.putText(frame, qr_code, (50, 50), font, 2, (255, 0, 0), 3)
        time.sleep(3)
        prev_qr = ""

    cv2.imshow("QR Scanner", frame)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
conn.close()
arduino.close()
