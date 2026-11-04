"""
Unit and integration tests for Shotgun Nerf (Max Range = 3 blocks, 30% damage at 3 blocks).
"""
import os
import sys
import math

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.main import Game
from src.core.settings import (
    SHOTGUN_MAX_RANGE,
    SHOTGUN_MIN_DAMAGE_RATIO,
    SHOTGUN_PELLETS,
    SHOTGUN_SPREAD,
)
from src.entities.enemy import Enemy
from src.graphics.sprite_object import ExplosiveBarrel


def test_shotgun_constants_and_attributes():
    """Verify default shotgun constants and weapon instance attributes."""
    print(">>> 1. Verifying shotgun settings & weapon attributes...")
    assert SHOTGUN_MAX_RANGE == 3.0, f"Expected 3.0, got {SHOTGUN_MAX_RANGE}"
    assert SHOTGUN_MIN_DAMAGE_RATIO == 0.30, f"Expected 0.30, got {SHOTGUN_MIN_DAMAGE_RATIO}"
    assert SHOTGUN_PELLETS == 12
    assert SHOTGUN_SPREAD == 0.045

    game = Game()
    assert hasattr(game, "weapon")
    assert game.weapon.max_range == 3.0
    assert game.weapon.min_damage_ratio == 0.30
    assert game.weapon.num_pellets == 12
    assert game.weapon.spread == 0.045
    print(">>> Shotgun constants verified.")


def test_shotgun_range_cutoff():
    """Test that enemies farther than 3.0 blocks cannot be hit by the shotgun."""
    print(">>> 2. Testing shotgun maximum range cutoff (> 3.0 blocks)...")
    game = Game()
    player = game.player
    # Place player at (2.0, 2.0) facing East (angle = 0)
    player.x, player.y = 2.0, 2.0
    player.angle = 0.0

    # Clear existing enemies
    game.enemy_manager.enemies.clear()

    # Place an enemy at (5.5, 2.0) -> distance = 3.5 blocks (beyond 3.0 max range)
    far_enemy = Enemy(game, pos=(5.5, 2.0))
    far_enemy.hp = 100
    game.enemy_manager.enemies.append(far_enemy)

    # Fire shotgun
    game.enemy_manager.process_shot(player)

    # Enemy beyond 3.0 blocks must NOT receive any damage
    assert far_enemy.hp == 100, f"Far enemy took damage! Expected HP 100, got {far_enemy.hp}"
    print(">>> Far enemy (>3.0 blocks) correctly took 0 damage.")


def test_shotgun_damage_at_max_range():
    """Test that enemy at 3.0 blocks receives approximately 30% damage and survives."""
    print(">>> 3. Testing shotgun damage falloff at 3.0 blocks (~30% damage)...")
    game = Game()
    player = game.player
    player.x, player.y = 2.0, 2.0
    player.angle = 0.0

    game.enemy_manager.enemies.clear()

    # Place enemy at exactly distance = 3.0 blocks: (5.0, 2.0)
    edge_enemy = Enemy(game, pos=(5.0, 2.0))
    edge_enemy.hp = 100
    game.enemy_manager.enemies.append(edge_enemy)

    # Fire shotgun
    game.enemy_manager.process_shot(player)

    damage_dealt = 100 - edge_enemy.hp
    print(f">>> Damage dealt at 3.0 blocks: {damage_dealt} HP (Remaining HP: {edge_enemy.hp})")

    # Full shotgun base damage is ~144 - 216 (12 pellets * 12..18).
    # 30% of base damage should be ~43 - 65.
    # The enemy must take damage, but MUST survive (HP > 0).
    assert damage_dealt > 0, "Enemy at 3.0 blocks should take damage"
    assert edge_enemy.hp > 0, f"Enemy at 3.0 blocks should survive, but died! HP={edge_enemy.hp}"
    assert 35 <= damage_dealt <= 75, f"Damage at 3.0 blocks outside expected ~30% range: {damage_dealt}"
    print(">>> Edge enemy at 3.0 blocks took ~30% damage and survived as expected.")


def test_shotgun_close_range_high_damage():
    """Test that enemy at close range (< 1.0 block) takes high/full damage."""
    print(">>> 4. Testing shotgun close-range high damage (< 1.0 block)...")
    game = Game()
    player = game.player
    player.x, player.y = 2.0, 2.0
    player.angle = 0.0

    game.enemy_manager.enemies.clear()

    # Place enemy at close range: distance = 0.7 block (2.7, 2.0)
    close_enemy = Enemy(game, pos=(2.7, 2.0))
    close_enemy.hp = 200  # Give more HP to measure high damage without dying immediately
    game.enemy_manager.enemies.append(close_enemy)

    # Fire shotgun
    game.enemy_manager.process_shot(player)

    damage_dealt = 200 - close_enemy.hp
    print(f">>> Damage dealt at 0.7 blocks: {damage_dealt} HP")

    # At 0.7 blocks, falloff is 1 - 0.7 * (0.7/3) ≈ 83.7% of base damage.
    # Base is ~180, so damage should be around ~130 - 180 HP!
    assert damage_dealt >= 110, f"Expected high point-blank damage >= 110, got {damage_dealt}"
    print(">>> Close-range damage verified.")


def test_barrel_range_and_falloff():
    """Test that explosive barrels obey 3.0 range limit."""
    print(">>> 5. Testing explosive barrel range cutoff...")
    game = Game()
    player = game.player
    player.x, player.y = 2.0, 2.0
    player.angle = 0.0

    # Place barrel at distance 4.0 blocks (beyond 3.0)
    far_barrel = ExplosiveBarrel(game, pos=(6.0, 2.0))
    initial_hp = far_barrel.hp
    game.sprite_manager.sprite_list.append(far_barrel)

    # Fire shotgun
    game.enemy_manager.process_shot(player)
    assert far_barrel.hp == initial_hp, f"Far barrel took damage beyond 3.0 blocks! HP: {far_barrel.hp}"
    print(">>> Far barrel correctly took 0 damage.")


if __name__ == "__main__":
    test_shotgun_constants_and_attributes()
    test_shotgun_range_cutoff()
    test_shotgun_damage_at_max_range()
    test_shotgun_close_range_high_damage()
    test_barrel_range_and_falloff()
    print("\n>>> ALL SHOTGUN NERF TESTS PASSED! <<<")
