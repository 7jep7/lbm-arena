from pydantic import BaseModel, Field, constr
from typing import Optional
from datetime import datetime

class PlayerBase(BaseModel):
    # Use strict string constraint so numeric values are not silently coerced (tests expect 422 for non-string)
    display_name: constr(min_length=1, max_length=255, strict=True)  # type: ignore
    is_human: bool = False
    provider: Optional[str] = None
    model_id: Optional[str] = None

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    display_name: Optional[constr(min_length=1, max_length=255, strict=True)] = None  # type: ignore
    provider: Optional[str] = None
    model_id: Optional[str] = None

class Player(PlayerBase):
    id: int
    elo_chess: int = 1500
    elo_poker: int = 1500
    created_at: datetime
    
    class Config:
        orm_mode = True
