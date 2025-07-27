# Swiss Jass - Differenzler

A web-based implementation of the Swiss card game "Differenzler" where human players can compete against AI opponents powered by state-of-the-art language models.

## 🎮 Game Overview

**Differenzler** is a variant of Swiss Jass where players predict their exact score each round. The goal is to minimize penalty points by accurately predicting how many points you'll score. The player with the lowest total penalty after all rounds wins.

- **4 players**: 1 human + 3 AI opponents
- **5 rounds per game**
- **9 tricks per round**
- **36-card Swiss deck** with traditional suits (Schellen, Eicheln, Schilten, Rosen)

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Virtual environment** (recommended)
- **API Keys** for OpenAI and Anthropic

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Jass_LLM
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API keys**
   Create a `secrets.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

### Running the Application

**Start the web server:**
```bash
python app.py
```

**Open your browser and navigate to:**
- **Homepage**: http://localhost:5001
- **Game Interface**: http://localhost:5001/game

**That's it!** Click "Start Playing" and enjoy Swiss Jass against AI opponents.

## 🏗️ Architecture

### Overview
The application uses a **unified Flask architecture** where a single server handles both backend game logic and frontend serving.

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│   Browser       │ ◄─────────────► │   Flask Server   │
│   (Frontend)    │                 │   (Backend)      │
└─────────────────┘                 └──────────────────┘
│                                           │
├── HTML/CSS/JS                             ├── Game Logic
├── SVG Cards                               ├── AI Players
├── Socket.IO Client                        ├── WebSocket Server
└── Real-time UI                            └── Static File Serving
```

### Core Components

#### **Backend (`app.py`)**
- **Flask web server** with Socket.IO for real-time communication
- **WebSocket handlers** for game events (start game, make guess, play card)
- **Game session management** via `WebGameManager`
- **AI player integration** with OpenAI and Anthropic APIs

#### **Game Logic**
- **`game.py`**: Core Differenzler game implementation
- **`card.py`**: Card definitions and Swiss Jass rules
- **`player.py`**: Player classes including LLM-powered AI players
- **`web_game_manager.py`**: Web-specific game session handling
- **`web_player.py`**: Human player interface for web

#### **Frontend**
- **`templates/`**: Jinja2 HTML templates
  - `index.html`: Landing page
  - `game.html`: Main game interface
- **`static/css/`**: Responsive styling with animations
- **`static/js/game.js`**: Client-side game logic and WebSocket communication
- **`static/cards/`**: 37 custom SVG card graphics (36 cards + back)

### Technology Stack

**Backend:**
- **Flask**: Web framework
- **Flask-SocketIO**: Real-time WebSocket communication
- **OpenAI API**: GPT model integration
- **Anthropic API**: Claude model integration
- **Python-dotenv**: Environment variable management

**Frontend:**
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Flexbox/Grid
- **JavaScript ES6+**: Client-side logic
- **Socket.IO**: Real-time client communication
- **SVG**: Scalable card graphics

## 📁 Project Structure

```
Jass_LLM/
├── app.py                 # Main Flask application
├── web_game_manager.py    # Web game session management
├── web_player.py          # Human player web interface
├── game.py                # Core game logic
├── player.py              # Player classes (Human, AI)
├── card.py                # Card definitions and rules
├── prompt.py              # LLM prompts for AI players
├── requirements.txt       # Python dependencies
├── secrets.env           # API keys (not in git)
├── WEB_INTERFACE.md      # Detailed usage guide
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── index.html        # Landing page
│   └── game.html         # Game interface
│
├── static/               # Frontend assets
│   ├── css/
│   │   ├── index.css     # Landing page styles
│   │   └── game.css      # Game interface styles
│   ├── js/
│   │   └── game.js       # Client-side game logic
│   └── cards/            # SVG card graphics
│       ├── card_back.svg
│       └── [RANK]-[SUIT].svg (36 cards)
│
└── [other files]         # Stats, analysis, original CLI version
```

## 🛠️ Development Guide

### Adding New Features

#### **Backend Changes**
1. **Game Logic**: Modify `game.py` or `card.py` for rule changes
2. **AI Players**: Update `player.py` or `prompt.py` for AI behavior
3. **Web Handlers**: Add new Socket.IO events in `app.py`
4. **Session Management**: Extend `web_game_manager.py` for new game features

#### **Frontend Changes**
1. **UI Elements**: Update `templates/game.html` for new interface components
2. **Styling**: Modify `static/css/game.css` for visual changes
3. **Interactions**: Extend `static/js/game.js` for new user interactions
4. **Real-time Events**: Add Socket.IO event handlers in JavaScript

### Code Style & Standards

- **Python**: Follow PEP 8 style guidelines
- **JavaScript**: Use ES6+ features, consistent naming
- **HTML**: Semantic markup, accessibility considerations
- **CSS**: BEM methodology for class naming, mobile-first approach

### Testing

**Manual Testing:**
```bash
# Start the server
python app.py

# Test different scenarios:
# - Complete game flow
# - Network disconnection
# - Invalid moves
# - AI response errors
```

**API Key Testing:**
- Ensure both OpenAI and Anthropic keys work
- Test AI decision-making in various game states

### Common Development Tasks

#### **Adding a New AI Model**
1. Create new player class in `player.py`
2. Add model configuration in `app.py`
3. Test integration with existing game flow

#### **Modifying Game Rules**
1. Update core logic in `game.py` or `card.py`
2. Adjust AI prompts in `prompt.py` if needed
3. Update frontend validation in `game.js`

#### **Improving UI/UX**
1. Identify user interaction points in `game.html`
2. Enhance styling in `game.css`
3. Add smooth transitions and feedback

## 🤝 Contributing

### Getting Started
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the development guide
4. **Test thoroughly** with different game scenarios
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Areas for Contribution

- **🎨 UI/UX Improvements**: Better animations, mobile support, accessibility
- **🤖 AI Enhancements**: New models, improved prompting strategies
- **🎮 Game Features**: Tournament mode, statistics dashboard, replay system
- **🔧 Technical**: Performance optimization, error handling, testing framework
- **📱 Mobile Support**: Responsive design improvements
- **🌐 Internationalization**: Multi-language support

### Issue Guidelines

When reporting issues:
- **Describe the bug** with steps to reproduce
- **Include browser/OS information**
- **Provide console error messages** if applicable
- **Suggest potential solutions** if you have ideas

## 📊 Game Statistics

The project includes analysis tools in the main directory:
- **`main.py`**: Original CLI version for AI vs AI games
- **`stats.py`**: Statistical analysis of game results
- **Various `.png` files**: Performance visualizations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Swiss Jass Rules**: Traditional Swiss card game
- **AI Models**: OpenAI GPT and Anthropic Claude
- **Card Graphics**: Custom SVG implementations
- **Community**: Contributors and players

---

**Ready to play Swiss Jass?** Start the server and challenge the AIs! 🃏🎯
