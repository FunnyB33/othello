from app.routes import app
from app.socketio_events import socketio

if __name__ == '__main__':
    socketio.init_app(app, async_mode='eventlet')
    socketio.run(app, debug=True)
