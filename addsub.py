import random
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any

class ArenMathEngine:
    """
    Core Event-Driven State Engine for the AREN Math App.
    Designed for responsive cross-platform UI frameworks (Kivy/Flutter).
    Tracks separate operations, triggers 15s breaks, and processes Right-To-Left entry.
    """
    def __init__(self, save_file: str = "math_progress.json"):
        self.save_file = save_file
        self.active_screen = "SPLASH"  # SPLASH, ONBOARDING, HOME, PRACTICE, TEST, CERTIFICATE, BREAK
        self.active_operation = None   # "ADDITION" or "SUBTRACTION"
        
        # Runtime Input Buffers
        self.user_input_digits = []    # Stores typed numbers right-to-left
        self.current_question = None   # Raw question string
        self.current_correct_answer = None
        self.is_wrong_attempt = False  # Triggers the eye-catching "Teach Me" button
        self.test_question_index = 0   # Track graduation exam progress (1 to 25)
        self.test_score = 0
        
        # Placeholders for Graphic Assets (Aesthetic Path Mapping)
        self.assets = {
            "logo_image": "assets/logo_aesthetic.png",
            "dopamine_flash_anim": "assets/dopamine_spark.gif",
            "certificate_template": "assets/mastery_diploma.png"
        }
        
        self._load_progress()

    def _load_progress(self) -> None:
        """Loads persistent JSON profile tracking data with dual-operation support."""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.student_name = str(data.get("student_name", "Student"))
                self.addition_completed = int(data.get("addition_completed", 0))
                self.subtraction_completed = int(data.get("subtraction_completed", 0))
                self.addition_reviews = data.get("addition_reviews", [])
                self.subtraction_reviews = data.get("subtraction_reviews", [])
                self.graduated_addition = bool(data.get("graduated_addition", False))
                self.graduated_subtraction = bool(data.get("graduated_subtraction", False))
                self.best_exam_score = int(data.get("best_exam_score", 0))
            except Exception:
                self._set_default_state()
        else:
            self._set_default_state()

    def _set_default_state(self) -> None:
        self.student_name = "Student"
        self.addition_completed = 0
        self.subtraction_completed = 0
        self.addition_reviews = []
        self.subtraction_reviews = []
        self.graduated_addition = False
        self.graduated_subtraction = False
        self.best_exam_score = 0

    def save_progress(self) -> None:
        """Saves current state metrics atomically to protect user profiles."""
        try:
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump({
                    "student_name": self.student_name,
                    "addition_completed": self.addition_completed,
                    "subtraction_completed": self.subtraction_completed,
                    "addition_reviews": self.addition_reviews,
                    "subtraction_reviews": self.subtraction_reviews,
                    "graduated_addition": self.graduated_addition,
                    "graduated_subtraction": self.graduated_subtraction,
                    "best_exam_score": self.best_exam_score,
                    "last_accessed": datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Error caching progress database: {e}")

    # ==========================================
    # FRONTEND INTERFACE BUTTON TRIGGERS
    # ==========================================
    
    def handle_onboarding_submit(self, typed_name: str) -> None:
        """Validates entry name on first run and loads the home screen."""
        self.student_name = typed_name.strip() if typed_name.strip() else "Young Master"
        self.save_progress()
        self.change_screen("HOME")

    def select_operation(self, op_type: str) -> None:
        """Triggered when home menu panels are tapped."""
        if op_type in ["ADDITION", "SUBTRACTION"]:
            self.active_operation = op_type
            completed_count = self.addition_completed if op_type == "ADDITION" else self.subtraction_completed
            
            if completed_count >= 600:
                self.start_graduation_test()
            else:
                self.generate_next_session_problem()
        else:
            print(f"Error mapping unexpected menu route: {op_type}")

    def route_to_multiplication_division(self) -> str:
        """
        Triggered by coming soon UI placeholders.
        Prepped to route directly to md.py in the project folder root structure.
        """
        # Next phase integration file pointer reference: AREN/md.py
        return "COMING_SOON_POPUP"

    def handle_keypad_press(self, value: str) -> None:
        """Processes number pad interactions utilizing True Right-To-Left mechanics."""
        if value.isdigit():
            # RTL Rule: Insert new digits at index 0 to push older inputs leftward
            if len(self.user_input_digits) < 20:  
                self.user_input_digits.insert(0, int(value))
                
        elif value == "CLEAR":
            # Removes the most recently entered digit (at index 0)
            if self.user_input_digits:
                self.user_input_digits.pop(0)

    def get_current_input_string(self) -> str:
        """Returns the current user input as a standard printable string."""
        if not self.user_input_digits:
            return ""
        return "".join(map(str, self.user_input_digits))

    # ==========================================
    # CORE MATH GENERATOR & CALIBRATOR LOGIC
    # ==========================================
    
    def generate_next_session_problem(self) -> None:
        """Handles deficiency backlogs first or scales up dynamic problem ranges."""
        self.user_input_digits = []
        self.is_wrong_attempt = False
        
        reviews = self.addition_reviews if self.active_operation == "ADDITION" else self.subtraction_reviews
        completed = self.addition_completed if self.active_operation == "ADDITION" else self.subtraction_completed

        # Rule 6: Enforced Deficiency Queue check
        if reviews:
            target_item = reviews[0]
            self.current_question = target_item["q"]
            self.current_correct_answer = target_item["ans"]
            self.change_screen("PRACTICE")
            return

        # Rule 7: Check 50-Interval Energy Break locks
        if completed > 0 and completed % 50 == 0:
            self.change_screen("BREAK")
            return

        # Rule 8: Advanced Progression Scaling Logic
        self.current_question, self.current_correct_answer = self._calculate_bounds(completed)
        self.change_screen("PRACTICE")

    def _calculate_bounds(self, completed: int) -> Tuple[str, int]:
        """Calculates arithmetic sequences using rigorous target tiers."""
        random.seed()
        
        # Post-600 Sums: Unlimited Practice Tier (Max 8 Digits)
        if completed > 600:
            a = random.randint(10000000, 99999999)
            b = random.randint(10000000, 99999999)
            if self.active_operation == "ADDITION":
                return f"{a} + {b}", a + b
            else:
                return f"{a} - {b}", a - b

        # Standard Milestone Arrays
        if completed <= 50:
            low, high = 10, 99  # 2 Digits
        elif completed <= 150:
            low, high = 100, 999  # 3 Digits
        elif completed <= 300:
            low, high = 1000, 9999  # 4 Digits
        elif completed <= 450:
            low, high = 10000, 99999  # 5 Digits (Very Hard)
        else:
            low, high = 100000, 999999  # 6 Digits (VVVVV E Hard)

        a = random.randint(low, high)
        b = random.randint(low, high)

        if self.active_operation == "ADDITION":
            return f"{a} + {b}", a + b
        else:
            # Rule 9: Subtraction Safe Scale Threshold
            if completed < 100:
                if a < b: a, b = b, a
                return f"{a} - {b}", a - b
            else:
                # Post 100: Unlocks ultra hard random negative logic arrays
                return f"{a} - {b}", a - b

    # ==========================================
    # EVALUATION AND SCREEN TRANSITIONS
    # ==========================================
    
    def submit_answer(self) -> Dict[str, Any]:
        """Validates input entry against truth coordinates. Returns action metrics."""
        user_str = self.get_current_input_string()
        user_ans = int(user_str) if user_str else 0
        
        if self.active_screen == "TEST":
            return self._evaluate_test_submission(user_ans)
        else:
            return self._evaluate_practice_submission(user_ans)

    def _evaluate_practice_submission(self, user_ans: int) -> Dict[str, Any]:
        """Applies practice constraints, dopamine loop triggers, and retry safety windows."""
        reviews = self.addition_reviews if self.active_operation == "ADDITION" else self.subtraction_reviews
        
        if user_ans == self.current_correct_answer:
            # Clear historical deficiency tracker node if matched
            if reviews and reviews[0]["q"] == self.current_question:
                reviews.pop(0)
            else:
                if self.active_operation == "ADDITION":
                    self.addition_completed += 1
                else:
                    self.subtraction_completed += 1
            
            self.save_progress()
            
            # Rule 4 & 8: Trigger Dopamine Feedback Loop Animation
            return {"status": "CORRECT", "feedback_animation": self.assets["dopamine_flash_anim"]}
        else:
            # Rule 2 & 3: Lock Screen on error, deploy eye-catching help panel flag
            if not self.is_wrong_attempt:
                reviews.append({"q": self.current_question, "ans": self.current_correct_answer})
                self.is_wrong_attempt = True
                self.save_progress()
            
            self.user_input_digits = []  # Clear input layout matrix for retry
            return {"status": "INCORRECT", "show_teach_me_btn": True}

    def start_graduation_test(self) -> None:
        """Launches the elite senior graduation evaluation matrix screen."""
        self.active_screen = "TEST"
        self.test_question_index = 1
        self.test_score = 0
        self._generate_graduation_question()

    def _generate_graduation_question(self) -> None:
        """Rule 7: Creates massively scaled 12-18 digit worksheet profiles."""
        self.user_input_digits = []
        random.seed()
        
        # Scale dynamic lengths per problem between 12 and 18 lengths
        digits_length = random.randint(12, 18)
        low = 10**(digits_length - 1)
        high = (10**digits_length) - 1
        
        a = random.randint(low, high)
        b = random.randint(low, high)
        
        if self.active_operation == "ADDITION":
            self.current_question = f"{a} + {b}"
            self.current_correct_answer = a + b
        else:
            self.current_question = f"{a} - {b}"
            self.current_correct_answer = a - b

    def _evaluate_test_submission(self, user_ans: int) -> Dict[str, Any]:
        """Evaluates single-attempt exam metrics with strict operational tracking rules."""
        if user_ans == self.current_correct_answer:
            self.test_score += 1
            
        if self.test_question_index < 25:
            self.test_question_index += 1
            self._generate_graduation_question()
            return {"status": "NEXT_TEST_QUESTION", "current_index": self.test_question_index}
        else:
            # Final exam validation threshold processing
            self.best_exam_score = max(self.best_exam_score, self.test_score)
            if self.test_score >= 20:  # Rule 1: Passing criteria (80% accuracy)
                if self.active_operation == "ADDITION":
                    self.graduated_addition = True
                else:
                    self.graduated_subtraction = True
                self.save_progress()
                self.change_screen("CERTIFICATE")
                return {"status": "EXAM_PASSED", "score": self.test_score}
            else:
                self.change_screen("HOME")
                return {"status": "EXAM_FAILED", "score": self.test_score}

    def get_hint_matrix(self) -> Dict[str, Any]:
        """
        Rule 3 & 9: Returns the visualization matrix for carrying/borrowing.
        Fires only when the eye-catching 'Teach Me' button is clicked.
        """
        # Returns position coordinates for UI to paint carry digits above columns
        return {
            "question": self.current_question,
            "answer": self.current_correct_answer,
            "operation": self.active_operation,
            "show_hints": True
        }

    def change_screen(self, screen_name: str) -> None:
        """Centralized state navigator router."""
        self.active_screen = screen_name