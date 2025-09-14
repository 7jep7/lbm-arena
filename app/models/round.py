from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from uuid import uuid4


class Round(Base):
    __tablename__ = "rounds"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    game_id = Column(String(36), ForeignKey("games.id"), nullable=False)
    round_number = Column(Integer, nullable=False)  # sequential within a game
    dealer_player_id = Column(String(36), ForeignKey("players.id"), nullable=True)
    big_blind_player_id = Column(String(36), ForeignKey("players.id"), nullable=True)
    small_blind_player_id = Column(String(36), ForeignKey("players.id"), nullable=True)
    players_snapshot = Column(JSON, nullable=True)  # seat snapshot at start of round
    big_blind_seat = Column(Integer, nullable=True)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    game = relationship("Game", back_populates="rounds")
    round_players = relationship("RoundPlayer", back_populates="round", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Round(id={self.id}, game_id={self.game_id}, round_number={self.round_number})>"


class RoundPlayer(Base):
    __tablename__ = "round_players"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid4()))
    round_id = Column(String(36), ForeignKey("rounds.id"), nullable=False)
    player_id = Column(String(36), ForeignKey("players.id"), nullable=False)
    # role is dynamic per-round (e.g. dealer, big_blind, small_blind)
    role = Column(Text, nullable=True)
    seat_number = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    round = relationship("Round", back_populates="round_players")

    def __repr__(self):
        return f"<RoundPlayer(round_id={self.round_id}, player_id={self.player_id}, role='{self.role}')>"
