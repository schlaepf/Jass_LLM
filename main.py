from game import DifferenzlerGame
from player import (
    RandomGuesser,
    HumanPlayer,
    LLMPlayer,
    LLMPlayerAnthropic,
    LLMPlayerChatGPT,
    LLMPlayerGemma,
)
from dotenv import load_dotenv


def main():
    load_dotenv("secrets.env")
    players = [
        # HumanPlayer("Human"),
        # LLMPlayerGemma("Gemma"),
        LLMPlayerChatGPT("ChatGPT", "gpt-4.1-2025-04-14"),
        LLMPlayerChatGPT("ChatGPT", "o4-mini-2025-04-16"),
        LLMPlayerAnthropic("Anthropic", "claude-3-7-sonnet-20250219"),
        LLMPlayerChatGPT("ChatGPT", "gpt-4o-2024-05-13"),
        # LLMPlayerChatGPT("o3-mini", "o3-mini"),
    ]
    n_games = 4
    for i in range(n_games):
        game = DifferenzlerGame(players, n_rounds=1)
        game.play_game()


if __name__ == "__main__":
    main()
