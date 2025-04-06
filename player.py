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
    def __init__(self, name, llm_func_point_guess, llm_func_card_choice):
        super().__init__(name)
        self.llm_func_point_guess = llm_func_point_guess
        self.llm_func_card_choice = llm_func_card_choice

    def make_guess(self, game_state):
        def card_str(card):
            return f"{card.rank.name}-{card.suit.name}"

        prompt = f"""You are playing a variant of the Swiss card game Jass called Differenzler. The game uses a 36-card Swiss-German deck and is played with 4 players. Each round follows the same structure. Read all rules carefully and play according to them.
        CARD SETUP
        - Suits: Schellen (bells), Eicheln (acorns), Schilten (shields), Rosen (roses)
        - Ranks per suit: 6, 7, 8, 9, 10, Unter (Jack), Ober (Queen), King, Ace
        - Total cards: 36 (9 per player)
        - Each round, one suit is randomly selected as the trump suit. Trump cards are stronger than non-trump cards.
        If a suit is trump:
        - Jack is the strongest card (20 points). This is the only card that does not have to follow suit.
        - 9 is the second strongest card (14 points)
        - Ace is the third strongest card (11 points)
        - King is the fourth strongest card (4 points)
        - Queen is the fifth strongest card (3 points)
        - 10 is the sixth strongest card (10 points)
        - 8 is the seventh strongest card (0 points)
        - 7 is the eighth strongest card (0 points)
        - 6 is the weakest card (0 points)
        If a suit is not trump:
        - Ace is the strongest card (11 points)
        - King is the second strongest card (4 points)
        - Queen is the third strongest card (3 points)
        - Jack is the fourth strongest card (2 points)
        - 10 is the fifth strongest card (10 points)
        - 9 is the sixth strongest card (0 points)
        - 8 is the seventh strongest card (0 points)
        - 7 is the eighth strongest card (0 points)
        - 6 is the weakest card (0 points)
        - The player who plays the highest card of the leading suit wins the trick.
        - If a player cannot follow the leading suit, they can play any card.
        - The player who wins the trick leads the next trick.
        - The game continues until all cards have been played.
        Your goal is to minimize your total penalty over multiple rounds.
        The player with the lowest total penalty after all rounds is the winner.
        Round flow:
        1. Deal: Each player receives 9 cards.
        2. Trump: A trump suit is randomly selected and used for the round.
        3. Prediction: Before playing, each player privately predicts how many points they will score this round (a number between 0 and 157). This prediction stays secret until scoring.
        4. Play:
            - 9 tricks are played, one card per player per trick.
            - The player to the left of the dealer leads the first trick.
            - Each player must follow suit if possible.
            - If a player cannot follow suit, they may play any card, including trump.
            - The highest trump wins the trick. If no trump is played, the highest card of the leading suit wins.
            - The winner of each trick leads the next.
        5. Scoring:
            - After all 9 tricks, each player adds up the points from cards they won in tricks.
            - The difference between the predicted and actual score is calculated.
            - The player receives a penalty equal to the absolute difference. Example: prediction = 60, actual = 74 → penalty = 14.
        Reminders:
        - Play strictly by the rules (especially following suit).
        - Estimate your score based on your hand and the trump suit.
        - Avoid over- or under-shooting your prediction.
        - Try to hit your predicted score exactly.
        Trump suit: {game_state.trump_suit.name}\n"
        Leading suit: {game_state.leading_suit.name if game_state.leading_suit else 'None'}\n"
        Hand: {', '.join(card_str(c) for c in self.hand)}\n"

        Now guess how many points you will score this round (a number between 0 and 157). Output the number only.
        """
        self.guess = self.llm_func_point_guess(self.hand, prompt)
        self.guess = int(self.guess)
        print(f"{self.name} guesses {self.guess} points")

    def play_card(self, game_state):
        legal_cards = game_state.get_legal_cards(self.hand, game_state.leading_suit)

        def card_str(card):
            return f"{card.rank.name}-{card.suit.name}"

        prompt = f"""You are playing a variant of the Swiss card game Jass called Differenzler. The game uses a 36-card Swiss-German deck and is played with 4 players. Each round follows the same structure. Read all rules carefully and play according to them.
        CARD SETUP
        - Suits: Schellen (bells), Eicheln (acorns), Schilten (shields), Rosen (roses)
        - Ranks per suit: 6, 7, 8, 9, 10, Unter (Jack), Ober (Queen), King, Ace
        - Total cards: 36 (9 per player)
        - Each round, one suit is randomly selected as the trump suit. Trump cards are stronger than non-trump cards.
        If a suit is trump:
        - Jack is the strongest card (20 points). This is the only card that does not have to follow suit.
        - 9 is the second strongest card (14 points)
        - Ace is the third strongest card (11 points)
        - King is the fourth strongest card (4 points)
        - Queen is the fifth strongest card (3 points)
        - 10 is the sixth strongest card (10 points)
        - 8 is the seventh strongest card (0 points)
        - 7 is the eighth strongest card (0 points)
        - 6 is the weakest card (0 points)
        If a suit is not trump:
        - Ace is the strongest card (11 points)
        - King is the second strongest card (4 points)
        - Queen is the third strongest card (3 points)
        - Jack is the fourth strongest card (2 points)
        - 10 is the fifth strongest card (10 points)
        - 9 is the sixth strongest card (0 points)
        - 8 is the seventh strongest card (0 points)
        - 7 is the eighth strongest card (0 points)
        - 6 is the weakest card (0 points)
        - The player who plays the highest card of the leading suit wins the trick.
        - If a player cannot follow the leading suit, they can play any card.
        - The player who wins the trick leads the next trick.
        - The game continues until all cards have been played.
        Your goal is to minimize your total penalty over multiple rounds.
        The player with the lowest total penalty after all rounds is the winner.
        Round flow:
        1. Deal: Each player receives 9 cards.
        2. Trump: A trump suit is randomly selected and used for the round.
        3. Prediction: Before playing, each player privately predicts how many points they will score this round (a number between 0 and 157). This prediction stays secret until scoring.
        4. Play:
            - 9 tricks are played, one card per player per trick.
            - The player to the left of the dealer leads the first trick.
            - Each player must follow suit if possible.
            - If a player cannot follow suit, they may play any card, including trump.
            - The highest trump wins the trick. If no trump is played, the highest card of the leading suit wins.
            - The winner of each trick leads the next.
        5. Scoring:
            - After all 9 tricks, each player adds up the points from cards they won in tricks.
            - The difference between the predicted and actual score is calculated.
            - The player receives a penalty equal to the absolute difference. Example: prediction = 60, actual = 74 → penalty = 14.
        Reminders:
        - Play strictly by the rules (especially following suit).
        - Estimate your score based on your hand and the trump suit.
        - Avoid over- or under-shooting your prediction.
        - Try to hit your predicted score exactly.
        Trump suit: {game_state.trump_suit.name}\n"
        Leading suit: {game_state.leading_suit.name if game_state.leading_suit else 'None'}\n"
        Hand: {', '.join(card_str(c) for c in self.hand)}\n"
        Legal options: {', '.join(card_str(c) for c in legal_cards)}\n"
        Already played cards: {', '.join(card_str(c) for c in game_state.played_cards)}\n"
        Game history: {game_state.history}\n"
        Pick the best card to play and ONLY return the card string."""
        card = self.llm_func_card_choice(legal_cards, prompt)
        if card not in legal_cards:
            raise ValueError(f"{self.name} played illegal card: {card}")
        self.hand.remove(card)
        return card

    def __repr__(self):
        return "LLMPlayer (llm_func={self.llm_func.__name__})"


def chatgpt_llm_point_guess(legal_cards, prompt):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = openai_client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=10
    )
    answer = response.choices[0].message.content.strip()
    if answer.isdigit():
        answer = int(answer)
        if 0 <= answer <= 157:
            return answer
    print(f"ChatGPT returned illegal guess: {answer}")
    return random.randint(0, 157)


def chatgpt_llm_card_choice(legal_cards, prompt):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = openai_client.chat.completions.create(
        model="gpt-4o", messages=[{"role": "user", "content": prompt}], max_tokens=10
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


def anthropic_llm_point_guess(legal_cards, prompt):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
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


def anthropic_llm_card_choice(legal_cards, prompt):
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",
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
