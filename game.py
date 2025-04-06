import random
from card import generate_deck, Suit


class DifferenzlerGame:
    def __init__(self, players):
        self.players = players
        self.trump_suit = random.choice(list(Suit))
        self.deck = generate_deck()
        self.leading_suit = None
        print(f"\n🎯 Trump Suit: {self.trump_suit.name}")

    def get_legal_cards(self, hand, leading_suit):
        if not leading_suit:
            return hand
        suit_cards = [c for c in hand if c.suit == leading_suit]
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

    def play_round(self):
        self.deal_cards()
        self.collect_guesses()

        player_order = self.players[:]
        for _ in range(9):
            trick = []
            self.leading_suit = None
            for player in player_order:
                card = player.play_card(self)
                if not self.leading_suit:
                    self.leading_suit = card.suit
                trick.append((player, card))

            winner = self.determine_trick_winner(trick)
            winner.tricks_won.append([card for _, card in trick])
            print(f"{winner.name} wins the trick: {[c for _, c in trick]}")
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
            player.points = total_points
            diff = abs(total_points - player.guess)
            print(f"\n{player.name}:")
            print(f"  Guessed: {player.guess}")
            print(f"  Actual: {total_points}")
            print(f"  Difference (score): {diff}")
