from .Bank import Bank
from .Round import Round
from .Person import Person
from .Deck import Deck
import random


# В этом классе должны быть основные функции для управления игрой. Такие как:
# Игра начинается, создание игроков, начало раунда, ставка игрока, действие игрока, выбрать диллера, поменять диллера
# Удалить игрока, Добавить игрока, Добавить деньги игроку, Удалить деньги у игрока,
#
class Game:
    # Конструктор для игры
    def __init__(self):
        self.bank = Bank()
        self.players_in_room = []
        self.players_list = []
        self.round = None
        self.round_index = 0
        self.queue = []
        self.diller = None
        if len(self.players_list) >= 2:
            self.random_diller()
            self.round.refresh()

    def set_round(self):
        self.round_index += 1
        self.next_diller()
        self.round = Round(self.players_list, self.diller, self.bank, Deck())
        self.round.refresh()
        self.round.indicate_diller_for_bank()
        self.round.give_cards_to_players()

    def add_player(self, player):
        self.players_list.append(Person(player))

    def add_player_to_room(self, player):
        self.players_in_room.append(player)

    def is_player_in_game(self, name):
        for player in self.players_list:
            if player.name == name:
                return True
        return False

    def is_player_in_room(self, name):
        return name in self.players_in_room

    # Случайно определяет диллера
    def random_diller(self):
        self.diller = random.choice(self.players_list)
        message = str('Выбран диллер! Сегодня это - {}'.format(self.diller.name))
        return message

    # Назначает следующего диллера
    def next_diller(self):
        if self.diller and self.diller in self.players_list:
            ind = self.players_list.index(self.diller)
            if ind != len(self.players_list)-1:
                self.diller = self.players_list[ind+1]
            else:
                self.diller = self.players_list[0]
        else:
            self.random_diller()

    # Выводит имя диллера
    def show_diller(self):
        message = str('В этом раунде дилер {}!!'.format(self.diller.name))

    # Убирает человека из игры
    def delete_player(self, player):
        self.players_list.remove(player)

    # Убирает человека из игры, если он остался без денег
    def players_no_money(self):
        messages = []
        for player in self.players_list:
            if player.money <= 0:
                self.players_list.remove(player)
                messages.append(str('Игрок {} выбывает из игры'.format(player.name)))
        return messages

    # Убирает дилера, если он остался без денег
    # def diller_no_money(self):
    #     if self.diller.money <= 0:
    #         self.players_list.remove(self.diller)

    # Проверка: остался ли хоть кто-то играть, кроме одного человека
    def left_one_player(self):
        if len(self.players_list) == 1:
            message = str('Остался только {}, игра закончена'.format(self.players_list[0].name))
            return [message]
        return []

    def all_checks(self):
        messages = []
        messages += self.players_no_money()
        messages += self.left_one_player()
        return messages
