from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from uuid import uuid4

class Move(Base):
    __tablename__ = "moves"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    game_id = Column(String(36), ForeignKey("games.id"), nullable=False)
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    move_number = Column(Integer, nullable=False)
    move_data = Column(JSON, nullable=False)  # move details stored as JSON
    notation = Column(String(50), nullable=True)  # Human-readable move notation (e.g., "e4", "Nf3")
    time_taken = Column(Integer, nullable=True)  # Time taken in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="moves")
    player = relationship("Player", back_populates="moves")
    
    def __repr__(self):
        return f"<Move(id={self.id}, game_id={self.game_id}, notation='{self.notation}')>"

class GamePlayer(Base):
    __tablename__ = "game_players"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    game_id = Column(String(36), ForeignKey("games.id"), nullable=False)
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    # position is the immutable slot/identity of a player within a game
    position = Column(Text, nullable=False)  # e.g. 'White', 'Seat 1', 'Player A'
    elo_before = Column(Integer, nullable=True)
    elo_after = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    game = relationship("Game", back_populates="game_players")
    player = relationship("Player", back_populates="game_players")

    def __repr__(self):
        return f"<GamePlayer(game_id={self.game_id}, player_id={self.player_id}, position='{self.position}')>"
