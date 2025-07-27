from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import uuid
from threading import Thread
import time

from game import DifferenzlerGame
from player import LLMPlayerChatGPT, LLMPlayerAnthropic
from web_player import WebPlayer
from web_game_manager import WebGameManager
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global game manager
game_manager = WebGameManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    return render_template('game.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to Jass game server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    game_manager.remove_player(request.sid)

@socketio.on('start_game')
def handle_start_game(data):
    player_name = data.get('player_name', 'Human Player')
    
    # Create human player
    human_player = WebPlayer(player_name, request.sid)
    
    # Create AI players with different models
    ai_players = [
        LLMPlayerChatGPT("ChatGPT-4o-mini", "gpt-4o-mini"),
        LLMPlayerChatGPT("ChatGPT-4.1", "gpt-4.1-2025-04-14"),
        LLMPlayerAnthropic("Claude-3.5-Sonnet", "claude-3-5-sonnet-latest")
    ]
    
    all_players = [human_player] + ai_players
    
    # Create and start game
    game = DifferenzlerGame(all_players, n_rounds=5)  # 5 rounds per game
    game_id = game_manager.create_game(game, human_player)
    
    join_room(game_id)
    
    # Start game in a separate thread
    def run_game():
        game_manager.start_game(game_id, socketio)
    
    thread = Thread(target=run_game)
    thread.daemon = True
    thread.start()
    
    emit('game_started', {'game_id': game_id, 'players': [str(p) for p in all_players]})

@socketio.on('make_guess')
def handle_make_guess(data):
    game_id = data.get('game_id')
    guess = data.get('guess')
    
    if game_manager.handle_guess(game_id, request.sid, guess):
        emit('guess_received', {'guess': guess})
    else:
        emit('error', {'message': 'Invalid guess'})

@socketio.on('play_card')
def handle_play_card(data):
    game_id = data.get('game_id')
    card_suit = data.get('card_suit')
    card_rank = data.get('card_rank')
    
    if game_manager.handle_card_play(game_id, request.sid, card_suit, card_rank):
        emit('card_played', {'card_suit': card_suit, 'card_rank': card_rank})
    else:
        emit('error', {'message': 'Invalid card play'})

if __name__ == '__main__':
    load_dotenv("secrets.env")
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
