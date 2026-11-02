"""
2.5D Billboard Sprite system for Not-a-Doom.
Handles depth sorting, Z-buffer wall occlusion, perspective projection and distance shading.
"""
import os
import math
import pygame
from src.settings import (
    WIDTH,
    HEIGHT,
    HALF_WIDTH,
    HALF_HEIGHT,
    FOV,
    HALF_FOV,
    NUM_RAYS,
    SCREEN_DIST,
    SCALE,
    DELTA_ANGLE,
)

ASSETS_PROPS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites", "props")


def generate_barrel_sprite() -> pygame.Surface:
    """Generate classic DOOM toxic radioactive waste barrel."""
    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    # Dark green ribbed metal drum
    GREEN_DARK = (25, 60, 30)
    GREEN_MID = (45, 105, 50)
    GREEN_LIGHT = (70, 155, 75)
    SLIME_GLOW = (80, 255, 60)
    BLACK = (15, 20, 15)

    # Base cylinder
    pygame.draw.rect(surf, GREEN_MID, (14, 16, 36, 42), border_radius=4)
    # Highlights & shadows
    pygame.draw.rect(surf, GREEN_LIGHT, (17, 16, 8, 42))
    pygame.draw.rect(surf, GREEN_DARK, (38, 16, 12, 42))

    # Metallic reinforcement ribs (rings around the barrel)
    for ry in [20, 34, 48]:
        pygame.draw.line(surf, (30, 40, 30), (14, ry), (50, ry), 2)
        pygame.draw.line(surf, (80, 170, 85), (17, ry - 1), (25, ry - 1), 1)

    # Slime oozing out of top lid
    pygame.draw.ellipse(surf, GREEN_DARK, (14, 12, 36, 10))
    pygame.draw.ellipse(surf, SLIME_GLOW, (18, 14, 28, 6))

    # Biohazard toxic hazard symbol in yellow
    pygame.draw.polygon(surf, (240, 210, 30), [
        (cx, 32),
        (cx - 7, 44),
        (cx + 7, 44)
    ])
    pygame.draw.circle(surf, BLACK, (cx, 38), 3)

    # Outer outline
    pygame.draw.rect(surf, BLACK, (14, 16, 36, 42), 2, border_radius=4)
    return surf


def generate_pillar_sprite() -> pygame.Surface:
    """Generate ancient stone pillar monolith."""
    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    # Stone shaft
    pygame.draw.rect(surf, (90, 92, 100), (20, 12, 24, 48))
    pygame.draw.rect(surf, (135, 140, 150), (22, 12, 6, 48))
    pygame.draw.rect(surf, (60, 62, 70), (34, 12, 10, 48))

    # Capital & Base pedestal
    pygame.draw.rect(surf, (75, 78, 85), (16, 8, 32, 6))
    pygame.draw.rect(surf, (75, 78, 85), (16, 56, 32, 6))

    # Fire bowl on top
    pygame.draw.ellipse(surf, (40, 40, 45), (18, 6, 28, 6))
    # Glowing flame
    pygame.draw.polygon(surf, (255, 120, 20), [(cx, 0), (cx - 6, 8), (cx + 6, 8)])
    pygame.draw.polygon(surf, (255, 230, 40), [(cx, 2), (cx - 3, 7), (cx + 3, 7)])

    # Outline
    pygame.draw.rect(surf, (20, 20, 25), (20, 12, 24, 48), 2)
    return surf


def generate_medkit_sprite() -> pygame.Surface:
    """Generate classic first-aid medical supply kit."""
    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    # White metal case with dark shading
    pygame.draw.rect(surf, (225, 230, 235), (16, 32, 32, 24), border_radius=3)
    pygame.draw.rect(surf, (180, 185, 195), (36, 32, 12, 24), border_radius=3)
    pygame.draw.rect(surf, (40, 45, 50), (16, 32, 32, 24), 2, border_radius=3)

    # Red Cross emblem
    pygame.draw.rect(surf, (220, 25, 25), (cx - 2, 37, 4, 14))
    pygame.draw.rect(surf, (220, 25, 25), (cx - 7, 42, 14, 4))
    return surf


def get_prop_surface(name: str, generator_func) -> pygame.Surface:
    """Load cached PNG prop or generate and save it."""
    os.makedirs(ASSETS_PROPS_DIR, exist_ok=True)
    path = os.path.join(ASSETS_PROPS_DIR, f"{name}.png")
    if os.path.exists(path):
        return pygame.image.load(path).convert_alpha()
    surf = generator_func()
    pygame.image.save(surf, path)
    return surf


