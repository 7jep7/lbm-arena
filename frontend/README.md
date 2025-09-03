# LBM Arena Frontend

A simple, interactive web interface for the LBM Arena backend that demonstrates how to interact with the API, manage players and games, and analyze gameplay data.

## Features

### 🎮 Dashboard
- Real-time statistics overview
- Recent games display
- API status monitoring
- Quick insights into player and game counts

### 👥 Players Management
- Create human and AI players
- Support for OpenAI and Anthropic models
- View ELO ratings for both chess and poker
- Player CRUD operations

### 🎯 Games Management
- Create new chess and poker games
- Real-time game state viewing
- Move history tracking
- Game filtering and search

### 🏆 Leaderboard
- Chess and poker ELO rankings
- Real-time leaderboard updates
- Player performance analysis

### 🔧 API Tester
- Interactive API endpoint testing
- Custom API calls with JSON payloads
- Response visualization
- Quick action buttons for common operations

## How to Use

### Quick Start
From the project root directory:
```bash
./run.sh
```

This will start both the backend (port 8000) and frontend (port 3000).

### Manual Start
1. **Start the backend first**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   python3 -m http.server 3000
   ```

3. **Open your browser**:
   - Frontend: http://localhost:3000
   - Backend API Docs: http://localhost:8000/docs

## API Integration Examples

### Creating a Player
```javascript
// Create an AI player
const playerData = {
    display_name: "GPT-4 Chess Master",
    is_human: false,
    provider: "openai",
    model_id: "gpt-4"
};

const response = await fetch('http://localhost:8000/api/v1/players', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(playerData)
});
```

### Creating a Game
```javascript
// Create a chess game with 2 players
const gameData = {
    game_type: "chess",
    player_ids: [1, 2]  // Player IDs
};

const response = await fetch('http://localhost:8000/api/v1/games', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(gameData)
});
```

### Making a Move
```javascript
// Make a chess move
const moveData = {
    move_data: {
        move: "e2e4",  // UCI notation
        player_id: 1
    },
    notation: "e4"  // Human readable
};

const response = await fetch('http://localhost:8000/api/v1/games/1/move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(moveData)
});
```

## Database Analysis

The frontend demonstrates how to:

1. **Query Player Statistics**:
   - Retrieve ELO ratings
   - Compare human vs AI performance
   - Track player progress over time

2. **Analyze Game Data**:
   - View game state progression
   - Examine move sequences
   - Calculate win rates and patterns

3. **Generate Leaderboards**:
   - Rank players by ELO
   - Filter by game type
   - Real-time ranking updates

## Understanding the API Structure

### Core Endpoints
- `GET /api/v1/players` - List all players
- `POST /api/v1/players` - Create new player
- `GET /api/v1/games` - List all games
- `POST /api/v1/games` - Create new game
- `POST /api/v1/games/{id}/move` - Make a move

### Game State Management
- **Chess**: Uses FEN notation and UCI moves
- **Poker**: Tracks betting rounds and hand states
- **Move History**: Complete audit trail of all actions

### Data Relationships
- Players ↔ Games (many-to-many via game_players)
- Games → Moves (one-to-many)
- Players → Moves (one-to-many)

## Technology Stack

- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Styling**: CSS Grid, Flexbox, CSS Variables
- **Icons**: Font Awesome 6
- **API**: Fetch API for HTTP requests
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy

## Key Learning Points

### API Integration
- RESTful API consumption
- Error handling and validation
- Real-time data updates
- JSON payload construction

### Database Interaction
- CRUD operations via API
- Relationship management
- Data filtering and sorting
- Pagination handling

### Game State Management
- Understanding chess FEN notation
- Poker hand evaluation
- Move validation
- Game progression tracking

### UI/UX Patterns
- Tab-based navigation
- Modal dialogs
- Form validation
- Toast notifications
- Responsive design

## Files Structure

```
frontend/
├── index.html          # Main HTML structure
├── styles.css          # All CSS styling
├── app.js             # JavaScript application logic
└── README.md          # This file
```

## Browser Compatibility

- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

## Development Tips

1. **Use the API Tester tab** to experiment with endpoints
2. **Check the browser console** for detailed error messages
3. **Monitor network tab** to see actual API calls
4. **Use the game detail modal** to understand state structure
5. **Test with both human and AI players** for different scenarios

## Common Issues & Solutions

### CORS Errors
Make sure the backend is configured to allow requests from localhost:3000.

### API Connection Failed
1. Verify backend is running on port 8000
2. Check API status indicator in the header
3. Use the API Tester to debug specific endpoints

### Database Issues
1. Ensure PostgreSQL is running
2. Check environment variables
3. Run database initialization script

### Game Creation Fails
1. Verify players exist before creating games
2. Check game type requirements (chess = 2 players)
3. Ensure all player IDs are valid

This frontend serves as both a functional interface and a comprehensive example of how to build applications that interact with the LBM Arena backend.
