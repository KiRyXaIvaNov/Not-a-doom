"""
Main entry point and game loop for Not-a-Doom.
"""
import os
import sys

# Ensure project root is in sys.path regardless of how script is executed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.settings import RES, FPS
from src.sound import SoundManager
from src.map import Map
from src.player import Player
from src.textures import TextureManager
from src.raycasting import RayCasting
from src.sprite_object import SpriteManager
from src.enemy import EnemyManager
from src.particles import ParticleManager
from src.renderer import Renderer
from src.weapon import Weapon


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(RES)
        pygame.display.set_caption("Not-a-Doom (2.5D Retro FPS)")
        self.clock = pygame.time.Clock()
        self.delta_time = 1
        self.running = True
        self.mouse_grabbed = True
        self.pressed_scancodes = set()

        self.grab_mouse(True)
        self.new_game()

    def grab_mouse(self, grab: bool):
        """Toggle mouse capture and visibility."""
        self.mouse_grabbed = grab
        pygame.mouse.set_visible(not grab)
        pygame.event.set_grab(grab)

    def new_game(self):
        self.sound = SoundManager(self)
        self.map = Map()
        self.player = Player(self)
        self.textures = TextureManager()
        self.raycasting = RayCasting(self)
        self.enemy_manager = EnemyManager(self)
        self.particle_manager = ParticleManager(self)
        self.sprite_manager = SpriteManager(self)
        self.weapon = Weapon(self)
        self.renderer = Renderer(self)

    def update(self):
        self.delta_time = self.clock.tick(FPS)
        self.player.update()
        if self.mouse_grabbed:
            self.particle_manager.update()
            self.enemy_manager.update()
            self.raycasting.update()
            self.weapon.update()

        fps = int(self.clock.get_fps())
        status = "PLAYING" if self.mouse_grabbed else "PAUSED (Click or press ESC to resume, Q to quit)"
        pygame.display.set_caption(f"Not-a-Doom | {status} | FPS: {fps}")

    def draw(self):
        self.renderer.draw()
        pygame.display.flip()

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pressed_scancodes.add(event.scancode)
                if event.key == pygame.K_ESCAPE:
                    self.grab_mouse(not self.mouse_grabbed)
                elif not self.mouse_grabbed and event.key == pygame.K_q:
                    self.running = False
                elif self.mouse_grabbed and (event.key == pygame.K_SPACE or event.key == pygame.K_LCTRL):
                    self.weapon.fire()
            elif event.type == pygame.KEYUP:
                self.pressed_scancodes.discard(event.scancode)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.mouse_grabbed and event.button == 1:
                    self.grab_mouse(True)
                elif self.mouse_grabbed and event.button == 1:
                    self.weapon.fire()

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
