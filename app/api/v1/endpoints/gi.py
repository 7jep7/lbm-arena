from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json

from app.services.gi_service import GIService
from app.core.database import get_db
from app.models.game import Game as GameModel, GameType

router = APIRouter()
gi_service = GIService()


def _get_gi_tournament_or_error(tournament_id: int, db: Session) -> GameModel:
    """Helper to get a GI tournament or raise 404"""
    tournament = db.query(GameModel).filter(
        GameModel.id == tournament_id,
        GameModel.game_type == GameType.GI.value
    ).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="GI tournament not found")
    return tournament


@router.get("/")
def gi_info():
    """Get information about the General Intelligence game type"""
    return {
        "game_type": "gi",
        "name": "General Intelligence Tournament",
        "description": "AI agents compete across diverse intellectual challenges",
        "format": [
            "Tournament-based competition",
            "Players generate questions from seed prompts",
            "All players answer all questions (except their own)",
            "Players score each other's answers (0-10 scale)",
            "Highest total score wins"
        ],
        "phases": [
            "setup - Tournament initialization",
            "question_generation - Players create questions",
            "answering - Players answer questions",
            "scoring - Players evaluate answers",
            "completed - Final results available"
        ],
        "endpoints": {
            "create_tournament": "POST /tournament - Create new tournament",
            "get_status": "GET /{tournament_id}/status - Get tournament status",
            "assign_players": "POST /{tournament_id}/assign-players - Assign players to prompts",
            "submit_questions": "POST /{tournament_id}/questions - Submit questions",
            "submit_answer": "POST /{tournament_id}/answer - Submit answer",
            "submit_score": "POST /{tournament_id}/score - Submit score",
            "get_tasks": "GET /{tournament_id}/tasks/{player_id} - Get player tasks"
        }
    }


@router.post("/tournament")
def create_tournament(tournament_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new General Intelligence tournament"""
    try:
        num_players = tournament_data.get("num_players", 2)
        num_prompts = tournament_data.get("num_prompts", 3)
        
        tournament_state = gi_service.create_new_tournament(num_players, num_prompts)
        
        # Create game record in database
        game = GameModel(
            game_type=GameType.GI.value,
            status="pending",
            initial_state=tournament_state,
            current_state=tournament_state
        )
        
        db.add(game)
        db.commit()
        db.refresh(game)
        
        return {
            "tournament_id": game.id,
            "internal_tournament_id": tournament_state["tournament_id"],
            "status": tournament_state["status"],
            "num_players": tournament_state["num_players"],
            "num_prompts": tournament_state["num_prompts"],
            "seed_prompts": tournament_state["seed_prompts"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating tournament: {str(e)}")


@router.get("/{tournament_id}/status")
def get_tournament_status(tournament_id: int, db: Session = Depends(get_db)):
    """Get current tournament status"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid tournament state")
    
    status_info = gi_service.get_tournament_status(current_state)
    status_info["db_tournament_id"] = tournament_id
    
    return status_info


