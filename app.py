from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO

from forms import MessageForm, LoginForm
from game.Game import Game

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
bootstrap = Bootstrap(app)

game = Game()


def start_round():
    game.set_round()
    socketio.emit('players_info', game.round.players_info())
    socketio.emit('dealer_info', game.round.diller_info())
    socketio.emit('new_message', game.round.current_betting_player.name + ', делайте ставку!')
    socketio.emit('betting', game.round.current_betting_player.name)


def end_round():
    game.round.diller_turn()
    socketio.emit('new_message', 'У дилера ' + game.round.diller.name + ' карты '
                  + str(game.round.diller.hand[0]['hand_cards']))
    results = game.round.comprasion_points()
    for mes in results:
        socketio.emit('new_message', mes)
    socketio.emit('new_message', 'Конец раунда')


def taking_card():
    game.round.current_player.get_card(game.round.deck)
    socketio.emit('players_info', game.round.players_info(show_cards=True))
    if game.round.current_player.points_in_hand() > 21:
        socketio.emit('new_message', game.round.current_player.name + ' взял карту и перебрал.')
        game.round.next_player()
        if game.round.current_player is not None:
            socketio.emit('new_message', 'Ход ' + game.round.current_player.name)
            socketio.emit('player', {'name': game.round.current_player.name,
                                     'can_double': game.round.is_current_player_can_double()})
        else:
            end_round()
            start_round()

    else:
        socketio.emit('new_message', game.round.current_player.name + ' взял карту.')
        socketio.emit('player', {'name': game.round.current_player.name,
                                 'can_double': game.round.is_current_player_can_double()})
        socketio.emit('new_message', 'Ход ' + game.round.current_player.name)


@app.route('/play/')
def play():
    return render_template('play.html', form=MessageForm(), username=session['username'])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        session['username'] = form.username.data
        return redirect(url_for('play'))
    return render_template('index.html', form=form)


@socketio.on('connected')
def connected(data):
    if game.is_player(session['username']):
        game.add_player(session['username'])
        game.random_diller()
        start_round()


@socketio.on('bet')
def player_bet(bet):
    if game.round.push_bet(bet):
        socketio.emit('players_info', game.round.players_info())
        socketio.emit('new_message', game.round.current_betting_player.name + ' сделал ставку ' + str(bet))
        game.round.next_betting_player()
        if game.round.current_betting_player is not None:
            socketio.emit('new_message', game.round.current_betting_player.name + ', делайте ставку!')
            socketio.emit('betting', game.round.current_betting_player.name)
        else:
            socketio.emit('players_info', game.round.players_info(show_cards=True))
            socketio.emit('dealer_info', game.round.diller_info(show_cards=True))
            socketio.emit('new_message', 'Ход ' + game.round.current_player.name)
            socketio.emit('player', {'name': game.round.current_player.name,
                                     'can_double': game.round.is_current_player_can_double()})
    else:
        socketio.emit('betting', game.round.current_betting_player.name)


@socketio.on('take')
def player_take():
    taking_card()


@socketio.on('double')
def player_double():
    game.round.bank.double_bet(game.round.current_player)
    taking_card()


@socketio.on('next')
def player_next():
    socketio.emit('new_message', game.round.current_player.name + ' закончил свой ход.')
    game.round.next_player()
    if game.round.current_player is not None:
        socketio.emit('new_message', 'Ход ' + game.round.current_player.name)
        socketio.emit('player', {'name': game.round.current_player.name,
                                 'can_double': game.round.is_current_player_can_double()})
    else:
        end_round()
        start_round()


@socketio.on('chat_message')
def handle_message(json):
    mes = session['username'] + ' сказал: ' + json['message'] + '\n'
    socketio.emit("new_message", mes)


if __name__ == '__main__':
    socketio.run(app)