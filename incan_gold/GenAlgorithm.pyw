import numpy as np
from Game import Game
from Player import Player
from matplotlib import pyplot as plt
import pickle
import sys


class GenAlgorithm:
    def __init__(self, generations=500, games=500, variability=.1):
        self.generations = generations
        self.games = games
        self.variability = variability

    def run(self):
        # the original generation
        gen = [Player("p1"), Player("p2"), Player("p3"), Player("p4"),
               Player("p5"), Player("p6"), Player("p7"), Player("p8")]

        avg_scores = []
        max_avg = 0

        for g in range(self.generations):
            # make a game with this generation of players and reset the results
            game = Game(gen)
            results = np.array([0, 0, 0, 0, 0, 0, 0, 0])

            # play a bunch of games
            for i in range(self.games):
                result = game.sim_game()
                results += result

            # how to stay up to date on the progress
            print(end="\r")
            print("Generation {}/{}".format(g + 1, self.generations), end="")
            avg_score = sum(results) / (8 * self.games)
            max_avg = max(max_avg, avg_score)
            avg_scores.append(avg_score)
            print(" ; Average score = {} (max {})".format(avg_score, max_avg), end="")

            # get the next generation
            top_players = np.argsort(results)
            first = gen[top_players[-1]]
            second = gen[top_players[-2]]
            third = gen[top_players[-3]]

            gen = [first,
                   first.child(str(g) + "a", self.variability / 3),
                   first.child(str(g) + "b", self.variability / 3),
                   second,
                   second.child(str(g) + "c", self.variability / 2),
                   second.child(str(g) + "d", self.variability / 2),
                   third,
                   third.child(str(g) + "e", self.variability)]

        gens = range(self.generations)
        plt.plot(gens, avg_scores)
        plt.xlabel("Generation")
        plt.ylabel("Avg Score")
        plt.show()

        game = Game(gen)
        outcome = game.spectate_game()

        top_players = np.argsort(outcome)
        winner = game.players[top_players[-1]]

        print()
        print("Winner: ", end="")
        print(winner.name)
        return winner.strategy.weights


if __name__ == "__main__":
    filename = sys.argv[1]
    gens = int(sys.argv[2])
    games = int(sys.argv[3])
    var = float(sys.argv[4])

    gen_alg = GenAlgorithm(gens, games, var)
    winner_weights = gen_alg.run()
    print(winner_weights)

    with open(filename, mode='wb') as outfile:
        pickle.dump(winner_weights, outfile)
