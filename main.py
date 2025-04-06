from game import DifferenzlerGame
from player import RandomGuesser, HumanPlayer, LLMPlayer, anthropic_llm, chatgpt_llm


def main():
    players = [
        HumanPlayer("You"),
        LLMPlayer("ChatGPT", chatgpt_llm),
        LLMPlayer("Anthropic", anthropic_llm),
        RandomGuesser("RandomBot"),
    ]
    game = DifferenzlerGame(players)
    game.play_round()


if __name__ == "__main__":
    main()
