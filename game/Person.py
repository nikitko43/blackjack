class Person:

    # Конструктор игрока
    def __init__(self, name='noname', money=100):
        self.hand = []
        self.add_hand_element()
        # hand = [{ 'hand_cards':[] , 'hand_to_much':False } , ... }
        self.money = money
        self.name = name
        self.is_doubled = False

    def get_hand_card_images(self, hide=False, hide_second=False):
        if hide:
            return []
        hand_images = []

        if self.is_splitted():
            for i in self.hand:
                hand_images.append([card + '.png' for card in i['hand_cards']])
        else:
            hand_images = [card + '.png' for card in self.hand[0]['hand_cards']]

        if hide_second:
            hand_images = hand_images[:-1]

        return hand_images

    def is_splitted(self):
        return True if len(self.hand) > 1 else False

    # Добавить руку в случае сплита.
    def add_hand_element(self):
        self.hand.append({'hand_cards': [], 'hand_to_much': False})

    # Удаляет все карты из руки
    def refresh(self):
        self.hand.clear()
        self.is_doubled = False

    # Берёт одну или больше карт из колоды
    def get_card(self, deck, num_hand=0, count=1):
        for i in range(count):
            self.hand[num_hand]['hand_cards'].append(deck.get_one_card())

    # Делает ставку
    def betting(self, bet):
        if bet > 0 and bet <= self.money:
            self.money -= bet
            return True
        return False

    # Логика игры за диллера
    def diller_logic(self, deck):
        while self.points_in_hand() <= 16:
            self.get_card(deck)
            yield
        if self.points_in_hand() > 21:
            self.hand[0]['hand_to_much'] = True

    # Проверка на сплит
    def checkup_split(self, limit_money, num_hand=0):
        if len(self.hand[num_hand]['hand_cards']) == 2 and self.money > limit_money:
            if cost_card(self.hand[num_hand]['hand_cards'][0]) == cost_card(self.hand[num_hand]['hand_cards'][1]):
                return True
        return False

    # Проверка на удвоение
    def checkup_dubl(self, limit_money, num_hand=0):
        if len(self.hand[num_hand]['hand_cards']) == 2 and self.money >= limit_money:
            return True
        return False

    # Раздвоить карты (сплит)
    def split_cards(self, deck, num_hand=0):
        self.add_hand_element()
        self.hand[num_hand + 1]['hand_cards'].append(self.hand[num_hand]['hand_cards'][1])
        self.hand[num_hand]['hand_cards'].pop(1)
        self.get_card(deck, num_hand=1)
        self.get_card(deck)
        
    def is_two_aces_after_split(self):
        return self.hand[0]['hand_cards'][0][:-1] == 'a' and self.hand[1]['hand_cards'][0][:-1] == 'a'

    # Возвращает количество очков в руке
    def points_in_hand(self, num_hand=0):
        points = 0
        count_ace = 0
        for _item in self.hand[num_hand]['hand_cards']:
            item = _item[:-1]
            try:
                item = int(item)
                points += item
            except:
                if item == 'a':
                    points += 11
                    count_ace += 1
                else:
                    points += 10
            while points > 21:
                if count_ace > 0:
                    points -= 10
                    count_ace -= 1
                else:
                    break
            if points > 21:
                self.hand[num_hand]['hand_to_much'] = 1
        return points


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
