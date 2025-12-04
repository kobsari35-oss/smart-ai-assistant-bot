import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def init_db():
    """
    បង្កើត Table ដោយស្វ័យប្រវត្តិពេលចាប់ផ្តើម Bot
    """
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Table Users
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            premium BOOLEAN DEFAULT FALSE,
            expiry DATE,
            usage_count INTEGER DEFAULT 0,
            last_active_date DATE DEFAULT CURRENT_DATE,
            daily_limit INTEGER DEFAULT 0
        );
    """)
    
    # 2. Table Config (Global Limit)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key_name VARCHAR(50) PRIMARY KEY,
            value_int INTEGER
        );
    """)
    
    # ដាក់ Global Limit 15 ជាលំនាំដើម បើមិនទាន់មាន
    cur.execute("""
        INSERT INTO settings (key_name, value_int) 
        VALUES ('global_limit', 15) 
        ON CONFLICT DO NOTHING;
    """)
    
    cur.close()
    conn.close()
    print("✅ Database initialized (PostgreSQL).")

def get_global_limit():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value_int FROM settings WHERE key_name = 'global_limit'")
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else 15

def set_global_limit(limit: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE settings SET value_int = %s WHERE key_name = 'global_limit'", (limit,))
    cur.close()
    conn.close()

def get_user_status(user_id):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if user exists
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    
    today = datetime.now().date()
    
    if not user:
        # Create new user
        cur.execute(
            "INSERT INTO users (user_id, last_active_date) VALUES (%s, %s) RETURNING *",
            (user_id, today)
        )
        user = cur.fetchone()
    
    # Convert DB types to Python Dict format compatible with old code
    # Check Date Reset
    last_date = user['last_active_date']
    if last_date < today:
        cur.execute("UPDATE users SET usage_count = 0, last_active_date = %s WHERE user_id = %s", (today, user_id))
        user['usage_count'] = 0
        user['last_active_date'] = today
    
    # Check Expiry
    if user['premium'] and user['expiry']:
        # Note: 'expiry' from DB is a date object
        if user['expiry'] < today:
            cur.execute("UPDATE users SET premium = FALSE, expiry = NULL, daily_limit = 0 WHERE user_id = %s", (user_id,))
            user['premium'] = False
            user['expiry'] = None
            user['daily_limit'] = 0

    cur.close()
    conn.close()

    # Format output to match old JSON structure for handlers
    expiry_str = "Forever" if user['expiry'] is None and user['premium'] else str(user['expiry']) if user['expiry'] else None
    
    return {
        "premium": user['premium'],
        "expiry": expiry_str,
        "usage": user['usage_count'],
        "daily_limit": user['daily_limit']
    }

def add_user(user_id):
    # Just to ensure user exists
    get_user_status(user_id)

def check_limit(user_id):
    user = get_user_status(user_id)
    global_limit = get_global_limit()
    
    current_limit = user['daily_limit']
    if current_limit == 0:
        current_limit = global_limit
        
    # If Unlimited
    if current_limit == -1:
        # Just increment stat, return True
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET usage_count = usage_count + 1 WHERE user_id = %s", (user_id,))
        cur.close()
        conn.close()
        return True
        
    if user['usage'] < current_limit:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET usage_count = usage_count + 1 WHERE user_id = %s", (user_id,))
        cur.close()
        conn.close()
        return True
    
    return False

def set_premium(user_id, duration_days=None, limit=0):
    conn = get_connection()
    cur = conn.cursor()
    
    # Ensure user exists first
    cur.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING", (user_id,))
    
    if duration_days:
        expiry_date = datetime.now().date() + timedelta(days=duration_days)
        cur.execute(
            "UPDATE users SET premium = TRUE, daily_limit = %s, expiry = %s WHERE user_id = %s",
            (limit, expiry_date, user_id)
        )
    else:
        # Forever (NULL expiry)
        cur.execute(
            "UPDATE users SET premium = TRUE, daily_limit = %s, expiry = NULL WHERE user_id = %s",
            (limit, user_id)
        )
        
    cur.close()
    conn.close()

def remove_user_premium(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET premium = FALSE, expiry = NULL, daily_limit = 0 WHERE user_id = %s",
        (user_id,)
    )
    cur.close()
    conn.close()

def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]