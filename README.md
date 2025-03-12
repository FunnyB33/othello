# othello

オンラインで対戦するオセロを作っていきたいと思う
## 環境
- Flaskを使う
- リアルタイム通信は**Flask-SocketIO**を使う
## 仕様
- ユーザーはゲストプレイでも可能
    - ゲストプレイの場合、一時的なIDを発行後、プレイが終わるたびにゲームした情報は削除する。
- アカウント登録・編集とログイン、アカウント削除ができる。
    - アカウント登録の際は生年月日と、氏名、アカウント名を持って個人を特定するようにする。
          - 生年月日、氏名、アカウント名は暗号化してMySQLに登録するようにする。
    - データはアカウントのデータは勝率（カラムをwin・lose・drawで分ける）とともにMySQLに保存する。
- ユーザーがIDを打ち込むとマッチした上位一組がゲームを始まる。
    - ID入力時、マッチ待機時間を1minとし、待機時間を超えたらID入力画面に戻る。
    - ランダムマッチにした場合待機時間を2minとし、待機時間を超えたらID入力画面に戻る。
- ゲームにログインしてきたIPアドレスを取得して時間とログをとる。


## 開発の流れ
### Pythonのインストール
- **Pythonのバージョン**
    - FlaskはPython 3系で動作するので、Python 3.8以降の最新版をインストールするのがおすすめ。
（※すでにインストール済みならこのステップはスキップしてOKです）
- **インストール確認**
    - ターミナル（またはコマンドプロンプト）で以下のコマンドを実行しtえ、バージョンが表示されるか確認しよう。
  ``` bash
    python --version
  ```
    
### 仮装環境の作成
プロジェクトごとに依存かkん系を管理するための**仮想環境**を作成
- **仮想環境の作成**
``` bash 
    python -m venv venv
```
- **仮装環境の有効化**
  - Windowsの場合
    ``` bash
        venv\Scripts\activate
    ```
  - macOS/Linuxの場合
    ``` bash
        source venv/bin/activatet
    ```
    
### Flaskと必要なパッケージのインストール
- **Flaskのインストール**
  ``` bash
      pip install Flask
  ```
- **Flask-SocketIOを利用**
  オンライン対戦などリアルタイム通信を行うために必要
  ``` bash
      pip install flask-socketio
  ```
- **依存関係の管理**
  インストールしたパッケージを後から簡単に再現できるように **requirements.txt**を作成する。
  ``` bash
      pip freeze > requirements.txt
  ```
  
