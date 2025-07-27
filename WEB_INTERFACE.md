# Jass Web Interface

## Overview
The web interface allows you to play Swiss Jass (Differenzler) against AI opponents in your browser. The interface provides a complete game experience with interactive cards, real-time gameplay, and score tracking.

## Getting Started

### Prerequisites
- Python virtual environment (recommended)
- Required packages (install with `pip install -r requirements.txt`)
- API keys for OpenAI and Anthropic in `secrets.env`

### Running the Game
1. Start the web server:
   ```bash
   python app.py
   ```
2. Open your browser and go to: `http://localhost:5001`
3. Click "Start Playing" to begin

## Game Flow

### 1. Player Setup
- Enter your name when prompted
- The game automatically creates 3 AI opponents:
  - ChatGPT-4o-mini
  - ChatGPT-4.1 
  - Claude-3.5-Sonnet

### 2. Game Structure
- **5 rounds per game**
- **9 tricks per round**
- **4 players total** (you + 3 AI opponents)

### 3. Round Flow
1. **Cards are dealt** (9 cards per player)
2. **Trump suit is announced** (randomly selected)
3. **Make your guess** - predict how many points you'll score (0-157)
4. **Play tricks** - select cards from your hand when it's your turn
5. **Round scoring** - your penalty = |actual score - predicted score|

### 4. Playing Cards
- **Legal cards are highlighted in green**
- **Illegal cards are grayed out**
- **Click on a card to play it**
- **Follow suit if possible** (trump can always be played)

## Interface Elements

### Game Board
- **Trump suit display** - shows current trump
- **Round counter** - current round number
- **Trick area** - shows cards played in current trick
- **Opponent info** - AI player names and scores

### Your Area
- **Hand display** - your 9 cards (decreases as you play)
- **Score tracker** - your current penalty points
- **Guess display** - shows your prediction for the round

### Messages
- **Game log** - shows all game events and actions
- **Turn indicators** - tells you when it's your turn
- **Results** - shows trick winners and round results

## Scoring System

### Card Values
**Trump cards:**
- Jack: 20 points (highest trump)
- Nine: 14 points  
- Ace: 11 points
- Ten: 10 points
- King: 4 points
- Queen: 3 points
- Eight, Seven, Six: 0 points

**Non-trump cards:**
- Ace: 11 points (highest non-trump)
- Ten: 10 points
- King: 4 points
- Queen: 3 points
- Jack: 2 points
- Nine, Eight, Seven, Six: 0 points

### Penalty Calculation
- **Goal**: Predict your exact score
- **Penalty**: Absolute difference between predicted and actual score
- **Winner**: Player with lowest total penalty after all rounds

## Tips for Playing
1. **Count your sure points** - Aces and high trumps
2. **Watch the trump suit** - Jack of trumps is always strongest
3. **Consider your position** - playing last can be advantageous
4. **Track played cards** - remember what's been played
5. **Adjust predictions** - be conservative if unsure

## Technical Details
- **WebSocket communication** for real-time updates
- **SVG card graphics** for crisp display
- **Responsive design** works on desktop browsers
- **No page refreshes** - seamless gameplay experience

## Troubleshooting
- **Port conflict?** The game runs on port 5001 by default
- **Cards not loading?** Check browser console for errors
- **Game stuck?** Refresh the page and start a new game
- **AI not responding?** Ensure API keys are properly set in `secrets.env`

Enjoy playing Swiss Jass against AI opponents! 