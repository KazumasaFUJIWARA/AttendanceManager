import sqlite3
import os

# データベースファイルのパス
db_path = os.path.join(os.path.dirname(__file__), 'Attendance2025.db')

# データベースに接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# テーブル一覧を取得
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=== テーブル一覧 ===")
for table in tables:
    print(f"\nテーブル名: {table[0]}")
    # テーブルの構造を取得
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print("カラム構造:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

# 接続を閉じる
conn.close() 