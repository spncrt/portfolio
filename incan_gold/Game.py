import numpy as np


class Card:
    def __init__(self, hazard_or_treasure, value):
        self.type = hazard_or_treasure
        self.value = value

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value

    def __str__(self):
        return self.type + ": " + str(self.value)


class GameState:
    """
    What the players can actually see about the state of the game at any point in time
    """
    def __init__(self, game):
        self.deck_size = len(game.deck) - game.turns_taken
        self.turns_taken = game.turns_taken

        # Where are the treasure cards?
        self.treasures_left = game.treasure_left
        self.treasures_turned = game.treasure_turned

        # Where are the hazard cards?
        self.hazards_left = game.hazard_left
        self.hazards_turned = game.hazard_turned
        self.unique_hazards = set(h.value for h in self.hazards_turned)

        self.num_players = game.num_players
        self.players_in = game.players_in

        self.pot = game.pot

    def input(self):
        return np.array([self.deck_size,
                         self.turns_taken,
                         len(self.treasures_left),
                         sum(t.value for t in self.treasures_left),
                         len(self.hazards_turned),
                         len(self.unique_hazards),
                         self.num_players,
                         self.players_in,
                         self.pot
                         ])


class Game:
    def __init__(self, players):
        self.turns_taken = 0

        # Treasure cards
        self.treasure_cards = [Card('t', t) for t in [1, 2, 3, 4, 5, 5, 7, 7, 9, 11, 11, 13, 14, 15, 17]]
        self.treasure_turned = []
        self.treasure_left = self.treasure_cards.copy()

        # Hazard cards
        self.hazard_cards = [Card('h', h) for h in [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]]
        self.hazard_turned = []
        self.hazard_left = self.hazard_cards
        self.hazards_out = []

        # Shuffle the deck
        self.deck = self.treasure_cards + self.hazard_cards.copy()
        self.shuffle()

        self.num_players = len(players)
        self.players = players
        self.players_in = len(players)

        self.pot = 0

        for p in self.players:
            p.treasure = 0
            p.round_treasure = 0

    def get_state(self):
        return GameState(self)

    def give_treasure(self, card):
        treasure = card.value
        treasure_per_player = treasure // self.players_in
        self.pot += treasure % self.players_in  # add remaining treasure to the pot
        for p in self.players:
            if not p.out:
                p.round_treasure += treasure_per_player

    def update(self, card):
        self.turns_taken += 1
        if card.type == 't':
            # Treasure card
            self.treasure_left.remove(card)
            self.treasure_turned.append(card)
            self.give_treasure(card)
        else:
            # Hazard card
            if card in self.hazard_turned:
                self.hazards_out.append(card)
                return True
            self.hazard_left.remove(card)
            self.hazard_turned.append(card)
        return False

    def shuffle(self):
        np.random.shuffle(self.deck)

    def reset(self, hazard=None):
        """
        Reset the game between rounds
        """
        if hazard is not None:
            self.deck.remove(hazard)
            self.hazard_cards.remove(hazard)

        # Treasure cards
        self.treasure_turned = []
        self.treasure_left = self.treasure_cards.copy()

        # Hazard cards
        self.hazard_turned = []
        self.hazard_left = self.hazard_cards.copy()

        # Shuffle the deck
        self.shuffle()

        self.players_in = self.num_players

        self.turns_taken = 0

        self.pot = 0

        for p in self.players:
            p.round_treasure = 0

    def hard_reset(self):
        """
        Completely reset the state of the game, like restarting the game
        """
        # Treasure cards
        self.treasure_cards = [Card('t', t) for t in [1, 2, 3, 4, 5, 5, 7, 7, 9, 11, 11, 13, 14, 15, 17]]
        self.treasure_turned = []
        self.treasure_left = self.treasure_cards.copy()

        # Hazard cards
        self.hazard_cards = [Card('h', h) for h in [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4]]
        self.hazard_turned = []
        self.hazard_left = self.hazard_cards

        # Shuffle the deck
        self.shuffle()

        self.players_in = self.num_players

        self.turns_taken = 0

        self.pot = 0

        for p in self.players:
            p.treasure = 0
            p.round_treasure = 0

    def divide_pot(self, players_leaving):
        number_leaving = len(players_leaving)
        pot_per_player = self.pot // number_leaving
        self.pot = self.pot % number_leaving
        for p in players_leaving:
            p.round_treasure += pot_per_player

    def sim_turn(self):
        players_leaving = []
        for p in self.players:
            if not p.out:
                result = p.stay(self.get_state())
                if not result:
                    players_leaving.append(p)
        if len(players_leaving) > 0:
            self.divide_pot(players_leaving)
        if not self.anyone_in():
            return True
        card = self.deck[self.turns_taken]
        return self.update(card)

    def sim_round(self):
        game_over = False
        if len(self.hazards_out) == 0:
            self.reset()
        else:
            self.reset(hazard=self.hazards_out[-1])
        for p in self.players:
            p.out = False
        while not game_over:
            game_over = self.sim_turn()
        for p in self.players:
            if p.out:
                p.treasure += p.round_treasure

    def sim_game(self):
        self.hard_reset()
        rounds = range(5)
        for _ in rounds:
            self.sim_round()

        results = []
        for p in self.players:
            results.append(p.treasure)
        return np.array(results)

    def anyone_in(self):
        outs = [p.out for p in self.players]
        self.players_in = self.num_players - sum(outs)
        if sum(outs) == self.num_players:
            return False
        return True

    def spectate_game(self):
        self.hard_reset()
        rounds = range(5)
        for r in rounds:
            print("ROUND", r + 1)
            self.spectate_round()
            print()

        for p in self.players:
            print(p.name, ":", p.treasure)

        results = []
        for p in self.players:
            results.append(p.treasure)
        return np.array(results)

    def spectate_round(self):
        game_over = False
        self.reset()
        for p in self.players:
            p.out = False

        while not game_over:
            game_over = self.spectate_turn()
        for p in self.players:
            if p.out:
                p.treasure += p.round_treasure

    def spectate_turn(self):
        players_leaving = []
        for p in self.players:
            if not p.out:
                result = p.stay(self.get_state())
                print(p.name, "stays?", result)
                if not result:
                    players_leaving.append(p)
        if len(players_leaving) > 0:
            self.divide_pot(players_leaving)
        if not self.anyone_in():
            return True
        card = self.deck[self.turns_taken]
        print(card)
        print()
        return self.update(card)
