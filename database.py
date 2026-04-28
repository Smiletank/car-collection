import sqlite3
import os
from datetime import datetime

DB_PATH = "data/cars.db"

def init_db():
    """初始化数据库"""
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
    
    # 检查并添加缺失的列（兼容旧数据库）
    cursor.execute("PRAGMA table_info(cars)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'series' not in columns:
        cursor.execute('ALTER TABLE cars ADD COLUMN series TEXT')
    if 'code' not in columns:
        cursor.execute('ALTER TABLE cars ADD COLUMN code TEXT')
    
    conn.commit()
    conn.close()

def add_car(brand, model, color, series, code, note, image_path):
    """添加一辆车到数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cars (brand, model, color, series, code, note, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (brand, model, color, series, code, note, image_path))
    conn.commit()
    conn.close()

def get_all_cars():
    """获取所有收藏"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def search_cars(brand=None, model=None):
    """搜索相似车型"""
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
    """删除一辆车"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cars WHERE id = ?', (car_id,))
    conn.commit()
    conn.close()

# 初始化数据库
init_db()
