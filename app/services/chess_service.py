import chess
import chess.engine
from typing import Optional, Dict, Any, List
import json

class ChessService:
    def __init__(self):
        self.engine_path = None  # Path to chess engine (e.g., Stockfish)
    
    def create_new_game(self) -> Dict[str, Any]:
        """Create a new chess game and return initial state"""
        board = chess.Board()
        return {
            "board_fen": board.fen(),
            "turn": "white",
            "move_count": 0,
            "status": "in_progress",
            "legal_moves": [move.uci() for move in board.legal_moves],
            "check": board.is_check(),
            "checkmate": board.is_checkmate(),
            "stalemate": board.is_stalemate()
        }
    
    def make_move(self, game_state: Dict[str, Any], move_uci: str) -> Dict[str, Any]:
        """Make a move and return updated game state"""
        board = chess.Board(game_state["board_fen"])
        
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board.legal_moves:
                board.push(move)
                
                # Update game state
                new_state = {
                    "board_fen": board.fen(),
                    "turn": "black" if board.turn == chess.BLACK else "white",
                    "move_count": game_state["move_count"] + 1,
                    "last_move": move_uci,
                    "legal_moves": [move.uci() for move in board.legal_moves],
                    "check": board.is_check(),
                    "checkmate": board.is_checkmate(),
                    "stalemate": board.is_stalemate(),
                    "insufficient_material": board.is_insufficient_material(),
                    "threefold_repetition": board.is_repetition(3),
                    "fifty_moves": board.is_fifty_moves()
                }
                
                # Determine game status
                if board.is_checkmate():
                    new_state["status"] = "completed"
                    new_state["result"] = "checkmate"
                    new_state["winner"] = "white" if board.turn == chess.BLACK else "black"
                elif board.is_stalemate() or board.is_insufficient_material() or board.is_repetition(3) or board.is_fifty_moves():
                    new_state["status"] = "completed"
                    new_state["result"] = "draw"
                    new_state["winner"] = None
                else:
                    new_state["status"] = "in_progress"
                
                return new_state
            else:
                raise ValueError(f"Illegal move: {move_uci}")
        except ValueError as e:
            raise ValueError(f"Invalid move format: {move_uci}") from e
    
    def get_legal_moves(self, board_fen: str) -> List[str]:
        """Get all legal moves for current position"""
        board = chess.Board(board_fen)
        return [move.uci() for move in board.legal_moves]
    
    def move_to_san(self, board_fen: str, move_uci: str) -> str:
        """Convert UCI move to Standard Algebraic Notation"""
        board = chess.Board(board_fen)
        move = chess.Move.from_uci(move_uci)
        return board.san(move)
    
    def is_game_over(self, board_fen: str) -> bool:
        """Check if the game is over"""
        board = chess.Board(board_fen)
        return board.is_game_over()
    
    def get_game_result(self, board_fen: str) -> Optional[str]:
        """Get the result of the game if it's over"""
        board = chess.Board(board_fen)
        if not board.is_game_over():
            return None
        
        result = board.result()
        if result == "1-0":
            return "white_wins"
        elif result == "0-1":
            return "black_wins"
        else:
            return "draw"
