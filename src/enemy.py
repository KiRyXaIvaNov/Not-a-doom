"""
Enemy system and procedural demonic sprite generator for Not-a-Doom.
Generates animated retro Cacodemon-style 2.5D billboard sprites with pre-baked lightmaps.
"""
import os
import math
import pygame
from src.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT, NUM_RAYS,
    SCALE, DELTA_ANGLE, SCREEN_DIST, MAX_DEPTH
)

NUM_ENEMY_LIGHTS = 8
ENEMY_SPRITE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sprites", "enemy"))


def ensure_enemy_dir():
    os.makedirs(ENEMY_SPRITE_DIR, exist_ok=True)


def draw_spikes(surface: pygame.Surface, cx: int, cy: int, r: int, variant: int):
    """Draw demonic bone horns around the perimeter."""
    horn_color = (220, 210, 185)
    horn_shadow = (130, 120, 95)
    horn_tip = (245, 240, 220)

    # Horn angles: top-left, top, top-right, left-cheek, right-cheek
    angles = [-2.4, -1.9, -1.57, -1.2, -0.7, -2.8, -0.3]
    horn_lengths = [16, 22, 26, 22, 16, 14, 14]

    for ang, base_len in zip(angles, horn_lengths):
        length = base_len + (2 if variant % 2 == 1 else 0)
        base_x = cx + int(math.cos(ang) * (r - 2))
        base_y = cy + int(math.sin(ang) * (r - 2))
        tip_x = cx + int(math.cos(ang) * (r + length))
        tip_y = cy + int(math.sin(ang) * (r + length))

        # Perpendicular vector for horn width
        px = -math.sin(ang) * 4
        py = math.cos(ang) * 4

        pts = [
            (int(base_x - px), int(base_y - py)),
            (int(tip_x), int(tip_y)),
            (int(base_x + px), int(base_y + py)),
        ]
        pygame.draw.polygon(surface, horn_shadow, pts)
        pygame.draw.line(surface, horn_color, (base_x, base_y), (tip_x, tip_y), 2)
        pygame.draw.circle(surface, horn_tip, (int(tip_x), int(tip_y)), 1)


