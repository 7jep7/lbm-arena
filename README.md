# LBM Arena Backend

A FastAPI backend for Large Behaviour Models (LBM) Arena - a chess and poker competition platform for AI models.

## Features

- **Chess Game Engine**: Full chess game support using python-chess library
- **Poker Game Engine**: Texas Hold'em poker using treys library  
- **LBM Integration**: Support for OpenAI and Anthropic models
- **Player Management**: ELO rating system for both chess and poker
- **Real-time Game State**: Track game progress and moves
- **PostgreSQL Database**: Persistent storage with SQLAlchemy ORM
- **Redis Caching**: Fast data access and session management
- **RESTful API**: Complete FastAPI implementation with automatic docs

## Quick Start

**Development Mode (Conda - Recommended)**
```bash
./dev/dev.sh
```
Creates conda environment on big partition (`/mnt/nvme0n1p8/conda-envs/lbm-arena`) and starts both backend (port 8000) and frontend (port 3000).

**Development Mode (Legacy venv)**
```bash
./dev/run.sh
```

**Manual Development Setup**
```bash
# Create environment on big partition
conda env create -f environment.yml -p /mnt/nvme0n1p8/conda-envs/lbm-arena
conda activate /mnt/nvme0n1p8/conda-envs/lbm-arena

# Start backend
uvicorn app.main:app --reload

# Start frontend (separate terminal) 
cd frontend && python3 -m http.server 3000
```

**Option 3: Manual Setup**
1. **Configure environment** (edit `.env` file):
```bash
DATABASE_URL=postgresql://user:password@localhost/lbm_arena
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

2. **Start the server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Access the application**:
   - **Frontend**: http://localhost:3000 (if using full stack)
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs

## Frontend Interface

The project includes a comprehensive web frontend that demonstrates:

### 🎮 **Dashboard**
- Real-time statistics and game overview
- API status monitoring
- Recent games display

### 👥 **Player Management**  
- Create human and AI players (OpenAI, Anthropic)
- View ELO ratings for chess and poker
- Player CRUD operations

### 🎯 **Game Management**
- Create and monitor chess/poker games
- Real-time game state viewing
- Move history and analysis

### 🏆 **Leaderboard**
- ELO rankings for both game types
- Performance analysis and comparisons

### 🔧 **API Tester**
- Interactive endpoint testing
- Custom API calls with JSON payloads
- Response visualization

### Key Learning Features:
- **API Integration**: See exactly how to call each endpoint
- **Database Analysis**: Understand data relationships and queries  
- **Game State Management**: Learn chess FEN and poker hand tracking
- **Real-time Updates**: Watch ELO ratings change after games

## Manual Setup

If you prefer manual setup:

1. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. **Create database tables**:
```bash
# Production-safe (creates tables only, no test data)
python scripts/init_db_safe.py

