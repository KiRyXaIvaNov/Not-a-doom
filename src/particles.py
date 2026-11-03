"""
Particle system for Not-a-Doom.
Handles 3D blood splatters and wall impact sparks projected with Z-buffer occlusion.
"""
import math
import random
import pygame
from src.settings import (
    WIDTH, HEIGHT, HALF_WIDTH, HALF_HEIGHT,
    NUM_RAYS, SCALE, DELTA_ANGLE, SCREEN_DIST, MAX_DEPTH
)


class Particle:
    """A single 3D particle that moves with physics and projects onto the 2.5D view."""
    def __init__(self, x: float, y: float, z: float, vx: float, vy: float, vz: float,
                 color: tuple[int, int, int], radius: int, life: float, is_blood: bool = False):
        self.x = x
        self.y = y
        self.z = z  # 0.0 = floor, 1.0 = ceiling, 0.5 = chest height
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.color = color
        self.radius = radius
        self.life = life
        self.max_life = life
        self.is_blood = is_blood
        self.on_floor = False

    def update(self, dt: float):
        self.life -= dt
        if self.on_floor:
            # Blood puddle remains on floor
            return

        # Gravity
        self.vz -= 0.0035 * dt

        # Move
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt

        # Floor collision
        if self.z <= 0.05:
            self.z = 0.05
            self.on_floor = True
            self.vx = 0.0
            self.vy = 0.0
            self.vz = 0.0


class ParticleManager:
    """Spawns, updates, and renders all active particles."""
    def __init__(self, game):
        self.game = game
        self.particles: list[Particle] = []

    def emit_blood(self, x: float, y: float, z: float = 0.5, count: int = 14):
        """Spawn energetic blood splatter spraying outwards."""
        blood_shades = [
            (225, 20, 25),
            (190, 15, 20),
            (145, 10, 15),
            (100, 5, 10),
            (255, 45, 45),
        ]
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(0.0015, 0.005)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            vz = random.uniform(0.0005, 0.004)
            color = random.choice(blood_shades)
            rad = random.randint(3, 5)
            life = random.uniform(800, 1600)
            self.particles.append(Particle(x, y, z, vx, vy, vz, color, rad, life, is_blood=True))

    def emit_sparks(self, x: float, y: float, z: float = 0.5, count: int = 6):
        """Spawn bright wall ricochet sparks."""
        spark_colors = [
            (255, 240, 150),
            (255, 200, 80),
            (255, 140, 40),
            (240, 240, 240),
        ]
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(0.003, 0.008)
            vx = math.cos(ang) * spd
            vy = math.sin(ang) * spd
            vz = random.uniform(-0.003, 0.005)
            color = random.choice(spark_colors)
            rad = random.randint(2, 3)
            life = random.uniform(150, 350)
            self.particles.append(Particle(x, y, z, vx, vy, vz, color, rad, life, is_blood=False))

    def update(self):
        dt = self.game.delta_time
        alive = []
        for p in self.particles:
            p.update(dt)
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def render(self, screen: pygame.Surface):
        """Render all visible particles respecting depth buffer occlusion."""
        depth_buffer = self.game.raycasting.depth_buffer
        player = self.game.player

        for p in self.particles:
            dx = p.x - player.x
            dy = p.y - player.y
            dist = math.hypot(dx, dy)
            if dist < 0.25 or dist > MAX_DEPTH:
                continue

            theta = math.atan2(dy, dx)
            delta = (theta - player.angle + math.pi) % math.tau - math.pi

            norm_dist = dist * math.cos(delta)
            if norm_dist <= 0.2:
                continue

            delta_rays = delta / DELTA_ANGLE
            ray_idx = int(NUM_RAYS // 2 + delta_rays)

            if 0 <= ray_idx < NUM_RAYS and norm_dist < depth_buffer[ray_idx]:
                screen_x = int(ray_idx * SCALE)
                # Projected vertical offset based on particle 3D height z
                screen_y = int(HALF_HEIGHT + SCREEN_DIST * (0.5 - p.z) / norm_dist)

                # Size scales inversely with distance
                size = max(2, int(p.radius * SCREEN_DIST / (norm_dist * 550)))

                # Blood fading or darkening
                fade = p.life / p.max_life
                if p.is_blood:
                    c = (
                        int(p.color[0] * max(0.4, fade)),
                        int(p.color[1] * max(0.4, fade)),
                        int(p.color[2] * max(0.4, fade))
                    )
                else:
                    c = p.color

                pygame.draw.circle(screen, c, (screen_x, screen_y), size)
