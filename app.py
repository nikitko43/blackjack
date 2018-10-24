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
    if not game.is_player(session['username']):
        game.add_player(session['username'])
        game.random_diller()
        start_round()


@socketio.on('bet')
def player_bet(bet):
    if game.round.push_bet(bet):
        emit_players_info(show_cards=False)
        send_message(game.round.current_betting_player.name + ' сделал ставку ' + str(bet))
        game.round.next_betting_player()
        if game.round.current_betting_player is not None:
            emit_current_betting_player()
        else:
            emit_players_info(dealer=True)
            emit_current_player()
    else:
        emit_current_betting_player(with_message=False)


@socketio.on('take')
def player_take():
    taking_card()


@socketio.on('double')
def player_double():
    game.round.bank.double_bet(game.round.current_player)
    taking_card()


@socketio.on('next')
def player_next():
    send_message(game.round.current_player.name + ' закончил свой ход.')
    game.round.next_player()
    if game.round.current_player is not None:
        emit_current_player()
    else:
        end_round()
        start_round()


@socketio.on('chat_message')
def handle_message(json):
    mes = session['username'] + ' сказал: ' + json['message']
    send_message(mes)


def start_round():
    game.set_round()
    emit_players_info(dealer=True, show_cards=False)
    emit_current_betting_player()


def end_round():
    game.round.diller_turn()
    send_message('У дилера ' + game.round.diller.name + ' карты ' + str(game.round.diller.hand[0]['hand_cards']))
    results = game.round.comprasion_points()
    for mes in results:
        send_message(mes)
    send_message('Конец раунда')


def taking_card():
    game.round.current_player.get_card(game.round.deck)
    emit_players_info(dealer=False)
    if game.round.current_player.points_in_hand() > 21:
        send_message(game.round.current_player.name + ' взял карту и перебрал.')
        game.round.bank.diller_is_winner(game.round.current_player)
        game.round.next_player()
        if game.round.current_player is not None:
            emit_current_player()
        else:
            end_round()
            start_round()
    else:
        send_message(game.round.current_player.name + ' взял карту.')
        emit_current_player()


def emit_current_player():
    send_message('Ход ' + game.round.current_player.name)
    socketio.emit('player', {'name': game.round.current_player.name,
                             'can_double': game.round.is_current_player_can_double(),
                             'previous': game.round.previous_player.name if game.round.previous_player else None})


def emit_current_betting_player(with_message=True):
    if with_message:
        send_message(game.round.current_betting_player.name + ', делайте ставку!')
    socketio.emit('betting', {'name': game.round.current_betting_player.name,
                              'previous': game.round.previous_player.name if game.round.previous_player else None})


def emit_players_info(dealer=False, show_cards=True):
    socketio.emit('players_info', game.round.players_info(show_cards=show_cards))
    if dealer:
        socketio.emit('dealer_info', game.round.diller_info(show_cards=show_cards))


def send_message(str):
    socketio.emit('new_message', str)


if __name__ == '__main__':
    socketio.run(app)
