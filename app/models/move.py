from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Move(Base):
    __tablename__ = "moves"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    move_number = Column(Integer, nullable=False)
    move_data = Column(Text, nullable=False)  # JSON string of move details
    notation = Column(String(50), nullable=True)  # Human-readable move notation (e.g., "e4", "Nf3")
    time_taken = Column(Integer, nullable=True)  # Time taken in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="moves")
    player = relationship("Player")
    
    def __repr__(self):
        return f"<Move(id={self.id}, game_id={self.game_id}, notation='{self.notation}')>"

class GamePlayer(Base):
    __tablename__ = "game_players"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    position = Column(String(20), nullable=False)  # "white", "black", "player1", "player2", etc.
    elo_before = Column(Integer, nullable=True)
    elo_after = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    game = relationship("Game", back_populates="players")
    player = relationship("Player")
    
    def __repr__(self):
        return f"<GamePlayer(game_id={self.game_id}, player_id={self.player_id}, position='{self.position}')>"
