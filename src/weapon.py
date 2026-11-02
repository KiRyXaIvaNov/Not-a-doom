"""
Weapon system and procedural retro shotgun animation for Not-a-Doom.
"""
import math
import pygame
from src.settings import WIDTH, HEIGHT, HALF_WIDTH


def create_shotgun_frame(frame_index: int) -> pygame.Surface:
    """Procedurally create retro pixel-art shotgun frames with muzzle flash and recoil."""
    w, h = 320, 280
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    center_x = w // 2
    base_y = 120

    # Frame-specific offsets
    recoil_y = 0
    if frame_index == 1:
        recoil_y = -35  # Kick up on blast
    elif frame_index == 2:
        recoil_y = 15   # Drop down during pump
    elif frame_index == 3:
        recoil_y = 8

    # --- Draw Shotgun Barrels (Double-barrel / Pump steel) ---
    barrel_w = 46
    barrel_h = 130
    barrel_x = center_x - barrel_w // 2
    barrel_top = base_y + recoil_y

    # Outer dark gunmetal outline
    pygame.draw.rect(surf, (20, 22, 25), (barrel_x - 3, barrel_top - 3, barrel_w + 6, barrel_h + 6), border_radius=4)

    # Steel barrels
    pygame.draw.rect(surf, (75, 80, 88), (barrel_x, barrel_top, barrel_w, barrel_h))
    # Left barrel bore
    pygame.draw.rect(surf, (100, 105, 115), (barrel_x + 4, barrel_top + 4, 16, barrel_h - 10))
    # Right barrel bore
    pygame.draw.rect(surf, (85, 90, 100), (barrel_x + 26, barrel_top + 4, 16, barrel_h - 10))
    # Center barrel seam
    pygame.draw.line(surf, (30, 32, 38), (center_x, barrel_top), (center_x, barrel_top + barrel_h), 2)
    # Metallic specular highlight
    pygame.draw.line(surf, (170, 180, 195), (barrel_x + 8, barrel_top + 2), (barrel_x + 8, barrel_top + barrel_h), 2)

    # --- Wooden Stock & Foregrip ---
    wood_y = barrel_top + 70
    # Dark brown wooden grip
    wood_pts = [
        (barrel_x - 12, wood_y),
        (barrel_x + barrel_w + 12, wood_y),
        (barrel_x + barrel_w + 24, h),
        (barrel_x - 24, h),
    ]
    pygame.draw.polygon(surf, (110, 55, 30), wood_pts)
    # Wood grain highlights & shadows
    pygame.draw.polygon(surf, (140, 75, 40), [
        (barrel_x - 6, wood_y + 4),
        (barrel_x + 18, wood_y + 4),
        (barrel_x + 10, h - 10),
        (barrel_x - 18, h - 10),
    ])
    pygame.draw.polygon(surf, (30, 15, 8), wood_pts, 3)

    # --- Doom Guy's Gloved Hands ---
    # Left hand gripping underside
    hand_color = (60, 80, 50)  # Military green-gray glove
    hand_y = wood_y + 40
    pygame.draw.circle(surf, hand_color, (barrel_x - 6, hand_y + 15), 24)
    pygame.draw.circle(surf, (35, 45, 30), (barrel_x - 6, hand_y + 15), 24, 3)

    # Right hand trigger grip
    pygame.draw.circle(surf, hand_color, (barrel_x + barrel_w + 6, hand_y + 35), 26)
    pygame.draw.circle(surf, (35, 45, 30), (barrel_x + barrel_w + 6, hand_y + 35), 26, 3)

    # --- Muzzle Flash (Only on Frame 1 - Firing) ---
    if frame_index == 1:
        flash_y = barrel_top - 5
        # Large outer fiery orange flame burst
        outer_points = [
            (center_x, flash_y - 95),
            (center_x - 55, flash_y - 50),
            (center_x - 85, flash_y - 25),
            (center_x - 30, flash_y + 5),
            (center_x, flash_y - 15),
            (center_x + 30, flash_y + 5),
            (center_x + 85, flash_y - 25),
            (center_x + 55, flash_y - 50),
        ]
        pygame.draw.polygon(surf, (255, 120, 10), outer_points)

        # Bright yellow inner core
        inner_points = [
            (center_x, flash_y - 70),
            (center_x - 35, flash_y - 35),
            (center_x - 50, flash_y - 15),
            (center_x - 18, flash_y),
            (center_x, flash_y - 10),
            (center_x + 18, flash_y),
            (center_x + 50, flash_y - 15),
            (center_x + 35, flash_y - 35),
        ]
        pygame.draw.polygon(surf, (255, 230, 60), inner_points)

        # White-hot central blast
        pygame.draw.circle(surf, (255, 255, 255), (center_x, flash_y - 20), 18)

    return surf


class Weapon:
    def __init__(self, game):
        self.game = game
        self.images = [
            create_shotgun_frame(0),  # Idle
            create_shotgun_frame(1),  # Blast & Flash
            create_shotgun_frame(2),  # Recoil Down
            create_shotgun_frame(3),  # Pump
        ]
        self.scale_factor = 2.0
        self.scaled_images = [
            pygame.transform.scale(
                img,
                (int(img.get_width() * self.scale_factor), int(img.get_height() * self.scale_factor)),
            )
            for img in self.images
        ]

        self.frame_index = 0
        self.num_frames = len(self.scaled_images)
        self.is_firing = False
        self.fire_timer = 0
        self.frame_duration = 90  # Milliseconds per animation frame

        # Weapon bobbing parameters
        self.bob_timer = 0.0
        self.bob_x = 0
        self.bob_y = 0

    def fire(self):
        """Trigger shotgun blast if ready."""
        if not self.is_firing:
            self.is_firing = True
            self.frame_index = 1
            self.fire_timer = pygame.time.get_ticks()

    def update(self):
        """Update animation state and walking bobbing motion."""
        now = pygame.time.get_ticks()

        # Handle shooting sequence
        if self.is_firing:
            if now - self.fire_timer > self.frame_duration:
                self.fire_timer = now
                self.frame_index += 1
                if self.frame_index >= self.num_frames:
                    self.frame_index = 0
                    self.is_firing = False

        # Weapon sway / bobbing while moving
        keys = pygame.key.get_pressed()
        scancodes = self.game.pressed_scancodes

        moving = (
            keys[pygame.K_w]
            or keys[pygame.K_s]
            or keys[pygame.K_a]
            or keys[pygame.K_d]
            or pygame.KSCAN_W in scancodes
            or pygame.KSCAN_S in scancodes
            or pygame.KSCAN_A in scancodes
            or pygame.KSCAN_D in scancodes
            or keys[pygame.K_UP]
            or keys[pygame.K_DOWN]
        )

        if moving and self.game.mouse_grabbed:
            self.bob_timer += 0.008 * self.game.delta_time
            self.bob_x = int(math.sin(self.bob_timer) * 8)
            self.bob_y = int(abs(math.cos(self.bob_timer)) * 12)
        else:
            # Smoothly damp bobbing back to center
            self.bob_x = int(self.bob_x * 0.8)
            self.bob_y = int(self.bob_y * 0.8)

    def draw(self, screen: pygame.Surface):
        """Draw shotgun centered at bottom of viewport with bobbing offset."""
        current_surf = self.scaled_images[self.frame_index]
        x = HALF_WIDTH - current_surf.get_width() // 2 + self.bob_x
        y = HEIGHT - current_surf.get_height() + self.bob_y + 30
        screen.blit(current_surf, (x, y))
