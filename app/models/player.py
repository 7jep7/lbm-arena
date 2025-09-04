from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float
from sqlalchemy.sql import func
from app.core.database import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    is_human = Column(Boolean, default=False, nullable=False)
    display_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=True)  # openai, anthropic, etc.
    model_id = Column(String(255), nullable=True)  # gpt-4, claude-3, etc.
    elo_chess = Column(Integer, default=1200)
    elo_poker = Column(Integer, default=1200)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Removed for now
    
    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.display_name}', provider='{self.provider}')>"
