from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLiteデータベース初期化
DATABASE = 'database.db'

def init_db():
    if not os.path.exists(DATABASE):
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nickname TEXT NOT NULL)''')
            c.execute('''CREATE TABLE chats (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            sender TEXT,
                            receiver TEXT,
                            message TEXT)''')
            conn.commit()

init_db()

# ニックネーム入力画面
@app.route('/', methods=['GET', 'POST'])
def nickname():
    if request.method == 'POST':
        nickname = request.form['nickname']
        session['nickname'] = nickname
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (nickname) VALUES (?)", (nickname,))
            conn.commit()
        return redirect(url_for('matching'))
    return render_template('nickname.html')

# マッチング画面
@app.route('/matching')
def matching():
    nickname = session.get('nickname', None)
    if not nickname:
        return redirect(url_for('nickname'))
    # 他のユーザーとのマッチング確認
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT nickname FROM users WHERE nickname != ?", (nickname,))
        user = c.fetchone()
    if user:
        session['partner'] = user[0]
        return redirect(url_for('chat'))
    return render_template('matching.html')

# チャット画面
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    nickname = session.get('nickname', None)
    partner = session.get('partner', None)
    if not nickname or not partner:
        return redirect(url_for('nickname'))

    if request.method == 'POST':
        message = request.form['message']
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO chats (sender, receiver, message) VALUES (?, ?, ?)", 
                      (nickname, partner, message))
            conn.commit()
    # チャット履歴取得
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT sender, message FROM chats 
                     WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)''',
                  (nickname, partner, partner, nickname))
        chat_history = c.fetchall()

    return render_template('chat.html', nickname=nickname, partner=partner, chat_history=chat_history)

if __name__ == '__main__':
    app.run(debug=True)
