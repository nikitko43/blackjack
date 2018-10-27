import random


class Deck:
    # конструктор, который создаёт колоду
    def __init__(self, decks=8):
        self.decks = decks
        self.cards = []
        self.refresh_cards()

    # Метод обновляющие колоду для нового раунда
    def refresh_cards(self):
        self.cards = []
        l = list(range(2, 11)) + ['j', 'a', 'q', 'k']
        for i in l:
            for j in ['c', 'd', 'h', 's']:
                self.cards.append(str(i) + j)

        self.cards = self.cards[:] * self.decks

    # Возвращает одну случайную карту из колоды
    def get_one_card(self):
        card = random.choice(self.cards)
        self.cards.remove(card)
        return card
