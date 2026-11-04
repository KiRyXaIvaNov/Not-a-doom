"""
Integration tests for Pistol weapon: attributes, switching, long-range hitscan, and audio.
"""
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.main import Game
from src.core.settings import (
    PISTOL_MAX_RANGE,
    PISTOL_MIN_DAMAGE_RATIO,
    PISTOL_PELLETS,
    PISTOL_SPREAD,
    PISTOL_MIN_DAMAGE,
    PISTOL_MAX_DAMAGE,
    SHOTGUN_MAX_RANGE,
)
from src.combat.weapon import Pistol, Shotgun
from src.entities.enemy import Enemy


def test_pistol_settings_and_attributes():
    print(">>> 1. Verifying Pistol settings & weapon attributes...")
    assert PISTOL_MAX_RANGE == 30.0
    assert PISTOL_MIN_DAMAGE_RATIO == 1.0
    assert PISTOL_PELLETS == 1
    assert PISTOL_SPREAD == 0.008
    assert PISTOL_MIN_DAMAGE == 22
    assert PISTOL_MAX_DAMAGE == 30

    game = Game()
    pistol = game.pistol
    assert isinstance(pistol, Pistol)
    assert pistol.name == "PISTOL"
    assert pistol.slot == 1
    assert pistol.max_range == 30.0
    assert pistol.min_damage_ratio == 1.0
    assert pistol.num_pellets == 1
    assert pistol.spread == 0.008
    assert pistol.min_damage == 22
    assert pistol.max_damage == 30
    assert pistol.num_frames == 4
    print(">>> Pistol settings verified.")


def test_weapon_inventory_and_switching():
    print(">>> 2. Testing weapon inventory and switching...")
    game = Game()
    assert hasattr(game, "weapons")
    assert len(game.weapons) == 2
    assert isinstance(game.weapons[0], Pistol)
    assert isinstance(game.weapons[1], Shotgun)

    # Default starts on Shotgun (slot 2, idx 1)
    assert game.current_weapon_idx == 1
    assert game.weapon.name == "SHOTGUN"

    # Switch to Pistol (slot 1, idx 0)
    game.select_weapon(0)
    assert game.current_weapon_idx == 0
    assert game.weapon.name == "PISTOL"

    # Switch back to Shotgun
    game.select_weapon(1)
    assert game.current_weapon_idx == 1
    assert game.weapon.name == "SHOTGUN"
    print(">>> Weapon inventory switching verified.")


def test_pistol_long_range_hitscan():
    print(">>> 3. Testing Pistol long-range hitscan capability (> 3.0 blocks)...")
    game = Game()
    player = game.player
    player.x, player.y = 2.0, 2.0
    player.angle = 0.0

    # Switch to Pistol
    game.select_weapon(0)
    assert game.weapon.name == "PISTOL"

    game.enemy_manager.enemies.clear()

    # Place enemy at distance = 5.0 blocks (Shotgun cannot hit past 3.0)
    far_enemy = Enemy(game, pos=(7.0, 2.0))
    far_enemy.hp = 100
    game.enemy_manager.enemies.append(far_enemy)

    # Fire pistol
    game.weapon.fire()

    damage_dealt = 100 - far_enemy.hp
    print(f">>> Pistol damage dealt at 5.0 blocks: {damage_dealt} HP (Remaining: {far_enemy.hp})")

    # Pistol should hit and deal between 22 and 30 damage
    assert damage_dealt > 0, "Pistol should hit enemy at 5.0 blocks"
    assert 20 <= damage_dealt <= 32, f"Pistol damage outside expected range: {damage_dealt}"
    print(">>> Pistol long-range hit confirmed.")


def test_shotgun_cannot_hit_at_long_range():
    print(">>> 4. Testing that Shotgun still cannot hit at 5.0 blocks...")
    game = Game()
    player = game.player
    player.x, player.y = 2.0, 2.0
    player.angle = 0.0

    # Switch to Shotgun
    game.select_weapon(1)
    assert game.weapon.name == "SHOTGUN"

    game.enemy_manager.enemies.clear()
    far_enemy = Enemy(game, pos=(7.0, 2.0))
    far_enemy.hp = 100
    game.enemy_manager.enemies.append(far_enemy)

    # Fire shotgun
    game.weapon.fire()

    assert far_enemy.hp == 100, f"Shotgun hit enemy at 5.0 blocks! Expected HP 100, got {far_enemy.hp}"
    print(">>> Shotgun range cutoff confirmed.")


def test_pistol_animation_cadence():
    print(">>> 5. Testing Pistol animation cadence...")
    game = Game()
    game.select_weapon(0)
    pistol = game.weapon

    assert not pistol.is_firing
    assert pistol.frame_index == 0

    pistol.fire()
    assert pistol.is_firing
    assert pistol.frame_index == 1

    # Advance time through frames
    game.delta_time = 16
    for _ in range(30):
        pygame.time.wait(20)
        pistol.update()

    assert not pistol.is_firing
    assert pistol.frame_index == 0
    print(">>> Pistol animation cadence verified.")


def test_pistol_audio():
    print(">>> 6. Testing Pistol audio method...")
    game = Game()
    assert hasattr(game.sound, "play_pistol_shot")
    game.sound.play_pistol_shot()
    print(">>> Pistol audio verified.")


if __name__ == "__main__":
    test_pistol_settings_and_attributes()
    test_weapon_inventory_and_switching()
    test_pistol_long_range_hitscan()
    test_shotgun_cannot_hit_at_long_range()
    test_pistol_animation_cadence()
    test_pistol_audio()
    print("\n>>> ALL PISTOL TESTS PASSED SUCCESSFULLY! <<<")
