import random

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.tricks_won = []

    def receive_hand(self, cards):
        self.hand = cards

    def play_card(self, game_state):
        raise NotImplementedError

class RandomGuesser(Player):
    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)
        card = random.choice(legal_cards)
        self.hand.remove(card)
        return card

class HumanPlayer(Player):
    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)
        print(f"\n{self.name}, your hand: {', '.join(str(c) for c in self.hand)}")
        print(f"Legal cards: {', '.join(str(c) for c in legal_cards)}")
        while True:
            choice = input("Play a card (e.g. J-S): ").strip().upper()
            for card in legal_cards:
                if str(card).upper() == choice:
                    self.hand.remove(card)
                    return card
            print("Invalid card. Try again.")

class LLMPlayer(Player):
    def __init__(self, name, llm_func):
        super().__init__(name)
        self.llm_func = llm_func

    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)
        card = self.llm_func(self.hand, game_state)  # Stub for now
        if card not in legal_cards:
            raise ValueError(f"{self.name} hallucinated card: {card}")
        self.hand.remove(card)
        return card