### 基本的なFlaskアプリの作成
``` python
    # app.py
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello, Flask!"
    
    if __name__ == '__main__':
        app.run(debug=True)
```
**実行方法**
  ``` bash
      python app.py
  ```
 [http://127.0.0.1:5000](http://127.0.0.1:5000)
### 参考URL
-  [Flask公式ドキュメント](https://flask.palletsprojects.com/en/latest/)  
    - → Flaskの基本的な使い方や拡張機能の説明が豊富に記載されているよ。
- [Python公式 venv ドキュメント（日本語）](https://docs.python.org/ja/3/library/venv.html)
    -  → 仮想環境の詳細な使い方について解説されているよ。
---
全体の仕様を見ると、いくつかのモジュールに分けて実装すると整理しやすいよ。大まかな設計方針と各モジュールのポイントを以下にまとめるね。

---

## 1. システム全体のアーキテクチャ

### 使用技術
- **Flask:** Webアプリケーションの基盤として使う  
- **Flask-SocketIO:** リアルタイム通信（オセロの盤面更新やマッチング通知など）に利用  
- **MySQL:** ユーザー情報（アカウント情報・勝率）やログを永続化するために使う（ORMにはSQLAlchemyが便利）  
- **cryptography ライブラリ:** 生年月日、氏名、アカウント名などの個人情報を暗号化してMySQLに保存する  
- **Flask-Login:** 登録ユーザーのセッション管理を行う（必要に応じて）

### システム構成の概要
- **アカウント管理モジュール:**  
  - **ゲストプレイ:** 一時的なID発行、ゲーム終了後にゲーム情報（対局結果など）は削除  
  - **登録ユーザー:** 生年月日、氏名、アカウント名を入力し、暗号化してMySQLに保存。勝率情報（win・lose・draw）も管理する
- **マッチングモジュール:**  
  - ユーザーが入力したIDに基づいて、同じIDを持つユーザーを待機リストからマッチング  
  - 待機時間：ID入力の場合は1分、ランダムマッチの場合は2分。待機時間を超えると、再度ID入力画面に戻す処理を実装
- **ゲームモジュール（オセロ）:**  
  - 8×8の盤面管理、初期配置、石の配置・反転処理、ターン管理、勝敗判定などのロジック
  - マッチングが成立したら、各プレイヤーにゲームセッションを割り当て、Socket.IOで盤面状態を更新・共有
- **ログ管理モジュール:**  
  - ユーザーがゲームにログインした際、IPアドレスとログイン時間を記録  
  - ログはMySQLや別途ログファイルで管理する

---

## 2. 各モジュールの詳細と実装例

### アカウント管理

#### ゲストプレイと登録ユーザーの違い
- **ゲスト:**  
  - ゲスト用の一時IDを発行し、対局終了後はそのゲーム結果は削除（永続化しない）  
- **登録ユーザー:**  
  - 登録時に生年月日、氏名、アカウント名を入力  
  - これらは【cryptography】ライブラリで暗号化してMySQLに保存  
  - 勝率情報（win, lose, draw）のカラムを持たせ、対局結果を更新

#### サンプルコード（アカウントモデル）
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from cryptography.fernet import Fernet
import datetime

Base = declarative_base()

# ※実際の運用ではキーは安全に管理すること（環境変数など）
secret_key = Fernet.generate_key()
cipher = Fernet(secret_key)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    # 暗号化した値を文字列として保存する（base64エンコードされたバイト列）
    encrypted_birthdate = Column(String(256))
    encrypted_name = Column(String(256))
    encrypted_account_name = Column(String(256))
    win = Column(Integer, default=0)
    lose = Column(Integer, default=0)
    draw = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def set_sensitive_info(self, birthdate, name, account_name):
        self.encrypted_birthdate = cipher.encrypt(birthdate.encode()).decode()
        self.encrypted_name = cipher.encrypt(name.encode()).decode()
        self.encrypted_account_name = cipher.encrypt(account_name.encode()).decode()

    def get_sensitive_info(self):
        return {
            'birthdate': cipher.decrypt(self.encrypted_birthdate.encode()).decode(),
            'name': cipher.decrypt(self.encrypted_name.encode()).decode(),
            'account_name': cipher.decrypt(self.encrypted_account_name.encode()).decode(),
        }
```

※ここでは SQLAlchemy を利用したモデル定義例を示しているよ。実際は Flask-SQLAlchemy を使ってFlaskと統合すると便利だね。

---

### マッチングモジュール

#### 基本の流れ
1. **ID入力:**  
   ユーザーがID（もしくはランダムマッチの場合はそのフラグ）を入力すると、サーバー側で待機リストに追加する  
2. **待機時間の管理:**  
   - ID入力の場合：1分以内に同じIDのユーザーが現れたらマッチング  
   - ランダムマッチの場合：2分以内にマッチングが成立しなければ、再度ID入力画面へ  
   → タイマーを各ユーザーに設定するか、定期的にチェックする仕組みを実装
3. **マッチング成立:**  
   同じIDのユーザー同士を上位1組でペアにし、Socket.IO を使って「ゲーム開始」のイベントを両者に送信

#### 実装例（擬似コード）
```python
from flask_socketio import SocketIO, emit, join_room
import time

socketio = SocketIO(app)
waiting_users = {}  # { match_id: [ {sid: socket id, timestamp: 登録時間}, ... ] }

@socketio.on('join_match')
def handle_join_match(data):
    match_id = data.get('match_id')  # ID入力かランダムかによって決まる
    sid = request.sid
    current_time = time.time()

    if match_id not in waiting_users:
        waiting_users[match_id] = []

    waiting_users[match_id].append({'sid': sid, 'timestamp': current_time})
    
    # チェックしてマッチング可能ならマッチ成立
    if len(waiting_users[match_id]) >= 2:
        # 上位一組を選ぶ（例として最初の2人）
        players = waiting_users[match_id][:2]
        # ルームを作成して参加させる
        room = f"room_{match_id}_{int(current_time)}"
        for p in players:
            join_room(room, sid=p['sid'])
            emit('match_found', {'room': room}, room=p['sid'])
        # 削除またはリスト更新
        waiting_users[match_id] = waiting_users[match_id][2:]
    else:
        # タイムアウト処理は別途、バックグラウンドでチェック
        pass
```

※実際は、タイムアウト処理を定期的に実行するバッチ処理などで待機リストから期限切れのユーザーを除外し、再度ID入力画面に誘導する必要があるね。

---

### ゲーム（オセロ）モジュール

- **ゲームロジック:**  
  - 8x8の盤面を管理し、初期配置や石の配置・反転処理、ターン管理、勝敗判定を実装する  
  - Pythonのクラスとして `OthelloGame` を作成し、状態管理するのが一般的
- **リアルタイム更新:**  
  - Flask-SocketIO のイベントで、ユーザーが手を打ったときに盤面の状態を全員に送信  
  - クライアント側（HTML/JavaScript）で盤面の更新を反映

---

### ログ管理

- **ログ取得:**  
  - Flask のリクエスト情報から `request.remote_addr` を使ってユーザーのIPアドレスを取得  
  - ログイン時（またはゲーム開始時）に、IPアドレスと現在時刻をログとして記録（MySQLに保存するか、ログファイルに出力する）
- **サンプルコード**
```python
from flask import request
import datetime

def log_user_login(user_id):
    ip_address = request.remote_addr
    login_time = datetime.datetime.utcnow()
    # ログ用テーブルやログファイルに保存する処理
    print(f"User {user_id} logged in from {ip_address} at {login_time}")
```

---

## 3. 開発の進め方

1. **基盤構築:**  
   - 仮想環境作成、Flask、Flask-SocketIO、SQLAlchemy、cryptography ライブラリのインストール  
   - MySQLサーバーのセットアップとテーブル設計
2. **モジュールごとの実装:**  
   - アカウント管理（ゲストと登録ユーザーの区別、暗号化処理、ログイン・登録・削除機能の実装）  
   - マッチング処理（待機リスト管理とタイムアウト処理の実装）  
   - オセロのゲームロジック（盤面管理、石の反転、勝敗判定）  
   - Socket.IO を使ったリアルタイム通信で、各クライアントにゲーム状態を更新
3. **テストとデバッグ:**  
   - ローカル環境で各機能ごとにテスト  
   - 同時接続時やタイムアウト処理、ログの記録などを十分に確認

---

## 4. 参考URL

- [Flask公式ドキュメント](https://flask.palletsprojects.com/en/latest/)  
- [Flask-SocketIO公式ドキュメント](https://flask-socketio.readthedocs.io/en/latest/)  
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/en/14/)  
- [cryptographyライブラリ公式サイト](https://cryptography.io/en/latest/)

---

othello_project/
├── app.py               # Flaskアプリケーションのエントリーポイント
├── config.py            # MySQL接続情報、シークレットキーなどの設定
├── models.py            # SQLAlchemyによるデータベース（ユーザー、ログ等）のモデル定義
├── game.py              # オセロのゲームロジック（盤面管理、石の反転、勝敗判定など）
├── match.py             # マッチング処理（待機リスト、タイムアウト処理など）の実装
├── requirements.txt     # 利用するPythonパッケージ一覧
├── logs.py              # ログ管理（IPアドレスやアクセス時間などの記録用、必要に応じて）
├── templates/           # HTMLテンプレートディレクトリ
│   ├── base.html        # 共通レイアウト（ヘッダー・フッター等）
│   ├── index.html       # トップページ（ID入力やマッチング前画面）
│   ├── login.html       # ログインページ
│   ├── register.html    # アカウント登録ページ
│   ├── account_edit.html# アカウント編集ページ
│   └── game.html        # オセロ対戦画面
└── static/              # 静的ファイル（CSS, JavaScript, 画像など）
    ├── css/
    │   └── style.css    # サイト全体のスタイルシート
    └── js/
        └── socket_client.js  # Socket.IOクライアントのスクリプト（盤面更新やイベント処理）

