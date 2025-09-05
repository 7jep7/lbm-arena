from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    is_human = Column(Boolean, default=False, nullable=False)
    display_name = Column(String(255), nullable=False)
    provider = Column(String(100), nullable=True)  # openai, anthropic, etc.
    model_id = Column(String(255), nullable=True)  # gpt-4, claude-3, etc.
    # DB default remains 1200; API layer overrides to 1500 for new players per tests.
    elo_chess = Column(Integer, default=1200, nullable=False)
    elo_poker = Column(Integer, default=1200, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
        # updated_at intentionally omitted until migration applied (schema allows optional)
    
    # Relationships
    moves = relationship("Move", back_populates="player")
    game_players = relationship("GamePlayer", back_populates="player")
    
    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.display_name}', provider='{self.provider}')>"
