from game import DifferenzlerGame
from player import (
    RandomGuesser,
    HumanPlayer,
    LLMPlayer,
    LLMPlayerAnthropic,
    LLMPlayerChatGPT,
)
from dotenv import load_dotenv


def main():
    load_dotenv("secrets.env")
    players = [
        HumanPlayer("Human"),
        LLMPlayerChatGPT("ChatGPT"),
        LLMPlayerAnthropic("Anthropic"),
        LLMPlayerChatGPT("o3-mini", "o3-mini"),
    ]
    game = DifferenzlerGame(players, n_rounds=1)
    game.play_game()


if __name__ == "__main__":
    main()
