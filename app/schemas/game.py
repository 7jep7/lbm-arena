from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.game import GameType, GameStatus

# ---------------------------------------------------------------------------
# Player-in-game schemas expected by tests
# ---------------------------------------------------------------------------

class CompatBaseModel(BaseModel):
    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)
    @classmethod
    def model_validate(cls, data):
        return cls(**data)

class GamePlayerCreate(CompatBaseModel):
    player_id: int
    role: str  # e.g. white/black/player_0

    @validator('player_id')
    def validate_player_id(cls, v):
        if not isinstance(v, int):
            raise TypeError('player_id must be int')
        return v

    @validator('role')
    def validate_role(cls, v):
        if not isinstance(v, str):
            raise TypeError('role must be str')
        return v

class GamePlayerResponse(GamePlayerCreate):
    id: int
    game_id: int
    player: Optional[Dict[str, Any]] = None

class GamePlayer(CompatBaseModel):  # Backward compatibility with existing usages
    id: int
    game_id: int
    player_id: int
    position: str
    elo_before: Optional[int] = None
    elo_after: Optional[int] = None

    class Config:
        orm_mode = True

# ---------------------------------------------------------------------------
# Game schemas
# ---------------------------------------------------------------------------

ALLOWED_RESULTS = {"win", "loss", "draw", "aborted", None}

ALLOWED_GAME_TYPES = {"chess", "poker"}
ALLOWED_STATUSES = {"pending", "in_progress", "completed", "aborted", "waiting"}

class GameBase(CompatBaseModel):
    game_type: str

    @validator('game_type')
    def validate_game_type(cls, v):
        if v not in ALLOWED_GAME_TYPES:
            raise ValueError('invalid game_type')
        return v

class GameCreate(GameBase):
    status: str
    players: List[GamePlayerCreate]
    # tests & endpoints expect list of raw player ids sometimes
    player_ids: Optional[List[int]] = None

    @validator('status')
    def validate_status(cls, v):
        if v not in ALLOWED_STATUSES:
            raise ValueError('invalid status')
        return v

    @validator('players')
    def validate_players(cls, v):
        if not v or len(v) == 0:
            raise ValueError('players must not be empty')
        return v

    @validator('player_ids', always=True)
    def derive_player_ids(cls, v, values):  # type: ignore
        if v is None and 'players' in values and values['players']:
            return [p.player_id for p in values['players']]
        return v

class GameUpdate(CompatBaseModel):
    status: Optional[str] = None
    result: Optional[str] = None
    current_state: Optional[Dict[str, Any]] = None
    winner_id: Optional[int] = None

    @validator('result')
    def validate_result(cls, v):
        if v is not None and v not in ALLOWED_RESULTS:
            raise ValueError('invalid result')
        return v

class Game(CompatBaseModel):
    id: int
    game_type: str
    status: str
    result: Optional[str] = None
    winner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    players: List[GamePlayerCreate] = []

    class Config:
        orm_mode = True

class GameResponse(Game):
    pass

# ---------------------------------------------------------------------------
# Move schemas
# ---------------------------------------------------------------------------
class MoveCreate(CompatBaseModel):
    player_id: int
    move_number: int
    move_notation: str
    position_before: Optional[str] = None
    position_after: Optional[str] = None
    time_taken: Optional[float] = None
    analysis: Optional[Dict[str, Any]] = None

    @validator('move_number')
    def validate_move_number(cls, v):
        if v <= 0:
            raise ValueError('move_number must be positive')
        return v

    @validator('time_taken')
    def validate_time_taken(cls, v):
        if v is not None and v < 0:
            raise ValueError('time_taken must be non-negative')
        return v

class MoveUpdate(CompatBaseModel):
    move_notation: Optional[str] = None
    position_after: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    time_taken: Optional[float] = None

class Move(CompatBaseModel):
    id: int
    game_id: int
    player_id: int
    move_number: int
    move_notation: str
    position_before: Optional[str] = None
    position_after: Optional[str] = None
    time_taken: Optional[float] = None
    analysis: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        orm_mode = True

class MoveResponse(Move):
    pass
