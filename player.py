import os
import random
from openai import OpenAI
from anthropic import Anthropic
from prompt import get_prompt_for_points_guess, get_prompt_for_card_choice


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.tricks_won = []
        self.points = 0
        self.guess = 0

    def receive_hand(self, cards):
        self.hand = cards[:]
        # order hand by suit and rank
        self.hand.sort(key=lambda c: (c.suit.value, c.rank.value))
        self.tricks_won = []

    def update_points(self, points):
        self.points += abs(self.guess - points)

    def make_guess(self, game_state):
        raise NotImplementedError

    def play_card(self, game_state):
        raise NotImplementedError


class RandomGuesser(Player):
    def make_guess(self, game_state):
        self.guess = random.randint(0, 157)
        print(f"{self.name} guesses {self.guess} points")

    def play_card(self, game_state):
        legal = game_state.get_legal_cards(self.hand, game_state.leading_suit)
        card = random.choice(legal)
        self.hand.remove(card)
        return card


class HumanPlayer(Player):
    def make_guess(self, game_state):
        print(f"\nYour hand: {', '.join(str(c) for c in self.hand)}")
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
            choice = input("Play a card (e.g. Jack-Schilten): ").strip().upper()
            for card in legal:
                if str(card).upper() == choice:
                    self.hand.remove(card)
                    return card
            print("Invalid choice. Try again.")


class LLMPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def make_guess(self, game_state):
        prompt = get_prompt_for_points_guess(game_state, self.hand)
        self.guess = self.llm_func_point_guess(self.hand, prompt)
        self.guess = int(self.guess)
        print(f"{self.name} guesses {self.guess} points")

    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)

        prompt = get_prompt_for_card_choice(game_state, legal_cards, self.hand)
        card = self.llm_func_card_choice(legal_cards, prompt)
        self.hand.remove(card)
        return card

    def __repr__(self):
        return "LLMPlayer (llm_func={self.llm_func.__name__})"


class LLMPlayerChatGPT(Player):
    def __init__(self, name, openai_model="gpt-4o"):
        super().__init__(name)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = openai_model

    def _guess(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

        answer = response.choices[0].message.content.strip()
        if answer.isdigit():
            answer = int(answer)
            if 0 <= answer <= 157:
                return answer
        print(f"{self} returned illegal guess: {answer}")
        return random.randint(0, 157)

    def _get_card(self, prompt, legal_cards):
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

        answer = response.choices[0].message.content.strip().upper()
        for card in legal_cards:
            if (
                str(card).upper() == answer
                or f"{card.rank.name}-{card.suit.name}".upper() == answer
            ):
                return card

        print(f"ChatGPT returned illegal card: {answer}")
        return random.choice(legal_cards)

    def make_guess(self, game_state):
        prompt = get_prompt_for_points_guess(game_state, self.hand)
        self.guess = self._guess(prompt)
        self.guess = int(self.guess)
        print(f"{self.name} guesses {self.guess} points")

    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)

        prompt = get_prompt_for_card_choice(game_state, legal_cards, self.hand)
        card = self._get_card(prompt, legal_cards)
        self.hand.remove(card)
        return card

    def __repr__(self):
        return f"LLMPlayerChatGPT {self.model}"


class LLMPlayerAnthropic(Player):
    def __init__(self, name, anthropic_model="claude-3-5-sonnet-latest"):
        super().__init__(name)
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = anthropic_model

    def _guess(self, prompt):
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
        )

        answer = response.content[0].text.strip()
        if answer.isdigit():
            answer = int(answer)
            if 0 <= answer <= 157:
                return answer
        print(f"Claude returned illegal guess: {answer}")
        return random.randint(0, 157)

    def _get_card(self, prompt, legal_cards):
        response = self.client.messages.create(
            model=self.model,
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
        print(f"Claude returned illegal card: {answer}")
        return random.choice(legal_cards)

    def make_guess(self, game_state):
        prompt = get_prompt_for_points_guess(game_state, self.hand)
        self.guess = self._guess(prompt)
        self.guess = int(self.guess)
        print(f"{self.name} guesses {self.guess} points")

    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)

        prompt = get_prompt_for_card_choice(game_state, legal_cards, self.hand)
        card = self._get_card(prompt, legal_cards)
        self.hand.remove(card)
        return card

    def __repr__(self):
        return f"LLMPlayerAnthropic {self.model}"
