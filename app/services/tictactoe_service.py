from typing import Dict, Any, List, Optional, Tuple
import json


class TicTacToeService:
    """Service encapsulating tic-tac-toe logic for both API and unit tests."""

    def create_new_game(self) -> Dict[str, Any]:
        """Create a new tic-tac-toe game"""
        return {
            "board": [["", "", ""], ["", "", ""], ["", "", ""]],  # 3x3 grid
            "current_player": "X",  # X always goes first
            "status": "in_progress",
            "winner": None,
            "moves": [],
            "move_count": 0,
            "is_draw": False
        }

    def validate_move(self, game_state: Dict[str, Any], move_data: Dict[str, Any]) -> bool:
        """Validate if a move is legal"""
        if not game_state or 'board' not in game_state:
            raise ValueError("Malformed game state")
        
        if 'row' not in move_data or 'col' not in move_data:
            raise ValueError("Move data must include 'row' and 'col'")
        
        row = move_data['row']
        col = move_data['col']
        
        # Check if coordinates are valid
        if not (0 <= row <= 2 and 0 <= col <= 2):
            return False
        
        # Check if the game is still in progress
        if game_state.get('status') != 'in_progress':
            return False
        
        # Check if the cell is empty
        board = game_state['board']
        if board[row][col] != "":
            return False
        
        return True

    def make_move(self, game_state: Dict[str, Any], move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a move and return the new game state"""
        if not self.validate_move(game_state, move_data):
            raise ValueError(f"Invalid move: {move_data}")
        
        # Create a deep copy of the game state
        new_state = json.loads(json.dumps(game_state))
        
        row = move_data['row']
        col = move_data['col']
        player = new_state['current_player']
        
        # Make the move
        new_state['board'][row][col] = player
        new_state['move_count'] += 1
        
        # Record the move
        move_record = {
            "player": player,
            "row": row,
            "col": col,
            "move_number": new_state['move_count']
        }
        new_state['moves'].append(move_record)
        
        # Check for win condition
        winner = self._check_winner(new_state['board'])
        if winner:
            new_state['winner'] = winner
            new_state['status'] = 'completed'
        elif self._is_board_full(new_state['board']):
            new_state['is_draw'] = True
            new_state['status'] = 'completed'
        else:
            # Switch to the other player
            new_state['current_player'] = "O" if player == "X" else "X"
        
        return new_state

    def get_legal_moves(self, game_state: Dict[str, Any]) -> List[Dict[str, int]]:
        """Get all legal moves for the current game state"""
        if game_state.get('status') != 'in_progress':
            return []
        
        legal_moves = []
        board = game_state['board']
        
        for row in range(3):
            for col in range(3):
                if board[row][col] == "":
                    legal_moves.append({"row": row, "col": col})
        
        return legal_moves

    def is_game_over(self, game_state: Dict[str, Any]) -> bool:
        """Check if the game is over"""
        return game_state.get('status') == 'completed'

    def get_winner(self, game_state: Dict[str, Any]) -> Optional[str]:
        """Get the winner of the game"""
        return game_state.get('winner')

    def is_draw(self, game_state: Dict[str, Any]) -> bool:
        """Check if the game is a draw"""
        return game_state.get('is_draw', False)

    def _check_winner(self, board: List[List[str]]) -> Optional[str]:
        """Check if there's a winner on the board"""
        # Check rows
        for row in board:
            if row[0] == row[1] == row[2] != "":
                return row[0]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != "":
                return board[0][col]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != "":
            return board[0][0]
        
        if board[0][2] == board[1][1] == board[2][0] != "":
            return board[0][2]
        
        return None

    def _is_board_full(self, board: List[List[str]]) -> bool:
        """Check if the board is full"""
        for row in board:
            for cell in row:
                if cell == "":
                    return False
        return True

    def serialize_game_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize game state for storage"""
        return dict(state)

    def deserialize_game_state(self, serialized: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize game state from storage"""
        return dict(serialized)

    def load_game_from_state(self, state: Dict[str, Any] | str) -> Dict[str, Any]:
        """Load a game from a stored state"""
        if isinstance(state, str):
            try:
                state = json.loads(state)
            except Exception:
                raise ValueError("Invalid JSON state")
        
        if not isinstance(state, dict):
            raise ValueError("State must be a dictionary")
        
        # Validate required fields
        required_fields = ['board', 'current_player', 'status']
        for field in required_fields:
            if field not in state:
                raise ValueError(f"State missing required field: {field}")
        
        return state

    def get_board_display(self, game_state: Dict[str, Any]) -> str:
        """Get a string representation of the board for display"""
        board = game_state['board']
        lines = []
        for i, row in enumerate(board):
            display_row = []
            for cell in row:
                display_row.append(cell if cell else " ")
            lines.append(" | ".join(display_row))
            if i < 2:
                lines.append("---------")
        return "\n".join(lines)

    def move_to_notation(self, move_data: Dict[str, Any]) -> str:
        """Convert move data to a human-readable notation"""
        return f"{move_data['row']},{move_data['col']}"

    def notation_to_move(self, notation: str) -> Dict[str, Any]:
        """Convert notation to move data"""
        try:
            parts = notation.split(',')
            if len(parts) != 2:
                raise ValueError("Invalid notation format")
            row = int(parts[0])
            col = int(parts[1])
            return {"row": row, "col": col}
        except Exception:
            raise ValueError("Invalid notation format")
