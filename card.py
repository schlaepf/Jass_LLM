from enum import Enum

class Suit(Enum):
    SCHELLEN = 'Schellen'
    EICHELN = 'Eicheln'
    SCHILTEN = 'Schilten'
    ROSEN = 'Rosen'

class Rank(Enum):
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

NON_TRUMP_ORDER = {
    Rank.ACE: 8,
    Rank.KING: 7,
    Rank.QUEEN: 6,
    Rank.JACK: 5,
    Rank.TEN: 4,
    Rank.NINE: 3,
    Rank.EIGHT: 2,
    Rank.SEVEN: 1,
    Rank.SIX: 0,
}

TRUMP_ORDER = {
    Rank.JACK: 8,
    Rank.NINE: 7,
    Rank.ACE: 6,
    Rank.KING: 5,
    Rank.QUEEN: 4,
    Rank.TEN: 3,
    Rank.EIGHT: 2,
    Rank.SEVEN: 1,
    Rank.SIX: 0,
}

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank.name[0]}-{self.suit.name[0]}"

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return hash((self.suit, self.rank))

    def strength(self, trump_suit: Suit, leading_suit: Suit):
        if self.suit == trump_suit:
            return 100 + TRUMP_ORDER[self.rank]
        elif self.suit == leading_suit:
            return 50 + NON_TRUMP_ORDER[self.rank]
        else:
            return NON_TRUMP_ORDER[self.rank]

def generate_deck():
    return [Card(suit, rank) for suit in Suit for rank in Rank]
