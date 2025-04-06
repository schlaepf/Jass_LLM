import random
from card import generate_deck, Suit


class DifferenzlerGame:
    def __init__(self, players):
        self.players = players
        self.deck = generate_deck()
        self.trick_history = []
        self.trump_suit = random.choice(list(Suit))
        self.leading_suit = None
        print(f"Trump suit for this game is: {self.trump_suit.value}")

    def deal_cards(self):
        random.shuffle(self.deck)
        for i, player in enumerate(self.players):
            hand = self.deck[i*9:(i+1)*9]
            player.receive_hand(hand)

    def get_legal_cards(self, hand, leading_suit=None):
        if not leading_suit:
            return hand
        suit_cards = [card for card in hand if card.suit == leading_suit]
        return suit_cards if suit_cards else hand

    def play_round(self):
        for _ in range(9):  # 9 tricks
            trick = []
            self.leading_suit = None

            for player in self.players:
                card = player.play_card(self)
                if not self.leading_suit:
                    self.leading_suit = card.suit
                trick.append((player, card))
                print(f"{player.name} plays {card}")

            winner = self.determine_trick_winner(trick, self.leading_suit)
            winner.tricks_won.append(trick)
            self.trick_history.append((trick, winner))
            print(f"{winner.name} wins the trick.\n")

    def determine_trick_winner(self, trick, leading_suit):
        def card_strength(entry):
            player, card = entry
            return card.strength(self.trump_suit, leading_suit)
        return max(trick, key=card_strength)[0]

    def print_scores(self):
        print("Final Scores:")
        for player in self.players:
            points = sum(card.rank.value for trick in player.tricks_won for _, card in trick)
            print(f"{player.name}: {points} points")
