from typing import Dict, Any, List, Optional, Tuple
import json
import uuid
import re
from datetime import datetime


class SFCService:
    """Service encapsulating Sequential Function Charts (PLC programming) logic."""

    def __init__(self):
        # Sample SFC programming challenges
        self.default_challenges = [
            {
                "title": "Basic Traffic Light Controller",
                "description": "Create an SFC program for a simple traffic light that cycles through Red (10s), Green (8s), Yellow (2s).",
                "requirements": [
                    "Use steps for each light state",
                    "Use timers for transitions",
                    "Ensure safe transitions (red before green)",
                    "Include emergency stop functionality"
                ],
                "inputs": ["START_BTN", "EMERGENCY_STOP"],
                "outputs": ["RED_LIGHT", "YELLOW_LIGHT", "GREEN_LIGHT"],
                "test_cases": [
                    {"input_sequence": ["START_BTN"], "expected_output": "RED_LIGHT active for 10s, then GREEN_LIGHT for 8s"},
                    {"input_sequence": ["EMERGENCY_STOP"], "expected_output": "All lights off, system stops"}
                ]
            },
            {
                "title": "Conveyor Belt System",
                "description": "Program a conveyor belt system with loading, transport, and unloading stations.",
                "requirements": [
                    "Start sequence when part detected at loading station",
                    "Move belt until part reaches transport position",
                    "Wait for quality check signal",
                    "Continue to unloading if quality OK, reject if not"
                ],
                "inputs": ["PART_DETECTED", "QUALITY_OK", "QUALITY_FAIL", "UNLOAD_COMPLETE"],
                "outputs": ["BELT_MOTOR", "REJECT_ACTUATOR", "UNLOAD_SIGNAL"],
                "test_cases": [
                    {"input_sequence": ["PART_DETECTED", "QUALITY_OK", "UNLOAD_COMPLETE"], "expected_output": "Normal processing cycle"},
                    {"input_sequence": ["PART_DETECTED", "QUALITY_FAIL"], "expected_output": "Part rejected via REJECT_ACTUATOR"}
                ]
            },
            {
                "title": "Automated Parking Gate",
                "description": "Control a parking gate system with entry/exit sensors and payment validation.",
                "requirements": [
                    "Open gate when payment confirmed and vehicle detected",
                    "Keep gate open while vehicle passes",
                    "Close gate after vehicle clears sensor",
                    "Handle timeout scenarios"
                ],
                "inputs": ["VEHICLE_ENTRY", "PAYMENT_OK", "VEHICLE_EXIT", "GATE_OPEN_SENSOR", "GATE_CLOSED_SENSOR"],
                "outputs": ["GATE_MOTOR_OPEN", "GATE_MOTOR_CLOSE", "PAYMENT_DISPLAY"],
                "test_cases": [
                    {"input_sequence": ["VEHICLE_ENTRY", "PAYMENT_OK", "VEHICLE_EXIT"], "expected_output": "Gate opens and closes properly"},
                    {"input_sequence": ["VEHICLE_ENTRY"], "expected_output": "Gate remains closed without payment"}
                ]
            }
        ]

    def create_new_challenge(self, challenge_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new SFC programming challenge"""
        if challenge_id is None:
            challenge = self.default_challenges[0]  # Default to first challenge
        else:
            # In a real implementation, would lookup challenge by ID
            challenge = self.default_challenges[0]
        
        return {
            "challenge_id": str(uuid.uuid4()),
            "title": challenge["title"],
            "description": challenge["description"],
            "requirements": challenge["requirements"],
            "inputs": challenge["inputs"],
            "outputs": challenge["outputs"],
            "test_cases": challenge["test_cases"],
            "status": "active",
            "submissions": {},  # player_id -> submission_data
            "evaluations": {},  # player_id -> evaluation_result
            "created_at": datetime.now().isoformat(),
            "time_limit": 3600,  # 1 hour in seconds
            "max_submissions": 3
        }

    def submit_solution(self, challenge_state: Dict[str, Any], player_id: str, solution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a solution for evaluation"""
        new_state = json.loads(json.dumps(challenge_state))
        
        if new_state["status"] != "active":
            raise ValueError("Challenge is not active")
        
        # Check submission limit
        current_submissions = new_state["submissions"].get(player_id, [])
        if len(current_submissions) >= new_state["max_submissions"]:
            raise ValueError("Maximum submissions exceeded")
        
        # Validate solution structure
        required_fields = ["code_text", "description"]
        for field in required_fields:
            if field not in solution_data:
                raise ValueError(f"Solution missing required field: {field}")
        
        submission = {
            "id": str(uuid.uuid4()),
            "player_id": player_id,
            "code_text": solution_data["code_text"],
            "description": solution_data.get("description", ""),
            "code_json": solution_data.get("code_json", {}),
            "submitted_at": datetime.now().isoformat(),
            "submission_number": len(current_submissions) + 1
        }
        
        # Store submission
        if player_id not in new_state["submissions"]:
            new_state["submissions"][player_id] = []
        new_state["submissions"][player_id].append(submission)
        
        # Evaluate the submission
        evaluation = self._evaluate_solution(new_state, submission)
        new_state["evaluations"][submission["id"]] = evaluation
        
        return new_state

    def _evaluate_solution(self, challenge_state: Dict[str, Any], submission: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a submitted solution"""
        code_text = submission["code_text"]
        
        evaluation = {
            "submission_id": submission["id"],
            "player_id": submission["player_id"],
            "evaluated_at": datetime.now().isoformat(),
            "syntax_score": 0,
            "logic_score": 0,
            "requirements_score": 0,
            "total_score": 0,
            "max_score": 100,
            "feedback": [],
            "test_results": []
        }
        
        # Syntax evaluation (basic checks)
        syntax_score = self._evaluate_syntax(code_text, challenge_state)
        evaluation["syntax_score"] = syntax_score
        
        # Logic evaluation
        logic_score = self._evaluate_logic(code_text, challenge_state)
        evaluation["logic_score"] = logic_score
        
        # Requirements evaluation
        requirements_score = self._evaluate_requirements(code_text, challenge_state)
        evaluation["requirements_score"] = requirements_score
        
        # Test case evaluation
        test_results = self._run_test_cases(code_text, challenge_state)
        evaluation["test_results"] = test_results
        
        # Calculate total score
        test_score = sum(result["score"] for result in test_results) / len(test_results) if test_results else 0
        evaluation["total_score"] = (syntax_score + logic_score + requirements_score + test_score) / 4
        
        return evaluation

    def _evaluate_syntax(self, code_text: str, challenge_state: Dict[str, Any]) -> float:
        """Evaluate syntax and structure of SFC code"""
        score = 0
        feedback = []
        
        # Check for basic SFC elements
        if "STEP" in code_text.upper():
            score += 20
        else:
            feedback.append("Missing STEP declarations")
        
        if "TRANSITION" in code_text.upper():
            score += 20
        else:
            feedback.append("Missing TRANSITION declarations")
        
        # Check for required inputs/outputs
        required_inputs = challenge_state.get("inputs", [])
        required_outputs = challenge_state.get("outputs", [])
        
        inputs_found = sum(1 for inp in required_inputs if inp in code_text.upper())
        outputs_found = sum(1 for out in required_outputs if out in code_text.upper())
        
        if required_inputs:
            score += (inputs_found / len(required_inputs)) * 30
        if required_outputs:
            score += (outputs_found / len(required_outputs)) * 30
        
        return min(score, 100)

    def _evaluate_logic(self, code_text: str, challenge_state: Dict[str, Any]) -> float:
        """Evaluate logical correctness of the SFC program"""
        score = 0
        
        # Check for proper step sequencing
        step_pattern = r'STEP\s+(\w+)'
        steps = re.findall(step_pattern, code_text, re.IGNORECASE)
        
        if len(steps) >= 2:
            score += 25  # At least 2 steps
        
        # Check for timer usage (common in SFC)
        if re.search(r'T\d+|TIMER|TON|TOF', code_text, re.IGNORECASE):
            score += 25
        
        # Check for proper transitions
        transition_pattern = r'TRANSITION.*?END_TRANSITION'
        transitions = re.findall(transition_pattern, code_text, re.IGNORECASE | re.DOTALL)
        
        if len(transitions) >= len(steps) - 1:  # Should have at least n-1 transitions for n steps
            score += 25
        
        # Check for safety considerations (emergency stops, etc.)
        if re.search(r'EMERGENCY|STOP|SAFETY', code_text, re.IGNORECASE):
            score += 25
        
        return min(score, 100)

    def _evaluate_requirements(self, code_text: str, challenge_state: Dict[str, Any]) -> float:
        """Evaluate how well the solution meets the requirements"""
        requirements = challenge_state.get("requirements", [])
        if not requirements:
            return 100
        
        score = 0
        requirement_weight = 100 / len(requirements)
        
        for requirement in requirements:
            # Simple keyword matching for requirements
            if "timer" in requirement.lower() and re.search(r'T\d+|TIMER|TON', code_text, re.IGNORECASE):
                score += requirement_weight
            elif "step" in requirement.lower() and "STEP" in code_text.upper():
                score += requirement_weight
            elif "emergency" in requirement.lower() and "EMERGENCY" in code_text.upper():
                score += requirement_weight
            elif "transition" in requirement.lower() and "TRANSITION" in code_text.upper():
                score += requirement_weight
            else:
                # Partial credit for partially addressing requirement
                score += requirement_weight * 0.5
        
        return min(score, 100)

    def _run_test_cases(self, code_text: str, challenge_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run test cases against the submitted code"""
        test_cases = challenge_state.get("test_cases", [])
        results = []
        
        for i, test_case in enumerate(test_cases):
            result = {
                "test_case_id": i + 1,
                "description": test_case.get("description", f"Test case {i + 1}"),
                "input_sequence": test_case.get("input_sequence", []),
                "expected_output": test_case.get("expected_output", ""),
                "actual_output": "Simulated output",  # In real implementation, would run actual simulation
                "passed": True,  # Simplified - would be based on actual execution
                "score": 80,  # Simplified scoring
                "feedback": "Test passed with minor timing differences"
            }
            
            # Simplified test evaluation
            # In a real implementation, this would involve running the SFC code in a simulator
            input_sequence = test_case.get("input_sequence", [])
            
            # Check if the code references the test inputs
            inputs_referenced = sum(1 for inp in input_sequence if inp in code_text.upper())
            
            if inputs_referenced == len(input_sequence):
                result["score"] = 90
                result["passed"] = True
            elif inputs_referenced > 0:
                result["score"] = 60
                result["passed"] = False
                result["feedback"] = "Some inputs not properly handled"
            else:
                result["score"] = 20
                result["passed"] = False
                result["feedback"] = "Test inputs not found in code"
            
            results.append(result)
        
        return results

    def get_challenge_status(self, challenge_state: Dict[str, Any]) -> Dict[str, Any]:
        """Get current challenge status"""
        return {
            "challenge_id": challenge_state.get("challenge_id"),
            "title": challenge_state.get("title"),
            "status": challenge_state.get("status"),
            "total_submissions": sum(len(subs) for subs in challenge_state.get("submissions", {}).values()),
            "players_participated": len(challenge_state.get("submissions", {})),
            "time_limit": challenge_state.get("time_limit"),
            "created_at": challenge_state.get("created_at")
        }

    def get_leaderboard(self, challenge_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get leaderboard for the challenge"""
        leaderboard = []
        
        for player_id, submissions in challenge_state.get("submissions", {}).items():
            if not submissions:
                continue
            
            # Get best score for this player
            best_score = 0
            best_submission = None
            
            for submission in submissions:
                evaluation = challenge_state.get("evaluations", {}).get(submission["id"])
                if evaluation and evaluation.get("total_score", 0) > best_score:
                    best_score = evaluation.get("total_score", 0)
                    best_submission = submission
            
            if best_submission:
                leaderboard.append({
                    "player_id": player_id,
                    "best_score": best_score,
                    "submission_count": len(submissions),
                    "last_submission": best_submission["submitted_at"]
                })
        
        # Sort by score descending
        leaderboard.sort(key=lambda x: x["best_score"], reverse=True)
        
        # Add ranks
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        return leaderboard

    def get_player_submissions(self, challenge_state: Dict[str, Any], player_id: str) -> List[Dict[str, Any]]:
        """Get all submissions for a specific player"""
        submissions = challenge_state.get("submissions", {}).get(player_id, [])
        
        # Add evaluation data to each submission
        enriched_submissions = []
        for submission in submissions:
            enriched = submission.copy()
            evaluation = challenge_state.get("evaluations", {}).get(submission["id"])
            if evaluation:
                enriched["evaluation"] = evaluation
            enriched_submissions.append(enriched)
        
        return enriched_submissions

    def generate_sample_solution(self, challenge_state: Dict[str, Any]) -> str:
        """Generate a sample solution for reference (for testing/demo purposes)"""
        title = challenge_state.get("title", "")
        inputs = challenge_state.get("inputs", [])
        outputs = challenge_state.get("outputs", [])
        
        if "traffic" in title.lower():
            return self._generate_traffic_light_solution(inputs, outputs)
        elif "conveyor" in title.lower():
            return self._generate_conveyor_solution(inputs, outputs)
        elif "parking" in title.lower():
            return self._generate_parking_gate_solution(inputs, outputs)
        else:
            return self._generate_generic_solution(inputs, outputs)

    def _generate_traffic_light_solution(self, inputs: List[str], outputs: List[str]) -> str:
        return """
PROGRAM TrafficLight
VAR
    START_BTN: BOOL;
    EMERGENCY_STOP: BOOL;
    RED_LIGHT: BOOL;
    YELLOW_LIGHT: BOOL;
    GREEN_LIGHT: BOOL;
    T1: TON;  // Red light timer
    T2: TON;  // Green light timer
    T3: TON;  // Yellow light timer
END_VAR

SFC Traffic_Control
    STEP Init:
        RED_LIGHT := FALSE;
        YELLOW_LIGHT := FALSE;
        GREEN_LIGHT := FALSE;
    END_STEP
    
    TRANSITION Start_Trans FROM Init TO Red_State:
        START_BTN AND NOT EMERGENCY_STOP
    END_TRANSITION
    
    STEP Red_State:
        RED_LIGHT := TRUE;
        T1(IN := TRUE, PT := T#10s);
    END_STEP
    
    TRANSITION Red_To_Green FROM Red_State TO Green_State:
        T1.Q AND NOT EMERGENCY_STOP
    END_TRANSITION
    
    STEP Green_State:
        RED_LIGHT := FALSE;
        GREEN_LIGHT := TRUE;
        T2(IN := TRUE, PT := T#8s);
    END_STEP
    
    TRANSITION Green_To_Yellow FROM Green_State TO Yellow_State:
        T2.Q AND NOT EMERGENCY_STOP
    END_TRANSITION
    
    STEP Yellow_State:
        GREEN_LIGHT := FALSE;
        YELLOW_LIGHT := TRUE;
        T3(IN := TRUE, PT := T#2s);
    END_STEP
    
    TRANSITION Yellow_To_Red FROM Yellow_State TO Red_State:
        T3.Q AND NOT EMERGENCY_STOP
    END_TRANSITION
    
    TRANSITION Emergency_Stop FROM * TO Init:
        EMERGENCY_STOP
    END_TRANSITION
END_SFC

END_PROGRAM
"""

    def _generate_conveyor_solution(self, inputs: List[str], outputs: List[str]) -> str:
        return """
PROGRAM ConveyorSystem
VAR
    PART_DETECTED: BOOL;
    QUALITY_OK: BOOL;
    QUALITY_FAIL: BOOL;
    UNLOAD_COMPLETE: BOOL;
    BELT_MOTOR: BOOL;
    REJECT_ACTUATOR: BOOL;
    UNLOAD_SIGNAL: BOOL;
END_VAR

SFC Conveyor_Control
    STEP Wait_For_Part:
        BELT_MOTOR := FALSE;
        REJECT_ACTUATOR := FALSE;
        UNLOAD_SIGNAL := FALSE;
    END_STEP
    
    TRANSITION Part_Detected FROM Wait_For_Part TO Transport:
        PART_DETECTED
    END_TRANSITION
    
    STEP Transport:
        BELT_MOTOR := TRUE;
    END_STEP
    
    TRANSITION Quality_Check FROM Transport TO Quality_Decision:
        QUALITY_OK OR QUALITY_FAIL
    END_TRANSITION
    
    STEP Quality_Decision:
        BELT_MOTOR := FALSE;
    END_STEP
    
    TRANSITION Good_Part FROM Quality_Decision TO Unload:
        QUALITY_OK
    END_TRANSITION
    
    TRANSITION Bad_Part FROM Quality_Decision TO Reject:
        QUALITY_FAIL
    END_TRANSITION
    
    STEP Unload:
        UNLOAD_SIGNAL := TRUE;
    END_STEP
    
    TRANSITION Unload_Done FROM Unload TO Wait_For_Part:
        UNLOAD_COMPLETE
    END_TRANSITION
    
    STEP Reject:
        REJECT_ACTUATOR := TRUE;
    END_STEP
    
    TRANSITION Reject_Done FROM Reject TO Wait_For_Part:
        TRUE  // Automatic return after reject
    END_TRANSITION
END_SFC

END_PROGRAM
"""

    def _generate_parking_gate_solution(self, inputs: List[str], outputs: List[str]) -> str:
        return """
PROGRAM ParkingGate
VAR
    VEHICLE_ENTRY: BOOL;
    PAYMENT_OK: BOOL;
    VEHICLE_EXIT: BOOL;
    GATE_OPEN_SENSOR: BOOL;
    GATE_CLOSED_SENSOR: BOOL;
    GATE_MOTOR_OPEN: BOOL;
    GATE_MOTOR_CLOSE: BOOL;
    PAYMENT_DISPLAY: BOOL;
    T_TIMEOUT: TON;
END_VAR

SFC Gate_Control
    STEP Idle:
        GATE_MOTOR_OPEN := FALSE;
        GATE_MOTOR_CLOSE := FALSE;
        PAYMENT_DISPLAY := FALSE;
    END_STEP
    
    TRANSITION Vehicle_Approach FROM Idle TO Wait_Payment:
        VEHICLE_ENTRY
    END_TRANSITION
    
    STEP Wait_Payment:
        PAYMENT_DISPLAY := TRUE;
        T_TIMEOUT(IN := TRUE, PT := T#30s);
    END_STEP
    
    TRANSITION Payment_Received FROM Wait_Payment TO Open_Gate:
        PAYMENT_OK
    END_TRANSITION
    
    TRANSITION Payment_Timeout FROM Wait_Payment TO Idle:
        T_TIMEOUT.Q
    END_TRANSITION
    
    STEP Open_Gate:
        PAYMENT_DISPLAY := FALSE;
        GATE_MOTOR_OPEN := TRUE;
    END_STEP
    
    TRANSITION Gate_Opened FROM Open_Gate TO Wait_Vehicle_Pass:
        GATE_OPEN_SENSOR
    END_TRANSITION
    
    STEP Wait_Vehicle_Pass:
        GATE_MOTOR_OPEN := FALSE;
    END_STEP
    
    TRANSITION Vehicle_Passed FROM Wait_Vehicle_Pass TO Close_Gate:
        VEHICLE_EXIT
    END_TRANSITION
    
    STEP Close_Gate:
        GATE_MOTOR_CLOSE := TRUE;
    END_STEP
    
    TRANSITION Gate_Closed FROM Close_Gate TO Idle:
        GATE_CLOSED_SENSOR
    END_TRANSITION
END_SFC

END_PROGRAM
"""

    def _generate_generic_solution(self, inputs: List[str], outputs: List[str]) -> str:
        return f"""
PROGRAM GenericSFC
VAR
    {'; '.join([f'{inp}: BOOL' for inp in inputs])};
    {'; '.join([f'{out}: BOOL' for out in outputs])};
END_VAR

SFC Generic_Control
    STEP Initial:
        {'; '.join([f'{out} := FALSE' for out in outputs])};
    END_STEP
    
    TRANSITION Start FROM Initial TO Active:
        {inputs[0] if inputs else 'TRUE'}
    END_TRANSITION
    
    STEP Active:
        {outputs[0] if outputs else '// Add logic here'} := TRUE;
    END_STEP
    
    TRANSITION End FROM Active TO Initial:
        TRUE
    END_TRANSITION
END_SFC

END_PROGRAM
"""

    def serialize_challenge_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize challenge state for storage"""
        return dict(state)

    def deserialize_challenge_state(self, serialized: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize challenge state from storage"""
        return dict(serialized)