class SpriteObject:
    def __init__(self, game, name: str, pos: tuple, scale=0.7, shift=0.25):
        self.game = game
        self.name = name
        self.x, self.y = pos
        self.scale = scale
        self.shift = shift

        generators = {
            "barrel": generate_barrel_sprite,
            "pillar": generate_pillar_sprite,
            "medkit": generate_medkit_sprite,
        }
        self.image = get_prop_surface(name, generators.get(name, generate_barrel_sprite))
        self.IMAGE_WIDTH = self.image.get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2

        self.dist = 0.0
        self.screen_x = 0
        self.current_size = 0

    def get_sprite_projection(self):
        """Calculate polar angle, distance, screen X position and scale."""
        dx = self.x - self.game.player.x
        dy = self.y - self.game.player.y
        self.theta = math.atan2(dy, dx)

        delta = self.theta - self.game.player.angle
        if (dx > 0 and self.game.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = (NUM_RAYS // 2 + delta_rays) * SCALE

        # Distance with fish-eye elimination
        self.dist = math.hypot(dx, dy)
        norm_dist = self.dist * math.cos(delta)

        # Do not render if behind camera or too close
        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and norm_dist > 0.4:
            proj = SCREEN_DIST / norm_dist * self.scale
            proj_width, proj_height = int(proj), int(proj)

            # Center position
            half_proj_w = proj_width // 2
            height_shift = int(proj_height * self.shift)
            pos_x = self.screen_x - half_proj_w
            pos_y = HALF_HEIGHT - proj_height // 2 + height_shift

            return (norm_dist, self.image, (pos_x, pos_y), (proj_width, proj_height))
        return None


class SpriteManager:
    """Manages all 2.5D billboard sprites and renders them with Z-buffer occlusion."""
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.setup_map_props()

    def setup_map_props(self):
        """Place props around the game labyrinth."""
        self.sprite_list = [
            SpriteObject(self.game, "barrel", (3.5, 1.5), scale=0.7, shift=0.25),
            SpriteObject(self.game, "barrel", (4.5, 1.5), scale=0.7, shift=0.25),
            SpriteObject(self.game, "barrel", (9.5, 5.5), scale=0.7, shift=0.25),
            SpriteObject(self.game, "barrel", (13.5, 13.5), scale=0.7, shift=0.25),
            SpriteObject(self.game, "pillar", (7.5, 1.5), scale=0.9, shift=0.15),
            SpriteObject(self.game, "pillar", (1.5, 7.5), scale=0.9, shift=0.15),
            SpriteObject(self.game, "pillar", (13.5, 5.5), scale=0.9, shift=0.15),
            SpriteObject(self.game, "medkit", (1.5, 3.5), scale=0.45, shift=0.6),
            SpriteObject(self.game, "medkit", (5.5, 5.5), scale=0.45, shift=0.6),
            SpriteObject(self.game, "medkit", (11.5, 1.5), scale=0.45, shift=0.6),
        ]

    def render(self, screen: pygame.Surface):
        """Sort sprites by distance and draw slices that pass the Z-buffer depth test."""
        depth_buffer = self.game.raycasting.depth_buffer

        # Calculate projections and collect visible sprites
        visible_sprites = []
        for sprite in self.sprite_list:
            proj_data = sprite.get_sprite_projection()
            if proj_data:
                visible_sprites.append(proj_data)

        # Sort furthest to closest (Painters Algorithm)
        visible_sprites.sort(key=lambda item: item[0], reverse=True)

        for norm_dist, image, (pos_x, pos_y), (proj_w, proj_h) in visible_sprites:
            if proj_w <= 0 or proj_h <= 0:
                continue

            scaled_sprite = pygame.transform.scale(image, (proj_w, proj_h))

            # Apply distance lighting
            depth_factor = 1.0 / (1.0 + norm_dist * norm_dist * 0.04)
            brightness = max(0.12, min(1.0, depth_factor))
            if brightness < 0.95:
                val = int(255 * brightness)
                scaled_sprite.fill((val, val, val), special_flags=pygame.BLEND_MULT)

            # Draw vertical slices that pass the depth test against walls
            step = SCALE
            img_w = proj_w

            for col in range(0, img_w, step):
                screen_x = pos_x + col
                ray_idx = int(screen_x // SCALE)

                # Check if slice is on screen and in front of any wall at this column
                if 0 <= ray_idx < NUM_RAYS:
                    if norm_dist < depth_buffer[ray_idx]:
                        # Slice passes Z-test!
                        slice_w = min(step, img_w - col)
                        col_slice = scaled_sprite.subsurface(col, 0, slice_w, proj_h)
                        screen.blit(col_slice, (screen_x, pos_y))
