import openai
import anthropic
from typing import Optional, Dict, Any, List
from app.core.config import settings

class LLMService:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        else:
            self.anthropic_client = None
    
    async def get_chess_move(self, provider: str, model_id: str, game_state: Dict[str, Any], player_color: str) -> str:
        """Get a chess move from an LLM"""
        
        board_fen = game_state["board_fen"]
        legal_moves = game_state["legal_moves"]
        
        prompt = f"""
You are playing chess as {player_color}. 

Current board position (FEN): {board_fen}
Legal moves: {', '.join(legal_moves)}
Turn: {game_state.get('turn', 'unknown')}

Please choose one legal move from the list above. Respond with only the move in UCI format (e.g., 'e2e4').
Consider tactical and strategic factors in your decision.
"""

        if provider == "openai":
            return await self._get_openai_response(model_id, prompt, legal_moves)
        elif provider == "anthropic":
            return await self._get_anthropic_response(model_id, prompt, legal_moves)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def get_poker_action(self, provider: str, model_id: str, game_state: Dict[str, Any], player_id: str) -> Dict[str, Any]:
        """Get a poker action from an LLM"""
        
        player_data = game_state["players"][player_id]
        hole_cards = player_data["hole_cards"]
        community_cards = game_state["community_cards"]
        
        prompt = f"""
You are playing Texas Hold'em poker.

Your hole cards: {', '.join(hole_cards)}
Community cards: {', '.join(community_cards)}
Current stage: {game_state['stage']}
Pot size: {game_state['pot']}
Current bet: {game_state['current_bet']}
Your chips: {player_data['chips']}
Your current bet: {player_data['bet']}

Available actions:
- fold: Give up your hand
- call: Match the current bet ({game_state['current_bet'] - player_data['bet']} chips needed)
- raise: Increase the bet (specify amount)
- check: Pass without betting (only if no bet to call)

Respond with a JSON object like:
{{"action": "call"}} or {{"action": "raise", "amount": 100}} or {{"action": "fold"}} or {{"action": "check"}}
"""

        if provider == "openai":
            response = await self._get_openai_response(model_id, prompt)
        elif provider == "anthropic":
            response = await self._get_anthropic_response(model_id, prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # Parse JSON response
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to simple action
            if "fold" in response.lower():
                return {"action": "fold"}
            elif "call" in response.lower():
                return {"action": "call"}
            elif "check" in response.lower():
                return {"action": "check"}
            else:
                return {"action": "fold"}  # Default safe action
    
    async def _get_openai_response(self, model_id: str, prompt: str, valid_options: Optional[List[str]] = None) -> str:
        """Get response from OpenAI API"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        try:
            response = openai.ChatCompletion.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            # If valid options provided (for chess moves), validate
            if valid_options and content not in valid_options:
                # Try to extract valid move from response
                for option in valid_options:
                    if option in content:
                        return option
                # If no valid move found, return first legal move
                return valid_options[0] if valid_options else content
            
            return content
            
        except Exception as e:
            # Fallback for chess moves
            if valid_options:
                return valid_options[0]  # Return first legal move as fallback
            raise e
    
    async def _get_anthropic_response(self, model_id: str, prompt: str, valid_options: Optional[List[str]] = None) -> str:
        """Get response from Anthropic API"""
        if not self.anthropic_client:
            raise ValueError("Anthropic API key not configured")
        
        try:
            response = self.anthropic_client.messages.create(
                model=model_id,
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            # If valid options provided (for chess moves), validate
            if valid_options and content not in valid_options:
                # Try to extract valid move from response
                for option in valid_options:
                    if option in content:
                        return option
                # If no valid move found, return first legal move
                return valid_options[0] if valid_options else content
            
            return content
            
        except Exception as e:
            # Fallback for chess moves
            if valid_options:
                return valid_options[0]  # Return first legal move as fallback
            raise e
