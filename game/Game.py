from .Bank import Bank
from .Round import Round
from .Person import Person
from .Deck import Deck
import random


# В этом классе должны быть основные функции для управления игрой. Такие как:
# Игра начинается, создание игроков, начало раунда, ставка игрока, действие игрока, выбрать диллера, поменять диллера
# Удалить игрока, Добавить игрока, Добавить деньги игроку, Удалить деньги у игрока,
#


class Game():
    # Конструктор для игры
    def __init__(self):
        self.bank = Bank()
        self.players_list = []
        self.round = None
        if len(self.players_list) >= 2:
            self.random_diller()
            self.round.refresh()

    def set_round(self):
        if self.round:
            prev_player = self.round.previous_player
        else:
            prev_player = None
        self.round = Round(self.players_list, self.diller, self.bank, Deck(), prev_player)
        self.round.refresh()
        self.next_diller()
        self.round.indicate_diller_for_bank()
        self.round.give_cards_to_players()

    def add_player(self, player):
        self.players_list.append(Person(player))

    def is_player(self, name):
        for person in self.players_list:
            if person.name == name:
                return True
        return False

    # Случайно определяет диллера
    def random_diller(self):
        self.diller = random.choice(self.players_list)
        message = str('Выбран диллер! Сегодня это - {}'.format(self.diller.name))
        return message

    # Назначает следующего диллера
    def next_diller(self):
        ind = self.players_list.index(self.diller)
        if ind != len(self.players_list)-1:
            self.diller = self.players_list[ind+1]
        else:
            self.diller = self.players_list[0]
        # self.show_diller()

    # Выводит имя диллера
    def show_diller(self):
        message = str('В этом раунде дилер {}!!'.format(self.diller.name))

    # Убирает человека из игры
    def delete_player(self, player):
        self.players_list.remove(player)

    # Убирает человека из игры, если он остался без денег
    def players_no_money(self):
        for player in self.players_list:
            if player.money <= 0 and player != self.diller:
                self.players_list.remove(player)
                message = str('Игрок {} выбывает из игры'.format(player.name))

    # Убирает дилера, если он остался без денег
    def diller_no_money(self):
        if self.diller.money <= 0:
            self.players_list.remove(self.diller)

    # Проверка: остался ли хоть кто-то играть, кроме одного человека
    def left_one_player(self):
        if len(self.players_list) == 1:
            message = str('Остался только {}, игра закончена'.format(self.players_list[0].name))

    def all_checks(self):
        self.players_no_money()
        self.next_diller()
        self.diller_no_money()
        self.left_one_player()

    # Зацикливание раундов
    # def cycle_rounds_old(self):
    #     while True:
    #         round.indicate_diller_for_bank()
    #         round.push_bets()
    #         round.give_cards_to_players()
    #         round.players_move()
    #         round.diller_turn()
    #         round.comprasion_points()
    #         round.refresh_round()
    #         self.all_checks()

