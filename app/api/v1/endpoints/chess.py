from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from app.core.database import get_db
from app.models.game import Game as GameModel
from app.services.chess_service import ChessService

router = APIRouter()
chess_service = ChessService()

@router.get("/")
def get_chess_info(db: Session = Depends(get_db)):
    """Get chess-related information and available games"""
    chess_games = db.query(GameModel).filter(GameModel.game_type == "chess").all()
    return {
        "message": "Chess API endpoints",
        "available_endpoints": [
            "GET /{game_id}/state - Get current chess game state",
            "GET /{game_id}/legal-moves - Get legal moves for current position", 
            "POST /{game_id}/validate-move - Validate if a move is legal"
        ],
        "chess_games_count": len(chess_games),
        "available_chess_games": [{"id": game.id, "status": game.status.value} for game in chess_games]
    }

@router.get("/{game_id}/state")
def get_chess_game_state(game_id: int, db: Session = Depends(get_db)):
    """Get current chess game state"""
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.game_type != "chess":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not a chess game"
        )
    
    current_state = json.loads(game.current_state)
    return current_state

@router.get("/{game_id}/legal-moves")
def get_legal_moves(game_id: int, db: Session = Depends(get_db)):
    """Get legal moves for current position"""
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.game_type != "chess":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not a chess game"
        )
    
    current_state = json.loads(game.current_state)
    board_fen = current_state.get("board") or current_state.get("board_fen")
    if not board_fen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid game state: missing board position"
        )
    legal_moves = chess_service.get_legal_moves(board_fen)
    
    return {"legal_moves": legal_moves}

@router.post("/{game_id}/validate-move")
def validate_move(game_id: int, move_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Validate if a move is legal"""
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.game_type != "chess":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not a chess game"
        )
    
    current_state = json.loads(game.current_state)
    board_fen = current_state.get("board") or current_state.get("board_fen")
    if not board_fen:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid game state: missing board position"
        )
    move_uci = move_data.get("move")
    
    if not move_uci:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Move field is required"
        )
    
    legal_moves = chess_service.get_legal_moves(board_fen)
    is_legal = move_uci in legal_moves
    
    notation = None
    if is_legal:
        try:
            notation = chess_service.move_to_san(board_fen, move_uci)
        except:
            pass
    
    return {
        "is_legal": is_legal,
        "move": move_uci,
        "notation": notation
    }
