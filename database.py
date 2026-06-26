import sqlite3

DB_PATH = "student_helper.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deadlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            task TEXT NOT NULL,
            due_date TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            subject TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            grade REAL NOT NULL,
            label TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# --- Deadlines ---
def add_deadline(user_id, subject, task, due_date):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO deadlines (user_id, subject, task, due_date) VALUES (?, ?, ?, ?)",
                 (user_id, subject, task, due_date))
    conn.commit(); conn.close()

def get_deadlines(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT id, subject, task, due_date FROM deadlines WHERE user_id=? ORDER BY due_date", (user_id,))
    rows = cur.fetchall(); conn.close(); return rows

def delete_deadline(deadline_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM deadlines WHERE id=? AND user_id=?", (deadline_id, user_id))
    conn.commit(); conn.close()

# --- Schedule ---
def add_schedule(user_id, day, time, subject):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO schedule (user_id, day, time, subject) VALUES (?, ?, ?, ?)",
                 (user_id, day, time, subject))
    conn.commit(); conn.close()

def get_schedule(user_id):
    conn = sqlite3.connect(DB_PATH)
    days_order = "CASE day WHEN 'Понеділок' THEN 1 WHEN 'Вівторок' THEN 2 WHEN 'Середа' THEN 3 WHEN 'Четвер' THEN 4 WHEN 'Пятниця' THEN 5 ELSE 6 END"
    cur = conn.execute(f"SELECT id, day, time, subject FROM schedule WHERE user_id=? ORDER BY {days_order}, time", (user_id,))
    rows = cur.fetchall(); conn.close(); return rows

def delete_schedule(schedule_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM schedule WHERE id=? AND user_id=?", (schedule_id, user_id))
    conn.commit(); conn.close()

# --- Grades ---
def add_grade(user_id, subject, grade, label=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO grades (user_id, subject, grade, label) VALUES (?, ?, ?, ?)",
                 (user_id, subject, grade, label))
    conn.commit(); conn.close()

def get_grades(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT id, subject, grade, label FROM grades WHERE user_id=? ORDER BY subject", (user_id,))
    rows = cur.fetchall(); conn.close(); return rows

def delete_grade(grade_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM grades WHERE id=? AND user_id=?", (grade_id, user_id))
    conn.commit(); conn.close()

def get_subjects_with_grades(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT subject, AVG(grade), COUNT(*) FROM grades WHERE user_id=? GROUP BY subject ORDER BY subject",
        (user_id,))
    rows = cur.fetchall(); conn.close(); return rows

# --- Notes ---
def add_note(user_id, subject, content):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO notes (user_id, subject, content) VALUES (?, ?, ?)",
                 (user_id, subject, content))
    conn.commit(); conn.close()

def get_note_subjects(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute("SELECT DISTINCT subject FROM notes WHERE user_id=? ORDER BY subject", (user_id,))
    rows = cur.fetchall(); conn.close(); return [r[0] for r in rows]

def get_notes_by_subject(user_id, subject):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        "SELECT id, content, created_at FROM notes WHERE user_id=? AND subject=? ORDER BY created_at DESC",
        (user_id, subject))
    rows = cur.fetchall(); conn.close(); return rows

def delete_note(note_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM notes WHERE id=? AND user_id=?", (note_id, user_id))
    conn.commit(); conn.close()
