from player import Player
import time

class WebPlayer(Player):
    def __init__(self, name, session_id):
        super().__init__(name)
        self.session_id = session_id
        self.waiting_for_input = False
        self.input_type = None
        self.input_data = None
    
    def make_guess(self, game_state):
        """
        This method will be called by the game, but the actual guess
        will be handled by the WebGameManager through WebSocket communication
        """
        # The WebGameManager will set self.guess when the human player responds
        pass
    
    def play_card(self, game_state):
        """
        This method will be called by the game, but the actual card selection
        will be handled by the WebGameManager through WebSocket communication
        """
        # The WebGameManager will handle card selection and removal from hand
        # This should not be called directly in the web version
        raise NotImplementedError("WebPlayer card plays are handled by WebGameManager")
    
    def __repr__(self):
        return f"{self.name} (Human)" 