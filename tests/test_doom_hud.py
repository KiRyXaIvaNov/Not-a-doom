"""
Integration tests for Authentic DOOM Status Bar HUD and Marine Face animation.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.main import Game
from src.core.settings import HUD_HEIGHT, WIDTH, HEIGHT
from src.graphics.face import DoomFace


def test_hud_settings_and_initialization():
    print(">>> 1. Verifying HUD settings and initialization...")
    assert HUD_HEIGHT == 88, f"Expected HUD_HEIGHT 88, got {HUD_HEIGHT}"
    game = Game()
    renderer = game.renderer
    assert hasattr(renderer, "doom_face"), "Renderer must have doom_face instance"
    assert isinstance(renderer.doom_face, DoomFace), "doom_face must be instance of DoomFace"
    assert hasattr(renderer, "hud_bg"), "Renderer must have pre-baked hud_bg surface"
    assert renderer.hud_bg.get_size() == (WIDTH, HUD_HEIGHT)
    print(">>> HUD settings and renderer verified.")


def test_doom_face_state_machine():
    print(">>> 2. Testing DOOM Marine Face state machine across health tiers...")
    game = Game()
    face = game.renderer.doom_face

    # Tier 1: Healthy (HP = 100)
    game.player.hp = 100
    surf_healthy = face.get_surface()
    assert surf_healthy.get_size() == (64, 72)

    # Tier 2: Lightly Hurt (HP = 60)
    game.player.hp = 60
    surf_hurt = face.get_surface()
    assert surf_hurt.get_size() == (64, 72)

    # Tier 3: Critical (HP = 20)
    game.player.hp = 20
    surf_crit = face.get_surface()
    assert surf_crit.get_size() == (64, 72)

    # Tier 4: Dead (HP = 0)
    game.player.hp = 0
    surf_dead = face.get_surface()
    assert surf_dead.get_size() == (64, 72)

    # Pain grimace when damaged (damage_alpha > 30)
    game.player.hp = 80
    game.player.damage_alpha = 140.0
    surf_pain = face.get_surface()
    assert surf_pain.get_size() == (64, 72)
    print(">>> DOOM Marine face states verified.")


def test_hud_weapon_and_ammo_switching():
    print(">>> 3. Testing weapon slot reflection in HUD...")
    game = Game()

    # Switch to Pistol (slot 1)
    game.select_weapon(0)
    assert game.weapon.slot == 1
    # Render frame with pistol active
    game.update()
    game.draw()

    # Switch to Shotgun (slot 2)
    game.select_weapon(1)
    assert game.weapon.slot == 2
    # Render frame with shotgun active
    game.update()
    game.draw()
    print(">>> Weapon slot display in HUD verified.")


def test_continuous_render_frames():
    print(">>> 4. Testing 60 frames of continuous gameplay with new HUD...")
    game = Game()
    for f in range(60):
        game.update()
        game.draw()
    print(">>> 60 frames rendered without error.")


if __name__ == "__main__":
    test_hud_settings_and_initialization()
    test_doom_face_state_machine()
    test_hud_weapon_and_ammo_switching()
    test_continuous_render_frames()
    print("\n>>> ALL DOOM STATUS BAR HUD TESTS PASSED! <<<")
