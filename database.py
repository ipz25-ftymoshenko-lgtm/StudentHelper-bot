import sqlite3
import os

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
    conn.commit()
    conn.close()

def add_deadline(user_id: int, subject: str, task: str, due_date: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO deadlines (user_id, subject, task, due_date) VALUES (?, ?, ?, ?)",
                (user_id, subject, task, due_date))
    conn.commit()
    conn.close()

def get_deadlines(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, subject, task, due_date FROM deadlines WHERE user_id = ? ORDER BY due_date", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_deadline(deadline_id: int, user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM deadlines WHERE id = ? AND user_id = ?", (deadline_id, user_id))
    conn.commit()
    conn.close()

def add_schedule(user_id: int, day: str, time: str, subject: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO schedule (user_id, day, time, subject) VALUES (?, ?, ?, ?)",
                (user_id, day, time, subject))
    conn.commit()
    conn.close()

def get_schedule(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    days_order = "CASE day WHEN 'Понеділок' THEN 1 WHEN 'Вівторок' THEN 2 WHEN 'Середа' THEN 3 WHEN 'Четвер' THEN 4 WHEN 'Пятниця' THEN 5 ELSE 6 END"
    cur.execute(f"SELECT id, day, time, subject FROM schedule WHERE user_id = ? ORDER BY {days_order}, time", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows
