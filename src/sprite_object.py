"""
2.5D Billboard Sprite system for Not-a-Doom.
Handles depth sorting, Z-buffer wall occlusion, perspective projection,
and hardware-friendly span-based blitting with zero-allocation pre-baked lightmaps.
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
    MAX_DEPTH,
)

ASSETS_PROPS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites", "props")
NUM_PROP_LIGHTS = 8


def generate_barrel_sprite() -> pygame.Surface:
    """Generate classic DOOM toxic radioactive waste barrel."""
    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    GREEN_DARK = (25, 60, 30)
    GREEN_MID = (45, 105, 50)
    GREEN_LIGHT = (70, 155, 75)
    SLIME_GLOW = (80, 255, 60)
    BLACK = (15, 20, 15)

    pygame.draw.rect(surf, GREEN_MID, (14, 16, 36, 42), border_radius=4)
    pygame.draw.rect(surf, GREEN_LIGHT, (17, 16, 8, 42))
    pygame.draw.rect(surf, GREEN_DARK, (38, 16, 12, 42))

    for ry in [20, 34, 48]:
        pygame.draw.line(surf, (30, 40, 30), (14, ry), (50, ry), 2)
        pygame.draw.line(surf, (80, 170, 85), (17, ry - 1), (25, ry - 1), 1)

    pygame.draw.ellipse(surf, GREEN_DARK, (14, 12, 36, 10))
    pygame.draw.ellipse(surf, SLIME_GLOW, (18, 14, 28, 6))

    pygame.draw.polygon(surf, (240, 210, 30), [
        (cx, 32),
        (cx - 7, 44),
        (cx + 7, 44)
    ])
    pygame.draw.circle(surf, BLACK, (cx, 38), 3)
    pygame.draw.rect(surf, BLACK, (14, 16, 36, 42), 2, border_radius=4)
    return surf


def generate_pillar_sprite() -> pygame.Surface:
    """Generate ancient stone pillar monolith."""
    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    pygame.draw.rect(surf, (90, 92, 100), (20, 12, 24, 48))
    pygame.draw.rect(surf, (135, 140, 150), (22, 12, 6, 48))
    pygame.draw.rect(surf, (60, 62, 70), (34, 12, 10, 48))

    pygame.draw.rect(surf, (75, 78, 85), (16, 8, 32, 6))
    pygame.draw.rect(surf, (75, 78, 85), (16, 56, 32, 6))

    pygame.draw.ellipse(surf, (40, 40, 45), (18, 6, 28, 6))
    pygame.draw.polygon(surf, (255, 120, 20), [(cx, 0), (cx - 6, 8), (cx + 6, 8)])
    pygame.draw.polygon(surf, (255, 230, 40), [(cx, 2), (cx - 3, 7), (cx + 3, 7)])

    pygame.draw.rect(surf, (20, 20, 25), (20, 12, 24, 48), 2)
    return surf


def generate_medkit_sprite() -> pygame.Surface:
    """Generate classic first-aid medical supply kit."""
    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx = size // 2

    pygame.draw.rect(surf, (225, 230, 235), (16, 32, 32, 24), border_radius=3)
    pygame.draw.rect(surf, (180, 185, 195), (36, 32, 12, 24), border_radius=3)
    pygame.draw.rect(surf, (40, 45, 50), (16, 32, 32, 24), 2, border_radius=3)

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


def generate_portal_frame(frame_idx: int) -> pygame.Surface:
    """Procedurally create animated swirling emerald exit portal (80x80)."""
    size = 80
    cx, cy = size // 2, size // 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # Base pedestal
    ped_w, ped_h = 40, 10
    ped_y = size - 14
    pygame.draw.ellipse(surf, (45, 50, 60), (cx - ped_w // 2, ped_y, ped_w, ped_h))
    pygame.draw.ellipse(surf, (80, 90, 105), (cx - ped_w // 2 + 2, ped_y + 1, ped_w - 4, ped_h - 2))

    # Swirling gateway oval
    portal_rx, portal_ry = 18, 28
    portal_y = cy - 4

    # Outer glow & main vortex
    pygame.draw.ellipse(surf, (0, 180, 140, 140), (cx - portal_rx - 4, portal_y - portal_ry - 4, (portal_rx + 4) * 2, (portal_ry + 4) * 2))
    pygame.draw.ellipse(surf, (0, 240, 190), (cx - portal_rx, portal_y - portal_ry, portal_rx * 2, portal_ry * 2))
    pygame.draw.ellipse(surf, (180, 255, 240), (cx - portal_rx + 5, portal_y - portal_ry + 6, (portal_rx - 5) * 2, (portal_ry - 6) * 2))
    pygame.draw.ellipse(surf, (255, 255, 255), (cx - 5, portal_y - 12, 10, 24))

    # Rotating energy tendrils
    angle_offset = frame_idx * (math.pi / 2)
    for i in range(4):
        ang = angle_offset + i * (math.pi / 2)
        tx = cx + int(math.cos(ang) * (portal_rx - 4))
        ty = portal_y + int(math.sin(ang) * (portal_ry - 8))
        pygame.draw.circle(surf, (255, 255, 255), (tx, ty), 2)
    return surf


class PortalObject:
    """Animated exit portal that triggers level victory when reached."""
    def __init__(self, game, pos: tuple[float, float], scale: float = 0.95, shift: float = 0.12):
        self.game = game
        self.name = "portal"
        self.x, self.y = pos
        self.scale = scale
        self.shift = shift
        self.frames = self._load_or_generate_frames()
        self.IMAGE_WIDTH = self.frames[0].get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2
        self.frame_idx = 0
        self.anim_timer = 0.0
        self.dist = 0.0
        self.screen_x = 0

    def _load_or_generate_frames(self) -> list[pygame.Surface]:
        os.makedirs(ASSETS_PROPS_DIR, exist_ok=True)
        frames = []
        for i in range(4):
            path = os.path.join(ASSETS_PROPS_DIR, f"portal_{i}.png")
            if os.path.exists(path):
                try:
                    frames.append(pygame.image.load(path).convert_alpha())
                    continue
                except Exception:
                    pass
            surf = generate_portal_frame(i)
            pygame.image.save(surf, path)
            frames.append(surf)
        return frames

    def update(self):
        dt = self.game.delta_time
        self.anim_timer += dt
        if self.anim_timer >= 120.0:
            self.anim_timer = 0.0
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)

        # Trigger victory if player steps into portal
        player = self.game.player
        if player.alive and not self.game.victory:
            dist = math.hypot(self.x - player.x, self.y - player.y)
            if dist < 0.70:
                self.game.trigger_victory()

    def get_sprite_projection(self):
        dx = self.x - self.game.player.x
        dy = self.y - self.game.player.y
        theta = math.atan2(dy, dx)

        delta = theta - self.game.player.angle
        if (dx > 0 and self.game.player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        self.screen_x = int((NUM_RAYS // 2 + delta_rays) * SCALE)

        self.dist = math.hypot(dx, dy)
        norm_dist = self.dist * math.cos(delta)

        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and 0.35 < norm_dist < MAX_DEPTH:
            proj = SCREEN_DIST / norm_dist * self.scale
            max_size = int(HEIGHT * 1.4)
            proj_w = int(min(max_size, int(proj)))
            proj_h = int(min(max_size, int(proj)))

            half_proj_w = proj_w // 2
            height_shift = int(proj_h * self.shift)
            pos_x = int(self.screen_x - half_proj_w)
            pos_y = int(HALF_HEIGHT - proj_h // 2 + height_shift)

            # Portal is an energy gateway, always bright
            return (norm_dist, self.frames[self.frame_idx], (pos_x, pos_y), (proj_w, proj_h))
        return None


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
        self.base_image = get_prop_surface(name, generators.get(name, generate_barrel_sprite))
        self.IMAGE_WIDTH = self.base_image.get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2

        self.shaded_images = self._bake_light_levels()
        self.dist = 0.0
        self.screen_x = 0

    def _bake_light_levels(self):
        levels = []
        for i in range(NUM_PROP_LIGHTS):
            ratio = i / (NUM_PROP_LIGHTS - 1)
            brightness = max(0.12, ratio)
            val = int(255 * brightness)
            shaded = self.base_image.copy()
            shaded.fill((val, val, val), special_flags=pygame.BLEND_MULT)
            levels.append(shaded)
        return levels

    def get_shaded_image(self, brightness: float) -> pygame.Surface:
        idx = int(brightness * (NUM_PROP_LIGHTS - 1))
        idx = max(0, min(NUM_PROP_LIGHTS - 1, idx))
        return self.shaded_images[idx]

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

        self.dist = math.hypot(dx, dy)
        norm_dist = self.dist * math.cos(delta)

        if -self.IMAGE_HALF_WIDTH < self.screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and 0.35 < norm_dist < MAX_DEPTH:
            proj = SCREEN_DIST / norm_dist * self.scale
            max_size = int(HEIGHT * 1.4)
            proj_w = int(min(max_size, int(proj)))
            proj_h = int(min(max_size, int(proj)))

            half_proj_w = proj_w // 2
            height_shift = int(proj_h * self.shift)
            pos_x = int(self.screen_x - half_proj_w)
            pos_y = int(HALF_HEIGHT - proj_h // 2 + height_shift)

            depth_factor = 1.0 / (1.0 + norm_dist * norm_dist * 0.04)
            brightness = max(0.12, min(1.0, depth_factor))
            shaded_img = self.get_shaded_image(brightness)

            return (norm_dist, shaded_img, (pos_x, pos_y), (proj_w, proj_h))
        return None


class SpriteManager:
    """Manages all 2.5D billboard sprites and renders them with span-based Z-buffer occlusion."""
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.setup_map_props()

    def update(self):
        for sprite in self.sprite_list:
            if hasattr(sprite, 'update'):
                sprite.update()

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
            PortalObject(self.game, (14.5, 14.5), scale=0.95, shift=0.12),
        ]

    def render(self, screen: pygame.Surface):
        """Sort sprites by distance and draw contiguous spans that pass the Z-buffer depth test."""
        depth_buffer = self.game.raycasting.depth_buffer

        visible_sprites = []
        for sprite in self.sprite_list:
            proj_data = sprite.get_sprite_projection()
            if proj_data:
                visible_sprites.append(proj_data)

        if hasattr(self.game, 'enemy_manager'):
            for enemy in self.game.enemy_manager.enemies:
                proj_data = enemy.get_projection_data()
                if proj_data:
                    visible_sprites.append(proj_data)

        if hasattr(self.game, 'projectile_manager'):
            for proj in self.game.projectile_manager.projectiles:
                proj_data = proj.get_projection_data()
                if proj_data:
                    visible_sprites.append(proj_data)

        visible_sprites.sort(key=lambda item: item[0], reverse=True)

        for norm_dist, shaded_image, (pos_x, pos_y), (proj_w, proj_h) in visible_sprites:
            if proj_w <= 0 or proj_h <= 0:
                continue

            start_col = int(max(0, -pos_x))
            end_col = int(min(proj_w, WIDTH - pos_x))
            if end_col <= start_col:
                continue

            scaled_sprite = pygame.transform.scale(shaded_image, (proj_w, proj_h))

            span_start = None
            step = int(SCALE)

            for col in range(start_col, end_col, step):
                screen_x = pos_x + col
                ray_idx = int(screen_x // SCALE)

                visible = (0 <= ray_idx < NUM_RAYS and norm_dist < depth_buffer[ray_idx])

                if visible:
                    if span_start is None:
                        span_start = col
                else:
                    if span_start is not None:
                        span_w = int(col - span_start)
                        col_slice = scaled_sprite.subsurface(span_start, 0, span_w, proj_h)
                        screen.blit(col_slice, (pos_x + span_start, pos_y))
                        span_start = None

            if span_start is not None:
                span_w = int(end_col - span_start)
                col_slice = scaled_sprite.subsurface(span_start, 0, span_w, proj_h)
                screen.blit(col_slice, (pos_x + span_start, pos_y))
