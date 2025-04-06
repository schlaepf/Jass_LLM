from game import DifferenzlerGame
from player import (
    RandomGuesser,
    HumanPlayer,
    LLMPlayer,
    anthropic_llm_card_choice,
    anthropic_llm_point_guess,
    chatgpt_llm_point_guess,
    chatgpt_llm_card_choice,
)
from dotenv import load_dotenv


def main():
    load_dotenv("secrets.env")
    players = [
        HumanPlayer("Human"),
        LLMPlayer("ChatGPT", chatgpt_llm_point_guess, chatgpt_llm_card_choice),
        LLMPlayer("Anthropic", anthropic_llm_point_guess, anthropic_llm_card_choice),
        RandomGuesser("RandomBot"),
    ]
    game = DifferenzlerGame(players)
    game.play_game()


if __name__ == "__main__":
    main()
