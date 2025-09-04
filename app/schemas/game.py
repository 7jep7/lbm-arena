from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json
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
    id: int
    game_id: int
    player_id: int
    position: str
    elo_before: Optional[int] = None
    elo_after: Optional[int] = None
    
    class Config:
        orm_mode = True

class Game(GameBase):
    id: int
    status: GameStatus
    player1_id: int
    player2_id: int
    initial_state: Optional[Union[Dict[str, Any], str]] = None
    current_state: Optional[Union[Dict[str, Any], str]] = None
    winner_id: Optional[int] = None
    created_at: datetime
    
    @validator('initial_state', pre=True)
    def parse_initial_state(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except json.JSONDecodeError:
                return None
        return v
    
    @validator('current_state', pre=True)
    def parse_current_state(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v) if v else None
            except json.JSONDecodeError:
                return None
        return v
    
    class Config:
        orm_mode = True
