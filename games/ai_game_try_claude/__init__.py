raise Exception("Completely Broken, not even gonna try to fix this mess")
from typing import Tuple, Optional, Any, Union, List
from custom_typing import (
    ExtraInfo, MainReturn, SetupInput, GameInfo, Action
)
import json
from random import randint

class Game:
    def info(self) -> GameInfo:
        return {
            "name": "Pattern Echo",
            "id": "pattern_echo",
            "description": "Memorize and reproduce growing patterns. Each correct echo makes the pattern longer!"
        }
    
    def setup(
        self,
        info: SetupInput,
    ) -> Tuple[str, list[str], None, Optional[Union[Action, List[Action]]]]:
        # Initialize with numeric inputs 0-4
        initial_actions = [
            {
                "action": "does_object_exist",
                "value": "pattern_echo_scores.json"
            },
            {
                "action": "get_file_contents",
                "value": "pattern_echo_scores.json"
            }
        ]
        
        return (
            "Welcome to Pattern Echo!\n\nYou'll see a pattern of numbers (0-4).\n"
            "After it disappears, reproduce it using your inputs.\n"
            "Each success makes the pattern longer!\n\n"
            "Press any number to start...",
            "range-0-4",
            None,
            initial_actions
        )

    def main(
        self,
        input: int,
        info: Optional[ExtraInfo],
    ) -> Optional[MainReturn]:
        if not info:
            return None
            
        # Initialize game state from file or create new
        game_state = self._get_game_state(info)
        
        
        # Process the current game phase
        match game_state["phase"]:
            case "start":
                return self._start_new_game(game_state)
            case "show_pattern":
                raise Exception(game_state["phase"])
            case "hide_pattern":
                raise Exception(game_state["phase"])
            case "input":
                return self._process_input(input, game_state)
            case "game_over":
                return self._handle_game_over(input, game_state, info)
    
    def _get_game_state(self, info: ExtraInfo) -> dict:
        """Initialize or retrieve game state"""
        scores = {}
        if info.get("file_request_data"):
            # Process file operations results
            file_exists = False
            scores_data = None
            
            for data in info["file_request_data"]:
                if data["type"] == "does_object_exist":
                    file_exists = data["value"]
                elif data["type"] == "get_file_contents":
                    scores_data = data["value"]
            
            if not file_exists or not scores_data:
                scores = {}
            else:
                scores = json.loads(scores_data)
        
        # Check if we're in the middle of a game
        if "PATTERN:" in info["old_frame"]:
            return {
                "phase": "input",
                "pattern": self._extract_pattern(info["old_frame"]),
                "current_input": [],
                "scores": scores,
                "frame_count": info["frame"]
            }
        elif "Remember this pattern..." in info["old_frame"]:
            return {
                "phase": "hide_pattern",
                "pattern": self._extract_pattern(info["old_frame"]),
                "current_input": [],
                "scores": scores,
                "frame_count": info["frame"]
            }
        elif "Your turn!" in info["old_frame"]:
            pattern = self._extract_pattern(info["old_frame"])
            current_input = self._extract_current_input(info["old_frame"])
            return {
                "phase": "input",
                "pattern": pattern,
                "current_input": current_input,
                "scores": scores,
                "frame_count": info["frame"]
            }
        elif "Game Over!" in info["old_frame"]:
            return {
                "phase": "game_over",
                "pattern": self._extract_pattern(info["old_frame"]),
                "current_input": [],
                "scores": scores,
                "frame_count": info["frame"]
            }
        else:
            return {
                "phase": "start",
                "pattern": [],
                "current_input": [],
                "scores": scores,
                "frame_count": info["frame"]
            }

    def _start_new_game(self, state: dict) -> MainReturn:
        """Start a new game with an initial pattern"""
        pattern = [randint(0, 4)]
        return {
            "frame": f"Remember this pattern...\n\nPATTERN: {pattern}",
            "action": None
        }

    def _show_pattern(self, state: dict) -> MainReturn:
        """Display the current pattern briefly"""
        if state["frame_count"] > 2:  # Show pattern for 2 frames
            return {
                "frame": f"\n{'_' * 20}\n\nYour turn!\n\nPattern length: {len(state['pattern'])}\nYour input: []",
                "action": None
            }
        return {
            "frame": f"Remember this pattern...\n\nPATTERN: {state['pattern']}",
            "action": None
        }

    def _hide_pattern(self, state: dict) -> MainReturn:
        """Hide the pattern and prepare for input"""
        return {
            "frame": f"\n{'_' * 20}\n\nYour turn!\n\nPattern length: {len(state['pattern'])}\nYour input: []",
            "action": None
        }

    def _process_input(self, input: int, state: dict) -> MainReturn:
        """Process player input and check against pattern"""
        current_input = state["current_input"] + [input]
        
        # Check if input is complete
        if len(current_input) == len(state["pattern"]):
            if current_input == state["pattern"]:
                # Success! Add new number to pattern
                new_pattern = state["pattern"] + [randint(0, 4)]
                return {
                    "frame": f"Correct! Get ready for a longer pattern...\n\nPATTERN: {new_pattern}",
                    "action": None
                }
            else:
                # Game over, save score
                score = len(state["pattern"])
                username = "player"  # You could get this from info if needed
                
                if username not in state["scores"] or score > state["scores"][username]:
                    state["scores"][username] = score
                    save_action = {
                        "action": "write_to_file",
                        "value": {
                            "pattern_echo_scores.json": json.dumps(state["scores"])
                        }
                    }
                else:
                    save_action = None
                
                return {
                    "frame": (
                        f"Game Over!\n\n"
                        f"Your pattern length: {len(state['pattern'])}\n"
                        f"High score: {max(state['scores'].values()) if state['scores'] else 0}\n\n"
                        f"The pattern was: {state['pattern']}\n"
                        f"Your input was: {current_input}\n\n"
                        f"Press any number to play again!"
                    ),
                    "action": save_action
                }
        
        # Still inputting
        return {
            "frame": f"\n{'_' * 20}\n\nYour turn!\n\nPattern length: {len(state['pattern'])}\nYour input: {current_input}",
            "action": None
        }

    def _handle_game_over(self, input: int, state: dict, info: ExtraInfo) -> MainReturn:
        """Handle game over state and restart"""
        return self._start_new_game(state)

    def _extract_pattern(self, frame: str) -> List[int]:
        """Extract pattern from frame text"""
        if "PATTERN:" not in frame:
            return []
        try:
            pattern_str = frame.split("PATTERN:")[1].strip()
            return [int(x) for x in pattern_str.strip("[]").split(",")]
        except:
            return []

    def _extract_current_input(self, frame: str) -> List[int]:
        """Extract current input from frame text"""
        if "Your input:" not in frame:
            return []
        try:
            input_str = frame.split("Your input:")[1].strip()
            return [int(x) for x in input_str.strip("[]").split(",")]
        except:
            return []