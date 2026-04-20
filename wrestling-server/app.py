import os, pty, select, struct, fcntl, termios, signal
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wrestling-arena-secret'
socketio = SocketIO(app, cors_allowed_origins='*')

GAME_COMMAND = ['python3', '-u', 'WrestlingMenu.py']
COLS, ROWS = 90, 30

sessions = {}   # sid → (pid, fd)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    from flask_socketio import request as req
    sid = req.sid
    pid, fd = pty.fork()
    if pid == 0:
        # Child — set terminal size then exec the game
        winsize = struct.pack('HHHH', ROWS, COLS, 0, 0)
        fcntl.ioctl(pty.STDOUT_FILENO, termios.TIOCSWINSZ, winsize)
        os.execvp(GAME_COMMAND[0], GAME_COMMAND)
    else:
        # Parent — store the fd and start reading loop
        sessions[sid] = (pid, fd)
        socketio.start_background_task(read_and_forward, sid, fd)

def read_and_forward(sid, fd):
    while True:
        try:
            r, _, _ = select.select([fd], [], [], 0.04)
            if r:
                data = os.read(fd, 4096)
                if not data:
                    break
                socketio.emit('output', data.decode('utf-8', errors='replace'), room=sid)
        except OSError:
            break
    socketio.emit('disconnect_game', room=sid)

@socketio.on('input')
def on_input(data):
    from flask_socketio import request as req
    sid = req.sid
    if sid in sessions:
        _, fd = sessions[sid]
        try:
            os.write(fd, data.encode())
        except OSError:
            pass

@socketio.on('disconnect')
def on_disconnect():
    from flask_socketio import request as req
    sid = req.sid
    if sid in sessions:
        pid, fd = sessions.pop(sid)
        try:
            os.close(fd)
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
        except OSError:
            pass

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)