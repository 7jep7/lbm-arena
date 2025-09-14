from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import json

from app.services.sfc_service import SFCService
from app.core.database import get_db
from app.models.game import Game as GameModel, GameType

router = APIRouter()
sfc_service = SFCService()


def _get_sfc_challenge_or_error(challenge_id: int, db: Session) -> GameModel:
    """Helper to get an SFC challenge or raise 404"""
    challenge = db.query(GameModel).filter(
        GameModel.id == challenge_id,
        GameModel.game_type == GameType.SFC.value
    ).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="SFC challenge not found")
    return challenge


@router.get("/")
def sfc_info():
    """Get information about the SFC (Sequential Function Charts) game type"""
    return {
        "game_type": "sfc",
        "name": "Sequential Function Charts Programming",
        "description": "Program PLCs using Sequential Function Charts for industrial automation",
        "format": [
            "Challenge-based programming competition",
            "Players receive industrial automation requirements",
            "Must create SFC programs to meet specifications",
            "Solutions evaluated on syntax, logic, and requirements compliance",
            "Test cases verify program behavior"
        ],
        "skills_tested": [
            "PLC programming knowledge",
            "Sequential logic design",
            "Industrial automation concepts",
            "State machine design",
            "Safety system implementation"
        ],
        "evaluation_criteria": [
            "Syntax correctness (25%)",
            "Logic implementation (25%)",
            "Requirements compliance (25%)",
            "Test case results (25%)"
        ],
        "endpoints": {
            "create_challenge": "POST /challenge - Create new challenge",
            "get_challenge": "GET /{challenge_id} - Get challenge details",
            "submit_solution": "POST /{challenge_id}/submit - Submit solution",
            "get_evaluation": "GET /{challenge_id}/evaluation/{player_id} - Get evaluation results",
            "get_leaderboard": "GET /{challenge_id}/leaderboard - Get challenge leaderboard",
            "get_sample": "GET /{challenge_id}/sample - Get sample solution"
        }
    }


@router.post("/challenge")
def create_challenge(challenge_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Create a new SFC programming challenge"""
    try:
        challenge_id = challenge_data.get("challenge_id")
        challenge_state = sfc_service.create_new_challenge(challenge_id)
        
        # Create game record in database
        game = GameModel(
            game_type=GameType.SFC.value,
            status="pending",
            initial_state=challenge_state,
            current_state=challenge_state
        )
        
        db.add(game)
        db.commit()
        db.refresh(game)
        
        return {
            "challenge_id": game.id,
            "internal_challenge_id": challenge_state["challenge_id"],
            "title": challenge_state["title"],
            "description": challenge_state["description"],
            "requirements": challenge_state["requirements"],
            "inputs": challenge_state["inputs"],
            "outputs": challenge_state["outputs"],
            "time_limit": challenge_state["time_limit"],
            "max_submissions": challenge_state["max_submissions"],
            "status": challenge_state["status"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating challenge: {str(e)}")


@router.get("/{challenge_id}")
def get_challenge(challenge_id: int, db: Session = Depends(get_db)):
    """Get challenge details"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid challenge state")
    
    return {
        "challenge_id": challenge_id,
        "title": current_state.get("title"),
        "description": current_state.get("description"),
        "requirements": current_state.get("requirements", []),
        "inputs": current_state.get("inputs", []),
        "outputs": current_state.get("outputs", []),
        "test_cases": current_state.get("test_cases", []),
        "time_limit": current_state.get("time_limit"),
        "max_submissions": current_state.get("max_submissions"),
        "status": current_state.get("status"),
        "created_at": current_state.get("created_at")
    }


