// Simple API testing utilities for LBM Arena
const API_BASE = 'http://localhost:8000';

async function apiCall(endpoint) {
    try {
        const response = await fetch(API_BASE + endpoint);
        const data = await response.json();
        return { success: response.ok, status: response.status, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Console testing functions
window.testAPI = {
    health: () => apiCall('/health'),
    players: () => apiCall('/api/v1/players'),
    games: () => apiCall('/api/v1/games'),
    chess: () => apiCall('/api/v1/chess'),
    
    async all() {
        const tests = ['health', 'players', 'games', 'chess'];
        for (const test of tests) {
            console.log(`Testing ${test}:`, await this[test]());
        }
    }
};

console.log('API testing ready. Use testAPI.all() to test everything.');
