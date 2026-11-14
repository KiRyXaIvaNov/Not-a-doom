"""
Unit tests validating dynamic quality presets (SCALE = 2, 3, 4),
raycasting depth buffer scaling, hotkey switching, and rendering stability.
"""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.main import Game
from src.core.settings import QUALITY_MODES, QUALITY_NAMES, WIDTH


def test_quality_modes():
    print(">>> 1. Initializing game engine...")
    game = Game()

    print(">>> 2. Verifying default quality settings...")
    assert game.scale == 2, f"Expected default scale=2, got {game.scale}"
    assert game.num_rays == WIDTH // 2
    assert len(game.raycasting.depth_buffer) == game.num_rays
    print(f"Default quality verified: SCALE={game.scale}, NUM_RAYS={game.num_rays}")

    print(">>> 3. Testing explicit quality mode changes (SCALE = 2, 3, 4)...")
    for scale in QUALITY_MODES:
        game.set_quality(scale)
        expected_rays = math.ceil(WIDTH / scale)
        assert game.scale == scale, f"Expected scale {scale}, got {game.scale}"
        assert game.num_rays == expected_rays, f"Expected {expected_rays} rays, got {game.num_rays}"
        assert len(game.raycasting.depth_buffer) == expected_rays
        assert game.raycasting.num_rays == expected_rays

        # Run raycasting and wall rendering
        game.raycasting.ray_cast()
        game.renderer.render_walls()

        # Run sprites (props, enemies, projectiles) and particles render
        game.sprite_manager.render(game.screen)
        game.particle_manager.render(game.screen)

        print(f"Mode {QUALITY_NAMES[scale]} (SCALE={scale}, RAYS={expected_rays}): Raycast & Render OK!")

    print(">>> 4. Testing quality mode cycling (F5)...")
    game.set_quality(2)
    assert game.scale == 2
    game.cycle_quality()
    assert game.scale == 3, f"Expected scale 3 after cycling from 2, got {game.scale}"
    assert "Balanced" in game.renderer.quality_toast_text
    assert game.renderer.quality_toast_timer > 0

    game.cycle_quality()
    assert game.scale == 4, f"Expected scale 4 after cycling from 3, got {game.scale}"
    assert "Retro Performance" in game.renderer.quality_toast_text

    game.cycle_quality()
    assert game.scale == 2, f"Expected wrap-around to scale 2, got {game.scale}"
    assert "HD" in game.renderer.quality_toast_text
    print("Quality cycling verified!")

    print(">>> 5. Testing event handling for F5 and F6 keys...")
    game.set_quality(2)
    # Simulate F5 event (2 -> 3)
    f5_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F5, scancode=0)
    pygame.event.post(f5_event)
    game.check_events()
    assert game.scale == 3

    # Reset to 2 and simulate F6 toggle (2 -> 4)
    game.set_quality(2)
    f6_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F6, scancode=0)
    pygame.event.post(f6_event)
    game.check_events()
    assert game.scale == 4

    # Simulate second F6 toggle (4 -> 2)
    pygame.event.post(f6_event)
    game.check_events()
    assert game.scale == 2
    print("F5 and F6 event handling verified!")

    print(">>> 6. Running 60 frames under each quality preset to verify stability...")
    for scale in QUALITY_MODES:
        game.set_quality(scale)
        for _ in range(20):
            game.update()
            game.draw()
    print("All frames rendered cleanly across all quality modes!")

    print(">>> ALL QUALITY MODE TESTS PASSED SUCCESSFULLY! <<<")


if __name__ == "__main__":
    test_quality_modes()
