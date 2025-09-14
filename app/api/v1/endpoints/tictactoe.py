from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import json

from app.services.tictactoe_service import TicTacToeService
from app.core.database import get_db
from app.models.game import Game as GameModel, GameType

router = APIRouter()
tictactoe_service = TicTacToeService()


def _get_tictactoe_game_or_error(game_id: int, db: Session) -> GameModel:
    """Helper to get a tic-tac-toe game or raise 404"""
    game = db.query(GameModel).filter(
        GameModel.id == game_id,
        GameModel.game_type == GameType.TICTACTOE.value
    ).first()
    if not game:
        raise HTTPException(status_code=404, detail="Tic-tac-toe game not found")
    return game


@router.get("/")
def tictactoe_info():
    """Get information about the tic-tac-toe game type"""
    return {
        "game_type": "tictactoe",
        "description": "Classic tic-tac-toe game on a 3x3 grid",
        "rules": [
            "Players take turns placing X or O on a 3x3 grid",
            "First player to get 3 in a row (horizontal, vertical, or diagonal) wins",
            "If the grid is full with no winner, the game is a draw",
            "X always goes first"
        ],
        "endpoints": {
            "state": "GET /{game_id}/state - Get current game state",
            "legal_moves": "GET /{game_id}/legal-moves - Get available moves",
            "validate_move": "POST /{game_id}/validate-move - Validate a move",
            "make_move": "POST /{game_id}/move - Make a move"
        }
    }


@router.get("/{game_id}/state")
def get_tictactoe_state(game_id: int, db: Session = Depends(get_db)):
    """Get current state of a tic-tac-toe game"""
    game = _get_tictactoe_game_or_error(game_id, db)
    
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    except Exception:
        current_state = tictactoe_service.create_new_game()
    
    return {
        "game_id": game_id,
        "board": current_state.get("board"),
        "current_player": current_state.get("current_player"),
        "status": current_state.get("status"),
        "winner": current_state.get("winner"),
        "is_draw": current_state.get("is_draw", False),
        "move_count": current_state.get("move_count", 0)
    }


@router.get("/{game_id}/legal-moves")
def get_legal_moves(game_id: int, db: Session = Depends(get_db)):
    """Get legal moves for current game state"""
    game = _get_tictactoe_game_or_error(game_id, db)
    
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    except Exception:
        current_state = tictactoe_service.create_new_game()
    
    legal_moves = tictactoe_service.get_legal_moves(current_state)
    
    return {
        "game_id": game_id,
        "legal_moves": legal_moves,
        "count": len(legal_moves)
    }


@router.post("/{game_id}/validate-move")
def validate_move(game_id: int, move: Dict[str, Any], db: Session = Depends(get_db)):
    """Validate if a move is legal"""
    game = _get_tictactoe_game_or_error(game_id, db)
    
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    except Exception:
        current_state = tictactoe_service.create_new_game()
    
    try:
        is_valid = tictactoe_service.validate_move(current_state, move)
        return {
            "game_id": game_id,
            "move": move,
            "valid": is_valid,
            "message": "Valid move" if is_valid else "Invalid move"
        }
    except ValueError as e:
        return {
            "game_id": game_id,
            "move": move,
            "valid": False,
            "message": str(e)
        }


@router.post("/{game_id}/move")
def make_move(game_id: int, move: Dict[str, Any], db: Session = Depends(get_db)):
    """Make a move in the tic-tac-toe game"""
    game = _get_tictactoe_game_or_error(game_id, db)
    
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    except Exception:
        current_state = tictactoe_service.create_new_game()
    
    try:
        new_state = tictactoe_service.make_move(current_state, move)
        
        # Update the game in the database
        game.current_state = json.dumps(new_state)
        
        # Update game status if completed
        if new_state.get("status") == "completed":
            game.status = "completed"
            if new_state.get("winner"):
                # In a real implementation, you'd map the winner symbol to player ID
                # For now, just indicate completion
                game.result = {"winner": new_state.get("winner")}
        
        db.commit()
        
        return {
            "game_id": game_id,
            "move": move,
            "success": True,
            "new_state": {
                "board": new_state.get("board"),
                "current_player": new_state.get("current_player"),
                "status": new_state.get("status"),
                "winner": new_state.get("winner"),
                "is_draw": new_state.get("is_draw", False),
                "move_count": new_state.get("move_count", 0)
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making move: {str(e)}")


@router.get("/{game_id}/board")
def get_board_display(game_id: int, db: Session = Depends(get_db)):
    """Get a text representation of the game board"""
    game = _get_tictactoe_game_or_error(game_id, db)
    
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    except Exception:
        current_state = tictactoe_service.create_new_game()
    
    board_display = tictactoe_service.get_board_display(current_state)
    
    return {
        "game_id": game_id,
        "board_display": board_display,
        "current_player": current_state.get("current_player"),
        "status": current_state.get("status")
    }


@router.get("/{game_id}/moves")
def get_move_history(game_id: int, db: Session = Depends(get_db)):
    """Get the move history for the game"""
    game = _get_tictactoe_game_or_error(game_id, db)
    
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    except Exception:
        current_state = tictactoe_service.create_new_game()
    
    return {
        "game_id": game_id,
        "moves": current_state.get("moves", []),
        "move_count": current_state.get("move_count", 0)
    }
