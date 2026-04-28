import sqlite3
import os
from datetime import datetime

# Streamlit Cloud 用 /tmp 目录，本地用 data 目录
if os.path.exists('/mount/src'):
    DB_PATH = "/tmp/cars.db"
    IMAGE_DIR = "/tmp/images"
else:
    DB_PATH = "data/cars.db"
    IMAGE_DIR = "data/images"

os.makedirs(IMAGE_DIR, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            model TEXT,
            color TEXT,
            series TEXT,
            code TEXT,
            note TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def add_car(brand, model, color, series, code, note, image_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cars (brand, model, color, series, code, note, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (brand, model, color, series, code, note, image_path))
    conn.commit()
    conn.close()

def get_all_cars():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_cars(brand=None, model=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "SELECT * FROM cars WHERE 1=1"
    params = []
    if brand:
        query += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    if model:
        query += " AND model LIKE ?"
        params.append(f"%{model}%")
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_car(car_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cars WHERE id = ?', (car_id,))
    conn.commit()
    conn.close()

init_db()
