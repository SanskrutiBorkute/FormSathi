import os
import sqlite3
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), 'formsaathi.db')

def get_connection():
    # In a real environment, we'd check for POSTGRES_URL or similar environment variable
    # to connect to PostgreSQL. If not present, we use SQLite.
    pg_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if pg_url:
        try:
            import psycopg2
            conn = psycopg2.connect(pg_url)
            conn.autocommit = True
            return conn
        except ImportError:
            try:
                import pg8000
                conn = pg8000.connect(url=pg_url)
                return conn
            except ImportError:
                print("Warning: PostgreSQL driver not found. Falling back to SQLite.")
    
    # SQLite Fallback
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if we are running SQLite or PostgreSQL
    is_sqlite = isinstance(conn, sqlite3.Connection)
    
    id_type = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"
    text_type = "TEXT"
    timestamp_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    bool_type = "BOOLEAN"
    real_type = "REAL"
    
    # Users table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS users (
        id {id_type},
        name {text_type} NOT NULL,
        email {text_type} UNIQUE NOT NULL,
        password_hash {text_type} NOT NULL,
        created_at {timestamp_type}
    )
    """)
    
    # Forms table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS forms (
        id {id_type},
        user_id INTEGER,
        filename {text_type} NOT NULL,
        file_path {text_type} NOT NULL,
        form_type {text_type},
        difficulty_score {real_type},
        summary_json {text_type},
        created_at {timestamp_type}
    )
    """)
    
    # Fields table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS fields (
        id {id_type},
        form_id INTEGER,
        label {text_type} NOT NULL,
        expanded_label {text_type},
        detected_type {text_type},
        current_value {text_type},
        is_required {bool_type},
        confidence_score {real_type},
        explanation_json {text_type},
        status {text_type},
        error_message {text_type},
        created_at {timestamp_type}
    )
    """)
    
    # Activity logs table
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS activity_logs (
        id {id_type},
        user_id INTEGER,
        action {text_type} NOT NULL,
        details {text_type},
        created_at {timestamp_type}
    )
    """)
    # Alter table to add ocr_confidence and field_detection_confidence if they don't exist
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN ocr_confidence REAL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN field_detection_confidence REAL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN section_title TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN nearby_ocr_text TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN original_ocr_value TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN validation_score INTEGER")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN validation_json TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE fields ADD COLUMN expanded_label TEXT")
    except Exception:
        pass

    if not is_sqlite:
        conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
