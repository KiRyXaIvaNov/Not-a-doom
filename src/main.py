"""
Main entry point and game loop for Not-a-Doom.
"""
import os
import sys

# Ensure project root is in sys.path regardless of how script is executed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.core.settings import RES, FPS
from src.audio.sound import SoundManager
from src.core.map import Map
from src.entities.player import Player
from src.graphics.textures import TextureManager
from src.core.raycasting import RayCasting
from src.graphics.sprite_object import SpriteManager
from src.entities.enemy import EnemyManager
from src.combat.particles import ParticleManager
from src.combat.projectile import ProjectileManager
from src.graphics.renderer import Renderer
from src.combat.weapon import Weapon, Shotgun, Pistol
from src.core.editor import LevelEditor


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(RES)
        pygame.display.set_caption("Not-a-Doom (2.5D Retro FPS)")
        self.clock = pygame.time.Clock()
        self.delta_time = 1
        self.running = True
        self.mouse_grabbed = True
        self.is_fullscreen = False
        self.pressed_scancodes = set()
        self.mode = "game"  # "game" or "editor"

        self.grab_mouse(True)
        self.new_game()
        self.editor = LevelEditor(self)

    def toggle_fullscreen(self):
        """Toggle between windowed and fullscreen display with hardware scaling."""
        self.is_fullscreen = not self.is_fullscreen
        try:
            if self.is_fullscreen:
                self.screen = pygame.display.set_mode(RES, pygame.FULLSCREEN | pygame.SCALED)
            else:
                self.screen = pygame.display.set_mode(RES)
        except pygame.error:
            try:
                if self.is_fullscreen:
                    self.screen = pygame.display.set_mode(RES, pygame.FULLSCREEN)
                else:
                    self.screen = pygame.display.set_mode(RES)
            except pygame.error:
                self.is_fullscreen = False
        if hasattr(self, "renderer"):
            self.renderer.screen = self.screen

    def grab_mouse(self, grab: bool):
        """Toggle mouse capture and visibility."""
        self.mouse_grabbed = grab
        pygame.mouse.set_visible(not grab)
        pygame.event.set_grab(grab)

    def open_editor(self):
        """Switch to level editor mode, release mouse capture, and sync map data."""
        self.mode = "editor"
        self.grab_mouse(False)
        self.editor.sync_from_map()

    def close_editor(self, apply: bool = True):
        """Switch back to 3D game mode and capture mouse."""
        if apply:
            self.apply_editor_map()
        self.mode = "game"
        self.grab_mouse(True)

    def apply_editor_map(self):
        """Rebuild runtime game state from current map data after editor changes."""
        self.map._populate_world_map()
        self.player.reset_to_spawn()
        self.enemy_manager.setup_enemies()
        self.projectile_manager.projectiles.clear()
        self.particle_manager.particles.clear()
        self.sprite_manager.setup_map_props()
        self.victory = False
        self.start_ticks = pygame.time.get_ticks()

    def new_game(self):
        if not hasattr(self, 'sound'):
            self.sound = SoundManager(self)
        if not hasattr(self, 'textures'):
            self.textures = TextureManager()
        self.map = Map()
        self.player = Player(self)
        self.raycasting = RayCasting(self)
        self.enemy_manager = EnemyManager(self)
        self.projectile_manager = ProjectileManager(self)
        self.particle_manager = ParticleManager(self)
        self.sprite_manager = SpriteManager(self)
        self.pistol = Pistol(self)
        self.shotgun = Shotgun(self)
        self.weapons = [self.pistol, self.shotgun]
        self.current_weapon_idx = 1
        self.weapon = self.weapons[self.current_weapon_idx]
        self.renderer = Renderer(self)
        self.victory = False
        self.start_ticks = pygame.time.get_ticks()
        self.elapsed_time_str = "00:00"

    def select_weapon(self, index: int):
        """Switch active weapon by inventory index (0: Pistol, 1: Shotgun)."""
        if not (0 <= index < len(self.weapons)):
            return
        if self.current_weapon_idx == index:
            return
        self.weapon.is_firing = False
        self.weapon.frame_index = 0
        self.current_weapon_idx = index
        self.weapon = self.weapons[index]

    def trigger_victory(self):
        """Trigger level completion victory state."""
        if not self.victory:
            self.victory = True
            secs = max(0, (pygame.time.get_ticks() - self.start_ticks) // 1000)
            self.elapsed_time_str = f"{secs // 60:02d}:{secs % 60:02d}"
            if hasattr(self, "sound"):
                self.sound.play_teleport_win()

    def update(self):
        if self.mode == "editor":
            self.delta_time = min(self.clock.tick(FPS), 50)
            self.editor.update()
            fps = int(self.clock.get_fps())
            pygame.display.set_caption(f"Not-a-Doom | LEVEL EDITOR | FPS: {fps}")
            return

        self.delta_time = min(self.clock.tick(FPS), 50)
        self.player.update()
        if self.mouse_grabbed and not self.victory:
            self.particle_manager.update()
            self.projectile_manager.update()
            self.enemy_manager.update()
            self.sprite_manager.update()
            self.raycasting.update()
            self.weapon.update()

        fps = int(self.clock.get_fps())
        hp_str = f"HP: {self.player.hp}%" if self.player.alive else "DEAD"
        if self.victory:
            status = f"VICTORY! Time: {self.elapsed_time_str} (Press ENTER to replay)"
        elif not self.player.alive:
            status = "GAME OVER (Press R to respawn)"
        elif not self.mouse_grabbed:
            status = "PAUSED (Click/ESC to resume, F2 for Editor, Q to quit)"
        else:
            status = "PLAYING (Press F2 for Level Editor)"
        pygame.display.set_caption(f"Not-a-Doom | {hp_str} | {status} | FPS: {fps}")

    def draw(self):
        if self.mode == "editor":
            self.editor.draw(self.screen)
            pygame.display.flip()
            return

        self.renderer.draw()
        pygame.display.flip()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if self.mode == "editor":
                if event.type == pygame.KEYDOWN and (
                    event.key == pygame.K_F11
                    or (event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT))
                ):
                    self.toggle_fullscreen()
                else:
                    self.editor.handle_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                self.pressed_scancodes.add(event.scancode)
                if event.key == pygame.K_F2:
                    self.open_editor()
                elif (not self.player.alive or self.victory) and (
                    event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE)
                    or event.scancode == pygame.KSCAN_R
                ):
                    self.new_game()
                elif event.key == pygame.K_F11 or (
                    event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT)
                ):
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    self.grab_mouse(not self.mouse_grabbed)
                elif not self.mouse_grabbed and event.key == pygame.K_q:
                    self.running = False
                elif self.mouse_grabbed and event.key == pygame.K_1:
                    self.select_weapon(0)
                elif self.mouse_grabbed and event.key == pygame.K_2:
                    self.select_weapon(1)
                elif self.mouse_grabbed and event.key == pygame.K_q:
                    self.select_weapon(1 - self.current_weapon_idx)
                elif self.mouse_grabbed and (event.key == pygame.K_SPACE or event.key == pygame.K_LCTRL):
                    self.weapon.fire()
            elif event.type == pygame.KEYUP:
                self.pressed_scancodes.discard(event.scancode)
            elif event.type == pygame.MOUSEWHEEL and self.mouse_grabbed:
                if event.y != 0:
                    self.select_weapon(1 - self.current_weapon_idx)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.mouse_grabbed and event.button == 1:
                    self.grab_mouse(True)
                elif self.mouse_grabbed and event.button == 1:
                    self.weapon.fire()
                elif self.mouse_grabbed and event.button in (4, 5):
                    self.select_weapon(1 - self.current_weapon_idx)

    def run(self):
        while self.running:
            self.check_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
