from flask_socketio import SocketIO, emit, join_room # type: ignore
from flask import session

socketio = SocketIO(cors_allowed_origins="*")

room_turn = {}  # 各部屋ごとのターン（"black" or "white"）

# プレイヤーを部屋に入れる
@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    if room not in room_turn:
        room_turn[room] = "black"
    print(f"Player joined room: {room}")

# 手を打ったイベントを全員に送る
@socketio.on('put_stone')
def on_put_stone(data):
    room = data['room']
    x, y, color = data['x'], data['y'], data['color']
    print(f"Put stone:({x}, {y}) color={color} in room={room}")
    emit('update_board', {'x': x, 'y': y, 'color': color}, room=room)