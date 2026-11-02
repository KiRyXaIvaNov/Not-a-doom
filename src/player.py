"""
Player movement, rotation and collision handling for Not-a-Doom.
"""
import math
import pygame
from src.settings import (
    PLAYER_POS,
    PLAYER_ANGLE,
    PLAYER_SPEED,
    PLAYER_ROT_SPEED,
    MOUSE_SENSITIVITY,
    MOUSE_MAX_REL,
    HALF_WIDTH,
    HALF_HEIGHT,
)


class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.collision_margin = 0.25

    def movement(self):
        """Handle keyboard input for movement with wall sliding and delta time."""
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0.0, 0.0
        speed = PLAYER_SPEED * self.game.delta_time

        keys = pygame.key.get_pressed()

        # Forward / Backward
        if keys[pygame.K_w]:
            dx += cos_a * speed
            dy += sin_a * speed
        if keys[pygame.K_s]:
            dx += -cos_a * speed
            dy += -sin_a * speed

        # Strafe Left / Right
        if keys[pygame.K_a]:
            dx += sin_a * speed
            dy += -cos_a * speed
        if keys[pygame.K_d]:
            dx += -sin_a * speed
            dy += cos_a * speed

        # Check collision with wall sliding
        self.check_wall_collision(dx, dy)

        # Arrow keys rotation
        if keys[pygame.K_LEFT]:
            self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        if keys[pygame.K_RIGHT]:
            self.angle += PLAYER_ROT_SPEED * self.game.delta_time

        # Keep angle in [0, 2*pi]
        self.angle %= math.tau

    def check_wall(self, x: float, y: float) -> bool:
        """Check if grid cell at (x, y) is a solid wall."""
        return self.game.map.is_wall(int(x), int(y))

    def check_wall_collision(self, dx: float, dy: float):
        """Move player with collision box and allow sliding along walls."""
        scale = self.collision_margin

        # Try X movement
        next_x = self.x + dx
        if not (
            self.check_wall(next_x + scale, self.y)
            or self.check_wall(next_x - scale, self.y)
            or self.check_wall(next_x, self.y + scale)
            or self.check_wall(next_x, self.y - scale)
        ):
            self.x = next_x

        # Try Y movement
        next_y = self.y + dy
        if not (
            self.check_wall(self.x, next_y + scale)
            or self.check_wall(self.x, next_y - scale)
            or self.check_wall(self.x + scale, next_y)
            or self.check_wall(self.x - scale, next_y)
        ):
            self.y = next_y

    def mouse_control(self):
        """Rotate camera based on mouse movement and re-center cursor."""
        mx, _ = pygame.mouse.get_pos()
        rel_x = mx - HALF_WIDTH
        if abs(rel_x) > MOUSE_MAX_REL:
            rel_x = MOUSE_MAX_REL if rel_x > 0 else -MOUSE_MAX_REL
        self.angle += rel_x * MOUSE_SENSITIVITY
        pygame.mouse.set_pos((HALF_WIDTH, HALF_HEIGHT))

    def update(self):
        self.movement()
        self.mouse_control()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
