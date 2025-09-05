from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json
from app.core.database import get_db
from app.models.game import Game as GameModel, GameStatus
from app.models.move import Move as MoveModel, GamePlayer as GamePlayerModel
from app.schemas.game import Game, GameCreate, MoveCreate, GamePlayerCreate
from app.services.chess_service import ChessService
from app.services.poker_service import PokerService
from app.services.llm_service import LLMService

router = APIRouter()
chess_service = ChessService()
poker_service = PokerService()
llm_service = LLMService()

@router.get("/", response_model=List[Game])
def get_games(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of all games"""
    games = db.query(GameModel).offset(skip).limit(limit).all()
    return games

@router.get("/{game_id}", response_model=Game)
def get_game(game_id: int, db: Session = Depends(get_db)):
    """Get a specific game by ID"""
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    return game

@router.post("/", response_model=Game, status_code=status.HTTP_201_CREATED)
def create_game(game: GameCreate, db: Session = Depends(get_db)):
    """Create a new game"""
    
    # Validate player count
    player_ids = game.player_ids or [p.player_id for p in game.players]
    if len(player_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 players required"
        )
    
    # Create initial game state based on game type
    if game.game_type == "chess":
        if len(player_ids) != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chess requires exactly 2 players"
            )
        initial_state = chess_service.create_new_game()
    elif game.game_type == "poker":
        if len(player_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Poker supports maximum 10 players"
            )
        initial_state = poker_service.create_new_game(len(player_ids))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported game type"
        )
    
    # Create game record
    # Determine primary players for relational fields
    player1_id = player_ids[0] if player_ids else None
    player2_id = player_ids[1] if len(player_ids) > 1 else player_ids[0] if game.game_type == "chess" and player_ids else None

    db_game = GameModel(
        game_type=game.game_type,
        status=GameStatus.WAITING if game.status == 'waiting' else GameStatus.IN_PROGRESS,
        player1_id=player1_id,
        player2_id=player2_id,
        initial_state=initial_state,
        current_state=initial_state
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    
    # Add players to game
    positions = ["white", "black"] if game.game_type == "chess" else [f"player_{i}" for i in range(len(player_ids))]

    for i, player_id in enumerate(player_ids):
        game_player = GamePlayerModel(
            game_id=db_game.id,
            player_id=player_id,
            position=positions[i]
        )
        db.add(game_player)
    
    db.commit()
    db.refresh(db_game)
    return db_game

@router.post("/{game_id}/move")
async def make_move(
    game_id: int, 
    move: MoveCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Make a move in a game"""
    
    # Get game
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not in progress"
        )
    
    current_state = json.loads(game.current_state)
    
    try:
        # Process move based on game type
        if game.game_type == "chess":
            move_uci = move.move_data.get("move")
            if not move_uci:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chess move must include 'move' field with UCI notation"
                )
            
            new_state = chess_service.make_move(current_state, move_uci)
            notation = chess_service.move_to_san(current_state["board_fen"], move_uci)
            
        elif game.game_type == "poker":
            action = move.move_data.get("action")
            amount = move.move_data.get("amount", 0)
            player_id = move.move_data.get("player_id")
            
            if not action or not player_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Poker move must include 'action' and 'player_id'"
                )
            
            new_state = poker_service.make_action(current_state, player_id, action, amount)
            notation = f"{action}({amount})" if amount > 0 else action
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported game type"
            )
        
        # Save move
        move_number = db.query(MoveModel).filter(MoveModel.game_id == game_id).count() + 1
        db_move = MoveModel(
            game_id=game_id,
            player_id=move.move_data.get("player_id", 1),  # Should be passed in move_data
            move_number=move_number,
            move_data=json.dumps(move.move_data),
            notation=notation
        )
        db.add(db_move)
        
        # Update game state
        game.current_state = json.dumps(new_state)
        
        # Check if game is over
        if new_state.get("status") == "completed":
            game.status = GameStatus.COMPLETED
            if new_state.get("winner"):
                # Find winner player ID based on position
                winner_position = new_state.get("winner")
                game_player = db.query(GamePlayerModel).filter(
                    GamePlayerModel.game_id == game_id,
                    GamePlayerModel.position == winner_position
                ).first()
                if game_player:
                    game.winner_id = game_player.player_id
        
        db.commit()
        
        return {"message": "Move made successfully", "game_state": new_state}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{game_id}/ai-move")
async def trigger_ai_move(game_id: int, db: Session = Depends(get_db)):
    """Trigger an AI player to make a move"""
    
    # Get game
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.status != GameStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game is not in progress"
        )
    
    current_state = json.loads(game.current_state)
    
    # Determine whose turn it is and if they're an AI
    # This is a simplified implementation - you'd need more logic here
    
    return {"message": "AI move processing initiated"}

@router.delete("/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    """Delete a game"""
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    db.delete(game)
    db.commit()
    return {"message": "Game deleted successfully"}
