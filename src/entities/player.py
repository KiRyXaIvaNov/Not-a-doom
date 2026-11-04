"""
Player movement, rotation, footsteps and collision handling for Not-a-Doom.
"""
import math
import pygame
from src.core.settings import (
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
        spawn = getattr(self.game.map, 'player_spawn', PLAYER_POS)
        self.x, self.y = spawn[0], spawn[1]
        self.angle = PLAYER_ANGLE
        self.collision_margin = 0.25
        self.step_timer = 0

        # Health & damage system
        self.hp = 100
        self.max_hp = 100
        self.alive = True
        self.damage_alpha = 0.0
        self.heal_alpha = 0.0

    def reset_to_spawn(self):
        """Reset player to the map spawn location, full HP, alive state, and zero overlays."""
        spawn = getattr(self.game.map, 'player_spawn', PLAYER_POS)
        self.x, self.y = spawn[0], spawn[1]
        self.angle = PLAYER_ANGLE
        self.hp = self.max_hp
        self.alive = True
        self.damage_alpha = 0.0
        self.heal_alpha = 0.0
        self.step_timer = 0

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

        # Forward / Backward
        if (
            keys[pygame.K_w]
            or keys[pygame.K_UP]
            or pygame.KSCAN_W in scancodes
            or pygame.KSCAN_UP in scancodes
        ):
            dx += speed * cos_a
            dy += speed * sin_a
        if (
            keys[pygame.K_s]
            or keys[pygame.K_DOWN]
            or pygame.KSCAN_S in scancodes
            or pygame.KSCAN_DOWN in scancodes
        ):
            dx -= speed * cos_a
            dy -= speed * sin_a

        # Strafe Left / Right
        if keys[pygame.K_a] or pygame.KSCAN_A in scancodes:
            dx += speed * sin_a
            dy -= speed * cos_a
        if keys[pygame.K_d] or pygame.KSCAN_D in scancodes:
            dx -= speed * sin_a
            dy += speed * cos_a

        # Keyboard turning (Left / Right arrow keys)
        if keys[pygame.K_LEFT] or pygame.KSCAN_LEFT in scancodes:
            self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        if keys[pygame.K_RIGHT] or pygame.KSCAN_RIGHT in scancodes:
            self.angle += PLAYER_ROT_SPEED * self.game.delta_time

        # Wrap angle around tau
        self.angle %= math.tau

        # Apply displacement with collision sliding
        moved = (dx != 0.0 or dy != 0.0)
        self.check_wall_collision(dx, dy)

        # Footstep audio triggering
        if moved and self.game.mouse_grabbed:
            self.step_timer += self.game.delta_time
            if self.step_timer > 380:
                self.step_timer = 0
                if hasattr(self.game, 'sound'):
                    self.game.sound.play_footstep()
        else:
            self.step_timer = 200

    def is_colliding(self, x: float, y: float) -> bool:
        """Check if bounding box around position collides with any solid walls."""
        margin = self.collision_margin
        return (
            self.game.map.is_wall(int(x - margin), int(y - margin))
            or self.game.map.is_wall(int(x + margin), int(y - margin))
            or self.game.map.is_wall(int(x - margin), int(y + margin))
            or self.game.map.is_wall(int(x + margin), int(y + margin))
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
