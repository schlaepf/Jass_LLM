import uuid
import threading
import time
from typing import Dict, Optional
from card import Card, Suit, Rank

class WebGameManager:
    def __init__(self):
        self.games: Dict[str, dict] = {}
        self.player_sessions: Dict[str, str] = {}  # session_id -> game_id
        self.locks: Dict[str, threading.Lock] = {}
        
    def create_game(self, game, human_player):
        game_id = str(uuid.uuid4())
        self.games[game_id] = {
            'game': game,
            'human_player': human_player,
            'waiting_for_human': False,
            'human_action_type': None,  # 'guess' or 'play_card'
            'human_action_data': None,
            'status': 'waiting_to_start'
        }
        self.player_sessions[human_player.session_id] = game_id
        self.locks[game_id] = threading.Lock()
        return game_id
    
    def remove_player(self, session_id):
        if session_id in self.player_sessions:
            game_id = self.player_sessions[session_id]
            del self.player_sessions[session_id]
            if game_id in self.games:
                # Mark game as abandoned
                self.games[game_id]['status'] = 'abandoned'
    
    def start_game(self, game_id, socketio):
        if game_id not in self.games:
            return
        
        game_data = self.games[game_id]
        game = game_data['game']
        human_player = game_data['human_player']
        
        game_data['status'] = 'playing'
        
        # Override the game's play_game method to handle web interactions
        self._play_web_game(game, game_id, socketio)
    
    def _play_web_game(self, game, game_id, socketio):
        """Modified version of play_game that handles web interactions"""
        for round_num in range(game.n_rounds):
            self._play_web_round(game, game_id, socketio, round_num + 1)
            game.rounds_played += 1
            
            # Send round results to client
            socketio.emit('round_complete', {
                'round': round_num + 1,
                'scores': {str(player): player.points for player in game.players}
            }, room=game_id)
            
            time.sleep(2)  # Brief pause between rounds
        
        # Game complete
        final_scores = {str(player): player.points for player in game.players}
        winner = min(game.players, key=lambda p: p.points)
        
        socketio.emit('game_complete', {
            'final_scores': final_scores,
            'winner': str(winner)
        }, room=game_id)
    
    def _play_web_round(self, game, game_id, socketio, round_num):
        """Modified version of play_round that handles web interactions"""
        game.setup_round()
        game.deal_cards()
        
        # Send round start info to client
        human_player = self.games[game_id]['human_player']
        socketio.emit('round_start', {
            'round': round_num,
            'trump_suit': game.trump_suit.name,
            'hand': self._serialize_cards(human_player.hand)
        }, room=game_id)
        
        # Collect guesses (including from human player)
        self._collect_web_guesses(game, game_id, socketio)
        
        # Play tricks
        player_order = game.players[:]
        for trick_num in range(game.N_TRICKS):
            winner = self._play_web_trick(game, game_id, socketio, player_order, trick_num + 1)
            
            # Update player order for next trick
            winner_index = player_order.index(winner)
            player_order = player_order[winner_index:] + player_order[:winner_index]
        
        game.score_players()
        
        # Send round results with guess vs actual comparisons
        round_results = []
        for player in game.players:
            total_points = sum(
                card.point_value(game.trump_suit)
                for trick in player.tricks_won
                for card in trick
            )
            diff = abs(player.guess - total_points)
            round_results.append({
                'player': str(player),
                'guess': player.guess,
                'actual': total_points,
                'difference': diff
            })
        
        socketio.emit('round_guess_results', {
            'results': round_results,
            'round_data': {
                'round': round_num,
                'scores': {str(player): player.points for player in game.players}
            }
        }, room=game_id)
    
    def _collect_web_guesses(self, game, game_id, socketio):
        """Collect guesses from all players, handling human player via web"""
        human_player = self.games[game_id]['human_player']
        
        # Request guess from human player
        socketio.emit('request_guess', {
            'trump_suit': game.trump_suit.name,
            'hand': self._serialize_cards(human_player.hand)
        }, room=game_id)
        
        # Wait for human guess
        self._wait_for_human_action(game_id, 'guess')
        
        # Collect guesses from AI players (but don't show them yet)
        for player in game.players:
            if player != human_player:
                player.make_guess(game)
    
    def _play_web_trick(self, game, game_id, socketio, player_order, trick_num):
        """Play a single trick with web interaction"""
        trick = []
        game.leading_suit = None
        human_player = self.games[game_id]['human_player']
        
        socketio.emit('trick_start', {
            'trick_number': trick_num,
            'player_order': [str(p) for p in player_order]
        }, room=game_id)
        
        for player in player_order:
            if player == human_player:
                # Request card from human player
                legal_cards = game.get_legal_cards(player.hand, game.leading_suit)
                socketio.emit('request_card', {
                    'legal_cards': self._serialize_cards(legal_cards),
                    'current_trick': self._serialize_trick(trick),
                    'leading_suit': game.leading_suit.name if game.leading_suit else None
                }, room=game_id)
                
                # Wait for human card selection
                self._wait_for_human_action(game_id, 'play_card')
                
                # Get the selected card
                card_data = self.games[game_id]['human_action_data']
                card = self._deserialize_card(card_data['suit'], card_data['rank'])
                player.hand.remove(card)
            else:
                # AI player
                card = player.play_card(game)
            
            if not game.leading_suit:
                game.leading_suit = card.suit
            
            trick.append((player, card))
            
            # Broadcast card play
            socketio.emit('card_played', {
                'player': str(player),
                'card': self._serialize_card(card),
                'trick': self._serialize_trick(trick)
            }, room=game_id)
            
            time.sleep(1)  # Brief pause between cards
        
        # Determine winner
        winner = game.determine_trick_winner(trick)
        winner.tricks_won.append([card for _, card in trick])
        
        # Update game state
        game.played_cards.extend(card for _, card in trick)
        game.n_tricks_played += 1
        
        # Add extra 5 points for last trick
        if game.n_tricks_played == game.N_TRICKS:
            winner.points += 5
            socketio.emit('card_played', {
                'player': str(winner),
                'card': None,
                'message': f'{winner} gets 5 extra points for the last trick!'
            }, room=game_id)
        
        socketio.emit('trick_complete', {
            'winner': str(winner),
            'trick': self._serialize_trick(trick)
        }, room=game_id)
        
        time.sleep(2)  # Pause before next trick
        
        return winner
    
    def _wait_for_human_action(self, game_id, action_type):
        """Wait for human player to take an action"""
        game_data = self.games[game_id]
        game_data['waiting_for_human'] = True
        game_data['human_action_type'] = action_type
        game_data['human_action_data'] = None
        
        # Poll until action is received
        while game_data['waiting_for_human'] and game_data['status'] != 'abandoned':
            time.sleep(0.1)
    
    def handle_guess(self, game_id, session_id, guess):
        """Handle guess from human player"""
        if game_id not in self.games:
            return False
        
        game_data = self.games[game_id]
        if (game_data['waiting_for_human'] and 
            game_data['human_action_type'] == 'guess' and
            game_data['human_player'].session_id == session_id):
            
            # Validate guess
            if not (0 <= guess <= 157):
                return False
            
            game_data['human_player'].guess = guess
            game_data['waiting_for_human'] = False
            game_data['human_action_data'] = {'guess': guess}
            return True
        
        return False
    
    def handle_card_play(self, game_id, session_id, card_suit, card_rank):
        """Handle card play from human player"""
        if game_id not in self.games:
            return False
        
        game_data = self.games[game_id]
        if (game_data['waiting_for_human'] and 
            game_data['human_action_type'] == 'play_card' and
            game_data['human_player'].session_id == session_id):
            
            # Validate card is in hand and legal
            try:
                card = self._deserialize_card(card_suit, card_rank)
                player = game_data['human_player']
                game = game_data['game']
                
                if card not in player.hand:
                    return False
                
                legal_cards = game.get_legal_cards(player.hand, game.leading_suit)
                if card not in legal_cards:
                    return False
                
                game_data['waiting_for_human'] = False
                game_data['human_action_data'] = {'suit': card_suit, 'rank': card_rank}
                return True
            except:
                return False
        
        return False
    
    def _serialize_card(self, card):
        """Convert card to JSON-serializable format"""
        return {
            'suit': card.suit.name,
            'rank': card.rank.name,
            'value': card.rank.value
        }
    
    def _serialize_cards(self, cards):
        """Convert list of cards to JSON-serializable format"""
        return [self._serialize_card(card) for card in cards]
    
    def _serialize_trick(self, trick):
        """Convert trick to JSON-serializable format"""
        return [
            {
                'player': str(player),
                'card': self._serialize_card(card)
            }
            for player, card in trick
        ]
    
    def _deserialize_card(self, suit_name, rank_name):
        """Convert JSON data back to Card object"""
        suit = Suit[suit_name]
        rank = Rank[rank_name]
        return Card(suit, rank) 