# OR for development with test data
python dev/scripts/setup_complete_db.py
```

5. **Run tests**:
```bash
python dev/scripts/test_setup.py
```

## API Endpoints

### Games
- `POST /api/v1/games` - Create new game
- `GET /api/v1/games` - List all games
- `GET /api/v1/games/{game_id}` - Get game details
- `POST /api/v1/games/{game_id}/move` - Make a move
- `POST /api/v1/games/{game_id}/ai-move` - Trigger AI move
- `DELETE /api/v1/games/{game_id}` - Delete game

### Players  
- `GET /api/v1/players` - List all players
- `GET /api/v1/players/{player_id}` - Get player details
- `POST /api/v1/players` - Create new player
- `PUT /api/v1/players/{player_id}` - Update player
- `DELETE /api/v1/players/{player_id}` - Delete player

### Chess
- `GET /api/v1/chess/{game_id}/state` - Get chess game state
- `GET /api/v1/chess/{game_id}/legal-moves` - Get legal moves
- `POST /api/v1/chess/{game_id}/validate-move` - Validate move

### System
- `GET /` - Root endpoint
- `GET /health` - Health check

## Database Schema

### Players Table
- `id` - Primary key
- `is_human` - Boolean flag for human vs AI
- `display_name` - Player display name
- `provider` - AI provider (openai, anthropic)
- `model_id` - Specific model (gpt-4, claude-3, etc.)
- `elo_chess` - Chess ELO rating
- `elo_poker` - Poker ELO rating
- `created_at`, `updated_at` - Timestamps

### Games Table
- `id` - Primary key
- `game_type` - chess or poker
- `status` - waiting, in_progress, completed, aborted
- `initial_state` - JSON of starting game state
- `current_state` - JSON of current game state
- `winner_id` - Reference to winning player
- `created_at`, `updated_at` - Timestamps

### Game Players Table (Junction)
- `id` - Primary key
- `game_id` - Reference to game
- `player_id` - Reference to player
- `position` - white/black for chess, player_0/player_1 for poker
- `elo_before`, `elo_after` - ELO ratings before/after game

### Moves Table
- `id` - Primary key
- `game_id` - Reference to game
- `player_id` - Reference to player making move
- `move_number` - Sequential move number
- `move_data` - JSON of move details
- `notation` - Human-readable move notation
- `time_taken` - Time taken for move (milliseconds)
- `created_at` - Timestamp

## Game Types

### Chess
- Uses standard FEN notation for board state
- Supports all chess rules including castling, en passant
- Move validation using python-chess library
- UCI notation for moves (e.g., "e2e4", "g1f3")

### Poker (Texas Hold'em)
- 2-10 players supported
- Standard 52-card deck
- Betting rounds: preflop, flop, turn, river
- Hand evaluation using treys library
- Actions: fold, call, raise, check

## LBM Integration

### Supported Providers
- **OpenAI**: GPT-3.5, GPT-4, etc.
- **Anthropic**: Claude-3, Claude-2, etc.

### Move Generation
AI models are prompted with:
- Current game state
- Legal moves (for chess)
- Game context and rules
- Strategic considerations

## Development

### Project Structure
```
lbm-arena/
├── app/                    # 🚀 Production Application
│   ├── core/              # Configuration, database, redis
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── api/v1/            # API endpoints
│   └── services/          # Business logic
├── frontend/              # 🌐 Production Frontend
├── scripts/               # 🔒 Production-Safe Scripts
│   ├── init_db_safe.py    # Safe DB initialization (used in build.sh)
│   └── verify_deployment.py # Deployment verification
├── dev/                   # 🛠️ Development Tools Only
│   ├── scripts/           # Development database scripts
│   │   ├── setup_complete_db.py  # ⚠️ Drops all data! Full reset
│   │   ├── recreate_db.py        # ⚠️ Drops tables! Fresh schema
│   │   ├── add_test_data.py      # Add sample data
│   │   └── test_setup.py         # Test database setup
│   ├── dev.sh             # Quick development start (conda)
│   ├── run.sh             # Development environment setup
│   └── cleanup.sh         # Environment cleanup
├── requirements.txt       # Dependencies
├── environment.yml        # Conda environment
├── build.sh              # Production build script
└── render.yaml           # Deployment configuration
```

**🔒 Production vs Development**
- **Production**: Uses only `scripts/init_db_safe.py` - never overwrites data
- **Development**: Uses `dev/scripts/*` - includes destructive operations for testing

**⚠️ Important**: Never use `dev/` scripts in production! They can delete all your data.

### Adding New Games
1. Create service in `app/services/`
2. Add game logic and state management
3. Update `GameType` enum in `app/models/game.py`
4. Add endpoints in `app/api/v1/endpoints/`
5. Update LLM prompts in `app/services/llm_service.py`

### Testing
```bash
python dev/scripts/test_setup.py  # Basic setup tests
pytest                            # Full test suite (when implemented)
```

## Deployment

### Render.com
The included `render.yaml` provides configuration for Render deployment:
- PostgreSQL database
- Redis instance  
- Auto-deploy from Git

### Docker (Future)
```dockerfile
# Dockerfile coming soon
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## License

MIT License - see LICENSE file for details.
