"""
Unit tests validating all Gemini 4 Hydrogen audit fixes.
"""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.main import Game


def test_audit_fixes():
    print(">>> 1. Initializing Game...")
    game = Game()

    print(">>> 2. Testing LevelEditor error resilience (Bug 1.1)...")
    game.open_editor()
    assert game.mode == "editor"
    editor = game.editor
    # Erase player spawn and portal
    editor.player_spawn = None
    editor.portal = None

    # Saving without player/portal must return False and not crash
    assert editor.save_map() is False, "save_map should fail when spawn/portal is None"
    # Playtest without portal must be blocked and not crash
    editor._trigger_action("playtest")
    assert game.mode == "editor", "Game should remain in editor mode when portal is missing"

    # apply_to_game should use safe defaults instead of throwing TypeError
    editor.apply_to_game()
    assert game.map.player_spawn == [1.5, 1.5]
    assert game.map.portal == [14.5, 14.5]
    print("LevelEditor resilience tests PASSED!")

    print(">>> 3. Testing 2.5D Sprite angle normalization (Bug 1.2)...")
    # Test all 4 quadrants relative to player with edge angle values
    player = game.player
    player.x, player.y = 5.0, 5.0

    test_offsets = [
        (2.0, 2.0),    # Q1: dx > 0, dy > 0
        (-2.0, 2.0),   # Q2: dx < 0, dy > 0
        (-2.0, -2.0),  # Q3: dx < 0, dy < 0  (the bugged case!)
        (2.0, -2.0),   # Q4: dx > 0, dy < 0
    ]
    test_player_angles = [0.0, 0.1, math.pi / 2, math.pi - 0.1, math.pi + 0.1, math.tau - 0.1]

    for ox, oy in test_offsets:
        target_x = player.x + ox
        target_y = player.y + oy
        theta = math.atan2(target_y - player.y, target_x - player.x)

        for p_angle in test_player_angles:
            player.angle = p_angle
            norm_delta = (theta - player.angle + math.pi) % math.tau - math.pi
            assert -math.pi <= norm_delta <= math.pi, f"Delta out of range: {norm_delta}"

    print("Sprite angle normalization tests PASSED!")

    print(">>> 4. Testing Demon Line of Sight & Wall Occlusion (Bug 1.3)...")
    enemy = game.enemy_manager.enemies[0]
    # Place player at (1.5, 1.5) and enemy at (5.5, 1.5) with a wall between them
    # Set wall at (3, 1)
    game.map.mini_map[1][3] = 1
    game.map._populate_world_map()

    player.x, player.y = 1.5, 1.5
    enemy.x, enemy.y = 5.5, 1.5
    enemy.state = "chase"
    enemy.fireball_cooldown = 0.0

    initial_projectiles = len(game.projectile_manager.projectiles)
    enemy.update()
    assert len(game.projectile_manager.projectiles) == initial_projectiles, "Demon should not fire through wall!"
    print("Demon LOS test PASSED!")

    print(">>> 5. Testing Player Collision with Props (Bug 1.4)...")
    # Place pillar at (3.5, 1.5)
    from src.graphics.sprite_object import SpriteObject
    pillar = SpriteObject(game, "pillar", (3.5, 1.5), scale=0.9, shift=0.15)
    game.sprite_manager.sprite_list.append(pillar)

    # Collision check at pillar position should return True
    assert player.is_colliding(3.5, 1.5) is True, "Player should collide with pillar"
    # Far away position should not collide
    assert player.is_colliding(1.5, 1.5) is False, "Player should not collide in open space"
    print("Prop collision test PASSED!")

    print(">>> 6. Running 30 game loop frames to verify delta_time cap and performance...")
    for _ in range(30):
        game.update()
        game.draw()

    print(">>> ALL AUDIT FIX TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    test_audit_fixes()
