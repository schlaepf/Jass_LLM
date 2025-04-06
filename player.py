import os
import random
from openai import OpenAI
from anthropic import Anthropic


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.tricks_won = []
        self.points = 0
        self.guess = 0

    def receive_hand(self, cards):
        self.hand = cards[:]
        self.tricks_won = []
        self.points = 0

    def make_guess(self):
        raise NotImplementedError

    def play_card(self, game_state):
        raise NotImplementedError


class RandomGuesser(Player):
    def make_guess(self):
        self.guess = random.randint(30, 90)
        print(f"{self.name} guesses {self.guess} points")

    def play_card(self, game_state):
        legal = game_state.get_legal_cards(self.hand, game_state.leading_suit)
        card = random.choice(legal)
        self.hand.remove(card)
        return card


class HumanPlayer(Player):
    def make_guess(self):
        while True:
            try:
                guess = int(input(f"{self.name}, guess your total points: "))
                if 0 <= guess <= 157:
                    self.guess = guess
                    break
                print("Guess must be between 0 and 157")
            except ValueError:
                print("Enter a number.")

    def play_card(self, game_state):
        legal = game_state.get_legal_cards(self.hand, game_state.leading_suit)
        print(f"\nYour hand: {', '.join(str(c) for c in self.hand)}")
        print(f"Legal cards: {', '.join(str(c) for c in legal)}")
        while True:
            choice = input("Play a card (e.g. J-S): ").strip().upper()
            for card in legal:
                if str(card).upper() == choice:
                    self.hand.remove(card)
                    return card
            print("Invalid choice. Try again.")


class LLMPlayer(Player):
    def __init__(self, name, llm_func):
        super().__init__(name)
        self.llm_func = llm_func

    def make_guess(self):
        self.guess = random.randint(30, 90)
        print(f"{self.name} guesses {self.guess} points")

    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)
        card = self.llm_func(self.hand, legal_cards, game_state)
        if card not in legal_cards:
            raise ValueError(f"{self.name} played illegal card: {card}")
        self.hand.remove(card)
        return card


def chatgpt_llm(hand, legal_cards, game_state):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def card_str(card):
        return f"{card.rank.name}-{card.suit.name}"

    prompt = (
        f"Trump suit: {game_state.trump_suit.name}\n"
        f"Leading suit: {game_state.leading_suit.name if game_state.leading_suit else 'None'}\n"
        f"Hand: {', '.join(card_str(c) for c in hand)}\n"
        f"Legal options: {', '.join(card_str(c) for c in legal_cards)}\n"
        f"Pick the best card to play and ONLY return the card string."
    )

    response = openai_client.chat.completions.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}], max_tokens=10
    )

    answer = response.choices[0].message.content.strip().upper()
    for card in legal_cards:
        if (
            str(card).upper() == answer
            or f"{card.rank.name}-{card.suit.name}".upper() == answer
        ):
            return card
    return random.choice(legal_cards)


def anthropic_llm(hand, legal_cards, game_state):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def card_str(card):
        return f"{card.rank.name}-{card.suit.name}"

    prompt = (
        f"Trump suit: {game_state.trump_suit.name}\n"
        f"Leading suit: {game_state.leading_suit.name if game_state.leading_suit else 'None'}\n"
        f"Hand: {', '.join(card_str(c) for c in hand)}\n"
        f"Legal options: {', '.join(card_str(c) for c in legal_cards)}\n"
        f"Pick the best card to play and ONLY return the card string."
    )

    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=10,
    )

    answer = response.content[0].text.strip().upper()
    for card in legal_cards:
        if (
            str(card).upper() == answer
            or f"{card.rank.name}-{card.suit.name}".upper() == answer
        ):
            return card
    return random.choice(legal_cards)
