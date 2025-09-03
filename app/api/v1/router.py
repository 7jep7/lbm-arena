from fastapi import APIRouter
from app.api.v1.endpoints import games, players, chess

api_router = APIRouter()

api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(chess.router, prefix="/chess", tags=["chess"])
