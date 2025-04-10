# -*- coding: utf-8 -*-
import sqlite3
import os

# データベースファイルのパス
db_path = os.path.join(os.path.dirname(__file__), 'Attendance2025.db')

# データベースに接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# テーブル作成
cursor.execute('''
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    core_time_1_day INTEGER DEFAULT 0,  -- 1:月曜 2:火曜 ... 7:日曜
    core_time_1_period INTEGER DEFAULT 0,  -- 1:1限 2:2限 ... 6:6限
    core_time_2_day INTEGER DEFAULT 0,
    core_time_2_period INTEGER DEFAULT 0,
    core_time_violations INTEGER DEFAULT 0
)
''')

cursor.execute('''
CREATE TABLE attendance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    entry_time DATETIME,
    exit_time DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

cursor.execute('''
CREATE TABLE current_status (
    student_id TEXT PRIMARY KEY,
    entry_time DATETIME,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

cursor.execute('''
CREATE TABLE alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    alert_date DATE,
    alert_period INTEGER,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
)
''')

# 変更を保存して接続を閉じる
conn.commit()
conn.close()

print("データベースの作成が完了しました。") 