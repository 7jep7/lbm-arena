from pydantic import BaseModel, validator, Field, root_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.game import GameType, GameStatus
from app.schemas.player import Player

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
    # Accept a nested Player schema so Pydantic will coerce raw dicts into
    # a `Player` model instance. Tests expect attribute access (e.g. player.id)
    # rather than a plain dict.
    player: Optional[Player] = None

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

ALLOWED_GAME_TYPES = {"chess", "poker", "tictactoe", "gi", "sfc"}
ALLOWED_STATUSES = {"pending", "in_progress", "completed", "aborted", "waiting"}

class GameBase(CompatBaseModel):
    game_type: str

    @validator('game_type')
    def validate_game_type(cls, v):
        if v not in ALLOWED_GAME_TYPES:
            raise ValueError('invalid game_type')
        return v

class GameCreate(GameBase):
    # Allow clients/tests to omit `status` and/or `players` and instead provide
    # `player_ids`. This makes the API more flexible for test helpers that
    # sometimes send only `player_ids`.
    status: str = "pending"
    players: Optional[List[GamePlayerCreate]] = None
    # tests & endpoints expect list of raw player ids sometimes
    player_ids: Optional[List[int]] = None
    @validator('status')
    def validate_status(cls, v):
        if v not in ALLOWED_STATUSES:
            raise ValueError('invalid status')
        return v

    @root_validator(pre=True)
    def ensure_players_or_ids(cls, values):
        # Only derive player_ids when players provided; don't raise here so
        # field-level validators can surface proper field locations.
        players = values.get('players')
        player_ids = values.get('player_ids')

        if (player_ids is None or len(player_ids or []) == 0) and players:
            try:
                values['player_ids'] = [p.get('player_id') if isinstance(p, dict) else p.player_id for p in players]
            except Exception:
                pass

        return values

    @validator('players', pre=True, always=True)
    def validate_players_present(cls, v, values):
        player_ids = values.get('player_ids')
        if (v is None or (isinstance(v, list) and len(v) == 0)) and (player_ids is None or len(player_ids or []) == 0):
            raise ValueError('players must not be empty')
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
    # Make initial/current state optional for serialization tests that don't
    # include full state payloads.
    initial_state: Optional[Dict[str, Any]] = None
    current_state: Optional[Dict[str, Any]] = None
    status: str
    result: Optional[str] = None
    winner_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    players: List[GamePlayerResponse] = []

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
    # Accept optional move_notation so compatibility wrapper may omit it when
    # move data is passed as structured `move_data` (e.g. poker actions).
    move_notation: Optional[str]
    position_before: Optional[str] = None
    position_after: Optional[str] = None
    time_taken: Optional[float] = None
    analysis: Optional[Dict[str, Any]] = None

    @validator('move_number')
    def validate_move_number(cls, v):
        if v is None:
            return v
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
