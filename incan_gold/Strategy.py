import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class Strategy:
    def __init__(self, genes=None, variability=.1):
        if genes is None:
            self.weights = np.random.randn(9)
        else:
            self.weights = genes + np.random.randn(9)*variability

    def stay(self, game_state):
        if self.think(game_state) > .5:
            return True
        else:
            return False

    def think(self, game_state):
        return sigmoid(np.dot(game_state, self.weights))
