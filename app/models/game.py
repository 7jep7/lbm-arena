from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class GameType(str, enum.Enum):
    CHESS = "chess"
    POKER = "poker"

class GameStatus(str, enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABORTED = "aborted"

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    game_type = Column(Enum(GameType), nullable=False)
    status = Column(Enum(GameStatus), default=GameStatus.WAITING)
    player1_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    initial_state = Column(Text, nullable=True)  # JSON string of initial game state
    current_state = Column(Text, nullable=True)  # JSON string of current game state
    winner_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Removed for now
    
    # Relationships
    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])
    winner = relationship("Player", foreign_keys=[winner_id])
    # moves = relationship("Move", back_populates="game")  # Commented out for now
    
    def __repr__(self):
        return f"<Game(id={self.id}, type='{self.game_type}', status='{self.status}')>"
