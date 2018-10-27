import copy

from game.Deck import Deck


class Round:
    # Конструктор класса раунд
    def __init__(self, all_players, diller, bank, deck):
        self.bank = bank
        self.count_player = len(all_players)
        self.all_players = copy.copy(all_players)   #Все игроки
        self.players = copy.copy(all_players)       #Все игроки раунда кроме дилера
        self.players.remove(diller)
        self.diller = diller
        self.deck = deck
        self.previous_player = None
        self.current_betting_player = self.players[0] if len(self.players) > 0 else None
        self.current_player = self.players[0]
        self.current_player_num_hand = None
        self.move = None

    def is_current_player_can_double(self):
        bet = self.bank.return_value(self.current_player)
        diller = (self.diller.money - self.bank.return_sum()) >= bet
        return self.current_player.checkup_dubl(bet) and diller and not self.current_player.is_splitted() \
               and not self.current_player.is_doubled

    def next_player(self):
        if self.current_player_num_hand == 0:
            self.current_player_num_hand = 1
        else:
            self.previous_player = self.current_player
            ind = self.players.index(self.current_player) + 1
            if ind < len(self.players):
                self.current_player = self.players[ind]
                if self.current_player.is_splitted():
                    self.current_player_num_hand = 0
                else:
                    self.current_player_num_hand = None
            else:
                self.current_player = None

    def get_max_bet(self):
        dealer_max = self.diller.money - self.bank.return_sum()
        player_max = self.current_betting_player.money
        if dealer_max > player_max:
            return player_max
        return dealer_max

    def next_betting_player(self):
        self.previous_player = self.current_betting_player
        if self.diller.money == self.bank.return_sum():
            for player in self.players:
                if player not in self.bank.bank:
                    self.players.remove(player)
            self.current_betting_player = None
        else:
            ind = self.players.index(self.current_betting_player) + 1
            self.current_betting_player = self.players[ind] if ind < len(self.players) else None

    def is_current_player_splitted(self):
        return self.current_player.is_splitted()

    def is_current_player_can_split(self):
        bet = self.bank.return_value(self.current_player)
        diller = (self.diller.money - self.bank.return_sum()) >= bet
        return self.current_player.checkup_split(bet) and diller and not self.current_player.is_doubled \
               and not self.is_current_player_splitted()

    def split_current_player(self):
        self.current_player.split_cards(self.deck)
        self.current_player_num_hand = 0
        self.bank.bet_in_split_bank(self.current_player)
        if self.current_player.is_two_aces_after_split():
            self.current_player_num_hand = 1
            self.next_player()

    # Показать карты диллера
    def diller_info(self, hide_second=True, show_cards=False):
        if hide_second:
            return {'name': self.diller.name, 'cards': [self.diller.hand[0]['hand_cards'][0], '?'] if show_cards else [],
                    'money': self.diller.money,
                    'score': None,
                    'cards_images': self.diller.get_hand_card_images(hide_second=True) if show_cards else []}
        else:
            return {'name': self.diller.name, 'cards': self.diller.hand[0]['hand_cards'], 'money': self.diller.money,
                    'score': self.diller.points_in_hand() if show_cards else None,
                    'cards_images': self.diller.get_hand_card_images() if show_cards else []}

    def players_info(self, show_cards=False):
        return [{'name': player.name, 'cards': player.hand if show_cards else [],
                 'money': player.money, 'is_splitted': player.is_splitted(),
                 'cards_images': player.get_hand_card_images(hide=(not show_cards)),
                 'score': player.points_in_hand() if show_cards else None,
                 'second_score': player.points_in_hand(1) if player.is_splitted() else None,
                 'bet': self.bank.return_value(player)} for player in self.players]

    def refill_deck_if_empty(self):
        if len(self.deck.cards) < 20:
            self.deck = Deck()
            return True
        return False

    # Игроки делают ставки
    def push_bet(self, bet):
        try:
            bet = int(bet)
        except:
            bet = -1
        if bet + self.bank.return_sum() <= self.diller.money and self.current_betting_player.betting(bet):
            self.bank.bet_in_bank(self.current_betting_player, bet)
            return True
        return False

    # Раздать карты игрокам
    def give_cards_to_players(self):
        for player in self.all_players:
            player.get_card(self.deck, count=2)

    # Сравнивает очки
    def comprasion_points(self):
        results = []
        if self.diller.hand[0]['hand_to_much']:
            for player in self.players:
                for num_hand in range(len(player.hand)):
                    if not player.hand[num_hand]['hand_to_much']:
                        results.append(self.result_win(player, num_hand))
        else:
            for player in self.players:
                for num_hand in range(len(player.hand)):
                    if player.hand[num_hand]['hand_to_much'] == False:
                        if player.points_in_hand(num_hand) > self.diller.points_in_hand():
                            results.append(self.result_win(player, num_hand))
                        elif player.points_in_hand(num_hand) < self.diller.points_in_hand():
                            results.append(self.player_lose(player, num_hand))
                        else:
                            results.append(self.result_draw(player, num_hand))
        return results

    # Указать диллера для банка
    def indicate_diller_for_bank(self):
        self.bank.indicate_diller(self.diller)

    # Реализация выигрыша
    def result_win(self, player, num_hand):
        self.bank.rewarding(player, num_hand)
        return ('{},{}={} > Вы выиграли!'.format(player.name, player.hand[num_hand]['hand_cards'], player.points_in_hand(num_hand)))

    # Если игрок проиграл
    def player_lose(self, player, num_hand):
        self.bank.diller_is_winner(player, num_hand)
        return ('{},{}={} > Вы проиграли!'.format(player.name, player.hand[num_hand]['hand_cards'], player.points_in_hand(num_hand)))

    # Реализация ничьи
    def result_draw(self,player, num_hand):
        self.bank.return_money(player, num_hand)
        return ('{},{}={} > Ничья!'.format(player.name, player.hand[num_hand]['hand_cards'], player.points_in_hand(num_hand)))

    # Обновление карт, to_much
    def refresh(self):
        self.players = copy.copy(self.all_players)
        for player in self.all_players:
            player.refresh()
            player.add_hand_element()
        self.players.remove(self.diller)
        self.deck.refresh_cards()
        self.bank.refresh_bank()

    # Красиво выводит имя игроков, кто ещё не проиграл
    # Использовалось для дебагов
    def list_name_players(self):
        for i in self.players:
            yield i.name

    # используется для подсчёта игроков, которые не выбыли из игры
    # Это делается на случай, если все переберут и чтобы диллер не продолжал играть
    def count_to_much(self):
        count = 0
        for player in self.players:
            for num_hand in range(len(player.hand)):
                if player.hand[num_hand]['hand_to_much'] == False:
                    count += 1
        return count
