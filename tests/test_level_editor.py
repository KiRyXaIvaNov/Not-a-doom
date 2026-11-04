"""
Automated headless integration test for In-Game Level Editor in Not-a-Doom.
"""
import os
import sys

# Headless video driver for CI / test execution
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.main import Game
from src.core.settings import DEFAULT_MAP_PATH, ASSETS_MAPS_DIR


def test_level_editor():
    print(">>> 1. Initializing game engine headlessly...")
    game = Game()
    assert game.mode == "game", f"Expected mode 'game', got '{game.mode}'"
    assert hasattr(game, "editor"), "Game has no editor attribute"
    assert os.path.exists(DEFAULT_MAP_PATH), f"Expected default map at {DEFAULT_MAP_PATH}"

    print(">>> 2. Switching to Level Editor...")
    game.open_editor()
    assert game.mode == "editor", f"Expected mode 'editor', got '{game.mode}'"
    assert not game.mouse_grabbed, "Mouse should be ungrabbed in editor"

    editor = game.editor
    editor.update()
    editor.draw(game.screen)
    print(">>> Editor draw and update successful.")

    print(">>> 3. Testing tile & entity painting...")
    # Paint a brick wall at (5, 5)
    editor.selected_tool = "wall_1"
    editor.paint_cell(5, 5, button=1)
    assert editor.grid[5][5] == 1, f"Expected wall 1 at (5, 5), got {editor.grid[5][5]}"

    # Paint a stone wall at (5, 6)
    editor.selected_tool = "wall_2"
    editor.paint_cell(5, 6, button=1)
    assert editor.grid[6][5] == 2, f"Expected wall 2 at (5, 6), got {editor.grid[6][5]}"

    # Place player spawn at (2, 2) -> center [2.5, 2.5]
    editor.selected_tool = "player"
    editor.paint_cell(2, 2, button=1)
    assert editor.player_spawn == [2.5, 2.5], f"Player spawn mismatch: {editor.player_spawn}"
    assert editor.grid[2][2] == 0, "Grid cell under player must be floor"

    # Place exit portal at (13, 13) -> center [13.5, 13.5]
    editor.selected_tool = "portal"
    editor.paint_cell(13, 13, button=1)
    assert editor.portal == [13.5, 13.5], f"Portal mismatch: {editor.portal}"
    assert editor.grid[13][13] == 0, "Grid cell under portal must be floor"

    # Place a demon at (6, 6)
    editor.selected_tool = "demon"
    editor.paint_cell(6, 6, button=1)
    assert any(int(e[0]) == 6 and int(e[1]) == 6 for e in editor.enemies), "Demon not found in enemies list"

    # Place a barrel at (7, 7)
    editor.selected_tool = "barrel"
    editor.paint_cell(7, 7, button=1)
    assert any(int(b[0]) == 7 and int(b[1]) == 7 for b in editor.barrels), "Barrel not found in barrels list"

    # Place a medkit at (8, 8)
    editor.selected_tool = "medkit"
    editor.paint_cell(8, 8, button=1)
    assert any(int(m[0]) == 8 and int(m[1]) == 8 for m in editor.medkits), "Medkit not found in medkits list"

    # Place a pillar at (9, 9)
    editor.selected_tool = "pillar"
    editor.paint_cell(9, 9, button=1)
    assert any(int(p[0]) == 9 and int(p[1]) == 9 for p in editor.pillars), "Pillar not found in pillars list"

    # Test RMB erasing: erase the pillar at (9, 9)
    editor.paint_cell(9, 9, button=3)
    assert not any(int(p[0]) == 9 and int(p[1]) == 9 for p in editor.pillars), "Pillar was not erased"

    print(">>> 4. Testing map save and reload...")
    test_map_path = os.path.join(ASSETS_MAPS_DIR, "test_custom_level.json")
    save_ok = editor.save_map(test_map_path)
    assert save_ok, "Failed to save test map"
    assert os.path.isfile(test_map_path), "Test map file was not created"

    # Clear interior and verify it wiped
    editor.clear_interior()
    assert len(editor.enemies) == 0, "Enemies not cleared"
    assert editor.grid[5][5] == 0, "Wall at (5, 5) not cleared"

    # Load back the saved map
    load_ok = editor.load_map(test_map_path)
    assert load_ok, "Failed to load test map"
    assert editor.grid[5][5] == 1, "Wall 1 was not restored"
    assert editor.grid[6][5] == 2, "Wall 2 was not restored"
    assert editor.player_spawn == [2.5, 2.5], "Player spawn was not restored"
    assert any(int(e[0]) == 6 and int(e[1]) == 6 for e in editor.enemies), "Demon was not restored"

    print(">>> 5. Testing zero-restart hot transition to 3D Game Playtest...")
    game.close_editor(apply=True)
    assert game.mode == "game", f"Expected mode 'game', got '{game.mode}'"
    assert game.mouse_grabbed, "Mouse should be grabbed when entering game mode"

    # Verify game world state matches editor
    assert game.player.x == 2.5 and game.player.y == 2.5, f"Player pos mismatch: {game.player.pos}"
    assert any(abs(e.x - 6.5) < 0.01 and abs(e.y - 6.5) < 0.01 for e in game.enemy_manager.enemies), "Demon missing in game"
    assert any(abs(b.x - 7.5) < 0.01 and abs(b.y - 7.5) < 0.01 for b in game.sprite_manager.sprite_list), "Barrel missing in game"
    assert any(abs(m.x - 8.5) < 0.01 and abs(m.y - 8.5) < 0.01 for m in game.sprite_manager.sprite_list), "Medkit missing in game"

    print(">>> 6. Running 20 game loop frames...")
    for frame in range(20):
        game.update()
        game.draw()

    print(">>> 7. Testing F2 re-entry to editor...")
    event_f2 = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F2, scancode=pygame.KSCAN_F2, mod=0)
    pygame.event.post(event_f2)
    game.check_events()
    assert game.mode == "editor", f"Expected editor mode after F2, got '{game.mode}'"

    # Clean up test map file
    if os.path.exists(test_map_path):
        os.remove(test_map_path)

    print(">>> ALL LEVEL EDITOR TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    test_level_editor()
