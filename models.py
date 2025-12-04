import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DATABASE = 'database.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # 1. Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            department TEXT,
            job_role TEXT,
            role TEXT NOT NULL DEFAULT 'user', -- 'user' or 'admin'
            is_active BOOLEAN NOT NULL DEFAULT 1
        );
    """)

    # 2. Reports Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_type TEXT NOT NULL, -- e.g., 'XSS', 'SQLi', 'Other'
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            file_path TEXT, -- Path to the uploaded file in static/uploads/
            status TEXT NOT NULL DEFAULT 'new', -- 'new', 'in_review', 'closed'
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    # 3. Articles Table (Cyber Awareness Portal)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_ar TEXT NOT NULL,
            title_en TEXT NOT NULL,
            content_ar TEXT NOT NULL,
            content_en TEXT NOT NULL,
            is_published BOOLEAN NOT NULL DEFAULT 1,
            views INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 4. Quizzes Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title_ar TEXT NOT NULL,
            title_en TEXT NOT NULL,
            pass_score INTEGER NOT NULL, -- Percentage
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 5. Quiz Questions Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_ar TEXT NOT NULL,
            question_en TEXT NOT NULL,
            correct_option INTEGER NOT NULL, -- Index of the correct option (0-based)
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        );
    """)

    # 6. Quiz Options Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS quiz_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            option_ar TEXT NOT NULL,
            option_en TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES quiz_questions (id)
        );
    """)

    # 7. User Quiz Results Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score INTEGER NOT NULL, -- Percentage
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        );
    """)

    # 8. Tips/Alerts Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tips_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL, -- 'tip' or 'alert'
            content_ar TEXT NOT NULL,
            content_en TEXT NOT NULL,
            publish_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

def create_user(full_name, email, password, department=None, job_role=None, role='user'):
    conn = get_db_connection()
    password_hash = generate_password_hash(password)
    try:
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, department, job_role, role) VALUES (?, ?, ?, ?, ?, ?)",
            (full_name, email, password_hash, department, job_role, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # Email already exists
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def check_password(user, password):
    return check_password_hash(user['password_hash'], password)

if __name__ == '__main__':
    init_db()
    print("Database schema initialized.")