def generate_cacodemon_frame(frame_idx: int, is_hurt: bool = False) -> pygame.Surface:
    """Procedurally create classic retro DOOM Cacodemon pixel art frame (128x128)."""
    size = 128
    cx, cy = 64, 66
    r = 38
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # 1. Horns (drawn behind body)
    draw_spikes(surf, cx, cy, r, frame_idx)

    # 2. Main spherical body with spherical gradient shading
    body_color = (235, 70, 70) if is_hurt else (190, 25, 30)
    shadow_color = (130, 10, 15) if is_hurt else (85, 10, 15)
    highlight_color = (255, 160, 160) if is_hurt else (235, 80, 70)

    # Shaded body layers
    for layer_r in range(r, 0, -1):
        ratio = layer_r / r
        # Light source from top-left
        ox = int(cx - (1.0 - ratio) * 10)
        oy = int(cy - (1.0 - ratio) * 10)

        if ratio > 0.8:
            col = shadow_color
        elif ratio > 0.4:
            col = body_color
        else:
            col = highlight_color

        pygame.draw.circle(surf, col, (ox, oy), layer_r)

    # Leathery demonic wrinkles / bumps
    wrinkle_color = (70, 8, 12)
    pygame.draw.arc(surf, wrinkle_color, (cx - 28, cy - 30, 56, 20), 0.2, 2.9, 2)
    pygame.draw.arc(surf, wrinkle_color, (cx - 32, cy - 18, 64, 18), 0.3, 2.8, 2)

    # 3. Demonic Eye in center
    eye_y = cy - 8 + (1 if frame_idx in (1, 2) else 0)
    eye_rx = 13
    eye_ry = 11

    # Eye socket
    pygame.draw.ellipse(surf, (40, 5, 8), (cx - eye_rx - 3, eye_y - eye_ry - 3, (eye_rx + 3) * 2, (eye_ry + 3) * 2))

    # Glowing Iris (cyan-blue to poisonous green)
    iris_col = (255, 255, 255) if is_hurt else ((0, 230, 220) if frame_idx % 2 == 0 else (50, 255, 180))
    pygame.draw.ellipse(surf, iris_col, (cx - eye_rx, eye_y - eye_ry, eye_rx * 2, eye_ry * 2))

    # Slit pupil
    pupil_w = 4 if not is_hurt else 7
    pupil_h = int(eye_ry * 1.6)
    pupil_col = (10, 15, 25) if not is_hurt else (220, 20, 20)
    pygame.draw.ellipse(surf, pupil_col, (cx - pupil_w // 2, eye_y - pupil_h // 2, pupil_w, pupil_h))

    # Eye specular glint
    pygame.draw.circle(surf, (255, 255, 255), (cx - 4, eye_y - 4), 2)

    # 4. Menacing Maw / Teeth
    jaw_open = 4 + (frame_idx % 3) * 3 if not is_hurt else 12
    mouth_w = 42
    mouth_h = 16 + jaw_open
    mouth_y = cy + 8

    # Dark mouth cavity
    mouth_rect = (cx - mouth_w // 2, mouth_y, mouth_w, mouth_h)
    pygame.draw.ellipse(surf, (15, 2, 5), mouth_rect)
    # Inner throat glow
    pygame.draw.ellipse(surf, (120, 20, 40), (cx - 14, mouth_y + 4, 28, mouth_h - 6))

    # Sharp triangular fangs
    fang_col = (245, 240, 220)
    # Upper fangs (pointing down)
    top_fangs = [-16, -10, -4, 4, 10, 16]
    for fx in top_fangs:
        pts = [
            (cx + fx - 2, mouth_y + 1),
            (cx + fx + 2, mouth_y + 1),
            (cx + fx, mouth_y + 8),
        ]
        pygame.draw.polygon(surf, fang_col, pts)

    # Lower fangs (pointing up)
    bot_fangs = [-13, -7, 0, 7, 13]
    for fx in bot_fangs:
        pts = [
            (cx + fx - 2, mouth_y + mouth_h - 1),
            (cx + fx + 2, mouth_y + mouth_h - 1),
            (cx + fx, mouth_y + mouth_h - 8),
        ]
        pygame.draw.polygon(surf, fang_col, pts)

    return surf


def get_cacodemon_frames() -> list[pygame.Surface]:
    """Load cached Cacodemon animation frames or procedural generate them."""
    ensure_enemy_dir()
    frames = []

    # 4 floating animation frames
    for i in range(4):
        path = os.path.join(ENEMY_SPRITE_DIR, f"demon_{i}.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                frames.append(img)
                continue
            except Exception:
                pass
        img = generate_cacodemon_frame(i, is_hurt=False)
        pygame.image.save(img, path)
        frames.append(img)

    # Hurt frame
    hurt_path = os.path.join(ENEMY_SPRITE_DIR, "demon_hurt.png")
    if os.path.exists(hurt_path):
        try:
            hurt_img = pygame.image.load(hurt_path).convert_alpha()
            frames.append(hurt_img)
            return frames
        except Exception:
            pass
    hurt_img = generate_cacodemon_frame(0, is_hurt=True)
    pygame.image.save(hurt_img, hurt_path)
    frames.append(hurt_img)

    return frames


class Enemy:
    """2.5D Demonic billboard enemy with floating animation, health, and lightmaps."""
    def __init__(self, game, pos: tuple[float, float], name: str = "cacodemon", scale: float = 0.85, shift: float = 0.05):
        self.game = game
        self.x, self.y = pos
        self.name = name
        self.scale = scale
        self.shift = shift
        self.hp = 100
        self.alive = True
        self.is_hurt = False
        self.hurt_timer = 0

        # Animation states
        self.raw_frames = get_cacodemon_frames()
        self.anim_frames = self.raw_frames[:4]
        self.hurt_frame = self.raw_frames[4]

        self.IMAGE_WIDTH = self.raw_frames[0].get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2

        # Pre-bake lightmaps for all animation frames for O(1) runtime shading
        self.shaded_anim_frames = [self._bake_light_levels(f) for f in self.anim_frames]
        self.shaded_hurt_frame = self._bake_light_levels(self.hurt_frame)

        self.frame_idx = 0
        self.anim_timer = 0
        self.bob_timer = (pos[0] * 3.7 + pos[1] * 2.1) % (2 * math.pi)  # Desynchronized floating phase
        self.dist = 0.0
        self.screen_x = 0

    def _bake_light_levels(self, base_image: pygame.Surface) -> list[pygame.Surface]:
        levels = []
        for i in range(NUM_ENEMY_LIGHTS):
            ratio = i / (NUM_ENEMY_LIGHTS - 1)
            brightness = max(0.15, ratio)
            val = int(255 * brightness)
            shaded = base_image.copy()
            shaded.fill((val, val, val), special_flags=pygame.BLEND_MULT)
            levels.append(shaded)
        return levels

    def get_shaded_image(self, brightness: float) -> pygame.Surface:
        idx = int(brightness * (NUM_ENEMY_LIGHTS - 1))
        idx = max(0, min(NUM_ENEMY_LIGHTS - 1, idx))
        if self.is_hurt:
            return self.shaded_hurt_frame[idx]
        return self.shaded_anim_frames[self.frame_idx][idx]

    def take_damage(self, amount: int):
        """Handle incoming weapon damage."""
        if not self.alive:
            return
        self.hp -= amount
        self.is_hurt = True
        self.hurt_timer = 180  # Hurt animation duration in ms
        if self.hp <= 0:
            self.alive = False

    def update(self):
        """Update floating bobbing, animation frames, and hurt status."""
        dt = self.game.delta_time

        # Floating bobbing
        self.bob_timer += dt * 0.003
        if self.bob_timer > math.tau:
            self.bob_timer -= math.tau

        # Hurt timer recovery
        if self.is_hurt:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.is_hurt = False

        # Animation frames cycling
        self.anim_timer += dt
        if self.anim_timer >= 180:
            self.anim_timer = 0
            self.frame_idx = (self.frame_idx + 1) % len(self.anim_frames)

    def get_projection_data(self):
        """Calculate polar angle, distance, screen X position and scale."""
        if not self.alive:
            return None

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
            max_size = int(HEIGHT * 1.5)
            proj_w = int(min(max_size, int(proj)))
            proj_h = int(min(max_size, int(proj)))

            half_proj_w = proj_w // 2

            # Smooth demonic floating bobbing above ground
            float_offset = math.sin(self.bob_timer) * 0.08
            height_shift = int(proj_h * (self.shift + float_offset))

            pos_x = int(self.screen_x - half_proj_w)
            pos_y = int(HALF_HEIGHT - proj_h // 2 + height_shift)

            depth_factor = 1.0 / (1.0 + norm_dist * norm_dist * 0.035)
            brightness = max(0.15, min(1.0, depth_factor))
            shaded_img = self.get_shaded_image(brightness)

            return (norm_dist, shaded_img, (pos_x, pos_y), (proj_w, proj_h))
        return None


class EnemyManager:
    """Manages spawning, updating, and rendering all active enemies."""
    def __init__(self, game):
        self.game = game
        self.enemies: list[Enemy] = []
        self.setup_enemies()

    def setup_enemies(self):
        """Spawn demons in labyrinth rooms."""
        self.enemies = [
            # Near central courtyard junction
            Enemy(self.game, (7.5, 4.5), name="cacodemon", scale=0.85, shift=0.08),
            # Inside right tech hall
            Enemy(self.game, (9.5, 3.5), name="cacodemon", scale=0.85, shift=0.08),
            # Deep in pillar corridor
            Enemy(self.game, (13.5, 10.5), name="cacodemon", scale=0.85, shift=0.08),
        ]

    def update(self):
        for enemy in self.enemies:
            enemy.update()
