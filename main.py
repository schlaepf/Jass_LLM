from game import DifferenzlerGame
from player import RandomGuesser, HumanPlayer, LLMPlayer, anthropic_llm, chatgpt_llm
from dotenv import load_dotenv


def main():
    load_dotenv("secrets.env")
    players = [
        HumanPlayer("You"),
        LLMPlayer("ChatGPT", chatgpt_llm),
        LLMPlayer("Anthropic", anthropic_llm),
        RandomGuesser("RandomBot"),
    ]
    game = DifferenzlerGame(players)
    game.play_game()


if __name__ == "__main__":
    main()