@router.post("/{tournament_id}/assign-players")
def assign_players(tournament_id: int, player_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Assign players to the tournament and their prompts"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
        player_ids = player_data.get("player_ids", [])
        
        if not player_ids:
            raise ValueError("player_ids must be provided")
        
        new_state = gi_service.assign_prompts_to_players(current_state, player_ids)
        
        # Update database
        tournament.current_state = json.dumps(new_state)
        tournament.status = "in_progress"
        db.commit()
        
        return {
            "tournament_id": tournament_id,
            "status": new_state["status"],
            "current_phase": new_state["current_phase"],
            "player_assignments": new_state["player_assignments"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error assigning players: {str(e)}")


@router.post("/{tournament_id}/questions")
def submit_questions(tournament_id: int, question_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Submit questions for the tournament"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
        
        player_id = question_data.get("player_id")
        questions = question_data.get("questions", [])
        
        if not player_id:
            raise ValueError("player_id must be provided")
        if not questions:
            raise ValueError("questions must be provided")
        
        new_state = gi_service.submit_questions(current_state, str(player_id), questions)
        
        # Update database
        tournament.current_state = json.dumps(new_state)
        db.commit()
        
        return {
            "tournament_id": tournament_id,
            "player_id": player_id,
            "questions_submitted": len(questions),
            "current_phase": new_state["current_phase"],
            "status": "success"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting questions: {str(e)}")


@router.get("/{tournament_id}/questions")
def get_questions(tournament_id: int, db: Session = Depends(get_db)):
    """Get all questions for answering"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid tournament state")
    
    questions = gi_service.get_questions_for_answering(current_state)
    
    return {
        "tournament_id": tournament_id,
        "questions": questions,
        "total_questions": len(questions)
    }


@router.post("/{tournament_id}/answer")
def submit_answer(tournament_id: int, answer_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Submit an answer to a question"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
        
        player_id = answer_data.get("player_id")
        question_id = answer_data.get("question_id")
        answer = answer_data.get("answer")
        
        if not all([player_id, question_id, answer]):
            raise ValueError("player_id, question_id, and answer must be provided")
        
        new_state = gi_service.submit_answer(current_state, str(player_id), question_id, answer)
        
        # Update database
        tournament.current_state = json.dumps(new_state)
        db.commit()
        
        return {
            "tournament_id": tournament_id,
            "player_id": player_id,
            "question_id": question_id,
            "current_phase": new_state["current_phase"],
            "status": "success"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting answer: {str(e)}")


@router.post("/{tournament_id}/score")
def submit_score(tournament_id: int, score_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Submit a score for an answer"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
        
        scorer_player_id = score_data.get("scorer_player_id")
        answer_id = score_data.get("answer_id")
        score = score_data.get("score")
        
        if not all([scorer_player_id, answer_id]):
            raise ValueError("scorer_player_id and answer_id must be provided")
        if score is None or not isinstance(score, int):
            raise ValueError("score must be an integer")
        
        new_state = gi_service.submit_score(current_state, str(scorer_player_id), answer_id, score)
        
        # Update database
        tournament.current_state = json.dumps(new_state)
        if new_state.get("status") == "completed":
            tournament.status = "completed"
        db.commit()
        
        return {
            "tournament_id": tournament_id,
            "scorer_player_id": scorer_player_id,
            "answer_id": answer_id,
            "score": score,
            "current_phase": new_state["current_phase"],
            "final_scores": new_state.get("final_scores", {}),
            "status": "success"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting score: {str(e)}")


@router.get("/{tournament_id}/tasks/{player_id}")
def get_player_tasks(tournament_id: int, player_id: str, db: Session = Depends(get_db)):
    """Get current tasks for a specific player"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid tournament state")
    
    tasks = gi_service.get_player_tasks(current_state, player_id)
    
    return {
        "tournament_id": tournament_id,
        "player_id": player_id,
        **tasks
    }


@router.get("/{tournament_id}/results")
def get_results(tournament_id: int, db: Session = Depends(get_db)):
    """Get final tournament results"""
    tournament = _get_gi_tournament_or_error(tournament_id, db)
    
    try:
        current_state = json.loads(tournament.current_state) if isinstance(tournament.current_state, str) else tournament.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid tournament state")
    
    if current_state.get("current_phase") != "completed":
        raise HTTPException(status_code=400, detail="Tournament not completed yet")
    
    final_scores = current_state.get("final_scores", {})
    
    # Create leaderboard
    leaderboard = []
    for player_id, score in final_scores.items():
        leaderboard.append({
            "player_id": player_id,
            "final_score": score,
            "rank": 0  # Will be set below
        })
    
    # Sort by score descending
    leaderboard.sort(key=lambda x: x["final_score"], reverse=True)
    
    # Add ranks
    for i, entry in enumerate(leaderboard):
        entry["rank"] = i + 1
    
    winner = leaderboard[0] if leaderboard else None
    
    return {
        "tournament_id": tournament_id,
        "status": "completed",
        "leaderboard": leaderboard,
        "winner": winner,
        "total_participants": len(final_scores)
    }
