from eventlet import sleep
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
connected_players = []


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
    username = session['username']
    if len(game.players_list) > 1:
        if game.round.bank.is_all_players_betted(game.round.players):
            emit_players_info(dealer=True, show_cards=True)
        else:
            emit_players_info(dealer=True, show_cards=False)
    if not game.is_player_in_room(username):
        send_message(username + ' зашел.', chat=True)
        game.add_player_to_room(username)
        if not game.is_player_in_game(username) and len(game.players_list) >= 2:
            game.queue.append(username)
        elif not game.is_player_in_game(username):
            game.add_player(username)
            start_round()


@socketio.on('disconnect')
def disconnect():
    check_connected_players()


@socketio.on('bet')
def player_bet(bet, username):
    player = game.get_player_by_name(username)
    if player:
        if game.round.push_bet(bet, player):
            emit_players_info(show_cards=False)
            send_message(player.name + ' сделал ставку ' + str(bet))

    if game.round.bank.is_all_players_betted(game.round.players):
        emit_players_info(dealer=True)
        emit_current_player()


@socketio.on('take')
def player_take():
    taking_card()


@socketio.on('double')
def player_double():
    game.round.bank.double_bet(game.round.current_player)
    taking_card(with_double=True)


@socketio.on('next')
def player_next():
    next_player()


@socketio.on('split')
def player_split():
    game.round.split_current_player()
    send_message(game.round.current_player.name + ' сделал сплит.')
    if game.round.deck.refilled():
        send_message('Колода была перемешана.')
    emit_current_player()
    emit_players_info(dealer=False)
    if game.round.current_player.is_two_aces_after_split():
        game.round.current_player_num_hand = 1
        next_player()


@socketio.on('chat_message')
def handle_message(json):
    mes = session['username'] + ' сказал: ' + json['message']
    send_message(mes, chat=True)


@socketio.on('check_connected')
def check_connected(username):
    connected_players.append(username)


def start_round():
    for player in game.queue:
        game.add_player(player)
    game.queue = []
    game.set_round()
    if game.round.deck.refilled():
        send_message('Колода была перемешана.')
    emit_players_info(dealer=True, show_cards=False)
    emit_current_betting_player()


def end_round():
    if game.round.count_to_much() > 0:
        emit_players_info(dealer=True, show_cards=True, hide_second_dealer=False)
        sleep(2)
        for _ in game.round.diller.diller_logic(game.round.deck):
            emit_players_info(dealer=True, show_cards=True, hide_second_dealer=False)
            sleep(2)

    send_message('У дилера ' + game.round.diller.name + ' карты ' + str(game.round.diller.hand[0]['hand_cards']))
    emit_players_info(dealer=True, show_cards=True, hide_second_dealer=False)

    results = game.round.comprasion_points()
    for mes in results:
        send_message(mes)

    messages = game.all_checks()
    for mes in messages:
        send_message(mes)

    if len(game.players_list) == 1 and len(game.players_in_room) != 1:
        send_message('Новая игра...')
        game.players_list = []
        for player in game.players_in_room:
            game.add_player(player)
    sleep(3)


def kick_player(username):
    if username in game.queue:
        game.queue.remove(username)

    player = None
    for pl in game.players_list:
        if pl.name == username:
            player = pl

    if username in game.players_in_room:
        game.players_in_room.remove(username)

    if player:
        if player in game.players_list:
            game.players_list.remove(player)

        if game.round.current_player == player:
            next_player()

        if player in game.round.players:
            game.round.players.remove(player)


def taking_card(with_double=False):
    game.round.current_player.is_doubled = with_double
    if game.round.current_player_num_hand == 1:
        take_card_for_hand(1, with_double)
    else:
        take_card_for_hand(0, with_double)


def take_card_for_hand(num_hand, with_double):
    game.round.current_player.get_card(game.round.deck, num_hand=num_hand)
    if game.round.deck.refilled():
        send_message('Колода была перемешана.')
    emit_players_info(dealer=False)
    if game.round.current_player.points_in_hand(num_hand=num_hand) > 21:
        send_message(game.round.current_player.name + ' взял карту и перебрал.')
        game.round.bank.diller_is_winner(game.round.current_player, num_hand=num_hand)
        next_player()
    else:
        if with_double:
            send_message(game.round.current_player.name + ' удвоил и взял карту.')
            next_player()
        else:
            send_message(game.round.current_player.name + ' взял карту.')
        emit_current_player()


def next_player():
    game.round.next_player()
    if game.round.current_player is not None:
        emit_current_player()
    else:
        socketio.emit('player', {'name': '_________________________________________________________________________',
                                 'previous': game.round.previous_player.name if game.round.previous_player else None})
        end_round()
        start_round()


def next_betting_player():
    game.round.next_betting_player()
    if game.round.current_betting_player is not None:
        emit_current_betting_player()
    else:
        emit_players_info(dealer=True)
        emit_current_player()


def check_connected_players():
    global connected_players
    connected_players = []
    socketio.emit('check_connection')
    sleep(5)
    for player in game.players_in_room:
        if player not in connected_players:
            kick_player(player)
            send_message(player + ' покинул игру.', chat=True)


def emit_current_player():
    socketio.emit('player', {'name': game.round.current_player.name,
                             'can_double': game.round.is_current_player_can_double(),
                             'can_split': game.round.is_current_player_can_split(),
                             'is_splitted': game.round.is_current_player_splitted(),
                             'previous': game.round.previous_player.name if game.round.previous_player else None})


def emit_current_betting_player():
    socketio.emit('betting', {player.name: game.round.get_max_bet(player) for player in game.round.players})

    # socketio.emit('betting', {'name': game.round.current_betting_player.name,
    #                           'previous': game.round.previous_player.name if game.round.previous_player else None,
    #                           'max': game.round.get_max_bet()})


def emit_players_info(dealer=False, show_cards=True, hide_second_dealer=True):
    socketio.emit('players_info', game.round.players_info(show_cards=show_cards))
    if dealer:
        socketio.emit('dealer_info', game.round.diller_info(show_cards=show_cards, hide_second=hide_second_dealer))


def send_message(str, chat=False):
    socketio.emit('new_message', {'message': str, 'chat': chat})


if __name__ == '__main__':
    socketio.run(app)
