from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlayerBase(BaseModel):
    display_name: str
    is_human: bool = False
    provider: Optional[str] = None
    model_id: Optional[str] = None

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(BaseModel):
    display_name: Optional[str] = None
    provider: Optional[str] = None
    model_id: Optional[str] = None

class Player(PlayerBase):
    id: int
    elo_chess: int
    elo_poker: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
