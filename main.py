"""
Convenience launcher for Not-a-Doom from repository root.
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    from src.main import Game
    game = Game()
    game.run()
