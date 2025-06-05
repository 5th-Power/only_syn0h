from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
import os

# 설정
app = Flask(__name__)
app.secret_key = '🧠-change-this-key-now'  # 배포 전에 바꿔
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 업로드 권한 비밀번호
OWNER_PASSWORD = 'tptfkdls'  # 너만 아는 비밀번호로 바꿔

# 파일 허용 체크
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# DB 연결
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# 루트: 게시물 목록
@app.route('/')
def index():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY created_at DESC").fetchall()
    comments = db.execute("SELECT * FROM comments").fetchall()
    return render_template('index.html', posts=posts, comments=comments)

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == OWNER_PASSWORD:
            session['user'] = 'owner'
            return redirect(url_for('upload'))
        else:
            return "비밀번호 틀림"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

# 게시물 업로드 (로그인한 나만 가능)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if session.get('user') != 'owner':
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '')
        files = request.files.getlist('photos')
        if not files or len(files) < 1:
            return "사진 최소 1장 이상 올려야 함", 400

        filenames = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                filenames.append(filename)

        db = get_db()
        db.execute("INSERT INTO posts (title, images, created_at) VALUES (?, ?, ?)",
                   (title, ','.join(filenames), datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        db.commit()
        return redirect(url_for('index'))

    return render_template('upload.html')

# 프로필
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    db = get_db()
    if request.method == 'POST':
        nickname = request.form['nickname']
        bio = request.form['bio']
        db.execute("REPLACE INTO profile (id, nickname, bio) VALUES (1, ?, ?)", (nickname, bio))
        db.commit()
    profile = db.execute("SELECT * FROM profile WHERE id = 1").fetchone()
    return render_template('profile.html', profile=profile)

# 댓글
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    content = request.form['comment']
    ip = request.remote_addr or "0.0.0.0"
    if session.get('user') == 'owner':
        name = '나'
    else:
        name = ".".join(ip.split(".")[:2]) + ".*.*"
    db = get_db()
    db.execute("INSERT INTO comments (post_id, ip, content, created_at) VALUES (?, ?, ?, ?)",
               (post_id, name, content, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    db.commit()
    return redirect(url_for('index'))

# 이미지 업로드 URL
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
if __name__ == '__main__':
    print("🔥 Flask 서버 실행 중...")
    app.run(debug=False, host='0.0.0.0', port=25565)