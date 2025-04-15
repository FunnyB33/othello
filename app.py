from flask import Flask, request, jsonify
import uuid
import mysql.connector
import config

app = Flask(__name__)

# MySQL 
host = config.connection["HOST"]
user = config.connection["USER"]
password = config.connection["PASSWORD"]
database = config.connection["DB"]

conn = mysql.connector.connect(host, user, password, database)
cursor = conn.cursor(dictionary=True)

@app.route('/join_room', methods=['POST'])
def join_room():
    data = request.json
    nickname = data['nickname']
    room_id = data['room_id']

    # プレイヤー登録
    player_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO players (player_id, nickname, room_id) VALUES (%s, %s, %s)",
        (player_id, nickname, room_id)
    )
    conn.commit()

    # 同じroom_idのユーザーを取得 (作成日時の古い順に2人取得)
    cursor.execute(
        "SELECT * FROM players WHERE room_id = %s ORDER BY created_at ASC LIMIT 2",
        (room_id,)
    )
    players = cursor.fetchall()

    # 2人揃ったらマッチング作成
    if len(players) == 2:
        match_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO matches (match_id, player1_id, player2_id, room_id, status) VALUES (%s, %s, %s, %s, 'playing')",
            (match_id, players[0]['player_id'], players[1]['player_id'], room_id)
        )
        conn.commit()
        return jsonify({"message": "マッチング成立！", "match_id": match_id})

    return jsonify({"message": "プレイヤーを待っています。", "player_id": player_id})

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    match_id = data['match_id']
    player_id = data['player_id']
    position = data['position']
    move_number = data['move_number']

    cursor.execute(
        "INSERT INTO moves (match_id, player_id, move_position, move_number) VALUES (%s, %s, %s, %s)",
        (match_id, player_id, position, move_number)
    )
    conn.commit()

    return jsonify({"message": "駒の位置が記録されました。"})


if __name__ == '__main__':
    app.run(debug=True)
