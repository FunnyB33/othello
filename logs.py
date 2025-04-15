# logs.py
from flask import request
from datetime import datetime
from models import db, LoginLog

def log_user_login(user_id):
    ip_address = request.remote_addr
    log = LoginLog(user_id=user_id, ip_address=ip_address, login_time=datetime.utcnow())
    db.session.add(log)
    db.session.commit()
