from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.game import GameType, GameStatus

class GameBase(BaseModel):
    game_type: GameType

class GameCreate(GameBase):
    player_ids: List[int]
    initial_state: Optional[Dict[str, Any]] = None

class GameUpdate(BaseModel):
    status: Optional[GameStatus] = None
    current_state: Optional[Dict[str, Any]] = None
    winner_id: Optional[int] = None

class MoveCreate(BaseModel):
    move_data: Dict[str, Any]
    notation: Optional[str] = None

class Move(BaseModel):
    id: int
    game_id: int
    player_id: int
    move_number: int
    move_data: Dict[str, Any]
    notation: Optional[str] = None
    time_taken: Optional[int] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class GamePlayer(BaseModel):
    player_id: int
    position: str
    elo_before: Optional[int] = None
    elo_after: Optional[int] = None
    
    class Config:
        orm_mode = True

class Game(GameBase):
    id: int
    status: GameStatus
    initial_state: Optional[Dict[str, Any]] = None
    current_state: Optional[Dict[str, Any]] = None
    winner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    players: List[GamePlayer] = []
    moves: List[Move] = []
    
    class Config:
        orm_mode = True
