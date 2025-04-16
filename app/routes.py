from flask import Flask, session, request, redirect, render_template, url_for
from app.socketio_events import socketio
import uuid

app = Flask(__name__)
app.secret_key = "prometheus"
waiting_room = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['keyword']
        player_id = str(uuid.uuid4())
        session['player_id'] = player_id
        session['keyword'] = keyword

        if keyword in waiting_room:
            opponent_id = waiting_room.pop(keyword)
            session['opponent_id'] = opponent_id
            # マッチング成立 -> game画面へ
            # 2人とも揃ったので通知を送る
            socketio.emit('match_success', room=keyword)
            return redirect(url_for('game'))
        else:
            # 自分が先に来た -> 待機状態
            waiting_room[keyword] = player_id
            return render_template('waiting.html', room=keyword) #待機ページへ

    return render_template('index.html')

@app.route('/game')
def game():
    # セッションに必要な情報がなければ戻す
    if 'player_id' not in session or 'keyword' not in session:
        return redirect(url_for('index'))

    return render_template('game.html', room=session['keyword'])
