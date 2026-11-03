"""
Projectile system for Not-a-Doom.
Handles demonic fireballs, projectile flight physics, collision, and 2.5D billboard projection.
"""
import os
import math
import random
import pygame
from src.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT,
    NUM_RAYS, SCALE, DELTA_ANGLE, SCREEN_DIST, MAX_DEPTH
)

ASSETS_FIREBALL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sprites", "fireball.png"))


def get_fireball_surface() -> pygame.Surface:
    """Load cached fireball sprite or generate procedural plasma ball."""
    if os.path.exists(ASSETS_FIREBALL_PATH):
        try:
            return pygame.image.load(ASSETS_FIREBALL_PATH).convert_alpha()
        except Exception:
            pass

    size = 64
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    # Fiery plasma gradients
    for r in range(24, 0, -2):
        ratio = r / 24
        if ratio > 0.7:
            col = (210, 30, 10, int(200 * (1.0 - ratio)))
        elif ratio > 0.4:
            col = (255, 130, 20)
        elif ratio > 0.2:
            col = (255, 215, 60)
        else:
            col = (255, 255, 240)
        pygame.draw.circle(surf, col, (cx, cy), r)

    # Fiery perimeter sparks
    for ang in [0.3, 1.1, 1.9, 2.8, 3.7, 4.6, 5.5]:
        tx = cx + int(math.cos(ang) * 22)
        ty = cy + int(math.sin(ang) * 22)
        pygame.draw.circle(surf, (255, 110, 15), (tx, ty), 3)

    os.makedirs(os.path.dirname(ASSETS_FIREBALL_PATH), exist_ok=True)
    pygame.image.save(surf, ASSETS_FIREBALL_PATH)
    return surf


class Fireball:
    """Demonic projectile that flies through 3D space and impacts walls or the player."""
    def __init__(self, game, pos: tuple[float, float, float], target_pos: tuple[float, float, float], speed: float = 0.0055):
        self.game = game
        self.x, self.y, self.z = pos
        self.base_image = get_fireball_surface()
        self.IMAGE_WIDTH = self.base_image.get_width()
        self.IMAGE_HALF_WIDTH = self.IMAGE_WIDTH // 2

        # Direction vector
        dx = target_pos[0] - self.x
        dy = target_pos[1] - self.y
        dist_2d = math.hypot(dx, dy) or 1.0

        self.vx = (dx / dist_2d) * speed
        self.vy = (dy / dist_2d) * speed
        self.vz = ((target_pos[2] - self.z) / dist_2d) * speed

        self.alive = True
        self.life = 4000.0  # Max flight time (4 seconds)
        self.trail_timer = 0.0
        self.damage = random.randint(18, 26)

    def update(self):
        dt = self.game.delta_time
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return

        # Move
        new_x = self.x + self.vx * dt
        new_y = self.y + self.vy * dt
        self.z += self.vz * dt

        # Spawn flame trail particles
        self.trail_timer += dt
        if self.trail_timer >= 45.0:
            self.trail_timer = 0.0
            if hasattr(self.game, 'particle_manager'):
                self.game.particle_manager.emit_sparks(self.x, self.y, self.z, count=1)

        # Wall collision
        if self.game.map.is_wall(int(new_x), int(new_y)):
            self.alive = False
            if hasattr(self.game, 'particle_manager'):
                self.game.particle_manager.emit_sparks(new_x, new_y, self.z, count=8)
            return

        self.x = new_x
        self.y = new_y

        # Player collision
        player = self.game.player
        p_dist = math.hypot(self.x - player.x, self.y - player.y)
        if p_dist < 0.42 and player.alive:
            self.alive = False
            player.take_damage(self.damage)
            if hasattr(self.game, 'particle_manager'):
                self.game.particle_manager.emit_sparks(self.x, self.y, self.z, count=10)

    def get_projection_data(self):
        """Calculate 2.5D projection for billboard rendering."""
        if not self.alive:
            return None

        player = self.game.player
        dx = self.x - player.x
        dy = self.y - player.y
        theta = math.atan2(dy, dx)

        delta = theta - player.angle
        if (dx > 0 and player.angle > math.pi) or (dx < 0 and dy < 0):
            delta += math.tau

        delta_rays = delta / DELTA_ANGLE
        screen_x = int((NUM_RAYS // 2 + delta_rays) * SCALE)

        dist = math.hypot(dx, dy)
        norm_dist = dist * math.cos(delta)

        if -self.IMAGE_HALF_WIDTH < screen_x < (WIDTH + self.IMAGE_HALF_WIDTH) and 0.25 < norm_dist < MAX_DEPTH:
            proj = SCREEN_DIST / norm_dist * 0.45
            proj_w = max(4, int(proj))
            proj_h = max(4, int(proj))

            half_proj_w = proj_w // 2
            # Fireball height shift based on 3D z
            z_offset = (0.5 - self.z)
            height_shift = int(SCREEN_DIST * z_offset / norm_dist)

            pos_x = int(screen_x - half_proj_w)
            pos_y = int(HALF_HEIGHT - proj_h // 2 + height_shift)

            # Fireballs emit their own light (always bright)
            return (norm_dist, self.base_image, (pos_x, pos_y), (proj_w, proj_h))
        return None


class ProjectileManager:
    """Manages active demonic projectiles."""
    def __init__(self, game):
        self.game = game
        self.projectiles: list[Fireball] = []

    def shoot_fireball(self, from_pos: tuple[float, float, float], to_pos: tuple[float, float, float]):
        """Cast a burning fireball from demon towards target."""
        fb = Fireball(self.game, from_pos, to_pos)
        self.projectiles.append(fb)
        if hasattr(self.game, 'sound'):
            self.game.sound.play_fireball_launch()

    def update(self):
        alive_projectiles = []
        for p in self.projectiles:
            p.update()
            if p.alive:
                alive_projectiles.append(p)
        self.projectiles = alive_projectiles
