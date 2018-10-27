import random
from collections import Counter


class Deck:
    # конструктор, который создаёт колоду
    def __init__(self, decks=3):
        self.decks = decks
        self.cards = []
        self.refresh_cards()
        self.was_refilled = False

    # Метод обновляющие колоду для нового раунда
    def refresh_cards(self):
        self.cards = []
        l = list(range(2, 11)) + ['j', 'a', 'q', 'k']
        for i in l:
            for j in ['c', 'd', 'h', 's']:
                self.cards.append(str(i) + j)

        self.cards = self.cards[:] * self.decks

    def refilled(self):
        if self.was_refilled:
            self.was_refilled = False
            return True

    # Возвращает одну случайную карту из колоды
    def get_one_card(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        if len(self.cards) == 0:
            self.was_refilled = True
            self.refresh_cards()
        return card

def cost_card(card):
    card = card[:-1]
    try:
        cost = int(card)
        return cost
    except:
        if card == 'a':
            return 11
        else:
            return 10
