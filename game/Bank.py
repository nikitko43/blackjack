class Bank:
    # Конструктор
    def __init__(self):
        self.bank = {}
        # bank = {[bet],[bet,bet],[bet],...}

    # Назначает диллера
    def indicate_diller(self, diller):
        self.diller = diller

    def is_all_players_betted(self, players):
        for player in players:
            if player not in self.bank:
                return False
        return True

    # Ставка сделана и сохранена в словаре
    def bet_in_bank(self, player, value, num_hand=0):
        if num_hand == 0:
            self.bank[player] = [value]
        else:
            self.bank[player].insert(num_hand, self.bank[player][0])

    # Сплитует ставку
    def bet_in_split_bank(self, player, num_hand = 0):
        try:
            if player in self.bank:
                player.money -= self.bank[player][num_hand]
                self.bank[player].append(self.bank[player][num_hand])
            else:
                raise Exception('Ошибка, игрок {} не делал ставку'.format(player.name))
        except Exception as e:
            pass

    # Удваивает ставку
    def double_bet(self, player, num_hand=0):
        try:
            if player in self.bank:
                player.money -= self.bank[player][num_hand]
                self.bank[player][num_hand] *= 2
            else:
                raise Exception('Ошибка, игрок {} не делал ставку'.format(player.name))
        except Exception as e:
            pass


    # Возвращает деньги при выигрыше
    def rewarding(self, player, num_hand, coef=1.):
        try:
            if player in self.bank:
                if self.diller.money < round(self.bank[player][num_hand] * 2 * coef):
                    player.money += self.diller.money
                    self.diller.money = 0
                else:
                    player.money += round(2 * coef * self.bank[player][num_hand])
                    self.diller.money -= round(self.bank[player][num_hand] * coef)
            else:
                raise Exception('Ошибка, игрок {} не делал ставку'.format(player.name))
        except Exception as e:
            pass

    # Возвращает деньги, если была ничья
    def return_money(self, player, num_hand):
        try:
            if player in self.bank:
                player.money += self.bank[player][num_hand]
            else:
                raise Exception('Ошибка, игрок {} не делал ставку'.format(player.name))
        except Exception as e:
            pass

    # Отдаёт деньги диллеру, при проигрыше игрока
    def diller_is_winner(self, player, num_hand=0):
        try:
            if player in self.bank:
                self.diller.money += self.bank[player][num_hand]
            else:
                raise Exception('Ошибка, игрок {} не делал ставку'.format(player.name))
        except Exception as e:
            pass

    def return_sum(self):
        bet_sum = 0
        for player in self.bank:
            bet_sum += sum(self.bank[player])
        return bet_sum

    # Возвращает значение (сколько было поставлено)
    def return_value(self, player, num_hand=0):
        if player in self.bank:
            return self.bank[player][num_hand]
        else:
            return None

    # Обновляется каждый раунд
    def refresh_bank(self):
        self.bank.clear()
