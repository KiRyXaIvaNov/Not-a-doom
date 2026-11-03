"""
Player movement, rotation, footsteps and collision handling for Not-a-Doom.
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
        self.step_timer = 0

        # Health & damage system
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.damage_alpha = 0.0
        self.heal_alpha = 0.0

    def take_damage(self, amount: int):
        """Apply damage, trigger pain audio and screen flash."""
        if not self.alive:
            return
        self.hp = max(0, self.hp - amount)
        self.damage_alpha = 140.0  # Intense red flash
        if hasattr(self.game, 'sound'):
            self.game.sound.play_player_hurt()
        if self.hp <= 0:
            self.alive = False

    def heal(self, amount: int) -> bool:
        """Heal player by amount up to max_hp. Returns True if healed."""
        if not self.alive or self.hp >= self.max_hp:
            return False
        self.hp = min(self.max_hp, self.hp + amount)
        self.heal_alpha = 120.0
        return True

    def movement(self):
        """Handle input for movement with wall sliding, supporting both EN/RU keyboard layouts and Arrows."""
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0.0, 0.0
        speed = PLAYER_SPEED * self.game.delta_time

        keys = pygame.key.get_pressed()
        scancodes = self.game.pressed_scancodes

        def pressed(keycode, scancode):
            return (keycode < len(keys) and keys[keycode]) or (scancode in scancodes)

        # Forward / Backward (W, Up arrow, S, Down arrow)
        if pressed(pygame.K_w, pygame.KSCAN_W) or pressed(pygame.K_UP, pygame.KSCAN_UP):
            dx += cos_a
            dy += sin_a
        if pressed(pygame.K_s, pygame.KSCAN_S) or pressed(pygame.K_DOWN, pygame.KSCAN_DOWN):
            dx += -cos_a
            dy += -sin_a

        # Strafe Left / Right (A, D)
        if pressed(pygame.K_a, pygame.KSCAN_A):
            dx += sin_a
            dy += -cos_a
        if pressed(pygame.K_d, pygame.KSCAN_D):
            dx += -sin_a
            dy += cos_a

        # Normalize movement vector to eliminate diagonal speed boost
        if dx != 0.0 or dy != 0.0:
            length = math.hypot(dx, dy)
            dx = (dx / length) * speed
            dy = (dy / length) * speed

        # Check collision with wall sliding
        self.check_wall_collision(dx, dy)

        # Soft rhythmic footstep audio when walking
        if (dx != 0.0 or dy != 0.0) and hasattr(self.game, "sound"):
            self.step_timer += self.game.delta_time
            if self.step_timer >= 440:
                self.step_timer = 0
                self.game.sound.play_step()
        else:
            self.step_timer = 380

        # Arrow keys rotation (Left / Right) with responsive rot speed
        if pressed(pygame.K_LEFT, pygame.KSCAN_LEFT):
            self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        if pressed(pygame.K_RIGHT, pygame.KSCAN_RIGHT):
            self.angle += PLAYER_ROT_SPEED * self.game.delta_time

        # Keep angle in [0, 2*pi]
        self.angle %= math.tau

    def check_wall(self, x: float, y: float) -> bool:
        """Check if grid cell at (x, y) is a solid wall."""
        return self.game.map.is_wall(int(x), int(y))

    def is_colliding(self, x: float, y: float) -> bool:
        """Check if player bounding box intersects any solid wall."""
        m = self.collision_margin
        return (
            self.check_wall(x - m, y - m)
            or self.check_wall(x + m, y - m)
            or self.check_wall(x - m, y + m)
            or self.check_wall(x + m, y + m)
        )

    def check_wall_collision(self, dx: float, dy: float):
        """Move player with collision box and allow sliding along walls."""
        if not self.is_colliding(self.x + dx, self.y):
            self.x += dx
        if not self.is_colliding(self.x, self.y + dy):
            self.y += dy

    def mouse_control(self):
        """Rotate camera based on mouse movement and re-center cursor when grabbed."""
        if not self.game.mouse_grabbed:
            return
        mx, _ = pygame.mouse.get_pos()
        rel_x = mx - HALF_WIDTH
        if abs(rel_x) > MOUSE_MAX_REL:
            rel_x = MOUSE_MAX_REL if rel_x > 0 else -MOUSE_MAX_REL
        self.angle += rel_x * MOUSE_SENSITIVITY
        pygame.mouse.set_pos((HALF_WIDTH, HALF_HEIGHT))

    def update(self):
        if self.game.mouse_grabbed:
            self.movement()
            self.mouse_control()

        # Fade out red damage overlay
        if self.damage_alpha > 0.0:
            self.damage_alpha = max(0.0, self.damage_alpha - self.game.delta_time * 0.45)

        # Fade out green heal overlay
        if self.heal_alpha > 0.0:
            self.heal_alpha = max(0.0, self.heal_alpha - self.game.delta_time * 0.45)

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)
