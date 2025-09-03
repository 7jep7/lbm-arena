// LBM Arena Frontend JavaScript

// Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let currentPlayers = [];
let currentGames = [];
let selectedPlayers = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
    loadDashboard();
    
    // Refresh data every 30 seconds
    setInterval(() => {
        if (document.querySelector('.tab-content.active').id === 'dashboard') {
            loadDashboard();
        }
    }, 30000);
});

// API Helper Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const config = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        config.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || `HTTP ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error('API Call Error:', error);
        throw error;
    }
}

// API Status Check
async function checkApiStatus() {
    const statusIndicator = document.getElementById('status-indicator');
    
    try {
        await fetch(`${API_BASE_URL}/health`);
        statusIndicator.textContent = 'Online';
        statusIndicator.className = 'status-online';
    } catch (error) {
        statusIndicator.textContent = 'Offline';
        statusIndicator.className = 'status-offline';
    }
}

// Tab Management
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Load content based on tab
    switch(tabName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'players':
            loadPlayers();
            break;
        case 'games':
            loadGames();
            break;
        case 'leaderboard':
            loadLeaderboard();
            break;
        case 'api-tester':
            // API tester doesn't need initial loading
            break;
    }
}

// Dashboard Functions
async function loadDashboard() {
    try {
        // Load statistics
        const players = await apiCall('/api/v1/players');
        const games = await apiCall('/api/v1/games');
        
        document.getElementById('total-players').textContent = players.length;
        document.getElementById('total-games').textContent = games.length;
        
        const chessGames = games.filter(game => game.game_type === 'chess').length;
        const pokerGames = games.filter(game => game.game_type === 'poker').length;
        
        document.getElementById('chess-games').textContent = chessGames;
        document.getElementById('poker-games').textContent = pokerGames;
        
        // Load recent games
        const recentGames = games.slice(-5).reverse();
        displayRecentGames(recentGames);
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

function displayRecentGames(games) {
    const container = document.getElementById('recent-games');
    
    if (games.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">No games yet</p>';
        return;
    }
    
    container.innerHTML = games.map(game => `
        <div class="game-item" onclick="showGameDetail(${game.id})">
            <div class="game-basic-info">
                <h4>${game.game_type.toUpperCase()} Game #${game.id}</h4>
                <p>Status: ${game.status} • Created: ${new Date(game.created_at).toLocaleDateString()}</p>
            </div>
            <div class="game-status status-${game.status}">${game.status}</div>
        </div>
    `).join('');
}

// Players Functions
async function loadPlayers() {
    try {
        const players = await apiCall('/api/v1/players');
        currentPlayers = players;
        displayPlayers(players);
    } catch (error) {
        console.error('Failed to load players:', error);
        showError('Failed to load players');
    }
}

function displayPlayers(players) {
    const container = document.getElementById('players-list');
    
    if (players.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem; grid-column: 1/-1;">No players yet. Create your first player!</p>';
        return;
    }
    
    container.innerHTML = players.map(player => `
        <div class="player-card">
            <div class="player-header">
                <span class="player-name">${player.display_name}</span>
                <span class="player-type type-${player.is_human ? 'human' : 'ai'}">
                    ${player.is_human ? 'Human' : 'AI'}
                </span>
            </div>
            ${!player.is_human ? `
                <div class="player-details">
                    <p><strong>Provider:</strong> ${player.provider || 'N/A'}</p>
                    <p><strong>Model:</strong> ${player.model_id || 'N/A'}</p>
                </div>
            ` : ''}
            <div class="player-stats">
                <div class="stat-row">
                    <span class="stat-label">Chess ELO</span>
                    <span class="stat-value">${player.elo_chess}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Poker ELO</span>
                    <span class="stat-value">${player.elo_poker}</span>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                <button class="btn btn-danger" onclick="deletePlayer(${player.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        </div>
    `).join('');
}

function showCreatePlayerForm() {
    document.getElementById('create-player-form').style.display = 'block';
}

function hideCreatePlayerForm() {
    document.getElementById('create-player-form').style.display = 'none';
    document.getElementById('create-player-form').querySelector('form').reset();
}

function toggleProviderFields() {
    const playerType = document.getElementById('player-type').value;
    const aiFields = document.getElementById('ai-fields');
    aiFields.style.display = playerType === 'ai' ? 'block' : 'none';
}

async function createPlayer(event) {
    event.preventDefault();
    
    const name = document.getElementById('player-name').value;
    const isHuman = document.getElementById('player-type').value === 'human';
    const provider = document.getElementById('provider').value;
    const modelId = document.getElementById('model-id').value;
    
    const playerData = {
        display_name: name,
        is_human: isHuman
    };
    
    if (!isHuman) {
        playerData.provider = provider;
        playerData.model_id = modelId;
    }
    
    try {
        await apiCall('/api/v1/players', 'POST', playerData);
        hideCreatePlayerForm();
        loadPlayers();
        showSuccess('Player created successfully!');
    } catch (error) {
        showError('Failed to create player: ' + error.message);
    }
}

async function deletePlayer(playerId) {
    if (!confirm('Are you sure you want to delete this player?')) {
        return;
    }
    
    try {
        await apiCall(`/api/v1/players/${playerId}`, 'DELETE');
        loadPlayers();
        showSuccess('Player deleted successfully!');
    } catch (error) {
        showError('Failed to delete player: ' + error.message);
    }
}

// Games Functions
async function loadGames() {
    try {
        const games = await apiCall('/api/v1/games');
        currentGames = games;
        displayGames(games);
        
        // Load players for game creation
        const players = await apiCall('/api/v1/players');
        currentPlayers = players;
    } catch (error) {
        console.error('Failed to load games:', error);
        showError('Failed to load games');
    }
}

function displayGames(games) {
    const container = document.getElementById('games-list');
    
    if (games.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem; grid-column: 1/-1;">No games yet. Create your first game!</p>';
        return;
    }
    
    container.innerHTML = games.map(game => `
        <div class="game-card" onclick="showGameDetail(${game.id})">
            <div class="game-header">
                <span class="game-title">${game.game_type.toUpperCase()} Game #${game.id}</span>
                <span class="game-status status-${game.status}">${game.status}</span>
            </div>
            <div class="game-info">
                <div class="info-row">
                    <span class="info-label">Type</span>
                    <span class="info-value">${game.game_type}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Players</span>
                    <span class="info-value">${game.players ? game.players.length : 'Loading...'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Created</span>
                    <span class="info-value">${new Date(game.created_at).toLocaleDateString()}</span>
                </div>
                ${game.winner_id ? `
                <div class="info-row">
                    <span class="info-label">Winner</span>
                    <span class="info-value">Player ${game.winner_id}</span>
                </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function showCreateGameForm() {
    document.getElementById('create-game-form').style.display = 'block';
    loadPlayersForSelection();
}

function hideCreateGameForm() {
    document.getElementById('create-game-form').style.display = 'none';
    document.getElementById('create-game-form').querySelector('form').reset();
    selectedPlayers = [];
}

function loadPlayersForSelection() {
    const container = document.getElementById('player-selection');
    
    if (currentPlayers.length === 0) {
        container.innerHTML = '<p>No players available. Create players first.</p>';
        return;
    }
    
    container.innerHTML = currentPlayers.map(player => `
        <div class="player-option">
            <input type="checkbox" id="player-${player.id}" value="${player.id}" 
                   onchange="togglePlayerSelection(${player.id})">
            <label for="player-${player.id}">
                ${player.display_name} (${player.is_human ? 'Human' : 'AI'})
            </label>
        </div>
    `).join('');
}

function togglePlayerSelection(playerId) {
    const checkbox = document.getElementById(`player-${playerId}`);
    if (checkbox.checked) {
        selectedPlayers.push(playerId);
    } else {
        selectedPlayers = selectedPlayers.filter(id => id !== playerId);
    }
}

async function createGame(event) {
    event.preventDefault();
    
    const gameType = document.getElementById('game-type').value;
    
    if (selectedPlayers.length < 2) {
        showError('Please select at least 2 players');
        return;
    }
    
    if (gameType === 'chess' && selectedPlayers.length !== 2) {
        showError('Chess requires exactly 2 players');
        return;
    }
    
    const gameData = {
        game_type: gameType,
        player_ids: selectedPlayers
    };
    
    try {
        await apiCall('/api/v1/games', 'POST', gameData);
        hideCreateGameForm();
        loadGames();
        showSuccess('Game created successfully!');
    } catch (error) {
        showError('Failed to create game: ' + error.message);
    }
}

function filterGames() {
    const filter = document.getElementById('game-filter').value;
    let filteredGames = [...currentGames];
    
    switch(filter) {
        case 'chess':
            filteredGames = currentGames.filter(game => game.game_type === 'chess');
            break;
        case 'poker':
            filteredGames = currentGames.filter(game => game.game_type === 'poker');
            break;
        case 'in_progress':
            filteredGames = currentGames.filter(game => game.status === 'in_progress');
            break;
        case 'completed':
            filteredGames = currentGames.filter(game => game.status === 'completed');
            break;
    }
    
    displayGames(filteredGames);
}

// Game Detail Modal
async function showGameDetail(gameId) {
    try {
        const game = await apiCall(`/api/v1/games/${gameId}`);
        
        let gameStateHtml = '';
        if (game.current_state) {
            const state = typeof game.current_state === 'string' 
                ? JSON.parse(game.current_state) 
                : game.current_state;
            
            if (game.game_type === 'chess') {
                gameStateHtml = `
                    <h4>Chess Board State</h4>
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; font-family: monospace;">
                        <strong>FEN:</strong> ${state.board_fen || 'N/A'}<br>
                        <strong>Turn:</strong> ${state.turn || 'N/A'}<br>
                        <strong>Move Count:</strong> ${state.move_count || 0}<br>
                        <strong>Check:</strong> ${state.check ? 'Yes' : 'No'}<br>
                        <strong>Legal Moves:</strong> ${state.legal_moves ? state.legal_moves.length : 0}
                    </div>
                `;
            } else if (game.game_type === 'poker') {
                gameStateHtml = `
                    <h4>Poker Game State</h4>
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; font-family: monospace;">
                        <strong>Stage:</strong> ${state.stage || 'N/A'}<br>
                        <strong>Pot:</strong> ${state.pot || 0}<br>
                        <strong>Current Bet:</strong> ${state.current_bet || 0}<br>
                        <strong>Community Cards:</strong> ${state.community_cards ? state.community_cards.join(', ') : 'None'}
                    </div>
                `;
            }
        }
        
        document.getElementById('game-detail').innerHTML = `
            <h2>${game.game_type.toUpperCase()} Game #${game.id}</h2>
            <div style="margin: 1.5rem 0;">
                <div class="info-row">
                    <span class="info-label">Status:</span>
                    <span class="info-value game-status status-${game.status}">${game.status}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Created:</span>
                    <span class="info-value">${new Date(game.created_at).toLocaleString()}</span>
                </div>
                ${game.winner_id ? `
                <div class="info-row">
                    <span class="info-label">Winner:</span>
                    <span class="info-value">Player ${game.winner_id}</span>
                </div>
                ` : ''}
            </div>
            
            ${gameStateHtml}
            
            <h4 style="margin-top: 2rem;">Players</h4>
            <div style="display: grid; gap: 1rem; margin-top: 1rem;">
                ${game.players ? game.players.map(player => `
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px;">
                        <strong>Player ${player.player_id}</strong> - Position: ${player.position}
                        ${player.elo_before ? `<br>ELO Before: ${player.elo_before}` : ''}
                        ${player.elo_after ? `<br>ELO After: ${player.elo_after}` : ''}
                    </div>
                `).join('') : '<p>No player data available</p>'}
            </div>
            
            <h4 style="margin-top: 2rem;">Moves</h4>
            <div style="max-height: 200px; overflow-y: auto; margin-top: 1rem;">
                ${game.moves && game.moves.length > 0 ? game.moves.map(move => `
                    <div style="background: #f8f9fa; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px;">
                        <strong>Move ${move.move_number}</strong> by Player ${move.player_id}
                        ${move.notation ? `<br>Notation: ${move.notation}` : ''}
                        <br><small>Time: ${new Date(move.created_at).toLocaleString()}</small>
                    </div>
                `).join('') : '<p>No moves yet</p>'}
            </div>
            
            <div style="margin-top: 2rem;">
                <button class="btn btn-danger" onclick="deleteGame(${game.id})">
                    <i class="fas fa-trash"></i> Delete Game
                </button>
            </div>
        `;
        
        document.getElementById('game-modal').style.display = 'block';
    } catch (error) {
        showError('Failed to load game details: ' + error.message);
    }
}

function closeGameModal() {
    document.getElementById('game-modal').style.display = 'none';
}

async function deleteGame(gameId) {
    if (!confirm('Are you sure you want to delete this game?')) {
        return;
    }
    
    try {
        await apiCall(`/api/v1/games/${gameId}`, 'DELETE');
        closeGameModal();
        loadGames();
        showSuccess('Game deleted successfully!');
    } catch (error) {
        showError('Failed to delete game: ' + error.message);
    }
}

// Leaderboard Functions
async function loadLeaderboard() {
    try {
        const players = await apiCall('/api/v1/players');
        showLeaderboard('chess', players);
    } catch (error) {
        console.error('Failed to load leaderboard:', error);
        showError('Failed to load leaderboard');
    }
}

function showLeaderboard(type, players = null) {
    // Update tab buttons
    document.querySelectorAll('.leaderboard-tabs .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event?.target?.classList.add('active');
    
    // Hide all leaderboard content
    document.querySelectorAll('.leaderboard-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Show selected leaderboard
    document.getElementById(`${type}-leaderboard`).style.display = 'block';
    
    if (players || currentPlayers.length > 0) {
        const playersToUse = players || currentPlayers;
        displayRankings(type, playersToUse);
    }
}

function displayRankings(type, players) {
    const eloField = type === 'chess' ? 'elo_chess' : 'elo_poker';
    const sortedPlayers = [...players].sort((a, b) => b[eloField] - a[eloField]);
    
    const container = document.getElementById(`${type}-rankings`);
    
    if (sortedPlayers.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666; padding: 2rem;">No players yet</p>';
        return;
    }
    
    container.innerHTML = sortedPlayers.map((player, index) => {
        const position = index + 1;
        let rankClass = '';
        if (position === 1) rankClass = 'gold';
        else if (position === 2) rankClass = 'silver';
        else if (position === 3) rankClass = 'bronze';
        
        return `
            <div class="ranking-item">
                <div class="rank-position ${rankClass}">${position}</div>
                <div class="rank-info">
                    <div class="rank-name">${player.display_name}</div>
                    <div class="rank-details">
                        ${player.is_human ? 'Human Player' : `${player.provider} - ${player.model_id}`}
                    </div>
                </div>
                <div class="rank-elo">${player[eloField]}</div>
            </div>
        `;
    }).join('');
}

// API Tester Functions
async function testEndpoint(method, endpoint) {
    try {
        const result = await apiCall(endpoint, method);
        displayApiResponse(method, endpoint, result, null);
    } catch (error) {
        displayApiResponse(method, endpoint, null, error);
    }
}

async function makeCustomApiCall() {
    const method = document.getElementById('api-method').value;
    const endpoint = document.getElementById('api-endpoint').value;
    const bodyText = document.getElementById('api-body').value;
    
    let data = null;
    if (bodyText.trim() && (method === 'POST' || method === 'PUT')) {
        try {
            data = JSON.parse(bodyText);
        } catch (error) {
            showError('Invalid JSON in request body');
            return;
        }
    }
    
    try {
        const result = await apiCall(endpoint, method, data);
        displayApiResponse(method, endpoint, result, null, data);
    } catch (error) {
        displayApiResponse(method, endpoint, null, error, data);
    }
}

function displayApiResponse(method, endpoint, result, error, requestData = null) {
    const responseElement = document.getElementById('api-response');
    
    let responseText = `${method} ${endpoint}\n`;
    responseText += `Timestamp: ${new Date().toISOString()}\n`;
    responseText += `${'='.repeat(50)}\n\n`;
    
    if (requestData) {
        responseText += `REQUEST BODY:\n${JSON.stringify(requestData, null, 2)}\n\n`;
    }
    
    if (error) {
        responseText += `ERROR:\n${error.message}\n`;
    } else {
        responseText += `SUCCESS:\n${JSON.stringify(result, null, 2)}\n`;
    }
    
    responseElement.textContent = responseText;
}

// Utility Functions
function showSuccess(message) {
    // Create a simple toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        z-index: 1001;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        document.body.removeChild(toast);
    }, 3000);
}

function showError(message) {
    // Create a simple error toast notification
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        z-index: 1001;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        document.body.removeChild(toast);
    }, 5000);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('game-modal');
    if (event.target === modal) {
        closeGameModal();
    }
}
