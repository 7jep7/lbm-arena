from treys import Card, Deck, Evaluator
from typing import Dict, Any, List, Optional
import random

class PokerService:
    def __init__(self):
        self.evaluator = Evaluator()
    
    def create_new_game(self, num_players: int = 2) -> Dict[str, Any]:
        """Create a new Texas Hold'em poker game"""
        if num_players < 2 or num_players > 10:
            raise ValueError("Number of players must be between 2 and 10")
        
        deck = Deck()
        deck.shuffle()
        
        # Deal hole cards to each player
        players = {}
        for i in range(num_players):
            player_cards = [deck.draw(1)[0], deck.draw(1)[0]]
            players[f"player_{i}"] = {
                "hole_cards": [Card.int_to_str(card) for card in player_cards],
                "hole_cards_int": player_cards,
                "chips": 1000,  # Starting chips
                "bet": 0,
                "folded": False,
                "all_in": False
            }
        
        return {
            "players": players,
            "community_cards": [],
            "community_cards_int": [],
            "pot": 0,
            "current_bet": 0,
            "dealer": 0,
            "current_player": 1,  # Player after dealer
            "stage": "preflop",  # preflop, flop, turn, river, showdown
            "deck_remaining": len(deck.cards),
            "round": 1
        }
    
    def deal_flop(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Deal the flop (3 community cards)"""
        if game_state["stage"] != "preflop":
            raise ValueError("Can only deal flop after preflop")
        
        deck = Deck()
        # Remove already dealt cards (approximate - in real implementation, track deck state)
        
        flop_cards = [deck.draw(1)[0] for _ in range(3)]
        
        game_state["community_cards"].extend([Card.int_to_str(card) for card in flop_cards])
        game_state["community_cards_int"].extend(flop_cards)
        game_state["stage"] = "flop"
        game_state["current_bet"] = 0
        
        return game_state
    
    def deal_turn(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Deal the turn (4th community card)"""
        if game_state["stage"] != "flop":
            raise ValueError("Can only deal turn after flop")
        
        deck = Deck()
        turn_card = deck.draw(1)[0]
        
        game_state["community_cards"].append(Card.int_to_str(turn_card))
        game_state["community_cards_int"].append(turn_card)
        game_state["stage"] = "turn"
        game_state["current_bet"] = 0
        
        return game_state
    
    def deal_river(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Deal the river (5th community card)"""
        if game_state["stage"] != "turn":
            raise ValueError("Can only deal river after turn")
        
        deck = Deck()
        river_card = deck.draw(1)[0]
        
        game_state["community_cards"].append(Card.int_to_str(river_card))
        game_state["community_cards_int"].append(river_card)
        game_state["stage"] = "river"
        game_state["current_bet"] = 0
        
        return game_state
    
    def evaluate_hand(self, hole_cards: List[int], community_cards: List[int]) -> int:
        """Evaluate a poker hand. Lower score is better."""
        if len(community_cards) < 5:
            return 0  # Can't evaluate until river
        
        return self.evaluator.evaluate(hole_cards, community_cards)
    
    def get_hand_strength(self, hole_cards: List[int], community_cards: List[int]) -> str:
        """Get human-readable hand strength"""
        if len(community_cards) < 5:
            return "Unknown"
        
        score = self.evaluator.evaluate(hole_cards, community_cards)
        return self.evaluator.class_to_string(self.evaluator.get_rank_class(score))
    
    def make_action(self, game_state: Dict[str, Any], player_id: str, action: str, amount: int = 0) -> Dict[str, Any]:
        """Process a player action (fold, call, raise, check)"""
        if player_id not in game_state["players"]:
            raise ValueError(f"Player {player_id} not in game")
        
        player = game_state["players"][player_id]
        
        if player["folded"]:
            raise ValueError(f"Player {player_id} has already folded")
        
        if action == "fold":
            player["folded"] = True
        elif action == "call":
            call_amount = game_state["current_bet"] - player["bet"]
            if call_amount > player["chips"]:
                # All-in
                game_state["pot"] += player["chips"]
                player["bet"] += player["chips"]
                player["chips"] = 0
                player["all_in"] = True
            else:
                game_state["pot"] += call_amount
                player["bet"] += call_amount
                player["chips"] -= call_amount
        elif action == "raise":
            total_bet = game_state["current_bet"] + amount
            bet_increase = total_bet - player["bet"]
            
            if bet_increase > player["chips"]:
                # All-in
                game_state["pot"] += player["chips"]
                player["bet"] += player["chips"]
                player["chips"] = 0
                player["all_in"] = True
            else:
                game_state["pot"] += bet_increase
                player["bet"] = total_bet
                player["chips"] -= bet_increase
                game_state["current_bet"] = total_bet
        elif action == "check":
            if game_state["current_bet"] > player["bet"]:
                raise ValueError("Cannot check when there's a bet to call")
        
        return game_state
    
    def is_round_complete(self, game_state: Dict[str, Any]) -> bool:
        """Check if the current betting round is complete"""
        active_players = [p for p in game_state["players"].values() if not p["folded"]]
        
        if len(active_players) <= 1:
            return True
        
        # All active players have matched the current bet or are all-in
        current_bet = game_state["current_bet"]
        for player in active_players:
            if not player["all_in"] and player["bet"] != current_bet:
                return False
        
        return True