@router.post("/{challenge_id}/submit")
def submit_solution(challenge_id: int, solution_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Submit a solution to the challenge"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
        
        player_id = solution_data.get("player_id")
        if not player_id:
            raise ValueError("player_id must be provided")
        
        new_state = sfc_service.submit_solution(current_state, str(player_id), solution_data)
        
        # Update database
        challenge.current_state = json.dumps(new_state)
        db.commit()
        
        # Get the latest submission and its evaluation
        player_submissions = new_state.get("submissions", {}).get(str(player_id), [])
        latest_submission = player_submissions[-1] if player_submissions else None
        evaluation = new_state.get("evaluations", {}).get(latest_submission["id"]) if latest_submission else None
        
        return {
            "challenge_id": challenge_id,
            "player_id": player_id,
            "submission_id": latest_submission["id"] if latest_submission else None,
            "submission_number": latest_submission["submission_number"] if latest_submission else None,
            "evaluation": evaluation,
            "status": "success"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting solution: {str(e)}")


@router.get("/{challenge_id}/submissions/{player_id}")
def get_player_submissions(challenge_id: int, player_id: str, db: Session = Depends(get_db)):
    """Get all submissions for a specific player"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid challenge state")
    
    submissions = sfc_service.get_player_submissions(current_state, player_id)
    
    return {
        "challenge_id": challenge_id,
        "player_id": player_id,
        "submissions": submissions,
        "submission_count": len(submissions),
        "max_submissions": current_state.get("max_submissions", 3)
    }


@router.get("/{challenge_id}/evaluation/{player_id}")
def get_evaluation(challenge_id: int, player_id: str, submission_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Get evaluation results for a player's submission"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid challenge state")
    
    submissions = sfc_service.get_player_submissions(current_state, player_id)
    
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found for player")
    
    # If submission_id not provided, get the latest submission
    if submission_id:
        target_submission = next((s for s in submissions if s["id"] == submission_id), None)
        if not target_submission:
            raise HTTPException(status_code=404, detail="Submission not found")
    else:
        target_submission = submissions[-1]  # Latest submission
    
    evaluation = target_submission.get("evaluation")
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    return {
        "challenge_id": challenge_id,
        "player_id": player_id,
        "submission_id": target_submission["id"],
        "evaluation": evaluation
    }


@router.get("/{challenge_id}/leaderboard")
def get_leaderboard(challenge_id: int, db: Session = Depends(get_db)):
    """Get challenge leaderboard"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid challenge state")
    
    leaderboard = sfc_service.get_leaderboard(current_state)
    
    return {
        "challenge_id": challenge_id,
        "leaderboard": leaderboard,
        "total_participants": len(leaderboard)
    }


@router.get("/{challenge_id}/status")
def get_challenge_status(challenge_id: int, db: Session = Depends(get_db)):
    """Get challenge status"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid challenge state")
    
    status_info = sfc_service.get_challenge_status(current_state)
    status_info["db_challenge_id"] = challenge_id
    
    return status_info


@router.get("/{challenge_id}/sample")
def get_sample_solution(challenge_id: int, db: Session = Depends(get_db)):
    """Get a sample solution for the challenge"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid challenge state")
    
    sample_code = sfc_service.generate_sample_solution(current_state)
    
    return {
        "challenge_id": challenge_id,
        "sample_solution": sample_code,
        "note": "This is a reference solution for educational purposes"
    }


@router.post("/{challenge_id}/validate")
def validate_solution(challenge_id: int, solution_data: Dict[str, Any], db: Session = Depends(get_db)):
    """Validate a solution without submitting it"""
    challenge = _get_sfc_challenge_or_error(challenge_id, db)
    
    try:
        current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
    except Exception:
        raise HTTPException(status_code=500, detail="Invalid challenge state")
    
    try:
        code_text = solution_data.get("code_text", "")
        if not code_text:
            raise ValueError("code_text must be provided")
        
        # Create a temporary submission for evaluation
        temp_submission = {
            "id": "temp",
            "player_id": "temp",
            "code_text": code_text,
            "description": solution_data.get("description", ""),
            "code_json": solution_data.get("code_json", {}),
            "submitted_at": "temp",
            "submission_number": 0
        }
        
        evaluation = sfc_service._evaluate_solution(current_state, temp_submission)
        
        return {
            "challenge_id": challenge_id,
            "validation": evaluation,
            "status": "validated"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating solution: {str(e)}")


@router.get("/challenges")
def list_challenges(db: Session = Depends(get_db)):
    """List all SFC challenges"""
    challenges = db.query(GameModel).filter(GameModel.game_type == GameType.SFC.value).all()
    
    challenge_list = []
    for challenge in challenges:
        try:
            current_state = json.loads(challenge.current_state) if isinstance(challenge.current_state, str) else challenge.current_state
            challenge_list.append({
                "challenge_id": challenge.id,
                "title": current_state.get("title"),
                "description": current_state.get("description"),
                "status": current_state.get("status"),
                "created_at": current_state.get("created_at"),
                "participants": len(current_state.get("submissions", {}))
            })
        except Exception:
            # Skip challenges with invalid state
            continue
    
    return {
        "challenges": challenge_list,
        "total_challenges": len(challenge_list)
    }
