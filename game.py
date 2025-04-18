import random
from card import Rank, generate_deck, Suit
import csv
import uuid


class DifferenzlerGame:
    def __init__(self, players, n_rounds=1):
        self.players = players
        self.leading_suit = None
        self.n_rounds = n_rounds
        self.rounds_played = 0
        self.n_tricks_played = 0
        self.game_id = str(uuid.uuid4())
        self.played_cards = []
        self.history = ""
        self.N_TRICKS = 9
        self.MAX_POINTS = 157
        # shuffle the players
        random.shuffle(self.players)

    def get_legal_cards(self, hand, leading_suit):
        # trump can always be played; jack suit is the only card that does not have to follow the leading suit
        legal_cards = set()
        trump_cards = set([c for c in hand if c.suit == self.trump_suit])
        legal_cards.update(trump_cards)
        suit_cards = set([c for c in hand if c.suit == leading_suit])
        legal_cards.update(suit_cards)
        if leading_suit is None or (
            len(legal_cards) == 1 and list(legal_cards)[0].rank == Rank.JACK
        ):
            return hand
        if len(suit_cards) == 0 or len(legal_cards) == 0:
            return hand
        legal_cards = list(legal_cards)
        legal_cards.sort(key=lambda c: (c.suit.value, c.rank.value))
        return legal_cards

    def deal_cards(self):
        random.shuffle(self.deck)
        for i, p in enumerate(self.players):
            p.receive_hand(self.deck[i * 9 : (i + 1) * 9])

    def collect_guesses(self):
        for player in self.players:
            player.make_guess(self)
            self.history += f"{player} guessed {player.guess} points\n"

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
                print(f"{player}: {player.points} points")
            self.save_stats()
        print(f"\n--- {self.rounds_played} rounds played ---")

        print("\n--- Game complete ---")
        for player in self.players:
            print(f"{player}: {player.points} points")

    def save_stats(self):
        # store the stats points of the players after a round to a csv file
        # csv file has the following structure: game_id, round, player1_name, player1_points, player2_name, player2_points, ...
        with open("game_stats.csv", "a") as csvfile:
            writer = csv.writer(csvfile)
            row = [self.game_id, self.rounds_played]
            for player in self.players:
                row.append(str(player))
                row.append(player.points)
            writer.writerow(row)
        print("Stats saved to game_stats.csv")

    def setup_round(self):
        self.n_tricks_played = 0
        self.deck = generate_deck()
        self.trump_suit = random.choice(list(Suit))
        self.leading_suit = None
        print(f"\n🎯 Trump Suit: {self.trump_suit.name}")

    def play_round(self):
        self.setup_round()
        self.deal_cards()
        self.collect_guesses()

        player_order = self.players[:]
        for _ in range(self.N_TRICKS):
            trick = []
            self.leading_suit = None
            for player in player_order:
                card = player.play_card(self)
                if not self.leading_suit:
                    self.leading_suit = card.suit
                print(f"{player} plays {card}")
                self.history += f"{player} plays {card}\n"
                trick.append((player, card))

            self.n_tricks_played += 1
            # the winner of the last trick gets an extra 5 points
            if self._is_last_trick():
                self.players[player_order.index(player)].points += 5
                print(f"{player} gets an extra 5 points for the last trick")
            winner = self.determine_trick_winner(trick)
            winner.tricks_won.append([card for _, card in trick])
            self.played_cards.extend(card for _, card in trick)
            self.played_cards = list(set(self.played_cards))
            print(f"{winner} wins the trick: {[c for _, c in trick]}\n\n")
            self.history += f"{winner} wins the trick: {[c for _, c in trick]}\n\n"
            winner_index = player_order.index(winner)
            player_order = player_order[winner_index:] + player_order[:winner_index]
            print(f"player order: {[p for p in player_order]}")
        self.score_players()
        self.history = ""

    def _assert_total_score(self):
        total_points = 0
        for player in self.players:
            total_points += sum(
                card.point_value(self.trump_suit)
                for trick in player.tricks_won
                for card in trick
            )
        assert (
            total_points == self.MAX_POINTS
        ), f"Total points: {total_points} != {self.MAX_POINTS}"

    def score_players(self):
        for player in self.players:
            total_points = sum(
                card.point_value(self.trump_suit)
                for trick in player.tricks_won
                for card in trick
            )
            player.update_points(total_points)
            diff = abs(player.guess - total_points)
            print(f"\n--- {player}'s score ---")
            print(f"\n{player}:")
            print(f"  Guessed: {player.guess}")
            print(f"  Actual: {total_points}")
            print(f"  Difference (score): {diff}")
            print(f"  Points: {player.points}")

    def _is_last_trick(self):
        return self.n_tricks_played == self.N_TRICKS
