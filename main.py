from game import DifferenzlerGame
from player import RandomGuesser, HumanPlayer

def main():
    players = [
        RandomGuesser("RandomBot"),
        HumanPlayer("You"),
        RandomGuesser("BotA"),
        RandomGuesser("BotB"),
    ]
    game = DifferenzlerGame(players)
    game.deal_cards()
    game.play_round()
    game.print_scores()

if __name__ == "__main__":
    main()
