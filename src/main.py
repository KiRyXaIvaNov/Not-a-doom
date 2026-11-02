"""
Main entry point and game loop for Not-a-Doom.
"""
import os
import sys

# Ensure project root is in sys.path regardless of how script is executed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.settings import RES, FPS
from src.map import Map
from src.player import Player
from src.textures import TextureManager
from src.raycasting import RayCasting
from src.renderer import Renderer


class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.screen = pygame.display.set_mode(RES)
        pygame.display.set_caption("Not-a-Doom (2.5D Retro FPS)")
        self.clock = pygame.time.Clock()
        self.delta_time = 1
        self.running = True
        self.mouse_grabbed = True
        self.pressed_scancodes = set()

        self.new_game()

    def new_game(self):
        self.map = Map()
        self.player = Player(self)
        self.textures = TextureManager()
        self.raycasting = RayCasting(self)
        self.renderer = Renderer(self)

    def update(self):
        self.delta_time = self.clock.tick(FPS)
        self.player.update()
        self.raycasting.update()

        # Display current FPS in title
        fps = int(self.clock.get_fps())
        pygame.display.set_caption(f"Not-a-Doom (2.5D Retro FPS) | FPS: {fps}")

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
                    # Toggle mouse grab
                    self.mouse_grabbed = not self.mouse_grabbed
                    pygame.mouse.set_visible(not self.mouse_grabbed)
                    pygame.event.set_grab(self.mouse_grabbed)
            elif event.type == pygame.KEYUP:
                self.pressed_scancodes.discard(event.scancode)

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
