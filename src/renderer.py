"""
3D World Renderer for Not-a-Doom.
Handles skybox scrolling, distance fog/shading, wall projection, and HUD overlays.
Optimized with vertical clipping and zero-runtime-cost pre-baked lightmaps (DOOM style).
"""
import math
import pygame
from src.settings import (
    WIDTH,
    HEIGHT,
    HALF_WIDTH,
    HALF_HEIGHT,
    FLOOR_COLOR,
    SCALE,
    TEXTURE_SIZE,
    WHITE,
    RED,
    GREEN,
)


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.textures = game.textures
        self.sky_offset = 0
        self.font_large = pygame.font.SysFont("impact", 48)
        self.font_small = pygame.font.SysFont("arial", 20, bold=True)

    def draw_background(self):
        """Draw panoramic scrolling sky and dark retro floor."""
        # Sky scrolling based on player rotation
        self.sky_offset = -int((self.game.player.angle / math.tau) * WIDTH) % WIDTH
        self.screen.blit(self.textures.sky, (self.sky_offset, 0))
        self.screen.blit(self.textures.sky, (self.sky_offset - WIDTH, 0))

        # Dark floor
        pygame.draw.rect(
            self.screen,
            FLOOR_COLOR,
            (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT),
        )

    def render_walls(self):
        """Render textured 3D wall slices with hardware clipping and instant O(1) pre-shaded texture lookup."""
        for depth, proj_height, texture_id, wall_x, ray, side in self.game.raycasting.ray_casting_result:
            # Distance shading / depth fog
            depth_factor = 1.0 / (1.0 + depth * depth * 0.04)
            # Side darkening for pseudo-3D lighting on wall edges
            side_factor = 0.75 if side == 1 else 1.0
            brightness = max(0.1, min(1.0, depth_factor * side_factor))

            # Fetch pre-shaded texture surface (zero runtime CPU multiplication!)
            texture = self.textures.get_shaded_texture(texture_id, brightness)
            col_x = int(wall_x * (TEXTURE_SIZE - 1))

            # Vertical clipping: avoid scaling massive offscreen surfaces when close to walls
            if proj_height < HEIGHT:
                slice_height = int(proj_height)
                screen_y = HALF_HEIGHT - slice_height // 2
                wall_slice = texture.subsurface(col_x, 0, 1, TEXTURE_SIZE)
                wall_column = pygame.transform.scale(wall_slice, (SCALE, slice_height))
            else:
                # Wall is taller than screen: crop only the visible portion of the texture
                slice_height = HEIGHT
                screen_y = 0
                texture_height_factor = HEIGHT / proj_height
                sub_y = int((1.0 - texture_height_factor) * 0.5 * TEXTURE_SIZE)
                sub_h = int(texture_height_factor * TEXTURE_SIZE)
                sub_y = max(0, min(TEXTURE_SIZE - 1, sub_y))
                sub_h = max(1, min(TEXTURE_SIZE - sub_y, sub_h))
                wall_slice = texture.subsurface(col_x, sub_y, 1, sub_h)
                wall_column = pygame.transform.scale(wall_slice, (SCALE, HEIGHT))

            # Blit directly to screen
            screen_x = ray * SCALE
            self.screen.blit(wall_column, (screen_x, screen_y))

    def draw_crosshair(self):
        """Draw minimalist classic shooter crosshair in center."""
        cx, cy = HALF_WIDTH, HALF_HEIGHT
        size = 6
        gap = 3
        # Horizontal bars
        pygame.draw.line(self.screen, (0, 255, 0), (cx - size - gap, cy), (cx - gap, cy), 2)
        pygame.draw.line(self.screen, (0, 255, 0), (cx + gap, cy), (cx + size + gap, cy), 2)
        # Vertical bars
        pygame.draw.line(self.screen, (0, 255, 0), (cx, cy - size - gap), (cx, cy - gap), 2)
        pygame.draw.line(self.screen, (0, 255, 0), (cx, cy + gap), (cx, cy + size + gap), 2)

    def draw_minimap(self):
        """Draw semi-transparent 2D radar minimap in top-right corner."""
        scale = 6
        map_w = self.game.map.cols * scale
        map_h = self.game.map.rows * scale
        pad = 12
        map_x = WIDTH - map_w - pad
        map_y = pad

        # Background panel
        bg_surf = pygame.Surface((map_w + 4, map_h + 4), pygame.SRCALPHA)
        bg_surf.fill((10, 10, 15, 180))
        self.screen.blit(bg_surf, (map_x - 2, map_y - 2))

        # Walls
        for (gx, gy) in self.game.map.world_map:
            rect = (map_x + gx * scale, map_y + gy * scale, scale, scale)
            pygame.draw.rect(self.screen, (100, 100, 120), rect)

        # Player icon & direction line
        px = map_x + int(self.game.player.x * scale)
        py = map_y + int(self.game.player.y * scale)
        pygame.draw.circle(self.screen, (0, 255, 255), (px, py), 3)

        dir_len = 10
        end_x = px + int(math.cos(self.game.player.angle) * dir_len)
        end_y = py + int(math.sin(self.game.player.angle) * dir_len)
        pygame.draw.line(self.screen, (255, 255, 0), (px, py), (end_x, end_y), 2)

    def draw_pause_overlay(self):
        """Darken screen and show pause instructions."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("PAUSED", True, (255, 215, 0))
        sub1 = self.font_small.render("Press ESC or Click to Resume", True, (240, 240, 240))
        sub2 = self.font_small.render("Press Q to Quit", True, (200, 200, 200))

        self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 40)))
        self.screen.blit(sub1, sub1.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 20)))
        self.screen.blit(sub2, sub2.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 55)))

    def draw(self):
        self.draw_background()
        self.render_walls()
        self.draw_crosshair()
        self.draw_minimap()

        if not self.game.mouse_grabbed:
            self.draw_pause_overlay()
