# match.py
from flask_socketio import join_room, emit
import time

# 待機中ユーザーの管理（例：{match_id: [ { 'sid': socket id, 'timestamp': 登録時刻 }, ... ] }）
waiting_users = {}

def add_to_waiting(match_id, sid):
    current_time = time.time()
    if match_id not in waiting_users:
        waiting_users[match_id] = []
    waiting_users[match_id].append({'sid': sid, 'timestamp': current_time})
    # マッチング成立の判定はここで行う

def check_and_match(socketio, match_id):
    # 例：待機中のユーザー数が2人以上ならマッチング成立
    if match_id in waiting_users and len(waiting_users[match_id]) >= 2:
        players = waiting_users[match_id][:2]
        room = f"room_{match_id}_{int(time.time())}"
        for p in players:
            join_room(room, sid=p['sid'])
            emit('match_found', {'room': room}, room=p['sid'])
        waiting_users[match_id] = waiting_users[match_id][2:]
