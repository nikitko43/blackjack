from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

from forms import MessageForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
bootstrap = Bootstrap(app)


@app.route('/play/')
def play():
    return render_template('play.html', form=MessageForm())


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)


if __name__ == '__main__':
    socketio.run(app)