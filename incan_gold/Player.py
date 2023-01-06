from Strategy import Strategy


class Player:
    def __init__(self, name, variability=.1):
        self.name = name
        self.strategy = Strategy(variability=variability)
        self.out = False
        self.round_treasure = 0
        self.treasure = 0

    def stay(self, game_state):
        stay = self.strategy.stay(game_state.input())
        if not stay:
            self.out = True
        return stay

    def child(self, name, variability=.1):
        baby = Player(str(name))
        baby.strategy = Strategy(self.strategy.weights, variability)
        return baby
