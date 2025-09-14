from typing import Dict, Any, List, Optional, Tuple
import json
import uuid
import random
from datetime import datetime


class GIService:
    """Service encapsulating General Intelligence tournament logic."""

    def __init__(self):
        # Default seed prompts for tournaments
        self.default_seed_prompts = [
            "Explain the concept of consciousness and whether AI can truly be conscious.",
            "Design a solution to climate change that is both practical and politically feasible.",
            "Analyze the ethical implications of genetic engineering in humans.",
            "Describe how you would organize society if you could start from scratch.",
            "Explain quantum computing to a 5-year-old and then to a PhD physicist.",
            "Propose a method to achieve world peace that accounts for human nature.",
            "Analyze the future of work in an AI-dominated world.",
            "Design an education system for the 22nd century.",
            "Explain the relationship between free will and determinism.",
            "Propose solutions to the problem of AI alignment."
        ]

    def create_new_tournament(self, num_players: int = 2, num_prompts: int = 3) -> Dict[str, Any]:
        """Create a new General Intelligence tournament"""
        if num_players < 2:
            raise ValueError("Tournament must have at least 2 players")
        
        if num_prompts < 1:
            raise ValueError("Tournament must have at least 1 prompt")

        # Select random seed prompts
        selected_prompts = random.sample(self.default_seed_prompts, min(num_prompts, len(self.default_seed_prompts)))
        
        return {
            "tournament_id": str(uuid.uuid4()),
            "status": "setup",  # setup -> question_generation -> answering -> scoring -> completed
            "num_players": num_players,
            "num_prompts": num_prompts,
            "seed_prompts": selected_prompts,
            "generated_questions": {},  # player_id -> [questions]
            "answers": {},  # question_id -> {player_id -> answer}
            "scores": {},  # answer_id -> {scorer_player_id -> score}
            "player_assignments": {},  # player_id -> assigned_seed_prompt_index
            "final_scores": {},  # player_id -> total_score
            "current_phase": "setup",
            "created_at": datetime.now().isoformat(),
            "phases_completed": []
        }

    def assign_prompts_to_players(self, tournament_state: Dict[str, Any], player_ids: List[str]) -> Dict[str, Any]:
        """Assign seed prompts to players for question generation"""
        new_state = json.loads(json.dumps(tournament_state))
        
        if len(player_ids) != new_state["num_players"]:
            raise ValueError("Player count mismatch")
        
        # Assign prompts cyclically to players
        for i, player_id in enumerate(player_ids):
            prompt_index = i % new_state["num_prompts"]
            new_state["player_assignments"][player_id] = prompt_index
        
        new_state["status"] = "question_generation"
        new_state["current_phase"] = "question_generation"
        
        return new_state

    def submit_questions(self, tournament_state: Dict[str, Any], player_id: str, questions: List[str]) -> Dict[str, Any]:
        """Submit generated questions for a player"""
        new_state = json.loads(json.dumps(tournament_state))
        
        if new_state["current_phase"] != "question_generation":
            raise ValueError("Tournament is not in question generation phase")
        
        if player_id not in new_state["player_assignments"]:
            raise ValueError("Player not assigned to this tournament")
        
        if len(questions) < 2:
            raise ValueError("Each player must submit at least 2 questions")
        
        # Store questions with unique IDs
        question_objects = []
        for question_text in questions:
            question_id = str(uuid.uuid4())
            question_objects.append({
                "id": question_id,
                "text": question_text,
                "author_player_id": player_id,
                "seed_prompt_index": new_state["player_assignments"][player_id]
            })
            # Initialize answer storage for this question
            new_state["answers"][question_id] = {}
        
        new_state["generated_questions"][player_id] = question_objects
        
        # Check if all players have submitted questions
        if len(new_state["generated_questions"]) == new_state["num_players"]:
            new_state["current_phase"] = "answering"
            new_state["phases_completed"].append("question_generation")
        
        return new_state

    def get_questions_for_answering(self, tournament_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all questions that need to be answered"""
        all_questions = []
        for player_questions in tournament_state["generated_questions"].values():
            all_questions.extend(player_questions)
        return all_questions

    def submit_answer(self, tournament_state: Dict[str, Any], player_id: str, question_id: str, answer: str) -> Dict[str, Any]:
        """Submit an answer to a question"""
        new_state = json.loads(json.dumps(tournament_state))
        
        if new_state["current_phase"] != "answering":
            raise ValueError("Tournament is not in answering phase")
        
        if question_id not in new_state["answers"]:
            raise ValueError("Invalid question ID")
        
        # Check if player is trying to answer their own question
        question_author = None
        for player_questions in new_state["generated_questions"].values():
            for q in player_questions:
                if q["id"] == question_id:
                    question_author = q["author_player_id"]
                    break
        
        if question_author == player_id:
            raise ValueError("Players cannot answer their own questions")
        
        answer_id = str(uuid.uuid4())
        new_state["answers"][question_id][player_id] = {
            "id": answer_id,
            "text": answer,
            "player_id": player_id,
            "submitted_at": datetime.now().isoformat()
        }
        
        # Initialize score storage for this answer
        new_state["scores"][answer_id] = {}
        
        # Check if all players have answered all questions they can answer
        total_expected_answers = 0
        total_submitted_answers = 0
        
        for q_id in new_state["answers"]:
            # Find the author of this question
            q_author = None
            for player_questions in new_state["generated_questions"].values():
                for q in player_questions:
                    if q["id"] == q_id:
                        q_author = q["author_player_id"]
                        break
            
            # Count expected answers (all players except the author)
            expected_for_this_q = new_state["num_players"] - 1
            total_expected_answers += expected_for_this_q
            
            # Count submitted answers
            total_submitted_answers += len(new_state["answers"][q_id])
        
        if total_submitted_answers >= total_expected_answers:
            new_state["current_phase"] = "scoring"
            new_state["phases_completed"].append("answering")
        
        return new_state

    def submit_score(self, tournament_state: Dict[str, Any], scorer_player_id: str, answer_id: str, score: int) -> Dict[str, Any]:
        """Submit a score for an answer"""
        new_state = json.loads(json.dumps(tournament_state))
        
        if new_state["current_phase"] != "scoring":
            raise ValueError("Tournament is not in scoring phase")
        
        if score < 0 or score > 10:
            raise ValueError("Score must be between 0 and 10")
        
        if answer_id not in new_state["scores"]:
            raise ValueError("Invalid answer ID")
        
        # Find the answer and check if scorer is trying to score their own answer
        answer_author = None
        for q_id, answers in new_state["answers"].items():
            for p_id, answer_data in answers.items():
                if answer_data["id"] == answer_id:
                    answer_author = p_id
                    break
        
        if answer_author == scorer_player_id:
            raise ValueError("Players cannot score their own answers")
        
        new_state["scores"][answer_id][scorer_player_id] = score
        
        # Check if all scoring is complete
        total_expected_scores = 0
        total_submitted_scores = 0
        
        for answer_id, scores in new_state["scores"].items():
            # Find the author of this answer
            answer_author = None
            for q_id, answers in new_state["answers"].items():
                for p_id, answer_data in answers.items():
                    if answer_data["id"] == answer_id:
                        answer_author = p_id
                        break
            
            # Expected scores = all players except the answer author
            expected_for_this_answer = new_state["num_players"] - 1
            total_expected_scores += expected_for_this_answer
            total_submitted_scores += len(scores)
        
        if total_submitted_scores >= total_expected_scores:
            new_state = self._calculate_final_scores(new_state)
            new_state["current_phase"] = "completed"
            new_state["status"] = "completed"
            new_state["phases_completed"].append("scoring")
        
        return new_state

    def _calculate_final_scores(self, tournament_state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final scores for all players"""
        player_scores = {}
        
        # Initialize scores
        for player_questions in tournament_state["generated_questions"].values():
            for q in player_questions:
                player_scores[q["author_player_id"]] = 0
        
        # Sum up scores for each player's answers
        for answer_id, scores in tournament_state["scores"].items():
            # Find the answer author
            answer_author = None
            for q_id, answers in tournament_state["answers"].items():
                for p_id, answer_data in answers.items():
                    if answer_data["id"] == answer_id:
                        answer_author = p_id
                        break
            
            if answer_author:
                # Calculate average score for this answer
                if scores:
                    avg_score = sum(scores.values()) / len(scores)
                    player_scores[answer_author] += avg_score
        
        tournament_state["final_scores"] = player_scores
        return tournament_state

    def get_tournament_status(self, tournament_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get current tournament status and progress"""
        status_info = {
            "tournament_id": tournament_state.get("tournament_id"),
            "current_phase": tournament_state.get("current_phase"),
            "status": tournament_state.get("status"),
            "phases_completed": tournament_state.get("phases_completed", []),
            "num_players": tournament_state.get("num_players"),
            "num_prompts": tournament_state.get("num_prompts")
        }
        
        if tournament_state.get("current_phase") == "question_generation":
            status_info["questions_submitted"] = len(tournament_state.get("generated_questions", {}))
            status_info["questions_remaining"] = tournament_state["num_players"] - len(tournament_state.get("generated_questions", {}))
        
        elif tournament_state.get("current_phase") == "answering":
            total_answers = sum(len(answers) for answers in tournament_state.get("answers", {}).values())
            status_info["answers_submitted"] = total_answers
        
        elif tournament_state.get("current_phase") == "scoring":
            total_scores = sum(len(scores) for scores in tournament_state.get("scores", {}).values())
            status_info["scores_submitted"] = total_scores
        
        elif tournament_state.get("current_phase") == "completed":
            status_info["final_scores"] = tournament_state.get("final_scores", {})
            if status_info["final_scores"]:
                # Determine winner
                winner_id = max(status_info["final_scores"].items(), key=lambda x: x[1])[0]
                status_info["winner"] = winner_id
        
        return status_info

    def get_player_tasks(self, tournament_state: Dict[str, Any], player_id: str) -> Dict[str, Any]:
        """Get current tasks for a specific player"""
        current_phase = tournament_state.get("current_phase")
        tasks = {"phase": current_phase, "tasks": []}
        
        if current_phase == "question_generation":
            if player_id not in tournament_state.get("generated_questions", {}):
                assigned_prompt_index = tournament_state.get("player_assignments", {}).get(player_id)
                if assigned_prompt_index is not None:
                    seed_prompt = tournament_state["seed_prompts"][assigned_prompt_index]
                    tasks["tasks"].append({
                        "type": "generate_questions",
                        "description": f"Generate 2-3 questions based on: {seed_prompt}",
                        "seed_prompt": seed_prompt
                    })
        
        elif current_phase == "answering":
            questions_to_answer = []
            for q_id, answers in tournament_state.get("answers", {}).items():
                if player_id not in answers:
                    # Find the question text and check if it's not authored by this player
                    for player_questions in tournament_state.get("generated_questions", {}).values():
                        for q in player_questions:
                            if q["id"] == q_id and q["author_player_id"] != player_id:
                                questions_to_answer.append({
                                    "question_id": q_id,
                                    "text": q["text"],
                                    "author": q["author_player_id"]
                                })
            
            tasks["tasks"] = [{
                "type": "answer_questions",
                "questions": questions_to_answer
            }]
        
        elif current_phase == "scoring":
            answers_to_score = []
            for answer_id, scores in tournament_state.get("scores", {}).items():
                if player_id not in scores:
                    # Find the answer and check if it's not authored by this player
                    for q_id, answers in tournament_state.get("answers", {}).items():
                        for p_id, answer_data in answers.items():
                            if answer_data["id"] == answer_id and p_id != player_id:
                                # Get the question text
                                question_text = ""
                                for player_questions in tournament_state.get("generated_questions", {}).values():
                                    for q in player_questions:
                                        if q["id"] == q_id:
                                            question_text = q["text"]
                                            break
                                
                                answers_to_score.append({
                                    "answer_id": answer_id,
                                    "question": question_text,
                                    "answer": answer_data["text"],
                                    "author": p_id
                                })
            
            tasks["tasks"] = [{
                "type": "score_answers",
                "answers": answers_to_score
            }]
        
        return tasks

    def serialize_tournament_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize tournament state for storage"""
        return dict(state)

    def deserialize_tournament_state(self, serialized: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize tournament state from storage"""
        return dict(serialized)
