import sqlite3
import os
from typing import List, Dict, Any

DATABASE_URL = "attendance.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn 