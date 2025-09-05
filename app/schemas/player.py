from pydantic import BaseModel, Field, StrictStr, StrictBool, validator
from typing import Optional
from datetime import datetime

class CompatBaseModel(BaseModel):
    def model_dump(self, *args, **kwargs):  # pydantic v2 compat
        return self.dict(*args, **kwargs)
    @classmethod
    def model_validate(cls, data):  # pydantic v2 compat
        return cls(**data)

class PlayerBase(CompatBaseModel):
    display_name: StrictStr = Field(min_length=1, max_length=255)
    is_human: StrictBool = Field(default=False)
    provider: Optional[str] = None
    model_id: Optional[str] = None

    # Provide deterministic error message for tests
    @validator('is_human', pre=True, always=True)
    def validate_is_human(cls, v):
        if isinstance(v, bool):
            return v
        raise TypeError('bool type expected')

class PlayerCreate(PlayerBase):
    pass

class PlayerUpdate(CompatBaseModel):
    display_name: Optional[StrictStr] = Field(default=None, min_length=1, max_length=255)
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
        anystr_strip_whitespace = False
        anystr_strip_whitespace = False
