"""
Enemy system and procedural demonic sprite generator for Not-a-Doom.
Generates animated retro Cacodemon-style 2.5D billboard sprites with pre-baked lightmaps,
AI line-of-sight tracking, acoustic gunshot alerts, wall-sliding pursuit, hitscan damage, and death animations.
"""
import os
import math
import random
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

    angles = [-2.4, -1.9, -1.57, -1.2, -0.7, -2.8, -0.3]
    horn_lengths = [16, 22, 26, 22, 16, 14, 14]

    for ang, base_len in zip(angles, horn_lengths):
        length = base_len + (2 if variant % 2 == 1 else 0)
        base_x = cx + int(math.cos(ang) * (r - 2))
        base_y = cy + int(math.sin(ang) * (r - 2))
        tip_x = cx + int(math.cos(ang) * (r + length))
        tip_y = cy + int(math.sin(ang) * (r + length))

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

    # 1. Horns
    draw_spikes(surf, cx, cy, r, frame_idx)

    # 2. Main spherical body with spherical gradient shading
    body_color = (235, 70, 70) if is_hurt else (190, 25, 30)
    shadow_color = (130, 10, 15) if is_hurt else (85, 10, 15)
    highlight_color = (255, 160, 160) if is_hurt else (235, 80, 70)

    for layer_r in range(r, 0, -1):
        ratio = layer_r / r
        ox = int(cx - (1.0 - ratio) * 10)
        oy = int(cy - (1.0 - ratio) * 10)

        if ratio > 0.8:
            col = shadow_color
        elif ratio > 0.4:
            col = body_color
        else:
            col = highlight_color

        pygame.draw.circle(surf, col, (ox, oy), layer_r)

    # Wrinkles
    wrinkle_color = (70, 8, 12)
    pygame.draw.arc(surf, wrinkle_color, (cx - 28, cy - 30, 56, 20), 0.2, 2.9, 2)
    pygame.draw.arc(surf, wrinkle_color, (cx - 32, cy - 18, 64, 18), 0.3, 2.8, 2)

    # 3. Demonic Eye
    eye_y = cy - 8 + (1 if frame_idx in (1, 2) else 0)
    eye_rx = 13
    eye_ry = 11

    pygame.draw.ellipse(surf, (40, 5, 8), (cx - eye_rx - 3, eye_y - eye_ry - 3, (eye_rx + 3) * 2, (eye_ry + 3) * 2))
    iris_col = (255, 255, 255) if is_hurt else ((0, 230, 220) if frame_idx % 2 == 0 else (50, 255, 180))
    pygame.draw.ellipse(surf, iris_col, (cx - eye_rx, eye_y - eye_ry, eye_rx * 2, eye_ry * 2))

    pupil_w = 4 if not is_hurt else 7
    pupil_h = int(eye_ry * 1.6)
    pupil_col = (10, 15, 25) if not is_hurt else (220, 20, 20)
    pygame.draw.ellipse(surf, pupil_col, (cx - pupil_w // 2, eye_y - pupil_h // 2, pupil_w, pupil_h))
    pygame.draw.circle(surf, (255, 255, 255), (cx - 4, eye_y - 4), 2)

    # 4. Menacing Maw / Teeth
    jaw_open = 4 + (frame_idx % 3) * 3 if not is_hurt else 12
    mouth_w = 42
    mouth_h = 16 + jaw_open
    mouth_y = cy + 8

    mouth_rect = (cx - mouth_w // 2, mouth_y, mouth_w, mouth_h)
    pygame.draw.ellipse(surf, (15, 2, 5), mouth_rect)
    pygame.draw.ellipse(surf, (120, 20, 40), (cx - 14, mouth_y + 4, 28, mouth_h - 6))

    fang_col = (245, 240, 220)
    top_fangs = [-16, -10, -4, 4, 10, 16]
    for fx in top_fangs:
        pts = [
            (cx + fx - 2, mouth_y + 1),
            (cx + fx + 2, mouth_y + 1),
            (cx + fx, mouth_y + 8),
        ]
        pygame.draw.polygon(surf, fang_col, pts)

    bot_fangs = [-13, -7, 0, 7, 13]
    for fx in bot_fangs:
        pts = [
            (cx + fx - 2, mouth_y + mouth_h - 1),
            (cx + fx + 2, mouth_y + mouth_h - 1),
            (cx + fx, mouth_y + mouth_h - 8),
        ]
        pygame.draw.polygon(surf, fang_col, pts)

    return surf


def generate_cacodemon_death_frame(frame_idx: int) -> pygame.Surface:
    """Procedurally generate death collapse & gore puddle frames (128x128)."""
    size = 128
    cx, cy = 64, 66
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    if frame_idx == 0:
        r = 42
        pygame.draw.circle(surf, (150, 20, 25), (cx, cy), r)
        pygame.draw.circle(surf, (220, 40, 50), (cx - 4, cy - 4), r - 6)
        pygame.draw.ellipse(surf, (30, 5, 10), (cx - 24, cy - 20, 48, 40))
        pygame.draw.circle(surf, (255, 100, 100), (cx - 8, cy - 8), 10)
        pygame.draw.line(surf, (20, 0, 0), (cx - 16, cy - 14), (cx, cy), 3)
        for ang in [0.4, 1.2, 2.1, 3.5, 4.2, 5.3]:
            bx = cx + int(math.cos(ang) * (r + 12))
            by = cy + int(math.sin(ang) * (r + 12))
            pygame.draw.circle(surf, (220, 20, 20), (bx, by), 3)

    elif frame_idx == 1:
        r_x, r_y = 44, 26
        flat_cy = cy + 20
        pygame.draw.ellipse(surf, (120, 15, 20), (cx - r_x, flat_cy - r_y, r_x * 2, r_y * 2))
        pygame.draw.ellipse(surf, (180, 25, 30), (cx - r_x + 6, flat_cy - r_y + 4, (r_x - 6) * 2, (r_y - 6) * 2))
        for tx in [-20, -10, 5, 15]:
            pygame.draw.polygon(surf, (230, 220, 200), [(cx + tx, flat_cy - 4), (cx + tx + 4, flat_cy - 4), (cx + tx + 2, flat_cy - 12)])
        pygame.draw.ellipse(surf, (20, 5, 5), (cx - 16, flat_cy - 8, 32, 16))

    else:
        r_x, r_y = 46, 16
        puddle_cy = cy + 38
        pygame.draw.ellipse(surf, (70, 8, 10), (cx - r_x - 2, puddle_cy - r_y - 2, (r_x + 2) * 2, (r_y + 2) * 2))
        pygame.draw.ellipse(surf, (160, 15, 20), (cx - r_x, puddle_cy - r_y, r_x * 2, r_y * 2))
        pygame.draw.ellipse(surf, (210, 30, 35), (cx - 25, puddle_cy - 7, 50, 14))
        pygame.draw.circle(surf, (220, 210, 190), (cx - 18, puddle_cy - 2), 3)
        pygame.draw.circle(surf, (220, 210, 190), (cx + 14, puddle_cy + 1), 2)
        pygame.draw.circle(surf, (240, 230, 200), (cx + 3, puddle_cy - 4), 2)

    return surf


def get_cacodemon_frames() -> list[pygame.Surface]:
    """Load cached Cacodemon animation frames or procedural generate them."""
    ensure_enemy_dir()
    frames = []

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


def get_cacodemon_death_frames() -> list[pygame.Surface]:
    """Load or generate death animation frames."""
    ensure_enemy_dir()
    death_frames = []
    for i in range(3):
        path = os.path.join(ENEMY_SPRITE_DIR, f"demon_death_{i}.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                death_frames.append(img)
                continue
            except Exception:
                pass
        img = generate_cacodemon_death_frame(i)
        pygame.image.save(img, path)
        death_frames.append(img)
    return death_frames


class Enemy:
    """2.5D Demonic billboard enemy with AI line-of-sight tracking and wall-sliding pursuit."""
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

        # AI State Machine: "idle" -> "chase"
        self.state = "idle"
        self.speed = 0.0016         # Floating pursuit speed per ms (~1.6 grid units/sec)
        self.attack_dist = 1.35     # Stops when close enough to attack
        self.size_radius = 0.32     # Collision boundary for sliding against walls
        self.has_alerted = False

        # Death states
        self.is_dying = False
        self.is_dead = False
        self.death_frame_idx = 0
        self.death_timer = 0

        # Load frames
        self.raw_frames = get_cacodemon_frames()
        self.anim_frames = self.raw_frames[:4]
        self.hurt_frame = self.raw_frames[4]
        self.death_frames = get_cacodemon_death_frames()

        self.IMAGE_WIDTH = self.raw_frames[0].get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2

        # Pre-bake lightmaps for all states for O(1) runtime shading
        self.shaded_anim_frames = [self._bake_light_levels(f) for f in self.anim_frames]
        self.shaded_hurt_frame = self._bake_light_levels(self.hurt_frame)
        self.shaded_death_frames = [self._bake_light_levels(f) for f in self.death_frames]

        self.frame_idx = 0
        self.anim_timer = 0
        self.bob_timer = (pos[0] * 3.7 + pos[1] * 2.1) % (2 * math.pi)
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

        if self.is_dying or self.is_dead:
            return self.shaded_death_frames[self.death_frame_idx][idx]
        if self.is_hurt:
            return self.shaded_hurt_frame[idx]
        return self.shaded_anim_frames[self.frame_idx][idx]

    def trigger_chase(self):
        """Wake demon up into active pursuit of player."""
        if not self.alive or self.is_dead or self.is_dying:
            return
        if self.state != "chase":
            self.state = "chase"
            if not self.has_alerted:
                self.has_alerted = True
                if hasattr(self.game, "sound"):
                    self.game.sound.play_demon_alert()

    def check_line_of_sight(self) -> bool:
        """Raycast towards player to determine if unobstructed line of sight exists."""
        player = self.game.player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist < 14.0:
            ang = math.atan2(dy, dx)
            wall_dist, _, _ = self.game.raycasting.cast_single_ray(self.x, self.y, ang)
            if wall_dist >= dist - 0.25:
                self.trigger_chase()
                return True
        return False

    def move_towards_player(self, dt: float):
        """Move towards player with soft repulsion from other demons and wall-sliding."""
        if self.state != "chase" or not self.alive:
            return

        player = self.game.player
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)

        if dist <= self.attack_dist:
            return

        step = self.speed * dt
        vx = (dx / dist) * step
        vy = (dy / dist) * step

        # Gentle demon-demon repulsion to prevent stacking
        for other in self.game.enemy_manager.enemies:
            if other is not self and other.alive:
                odx = self.x - other.x
                ody = self.y - other.y
                odist = math.hypot(odx, ody)
                if 0.01 < odist < 0.75:
                    repulsion = (0.75 - odist) * 0.001 * dt
                    vx += (odx / odist) * repulsion
                    vy += (ody / odist) * repulsion

        # Smooth sliding collision detection with map walls
        r = self.size_radius

        # Check horizontal move
        can_move_x = True
        for ox in (-r, r):
            for oy in (-r, r):
                if self.game.map.is_wall(int(self.x + vx + ox), int(self.y + oy)):
                    can_move_x = False
                    break
        if can_move_x:
            self.x += vx

        # Check vertical move
        can_move_y = True
        for ox in (-r, r):
            for oy in (-r, r):
                if self.game.map.is_wall(int(self.x + ox), int(self.y + vy + oy)):
                    can_move_y = False
                    break
        if can_move_y:
            self.y += vy

    def take_damage(self, amount: int):
        """Handle incoming weapon damage, pain reactions, and death."""
        if not self.alive:
            return
        self.hp -= amount
        self.trigger_chase()

        if self.hp <= 0:
            self.alive = False
            self.is_dying = True
            self.death_frame_idx = 0
            self.death_timer = 0
            if hasattr(self.game, "sound"):
                self.game.sound.play_demon_death()
        else:
            self.is_hurt = True
            self.hurt_timer = 180
            if hasattr(self.game, "sound"):
                self.game.sound.play_demon_pain()

    def update(self):
        """Update floating bobbing, AI pursuit, animation frames, hurt, or death."""
        dt = self.game.delta_time

        # If dying, cycle through collapsing frames
        if self.is_dying:
            self.death_timer += dt
            if self.death_timer >= 140:
                self.death_timer = 0
                if self.death_frame_idx < len(self.death_frames) - 1:
                    self.death_frame_idx += 1
                else:
                    self.is_dying = False
                    self.is_dead = True
            return

        if self.is_dead:
            return

        # AI tracking & movement
        self.check_line_of_sight()
        self.move_towards_player(dt)

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

            if self.is_dead:
                height_shift = int(proj_h * 0.55)
            elif self.is_dying:
                falling_shift = self.shift + (self.death_frame_idx * 0.18)
                height_shift = int(proj_h * falling_shift)
            else:
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
    """Manages spawning, updating, AI alerts, hitscan weapon damage, and rendering all active enemies."""
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

    def alert_all_by_noise(self, source_pos: tuple[float, float], radius: float = 18.0):
        """Alert all alive idle demons within acoustic hearing range when player shoots."""
        for enemy in self.enemies:
            if enemy.alive and enemy.state == "idle":
                dist = math.hypot(enemy.x - source_pos[0], enemy.y - source_pos[1])
                if dist < radius:
                    enemy.trigger_chase()

    def process_shot(self, player):
        """
        Hitscan raycast shotgun blast:
        Fires 12 buckshot pellets with a spread cone.
        Checks wall occlusion and enemy hit radius.
        Emits blood splatters, wall sparks, alerts nearby enemies, and deals distance-based damage.
        """
        # Gunshot sound alerts nearby demons
        self.alert_all_by_noise(player.pos)

        num_pellets = 12
        spread = 0.045
        hits: dict[Enemy, int] = {}

        for _ in range(num_pellets):
            pellet_angle = player.angle + random.uniform(-spread, spread)

            # Raycast distance to nearest wall
            wall_dist, hit_x, hit_y = self.game.raycasting.cast_single_ray(player.x, player.y, pellet_angle)

            # Check collision with alive enemies
            closest_enemy = None
            closest_dist = wall_dist

            for enemy in self.enemies:
                if not enemy.alive:
                    continue

                dx = enemy.x - player.x
                dy = enemy.y - player.y
                dist = math.hypot(dx, dy)

                if dist >= closest_dist or dist < 0.35:
                    continue

                theta = math.atan2(dy, dx)
                diff = (theta - pellet_angle + math.pi) % math.tau - math.pi
                hit_radius_angle = math.atan2(0.42, dist)

                if abs(diff) <= hit_radius_angle:
                    closest_dist = dist
                    closest_enemy = enemy

            if closest_enemy is not None:
                hits[closest_enemy] = hits.get(closest_enemy, 0) + 1
            else:
                if hasattr(self.game, "particle_manager") and wall_dist < MAX_DEPTH:
                    self.game.particle_manager.emit_sparks(hit_x, hit_y, 0.5, count=2)

        # Apply damage and spawn blood for each hit enemy
        for enemy, count in hits.items():
            dmg = count * random.randint(12, 18)
            enemy.take_damage(dmg)
            if hasattr(self.game, "particle_manager"):
                self.game.particle_manager.emit_blood(enemy.x, enemy.y, 0.5, count=count * 3)
