# app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from config import SECRET_KEY
from models import db  # Flask-SQLAlchemyで初期化したdb
import match  # マッチング処理モジュール
import logs   # ログ管理モジュール

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
# MySQL接続情報などもapp.configに設定する
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{app.config.get('MYSQL_USER')}:{app.config.get('MYSQL_PASSWORD')}@{app.config.get('MYSQL_HOST')}/{app.config.get('MYSQL_DB')}"
db.init_app(app)

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# ルーティング例（ログイン、登録、アカウント編集など）
@app.route('/login', methods=['GET', 'POST'])
def login():
    # ログイン処理
    return render_template('login.html')

# など必要なルーティングを追加

if __name__ == '__main__':
    socketio.run(app, debug=True)
