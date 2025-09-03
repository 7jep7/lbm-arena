"""
Simple test script to verify the LBM Arena backend setup
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.core.config import settings
        print("✓ Core config imported successfully")
        
        from app.services.chess_service import ChessService
        print("✓ Chess service imported successfully")
        
        from app.services.poker_service import PokerService  
        print("✓ Poker service imported successfully")
        
        from app.models.player import Player
        print("✓ Player model imported successfully")
        
        from app.models.game import Game
        print("✓ Game model imported successfully")
        
        from app.schemas.player import PlayerCreate
        print("✓ Player schema imported successfully")
        
        print("\n✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_chess_service():
    """Test basic chess service functionality"""
    try:
        from app.services.chess_service import ChessService
        
        chess = ChessService()
        initial_state = chess.create_new_game()
        
        print(f"✓ Chess game created with FEN: {initial_state['board_fen']}")
        print(f"✓ Legal moves count: {len(initial_state['legal_moves'])}")
        
        # Test a simple move
        new_state = chess.make_move(initial_state, "e2e4")
        print(f"✓ Move e2e4 executed successfully")
        print(f"✓ New FEN: {new_state['board_fen']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Chess service error: {e}")
        return False

def test_poker_service():
    """Test basic poker service functionality"""
    try:
        from app.services.poker_service import PokerService
        
        poker = PokerService()
        initial_state = poker.create_new_game(2)
        
        print(f"✓ Poker game created with {len(initial_state['players'])} players")
        print(f"✓ Current stage: {initial_state['stage']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Poker service error: {e}")
        return False

def main():
    """Run all tests"""
    print("🎮 Testing LBM Arena Backend Setup\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Chess Service Tests", test_chess_service),
        ("Poker Service Tests", test_poker_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        success = test_func()
        results.append(success)
        print()
    
    if all(results):
        print("🎉 All tests passed! The LBM Arena backend is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
