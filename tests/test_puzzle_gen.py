
import sys
import os
import unittest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.story_inspired_puzzles.puzzle_generator import CrosswordGenerator
from src.story_inspired_puzzles.prompts import PROMPT_SERIAL_INSPIRED_STORY, PROMPT_CROSSWORD_EXTRACTION

class TestPuzzleGen(unittest.TestCase):
    def test_prompts_formatting(self):
        """Test prompt formatting with dummy data."""
        try:
            p1 = PROMPT_SERIAL_INSPIRED_STORY.format(
                genre="Fantasy", 
                keywords="Magic", 
                input="A test prompt"
            )
            self.assertIn("Genre: Fantasy", p1)
            
            p2 = PROMPT_CROSSWORD_EXTRACTION.format(
                story_text="Once upon a time..."
            )
            self.assertIn("Once upon a time...", p2)
            print("\n[PASSED] Prompt Formatting")
        except Exception as e:
            self.fail(f"Prompt formatting failed: {e}")

    def test_puzzle_generator_logic(self):
        """Test crossword generation with dummy word list."""
        
        # Dummy data (Clean Telugu words ideally, but logic works on strings)
        words_data = [
            {"answer": "RAMUDU", "clue": "Hero"},
            {"answer": "SITA", "clue": "Heroine"},
            {"answer": "LANKA", "clue": "Island"},
            {"answer": "HANUMA", "clue": "Monkey God"},
            {"answer": "VANARA", "clue": "Monkey Army"},
            {"answer": "SETU", "clue": "Bridge"}
        ]
        
        generator = CrosswordGenerator()
        # Increased attempts for guaranteed hit on small word list
        layout = generator.generate_layout(words_data, attempts=50)
        
        # Assertions
        if layout:
            self.assertIn('words', layout)
            self.assertIn('width', layout)
            self.assertIn('height', layout)
            self.assertTrue(len(layout['words']) > 0)
            print(f"[PASSED] Puzzle Generation: Placed {len(layout['words'])} words.")
        else:
            # It's possible for generation to fail if words don't link. 
            # But with these words (Ramudu, Sita, Lanka...), they share letters (A, U, N, etc).
            # RAMUDU, SITA share A. LANKA, HANUMA share A, N.
            # So it should work.
            self.fail("Failed to generate puzzle layout from connectable words.")

if __name__ == '__main__':
    unittest.main()
