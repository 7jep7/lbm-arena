from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from app.services.chess_service import ChessService
from app.core.database import get_db
from app.models.game import Game as GameModel, GameType

router = APIRouter()
chess_service = ChessService()

@router.get("/")
def chess_info(db: Session = Depends(get_db)):
    games = db.query(GameModel).filter(GameModel.game_type == GameType.CHESS).all()
    serialized_games = [
        {"id": g.id, "status": g.status.value if hasattr(g.status, 'value') else g.status}
        for g in games
    ]
    return {
        "message": "Chess API",
        "available_endpoints": [
            "/api/v1/chess/{game_id}/state",
            "/api/v1/chess/{game_id}/legal-moves",
            "/api/v1/chess/{game_id}/validate-move"
        ],
        "chess_games_count": len(serialized_games),
        "available_chess_games": serialized_games
    }

def _get_chess_game_or_error(game_id: int, db: Session) -> GameModel:
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game_type_value = game.game_type.value if hasattr(game.game_type, 'value') else str(game.game_type)
    if game_type_value != GameType.CHESS.value:
        raise HTTPException(status_code=400, detail="Game is not a chess game")
    return game

@router.get("/{game_id}/state")
def get_chess_state(game_id: int, db: Session = Depends(get_db)):
    game = _get_chess_game_or_error(game_id, db)
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    except Exception:
        current_state = chess_service.create_new_game()
    # Provide minimal chess state info
    return {
        "board_fen": current_state.get("board_fen"),
        "turn": current_state.get("turn"),
        "status": current_state.get("status", game.status.value if hasattr(game.status, 'value') else str(game.status))
    }

@router.get("/{game_id}/legal-moves")
def get_legal_moves(game_id: int, db: Session = Depends(get_db)):
    game = _get_chess_game_or_error(game_id, db)
    try:
        current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
        moves = chess_service.get_legal_moves(current_state)
        return {"legal_moves": moves}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{game_id}/validate-move")
def validate_move(game_id: int, move: Dict[str, Any], db: Session = Depends(get_db)):
    game = _get_chess_game_or_error(game_id, db)
    current_state = json.loads(game.current_state) if isinstance(game.current_state, str) else game.current_state
    uci = move.get("move")
    if not uci:
        raise HTTPException(status_code=422, detail="'move' field is required")
    # Convert UCI to move_data structure expected by service (from/to)
    if len(uci) < 4:
        return {"valid": False, "reason": "invalid format"}
    move_data = {"from": uci[0:2], "to": uci[2:4]}
    try:
        valid = chess_service.validate_move(current_state, move_data)
        return {"valid": valid, "reason": None if valid else "illegal move"}
    except ValueError as e:
        return {"valid": False, "reason": str(e)}
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
