from fastapi import APIRouter
from app.api.v1.endpoints import games, players, chess, tictactoe, gi, sfc

api_router = APIRouter()

api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(players.router, prefix="/players", tags=["players"])
api_router.include_router(chess.router, prefix="/chess", tags=["chess"])
api_router.include_router(tictactoe.router, prefix="/tictactoe", tags=["tictactoe"])
api_router.include_router(gi.router, prefix="/gi", tags=["general-intelligence"])
api_router.include_router(sfc.router, prefix="/sfc", tags=["sequential-function-charts"])
