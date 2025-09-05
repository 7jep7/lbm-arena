from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base
import json

class GameType(str, enum.Enum):
    CHESS = "chess"
    POKER = "poker"

class GameStatus(str, enum.Enum):
    WAITING = "waiting"  # Added to match tests
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABORTED = "aborted"

    # Backward compatibility alias (older data that stored 'pending')
    PENDING = "pending"

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    game_type = Column(Enum(GameType), nullable=False)
    status = Column(Enum(GameStatus), default=GameStatus.WAITING)
    player1_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    # Store JSON as text for existing DB, but expose dict interface via properties
    initial_state_raw = Column("initial_state", Text, nullable=True)
    current_state_raw = Column("current_state", Text, nullable=True)
    winner_id = Column(Integer, ForeignKey("players.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])
    winner = relationship("Player", foreign_keys=[winner_id])
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")
    game_players = relationship("GamePlayer", back_populates="game", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Game(id={self.id}, type='{self.game_type}', status='{self.status}')>"

    # JSON convenience accessors -------------------------------------------------
    @property
    def initial_state(self):  # type: ignore
        if self.initial_state_raw is None:
            return None
        try:
            if isinstance(self.initial_state_raw, (dict, list)):
                return self.initial_state_raw
            return json.loads(self.initial_state_raw)
        except Exception:
            return self.initial_state_raw

    @initial_state.setter
    def initial_state(self, value):  # type: ignore
        if value is None:
            self.initial_state_raw = None
        elif isinstance(value, (dict, list)):
            self.initial_state_raw = json.dumps(value)
        else:
            self.initial_state_raw = value

    @property
    def current_state(self):  # type: ignore
        if self.current_state_raw is None:
            return None
        try:
            if isinstance(self.current_state_raw, (dict, list)):
                return self.current_state_raw
            return json.loads(self.current_state_raw)
        except Exception:
            return self.current_state_raw

    @current_state.setter
    def current_state(self, value):  # type: ignore
        if value is None:
            self.current_state_raw = None
        elif isinstance(value, (dict, list)):
            self.current_state_raw = json.dumps(value)
        else:
            self.current_state_raw = value

    # Backward compatibility for tests expecting game.players iterable
    @property
    def players(self):
        players = []
        if self.player1 is not None:
            players.append({"player_id": self.player1.id, "position": "white" if self.game_type == GameType.CHESS else "player1"})
        if self.player2 is not None:
            players.append({"player_id": self.player2.id, "position": "black" if self.game_type == GameType.CHESS else "player2"})
        # Also include any additional GamePlayer rows (e.g., poker with >2 players)
        if self.game_players:
            # Avoid duplicates for player1/player2 already added
            existing_ids = {p["player_id"] for p in players}
            for gp in self.game_players:
                if gp.player_id not in existing_ids:
                    players.append({"player_id": gp.player_id, "position": gp.position})
        return players
