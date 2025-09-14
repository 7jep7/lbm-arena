from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class GameType(str, enum.Enum):
    CHESS = "chess"
    POKER = "poker"
    TICTACTOE = "tictactoe"
    GI = "gi"  # General Intelligence
    SFC = "sfc"  # Sequential Function Charts


class GameStatus(str, enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    ABORTED = "aborted"
    PENDING = "pending"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    # Use plain string columns for enums to avoid native enum compatibility issues
    game_type = Column(String(50), nullable=False)
    status = Column(String(50), default=GameStatus.WAITING.value)
    player1_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    initial_state_raw = Column("initial_state", JSON, nullable=True)
    current_state_raw = Column("current_state", JSON, nullable=True)
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

    @property
    def initial_state(self):  # type: ignore
        return self.initial_state_raw

    @initial_state.setter
    def initial_state(self, value):  # type: ignore
        self.initial_state_raw = value

    @property
    def current_state(self):  # type: ignore
        return self.current_state_raw

    @current_state.setter
    def current_state(self, value):  # type: ignore
        self.current_state_raw = value

    @property
    def result(self):  # type: ignore
        cs = self.current_state
        if isinstance(cs, dict):
            return cs.get("result")
        return None

    @result.setter
    def result(self, value):  # type: ignore
        cs = self.current_state or {}
        if not isinstance(cs, dict):
            cs = {}
        if value is None:
            cs.pop("result", None)
        else:
            cs["result"] = value
        self.current_state = cs

    @property
    def players(self):
        players = []
        if self.player1 is not None:
            gt = (self.game_type or "").lower()
            players.append({
                "player_id": self.player1.id,
                "role": "white" if gt == GameType.CHESS.value else "player1",
            })
        if self.player2 is not None:
            gt = (self.game_type or "").lower()
            players.append({
                "player_id": self.player2.id,
                "role": "black" if gt == GameType.CHESS.value else "player2",
            })
        if self.game_players:
            existing_ids = {p["player_id"] for p in players}
            for gp in self.game_players:
                if gp.player_id not in existing_ids:
                    players.append({"player_id": gp.player_id, "role": gp.position})
        return players
