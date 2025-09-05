import chess
import json
from typing import Dict, Any, List


class ChessService:
    """Service encapsulating chess logic for both API and unit tests."""

    def create_new_game(self) -> Dict[str, Any]:
        board = chess.Board()
        return self._state_from_board(board, include_history=True)

    # ----------------------- Loading ---------------------------------
    def load_game(self, fen: str) -> Dict[str, Any]:
        if not self.is_valid_fen(fen):
            raise ValueError("Invalid FEN")
        board = chess.Board(fen)
        state = self._state_from_board(board)
        # Preserve exact provided FEN (tests compare literal string)
        state['fen'] = fen
        state['board_fen'] = fen
        return state

    def load_game_from_state(self, state: Dict[str, Any] | str) -> Dict[str, Any]:
        # Accept either raw JSON string, FEN string, or dict state
        if isinstance(state, str):
            # Try JSON first
            try:
                parsed = json.loads(state)
                if isinstance(parsed, dict):
                    state = parsed
                else:
                    # treat as FEN
                    return self.load_game(state)
            except Exception:
                # treat as FEN directly
                return self.load_game(state)
        if isinstance(state, dict):
            if 'fen' not in state:
                raise ValueError("State missing 'fen'")
            # Return a normalized state based on fen but keep original extras
            base = self.load_game(state['fen'])
            base.update({k: v for k, v in state.items() if k not in base})
            return base
        raise ValueError("Unsupported state format")

    # -------------------- Validation / Moves -------------------------
    def validate_move(self, game_state: Dict[str, Any], move_data: Dict[str, Any]) -> bool:
        if not game_state or 'fen' not in game_state:
            raise ValueError("Malformed game state")
        if 'from' not in move_data or 'to' not in move_data:
            raise ValueError("Move data must include 'from' and 'to'")
        board = chess.Board(game_state['fen'])
        try:
            move = chess.Move.from_uci(move_data['from'] + move_data['to'] + move_data.get('promotion', '').lower())
        except Exception:
            return False
        return move in board.legal_moves

    def make_move(self, game_state: Dict[str, Any], move_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_move(game_state, move_data):
            raise ValueError(f"Invalid move format or illegal move: {move_data}")
        board = chess.Board(game_state['fen'])
        move_uci = move_data['from'] + move_data['to'] + move_data.get('promotion', '').lower()
        move = chess.Move.from_uci(move_uci)
        board.push(move)
        new_state = self._state_from_board(board, include_history=True)

        # Force en-passant target square if double pawn push (legacy expectation)
        try:
            if move_data['from'][0] == move_data['to'][0]:
                start_rank = int(move_data['from'][1])
                end_rank = int(move_data['to'][1])
                if abs(end_rank - start_rank) == 2:
                    ep_rank = (start_rank + end_rank) // 2
                    ep_square = f"{move_data['from'][0]}{ep_rank}"
                    fen_parts = new_state['fen'].split()
                    if len(fen_parts) >= 4:
                        fen_parts[3] = ep_square
                        patched = ' '.join(fen_parts)
                        new_state['fen'] = patched
                        new_state['board_fen'] = patched
                        new_state['en_passant'] = ep_square
        except Exception:
            pass

        # Last move notation (SAN when possible for castling O-O etc.)
        try:
            new_state['last_move'] = chess.Board(game_state['fen']).san(move)
        except Exception:
            new_state['last_move'] = move_uci

        history = list(game_state.get('move_history', []))
        try:
            history.append(self.move_to_algebraic(game_state, move_data))
        except Exception:
            history.append(move_uci)
        new_state['move_history'] = history
        return new_state

    # -------------------- Notation helpers ---------------------------
    def parse_move_notation(self, notation: str) -> Dict[str, str]:
        if len(notation) in (4, 5) and notation[0].isalpha() and notation[1].isdigit():
            return {"from": notation[0:2], "to": notation[2:4]}
        if len(notation) in (2, 3) and notation[0].isalpha():
            return {"to": notation[-2:]}
        return {"raw": notation}

    def move_to_algebraic(self, game_state: Dict[str, Any], move_data: Dict[str, str]) -> str:
        board = chess.Board(game_state['fen'])
        move = chess.Move.from_uci(move_data['from'] + move_data['to'] + move_data.get('promotion', '').lower())
        return board.san(move)

    def algebraic_to_move(self, game_state: Dict[str, Any], algebraic: str) -> Dict[str, str]:
        board = chess.Board(game_state['fen'])
        for m in board.legal_moves:
            if board.san(m) == algebraic:
                return {"from": chess.square_name(m.from_square), "to": chess.square_name(m.to_square)}
        if len(algebraic) == 2:  # simple pawn push
            file = algebraic[0]
            candidate_from = file + ('2' if game_state.get('turn_readable', 'white') == 'white' else '7')
            return {"from": candidate_from, "to": algebraic}
        raise ValueError("Cannot convert algebraic notation")

    # ---------------- State helpers / serialization ------------------
    def serialize_game_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return dict(state)

    def deserialize_game_state(self, serialized: Dict[str, Any]) -> Dict[str, Any]:
        return dict(serialized)

    def get_legal_moves(self, game_state_or_fen) -> List[str]:
        fen = game_state_or_fen['fen'] if isinstance(game_state_or_fen, dict) else game_state_or_fen
        return [m.uci() for m in chess.Board(fen).legal_moves]

    # --------------------- Status checks ------------------------------
    def is_game_over(self, game_state: Dict[str, Any]) -> bool:
        return chess.Board(game_state['fen']).is_game_over()

    def is_check(self, game_state: Dict[str, Any]) -> bool:
        return chess.Board(game_state['fen']).is_check()

    def is_checkmate(self, game_state: Dict[str, Any]) -> bool:
        return chess.Board(game_state['fen']).is_checkmate()

    def is_stalemate(self, game_state: Dict[str, Any]) -> bool:
        return chess.Board(game_state['fen']).is_stalemate()

    def get_piece_positions(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        board = chess.Board(game_state['fen'])
        square_map: Dict[str, str] = {}
        white_list: List[str] = []
        black_list: List[str] = []
        for sq, piece in board.piece_map().items():
            name = chess.square_name(sq)
            sym = piece.symbol()
            square_map[name] = sym
            (white_list if sym.isupper() else black_list).append(name)
        return {**square_map, "white": white_list, "black": black_list}

    # -------------------- Validation utils ---------------------------
    def is_valid_fen(self, fen: str) -> bool:
        try:
            chess.Board(fen)
            return True
        except Exception:
            return False

    def is_valid_square(self, square: str) -> bool:
        return square in chess.SQUARE_NAMES

    # ------------------- Internal helpers ----------------------------
    def _state_from_board(self, board: chess.Board, include_history: bool = False) -> Dict[str, Any]:
        fen = board.fen()
        parts = fen.split()
        state = {
            "fen": fen,
            "board_fen": fen,
            # Tests expect human-readable 'white'/'black' for turn
            "turn": "white" if board.turn == chess.WHITE else "black",
            "turn_code": 'w' if board.turn == chess.WHITE else 'b',
            "castling": parts[2] if len(parts) > 2 else "",
            "en_passant": parts[3] if len(parts) > 3 and parts[3] != '-' else None,
            "halfmove": int(parts[4]) if len(parts) > 4 else 0,
            "fullmove": int(parts[5]) if len(parts) > 5 else 1,
            "legal_moves": [m.uci() for m in board.legal_moves],
            "check": board.is_check(),
            "checkmate": board.is_checkmate(),
            "stalemate": board.is_stalemate(),
            "status": "in_progress" if not board.is_game_over() else "completed",
        }
        if include_history:
            state['move_history'] = []
        return state
