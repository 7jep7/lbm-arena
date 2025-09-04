# LBM Arena - Simple API Testing

Simple frontend to test and verify the backend API functionality.

## Quick Start

1. Start both: `./dev/dev.sh` from root directory
2. Visit: http://localhost:3000
3. Click "Run All Tests" to verify everything works

## How to Use

### 1. Start the Backend
```bash
# From the root directory
./dev/run.sh
# OR manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Open the Frontend
```bash
# Simple way - open index.html in browser
open frontend/index.html

# OR serve it locally
cd frontend && python -m http.server 8080
# Then visit: http://localhost:8080
```

### 3. Test the API

#### **Using the Web Interface:**
1. Click "Test Health Check" to verify backend is running
2. Try "Create Model" to test data manipulation
3. Use "Create Game" to test game functionality  
4. Click "Run Full API Test Suite" for comprehensive testing

#### **Using Browser Console:**
```javascript
// Quick tests in browser console
testAPI.health()          // Check health
testAPI.models()          // List models
testAPI.createModel('test') // Create a model
testAPI.full()            // Run complete test suite
```

## What You'll Learn

### **API Patterns**
- RESTful endpoint design
- Request/response structure
- Error handling patterns
- Status codes and responses

### **Data Flow**
- How frontend communicates with backend
- JSON data formatting
- Asynchronous operations with fetch()
- State management basics

### **Testing Approaches**
- Individual endpoint testing
- Comprehensive test suites
- Error scenario handling
- Success/failure validation

## Expected Test Results

✅ **Health Check** - Should return API status
✅ **Database** - Should confirm DB connectivity  
✅ **List Models** - Should return model array (may be empty)
✅ **Create Model** - Should create and return model with ID
✅ **List Games** - Should return games array
✅ **Statistics** - Should return system stats
✅ **Leaderboard** - Should return rankings

## Next Steps

After verifying the backend works correctly with this simple frontend:

1. **Build Your Real Frontend** (in separate repo)
   - Use any framework (React, Vue, Angular, etc.)
   - Implement proper UI/UX design
   - Add advanced features and interactions

2. **Understanding Gained**
   - API endpoint structure
   - Request/response patterns
   - Error handling approaches
   - Data manipulation flows

3. **Confidence**
   - Backend is working correctly
   - API contracts are clear
   - Ready for full frontend development

## Troubleshooting

- **API calls fail**: Make sure backend is running on `http://localhost:8000`
- **CORS errors**: Backend includes CORS middleware, but check console for details
- **Database errors**: Ensure PostgreSQL/Supabase is configured correctly
- **Model creation fails**: Check backend logs for validation errors
