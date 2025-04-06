import random
from card import generate_deck, Suit
import csv


class DifferenzlerGame:
    def __init__(self, players, n_rounds=4):
        self.players = players
        self.leading_suit = None
        self.n_rounds = n_rounds
        self.rounds_played = 0

    def get_legal_cards(self, hand, leading_suit):
        if not leading_suit:
            return hand
        suit_cards = [
            c for c in hand if c.suit == leading_suit or c.suit == self.trump_suit
        ]
        return suit_cards if suit_cards else hand

    def deal_cards(self):
        random.shuffle(self.deck)
        for i, p in enumerate(self.players):
            p.receive_hand(self.deck[i * 9 : (i + 1) * 9])

    def collect_guesses(self):
        for player in self.players:
            player.make_guess()

    def determine_trick_winner(self, trick):
        def strength(entry):
            return entry[1].strength(self.trump_suit, self.leading_suit)

        return max(trick, key=strength)[0]

    def play_game(self):
        for _ in range(self.n_rounds):
            self.play_round()
            self.rounds_played += 1
            print(f"\n--- Round {_ + 1} complete ---")
            for player in self.players:
                print(f"{player.name}: {player.points} points")
        print(f"\n--- {self.rounds_played} rounds played ---")

        print("\n--- Game complete ---")
        for player in self.players:
            print(f"{player.name}: {player.points} points")
        self.save_stats()

    def save_stats(self):
        # store the stats points of the players after a game to a csv file
        # csv file has the following structure: player1_name, player1_points, player2_name, player2_points, ..., n_rounds_played
        with open("game_stats.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            row = [self.rounds_played]
            for player in self.players:
                row.append(player.name)
                row.append(player.points)
            writer.writerow(row)
        print("Stats saved to game_stats.csv")

    def setup_round(self):
        self.deck = generate_deck()
        self.trump_suit = random.choice(list(Suit))
        self.leading_suit = None
        print(f"\n🎯 Trump Suit: {self.trump_suit.name}")

    def play_round(self):
        self.setup_round()
        self.deal_cards()
        self.collect_guesses()

        # shuffle the players
        random.shuffle(self.players)
        player_order = self.players[:]
        for _ in range(9):
            trick = []
            self.leading_suit = None
            for player in player_order:
                card = player.play_card(self)
                if not self.leading_suit:
                    self.leading_suit = card.suit
                print(f"{player.name} plays {card}")
                trick.append((player, card))

            winner = self.determine_trick_winner(trick)
            winner.tricks_won.append([card for _, card in trick])
            print(f"{winner.name} wins the trick: {[c for _, c in trick]}\n\n")
            winner_index = player_order.index(winner)
            player_order = player_order[winner_index:] + player_order[:winner_index]

        self.score_players()

    def score_players(self):
        for player in self.players:
            total_points = sum(
                card.point_value(self.trump_suit)
                for trick in player.tricks_won
                for card in trick
            )
            player.update_points(total_points)
            diff = abs(player.guess - total_points)
            print(f"\n--- {player.name}'s score ---")
            print(f"\n{player.name}:")
            print(f"  Guessed: {player.guess}")
            print(f"  Actual: {total_points}")
            print(f"  Difference (score): {diff}")
            print(f"  Points: {player.points}")
