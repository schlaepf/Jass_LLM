// Game JavaScript
class JassGame {
    constructor() {
        this.socket = io();
        this.gameId = null;
        this.playerName = '';
        this.currentHand = [];
        this.legalCards = [];
        this.currentTrick = [];
        this.gameState = 'waiting'; // waiting, playing, guessing, card_selection
        this.opponentCardCounts = {}; // Track remaining cards for each AI player
        this.currentPlayerOrder = []; // Track player order for current trick
        this.currentPlayerIndex = 0; // Index of currently active player
        this.lastRoundData = null; // Store round data for scoreboard
        
        this.initializeEventListeners();
        this.setupSocketListeners();
    }

    initializeEventListeners() {
        // Start game button
        document.getElementById('start-game-btn').addEventListener('click', () => {
            this.showPlayerNameModal();
        });

        // Player name confirmation
        document.getElementById('confirm-name-btn').addEventListener('click', () => {
            const name = document.getElementById('player-name-input').value.trim();
            if (name) {
                this.playerName = name;
                this.startGame();
                this.hideModal('player-name-modal');
            }
        });

        // Guess confirmation
        document.getElementById('confirm-guess-btn').addEventListener('click', () => {
            const guess = parseInt(document.getElementById('guess-input').value);
            if (guess >= 0 && guess <= 157) {
                this.makeGuess(guess);
                this.hideModal('guess-modal');
            }
        });

        // New game buttons
        document.getElementById('new-game-btn').addEventListener('click', () => {
            this.resetGame();
        });

        document.getElementById('new-game-after-finish-btn').addEventListener('click', () => {
            this.hideModal('game-over-modal');
            this.resetGame();
        });

        // Close scoreboard button
        document.getElementById('close-scoreboard-btn').addEventListener('click', () => {
            console.log('Closing scoreboard modal');
            this.hideModal('round-scoreboard-modal');
        });

        // Debug: Test modal visibility (remove this later)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'T' && e.ctrlKey) {
                console.log('🧪 Testing modal visibility');
                const modal = document.getElementById('round-scoreboard-modal');
                if (modal) {
                    modal.style.display = 'block';
                    console.log('🧪 Test modal should be visible');
                } else {
                    console.error('🧪 Modal element not found');
                }
            }
        });

        // Enter key handlers
        document.getElementById('player-name-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                document.getElementById('confirm-name-btn').click();
            }
        });

        document.getElementById('guess-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                document.getElementById('confirm-guess-btn').click();
            }
        });
    }

    setupSocketListeners() {
        this.socket.on('connected', (data) => {
            console.log('Connected to server:', data.message);
            this.addMessage('Connected to game server');
        });

        this.socket.on('game_started', (data) => {
            console.log('Game started:', data);
            this.gameId = data.game_id;
            this.gameState = 'playing';
            
            // Filter out the human player properly
            const aiPlayers = data.players.filter(player => 
                !player.includes('Human') && player !== this.playerName
            );
            
            // Update AI player names from the actual game data
            if (aiPlayers.length >= 3) {
                document.getElementById('opponent-1-name').textContent = aiPlayers[0];
                document.getElementById('opponent-2-name').textContent = aiPlayers[1];
                document.getElementById('opponent-3-name').textContent = aiPlayers[2];
            }
            
            this.addMessage('Game started! Playing against: ' + aiPlayers.join(', '));
            this.updateGameControls();
        });

        this.socket.on('round_start', (data) => {
            console.log('Round started:', data);
            this.updateRoundInfo(data.round, data.trump_suit);
            this.updatePlayerHand(data.hand);
            this.updateOpponentCards(9); // Each player starts with 9 cards
            this.clearActivePlayerHighlight(); // Clear any previous highlighting
            this.addMessage(`Round ${data.round} started! Trump suit: ${data.trump_suit}`);
        });

        this.socket.on('request_guess', (data) => {
            console.log('Guess requested:', data);
            this.gameState = 'guessing';
            this.showGuessModal(data.trump_suit, data.hand);
        });

        this.socket.on('round_guess_results', (data) => {
            console.log('🎯 Round guess results received:', data);
            this.addMessage('--- Round Results ---');
            data.results.forEach(result => {
                this.addMessage(`Player ${result.player} guessed ${result.guess} points, scored ${result.actual}, difference: ${result.difference}`);
            });
            // Show the scoreboard modal with both round results and total scores
            console.log('🎯 About to show scoreboard modal');
            this.showRoundScoreboard(data.results, data.round_data);
        });

        this.socket.on('trick_start', (data) => {
            console.log('Trick started:', data);
            this.updateTrickInfo(data.trick_number);
            this.currentTrick = [];
            this.currentPlayerOrder = data.player_order;
            this.currentPlayerIndex = 0;
            this.updateTrickDisplay();
            this.highlightActivePlayer();
            this.addMessage(`Trick ${data.trick_number} started`);
        });

        this.socket.on('request_card', (data) => {
            console.log('Card requested:', data);
            this.gameState = 'card_selection';
            this.legalCards = data.legal_cards;
            this.currentTrick = data.current_trick;
            this.updateTrickDisplay();
            this.enableCardSelection();
            this.highlightActivePlayer(); // Ensure human player is highlighted
            this.addMessage('Your turn! Select a card to play.');
        });

        this.socket.on('card_played', (data) => {
            console.log('Card played:', data);
            this.addMessage(`${data.player} played ${data.card.rank}-${data.card.suit}`);
            this.currentTrick = data.trick;
            this.updateTrickDisplay();
            
            // Remove card from hand if it was played by human player
            if (data.player.includes('Human') || data.player === this.playerName) {
                this.removeCardFromHand(data.card);
            } else {
                // Update opponent card count when AI plays a card
                console.log('🃏 Updating card count for AI player:', data.player);
                console.log('🃏 Current counts before update:', this.opponentCardCounts);
                this.updateOpponentCardCount(data.player);
                console.log('🃏 Current counts after update:', this.opponentCardCounts);
            }
            
            // Move to next player and update highlighting
            this.currentPlayerIndex++;
            if (this.currentPlayerIndex < this.currentPlayerOrder.length) {
                this.highlightActivePlayer();
            }
        });

        this.socket.on('trick_complete', (data) => {
            console.log('Trick complete:', data);
            this.addMessage(`${data.winner} won the trick!`);
            this.showTrickWinner(data.winner);
            this.gameState = 'playing';
            this.disableCardSelection();
            this.clearActivePlayerHighlight(); // Remove all highlighting
            
            // Clear trick after a delay
            setTimeout(() => {
                this.clearTrick();
            }, 3000);
        });

        this.socket.on('round_complete', (data) => {
            console.log('Round complete:', data);
            this.addMessage(`Round ${data.round} complete!`);
            this.updateAllScores(data.scores);
            // Store the round and scores for the scoreboard
            this.lastRoundData = data;
        });

        this.socket.on('game_complete', (data) => {
            console.log('Game complete:', data);
            this.addMessage(`Game complete! Winner: ${data.winner}`);
            this.showGameOverModal(data.final_scores, data.winner);
            this.gameState = 'finished';
            this.updateGameControls();
        });

        this.socket.on('error', (data) => {
            console.error('Game error:', data);
            this.addMessage('Error: ' + data.message);
        });
    }

    startGame() {
        if (this.playerName) {
            this.socket.emit('start_game', {
                player_name: this.playerName
            });
            document.getElementById('human-name').textContent = this.playerName;
        }
    }

    makeGuess(guess) {
        if (this.gameId) {
            this.socket.emit('make_guess', {
                game_id: this.gameId,
                guess: guess
            });
            this.addMessage(`You made your guess`);
        }
    }

    playCard(card) {
        if (this.gameId && this.gameState === 'card_selection') {
            this.socket.emit('play_card', {
                game_id: this.gameId,
                card_suit: card.suit,
                card_rank: card.rank
            });
            this.gameState = 'playing';
            this.disableCardSelection();
        }
    }

    // UI Management Methods
    showPlayerNameModal() {
        document.getElementById('player-name-modal').style.display = 'block';
        document.getElementById('player-name-input').focus();
    }

    showGuessModal(trumpSuit, hand) {
        document.getElementById('guess-trump-suit').textContent = trumpSuit;
        
        // Render visual cards in the guess modal
        const guessHandCards = document.getElementById('guess-hand-cards');
        guessHandCards.innerHTML = '';
        
        hand.forEach((card) => {
            const cardDiv = document.createElement('div');
            cardDiv.className = 'card';
            cardDiv.style.backgroundImage = `url('/static/cards/${card.rank}-${card.suit}.svg')`;
            cardDiv.title = `${card.rank}-${card.suit}`;
            guessHandCards.appendChild(cardDiv);
        });
        
        document.getElementById('guess-modal').style.display = 'block';
        document.getElementById('guess-input').focus();
    }

    showGameOverModal(scores, winner) {
        const resultsDiv = document.getElementById('final-results');
        resultsDiv.innerHTML = '<h3>Final Scores:</h3>';
        
        Object.entries(scores).forEach(([player, score]) => {
            const row = document.createElement('div');
            row.className = 'result-row';
            if (player === winner) {
                row.classList.add('winner');
            }
            row.innerHTML = `<span>${player}</span><span>${score} points</span>`;
            resultsDiv.appendChild(row);
        });
        
        document.getElementById('game-over-modal').style.display = 'block';
    }

    showRoundScoreboard(roundResults, roundData) {
        console.log('Showing round scoreboard:', roundResults, roundData);
        
        // Set round number
        document.getElementById('scoreboard-round-number').textContent = roundData.round;
        
        // Populate round results table
        const roundResultsTable = document.getElementById('round-results-table');
        roundResultsTable.innerHTML = '';
        
        roundResults.forEach(result => {
            const row = document.createElement('div');
            row.className = 'result-row';
            
            // Highlight human player
            if (result.player.includes('Human') || result.player === this.playerName) {
                row.classList.add('human-player');
            }
            
            row.innerHTML = `
                <span class="player-name">${result.player}</span>
                <div class="player-stats">
                    <span>Guessed: ${result.guess}</span>
                    <span>Scored: ${result.actual}</span>
                    <span>Diff: ${result.difference}</span>
                </div>
            `;
            roundResultsTable.appendChild(row);
        });
        
        // Populate total scores table
        const totalScoresTable = document.getElementById('total-scores-table');
        totalScoresTable.innerHTML = '';
        
        Object.entries(roundData.scores).forEach(([player, score]) => {
            const row = document.createElement('div');
            row.className = 'result-row';
            
            // Highlight human player
            if (player.includes('Human') || player === this.playerName) {
                row.classList.add('human-player');
            }
            
            row.innerHTML = `
                <span class="player-name">${player}</span>
                <div class="player-stats">
                    <span>Total: ${score} points</span>
                </div>
            `;
            totalScoresTable.appendChild(row);
        });
        
        // Show the modal
        const modal = document.getElementById('round-scoreboard-modal');
        console.log('Modal element:', modal);
        if (modal) {
            modal.style.display = 'block';
            console.log('Modal should now be visible');
        } else {
            console.error('Could not find round-scoreboard-modal element');
        }
    }

    hideModal(modalId) {
        document.getElementById(modalId).style.display = 'none';
    }

    updateRoundInfo(round, trumpSuit) {
        document.getElementById('current-round').textContent = round;
        document.getElementById('trump-suit').textContent = trumpSuit;
    }

    updateTrickInfo(trickNumber) {
        document.getElementById('trick-number').textContent = `Trick ${trickNumber}`;
        document.getElementById('trick-winner').textContent = '';
    }

    updatePlayerHand(hand) {
        this.currentHand = hand;
        const handDiv = document.getElementById('player-hand');
        handDiv.innerHTML = '';
        
        hand.forEach((card, index) => {
            const cardDiv = document.createElement('div');
            cardDiv.className = 'card';
            cardDiv.style.backgroundImage = `url('/static/cards/${card.rank}-${card.suit}.svg')`;
            cardDiv.dataset.suit = card.suit;
            cardDiv.dataset.rank = card.rank;
            cardDiv.dataset.index = index;
            
            cardDiv.addEventListener('click', () => {
                if (this.gameState === 'card_selection') {
                    const isLegal = this.legalCards.some(legalCard => 
                        legalCard.suit === card.suit && legalCard.rank === card.rank
                    );
                    
                    if (isLegal) {
                        this.playCard(card);
                    }
                }
            });
            
            handDiv.appendChild(cardDiv);
        });
    }

    updateTrickDisplay() {
        // Clear all card areas first
        this.clearAllPlayedCards();
        
        this.currentTrick.forEach((play) => {
            const cardDiv = document.createElement('div');
            cardDiv.className = 'trick-card';
            cardDiv.style.backgroundImage = `url('/static/cards/${play.card.rank}-${play.card.suit}.svg')`;
            cardDiv.title = `${play.player}: ${play.card.rank}-${play.card.suit}`;
            
            // Place card in the appropriate position based on player
            const cardArea = this.getPlayerCardArea(play.player);
            if (cardArea) {
                cardArea.appendChild(cardDiv);
            }
        });
    }

    getPlayerCardArea(playerName) {
        // Human player always at bottom
        if (playerName.includes('Human') || playerName === this.playerName) {
            return document.getElementById('played-card-bottom');
        }
        
        // AI players - map to positions based on their UI position
        const opponent1Name = document.getElementById('opponent-1-name').textContent;
        const opponent2Name = document.getElementById('opponent-2-name').textContent;
        const opponent3Name = document.getElementById('opponent-3-name').textContent;
        
        if (playerName === opponent1Name) {
            return document.getElementById('played-card-left');  // Left position
        } else if (playerName === opponent2Name) {
            return document.getElementById('played-card-top');   // Top position
        } else if (playerName === opponent3Name) {
            return document.getElementById('played-card-right'); // Right position
        }
        
        console.warn('Could not find card area for player:', playerName);
        return document.getElementById('played-card-bottom'); // Fallback
    }

    clearAllPlayedCards() {
        ['played-card-left', 'played-card-top', 'played-card-right', 'played-card-bottom'].forEach(areaId => {
            const area = document.getElementById(areaId);
            if (area) {
                area.innerHTML = '';
            }
        });
    }

    enableCardSelection() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            const suit = card.dataset.suit;
            const rank = card.dataset.rank;
            
            const isLegal = this.legalCards.some(legalCard => 
                legalCard.suit === suit && legalCard.rank === rank
            );
            
            if (isLegal) {
                card.classList.add('legal');
                card.classList.remove('illegal');
            } else {
                card.classList.add('illegal');
                card.classList.remove('legal');
            }
        });
    }

    disableCardSelection() {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.classList.remove('legal', 'illegal');
        });
    }

    removeCardFromHand(playedCard) {
        this.currentHand = this.currentHand.filter(card => 
            !(card.suit === playedCard.suit && card.rank === playedCard.rank)
        );
        this.updatePlayerHand(this.currentHand);
    }

    showTrickWinner(winner) {
        document.getElementById('trick-winner').textContent = `Winner: ${winner}`;
    }

    clearTrick() {
        this.currentTrick = [];
        this.clearAllPlayedCards();
        document.getElementById('trick-winner').textContent = '';
    }

    highlightActivePlayer() {
        // Clear all highlighting first
        this.clearActivePlayerHighlight();
        
        if (this.currentPlayerOrder.length === 0 || this.currentPlayerIndex >= this.currentPlayerOrder.length) {
            return;
        }
        
        const currentPlayer = this.currentPlayerOrder[this.currentPlayerIndex];
        
        // Highlight human player
        if (currentPlayer.includes('Human') || currentPlayer === this.playerName) {
            document.querySelector('.human-player').classList.add('active-player');
        } else {
            // Highlight AI player
            const aiPlayers = document.querySelectorAll('.opponent .player-name');
            aiPlayers.forEach(nameElement => {
                if (nameElement.textContent === currentPlayer) {
                    nameElement.closest('.opponent').classList.add('active-player');
                }
            });
        }
    }

    clearActivePlayerHighlight() {
        // Remove highlighting from all players
        document.querySelector('.human-player').classList.remove('active-player');
        document.querySelectorAll('.opponent').forEach(opponent => {
            opponent.classList.remove('active-player');
        });
    }

    updateOpponentCards(cardCount) {
        console.log('🃏 Initializing opponent cards with count:', cardCount);
        
        // Update card backs for all AI players and initialize counts
        ['opponent-1-cards', 'opponent-2-cards', 'opponent-3-cards'].forEach((playerId, index) => {
            const cardsContainer = document.getElementById(playerId);
            cardsContainer.innerHTML = '';
            
            for (let i = 0; i < cardCount; i++) {
                const cardBack = document.createElement('div');
                cardBack.className = 'card-back';
                cardsContainer.appendChild(cardBack);
            }
            
            // Initialize card count tracking
            const playerName = document.getElementById(playerId.replace('-cards', '-name')).textContent;
            this.opponentCardCounts[playerName] = cardCount;
            console.log('🃏 Set', playerName, 'to', cardCount, 'cards');
        });
        
        console.log('🃏 Final opponent card counts:', this.opponentCardCounts);
    }

    updateOpponentCardCount(playerName) {
        console.log('🃏 updateOpponentCardCount called for:', playerName);
        console.log('🃏 Available player counts:', Object.keys(this.opponentCardCounts));
        
        // Decrease card count for the player who played a card
        if (this.opponentCardCounts[playerName] > 0) {
            this.opponentCardCounts[playerName]--;
            console.log('🃏 Decreased count for', playerName, 'to', this.opponentCardCounts[playerName]);
            
            // Find the corresponding card container and update display
            const playerNameElements = document.querySelectorAll('.opponent .player-name');
            let found = false;
            playerNameElements.forEach(nameElement => {
                if (nameElement.textContent === playerName) {
                    found = true;
                    const cardsContainer = nameElement.closest('.opponent').querySelector('.player-cards');
                    cardsContainer.innerHTML = '';
                    
                    // Render remaining cards
                    for (let i = 0; i < this.opponentCardCounts[playerName]; i++) {
                        const cardBack = document.createElement('div');
                        cardBack.className = 'card-back';
                        cardsContainer.appendChild(cardBack);
                    }
                    console.log('🃏 Updated display for', playerName, 'with', this.opponentCardCounts[playerName], 'cards');
                }
            });
            
            if (!found) {
                console.warn('🃏 Could not find UI element for player:', playerName);
                console.log('🃏 Available player name elements:', Array.from(playerNameElements).map(el => el.textContent));
            }
        } else {
            console.warn('🃏 No cards left to remove for player:', playerName, 'current count:', this.opponentCardCounts[playerName]);
        }
    }

    updateAllScores(scores) {
        Object.entries(scores).forEach(([player, score]) => {
            if (player.includes('Human')) {
                document.getElementById('human-score').textContent = score;
            } else {
                // Update AI player scores
                const aiPlayers = document.querySelectorAll('.opponent .player-name');
                aiPlayers.forEach(nameElement => {
                    if (nameElement.textContent === player) {
                        const scoreElement = nameElement.parentElement.querySelector('.player-score');
                        scoreElement.textContent = score;
                    }
                });
            }
        });
    }

    updateGameControls() {
        const startBtn = document.getElementById('start-game-btn');
        const newGameBtn = document.getElementById('new-game-btn');
        
        if (this.gameState === 'waiting') {
            startBtn.style.display = 'block';
            newGameBtn.style.display = 'none';
        } else {
            startBtn.style.display = 'none';
            newGameBtn.style.display = 'block';
        }
    }

    addMessage(message) {
        const messagesDiv = document.getElementById('game-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message fade-in';
        messageDiv.textContent = message;
        
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        
        // Remove old messages if there are too many
        while (messagesDiv.children.length > 20) {
            messagesDiv.removeChild(messagesDiv.firstChild);
        }
    }

    resetGame() {
        this.gameId = null;
        this.gameState = 'waiting';
        this.currentHand = [];
        this.legalCards = [];
        this.currentTrick = [];
        this.currentPlayerOrder = [];
        this.currentPlayerIndex = 0;
        this.lastRoundData = null;
        
        // Reset UI
        document.getElementById('current-round').textContent = '-';
        document.getElementById('trump-suit').textContent = '-';
        document.getElementById('human-score').textContent = '0';
        document.getElementById('player-hand').innerHTML = '';
        this.clearAllPlayedCards();
        document.getElementById('trick-number').textContent = 'Trick 1';
        document.getElementById('trick-winner').textContent = '';
        
        // Reset opponent scores
        document.querySelectorAll('.opponent .player-score').forEach(scoreElement => {
            scoreElement.textContent = '0';
        });
        
        // Clear highlighting
        this.clearActivePlayerHighlight();
        
        // Clear messages
        document.getElementById('game-messages').innerHTML = 
            '<div class="message">Welcome to Swiss Jass! Click "Start Game" to begin.</div>';
        
        this.updateGameControls();
        this.showPlayerNameModal();
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Jass Game...');
    window.jassGame = new JassGame();
}); 