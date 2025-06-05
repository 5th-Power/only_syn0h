# init_db.py
import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# 게시물 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    images TEXT,
    created_at TEXT
)
''')

# 댓글 테이블
c.execute('''
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    ip TEXT,
    content TEXT,
    created_at TEXT
)
''')

# 프로필 테이블 (너 전용)
c.execute('''
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY,
    nickname TEXT,
    bio TEXT
)
''')

conn.commit()
conn.close()
print("데이터베이스 초기화 완료.")