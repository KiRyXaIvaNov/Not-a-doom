"""
Weapon system and authentic classic Doom Super-Shotgun pixel-art for Not-a-Doom.
Includes seamless solid-underlay rendering (no transparent gaps) and PNG asset loading/saving.
"""
import os
import math
import pygame
from src.core.settings import WIDTH, HEIGHT, HALF_WIDTH, ASSETS_WEAPON_DIR

# ASSETS_WEAPON_DIR imported from settings


def generate_doom_shotgun_sprite(frame_index: int) -> pygame.Surface:
    """
    Generate high-fidelity retro DOOM shotgun sprite.
    Uses solid underlays before drawing facets, guaranteeing ZERO transparent gaps.
    """
    w, h = 80, 80
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    recoil_y = 0
    if frame_index == 1:   # Firing recoil & blast
        recoil_y = -9
    elif frame_index == 2:  # Heavy recoil kick down
        recoil_y = 8
    elif frame_index == 3:  # Pump / recovery
        recoil_y = 3

    BLACK = (18, 18, 22)
    STEEL_HIGHLIGHT = (185, 192, 205)
    STEEL_LIGHT = (140, 146, 160)
    STEEL_MID = (92, 98, 108)
    STEEL_DARK = (60, 64, 72)
    STEEL_SHADOW = (38, 40, 48)
    BREECH_METAL = (48, 50, 58)
    BREECH_DARK = (28, 30, 35)
    WOOD_LIGHT = (165, 88, 45)
    WOOD_MID = (125, 62, 30)
    WOOD_DARK = (80, 38, 18)
    WOOD_SHADOW = (50, 22, 10)
    SKIN_LIGHT = (215, 140, 100)
    SKIN_MID = (175, 108, 75)
    SKIN_SHADOW = (125, 68, 45)

    top_y = 12 + recoil_y
    breech_y = 52 + recoil_y
    top_w = 9
    bot_w = 21

    # Barrels solid underlay
    pygame.draw.polygon(surf, STEEL_MID, [
        (cx - top_w - 2, top_y),
        (cx + top_w + 2, top_y),
        (cx + bot_w + 2, breech_y + 2),
        (cx - bot_w - 2, breech_y + 2)
    ])

    # Wooden forend solid underlay
    wood_top = breech_y + 6
    pygame.draw.polygon(surf, WOOD_MID, [
        (cx - bot_w - 1, wood_top),
        (cx + bot_w + 1, wood_top),
        (cx + bot_w + 7, h),
        (cx - bot_w - 7, h)
    ])

    # Left Barrel highlight & bevel
    pygame.draw.polygon(surf, STEEL_LIGHT, [
        (cx - top_w, top_y + 1),
        (cx - top_w + 4, top_y + 1),
        (cx - bot_w + 8, breech_y),
        (cx - bot_w + 2, breech_y)
    ])
    pygame.draw.polygon(surf, STEEL_HIGHLIGHT, [
        (cx - top_w + 2, top_y + 2),
        (cx - top_w + 4, top_y + 2),
        (cx - bot_w + 6, breech_y - 2),
        (cx - bot_w + 4, breech_y - 2)
    ])
    # Left inner shadow near center rib
    pygame.draw.polygon(surf, STEEL_DARK, [
        (cx - 3, top_y + 1),
        (cx, top_y),
        (cx, breech_y),
        (cx - 7, breech_y)
    ])

    # Right Barrel shading
    pygame.draw.polygon(surf, STEEL_SHADOW, [
        (cx, top_y),
        (cx + 4, top_y + 1),
        (cx + 9, breech_y),
        (cx, breech_y)
    ])
    pygame.draw.polygon(surf, STEEL_DARK, [
        (cx + top_w - 3, top_y + 1),
        (cx + top_w, top_y + 2),
        (cx + bot_w, breech_y),
        (cx + bot_w - 4, breech_y)
    ])

    # Center dividing rib
    pygame.draw.line(surf, BLACK, (cx, top_y), (cx, breech_y), 2)

    # Muzzle tip openings and lip
    pygame.draw.line(surf, BLACK, (cx - top_w - 1, top_y + 2), (cx - 1, top_y), 2)
    pygame.draw.line(surf, BLACK, (cx, top_y), (cx + top_w + 1, top_y + 2), 2)
    pygame.draw.ellipse(surf, BLACK, (cx - top_w + 1, top_y + 1, 6, 3))
    pygame.draw.ellipse(surf, BLACK, (cx + 2, top_y + 1, 6, 3))

    # Outer barrel thick silhouette outlines
    pygame.draw.line(surf, BLACK, (cx - top_w - 2, top_y + 1), (cx - bot_w - 2, breech_y), 2)
    pygame.draw.line(surf, BLACK, (cx + top_w + 2, top_y + 1), (cx + bot_w + 2, breech_y), 2)

    # Breech block
    breech_pts = [
        (cx - bot_w - 2, breech_y),
        (cx, breech_y - 2),
        (cx + bot_w + 2, breech_y),
        (cx + bot_w - 3, breech_y + 12),
        (cx - bot_w + 3, breech_y + 12),
    ]
    pygame.draw.polygon(surf, BREECH_METAL, breech_pts)
    pygame.draw.rect(surf, BREECH_DARK, (cx - 5, breech_y - 1, 10, 9))
    pygame.draw.line(surf, BLACK, (cx, breech_y - 1), (cx, breech_y + 8), 2)
    pygame.draw.polygon(surf, BLACK, breech_pts, 2)

    # Wooden stock
    pygame.draw.polygon(surf, WOOD_LIGHT, [
        (cx - 10, wood_top + 2),
        (cx - 2, wood_top + 2),
        (cx - 4, h),
        (cx - 14, h)
    ])
    pygame.draw.polygon(surf, WOOD_DARK, [
        (cx + 3, wood_top + 2),
        (cx + 10, wood_top + 2),
        (cx + 14, h),
        (cx + 5, h)
    ])
    pygame.draw.line(surf, WOOD_SHADOW, (cx, wood_top), (cx, h), 2)

    # Hands & fingers
    left_hand = [
        (cx - bot_w - 2, breech_y + 6),
        (cx - bot_w - 9, breech_y + 14),
        (cx - bot_w - 11, h),
        (cx - bot_w + 2, h),
        (cx - bot_w + 1, breech_y + 14)
    ]
    pygame.draw.polygon(surf, SKIN_MID, left_hand)
    for offset_y in [12, 19, 26]:
        pygame.draw.circle(surf, SKIN_LIGHT, (cx - bot_w - 5, breech_y + offset_y), 3)
        pygame.draw.line(surf, SKIN_SHADOW, (cx - bot_w - 8, breech_y + offset_y + 3), (cx - bot_w, breech_y + offset_y + 2), 1)
    pygame.draw.lines(surf, BLACK, False, [
        (cx - bot_w - 2, breech_y + 6),
        (cx - bot_w - 9, breech_y + 14),
        (cx - bot_w - 11, h)
    ], 2)

    right_hand = [
        (cx + bot_w + 2, breech_y + 6),
        (cx + bot_w + 9, breech_y + 14),
        (cx + bot_w + 11, h),
        (cx + bot_w - 2, h),
        (cx + bot_w - 1, breech_y + 14)
    ]
    pygame.draw.polygon(surf, SKIN_MID, right_hand)
    for offset_y in [12, 19, 26]:
        pygame.draw.circle(surf, SKIN_LIGHT, (cx + bot_w + 5, breech_y + offset_y), 3)
        pygame.draw.line(surf, SKIN_SHADOW, (cx + bot_w + 8, breech_y + offset_y + 3), (cx + bot_w, breech_y + offset_y + 2), 1)
    pygame.draw.lines(surf, BLACK, False, [
        (cx + bot_w + 2, breech_y + 6),
        (cx + bot_w + 9, breech_y + 14),
        (cx + bot_w + 11, h)
    ], 2)

    # Muzzle Flash (Blast on Frame 1)
    if frame_index == 1:
        fy = top_y
        outer_flash = [
            (cx, fy - 26),
            (cx - 7, fy - 16),
            (cx - 20, fy - 20),
            (cx - 14, fy - 8),
            (cx - 25, fy - 1),
            (cx - 12, fy + 4),
            (cx - 7, fy),
            (cx, fy - 4),
            (cx + 7, fy),
            (cx + 12, fy + 4),
            (cx + 25, fy - 1),
            (cx + 14, fy - 8),
            (cx + 20, fy - 20),
            (cx + 7, fy - 16),
        ]
        pygame.draw.polygon(surf, (255, 130, 20), outer_flash)

        inner_flash = [
            (cx, fy - 19),
            (cx - 5, fy - 12),
            (cx - 14, fy - 14),
            (cx - 9, fy - 5),
            (cx - 16, fy),
            (cx - 5, fy + 2),
            (cx, fy - 2),
            (cx + 5, fy + 2),
            (cx + 16, fy),
            (cx + 9, fy - 5),
            (cx + 14, fy - 14),
            (cx + 5, fy - 12),
        ]
        pygame.draw.polygon(surf, (255, 240, 80), inner_flash)
        pygame.draw.circle(surf, (255, 255, 255), (cx, fy - 6), 5)

    return surf


class Weapon:
    def __init__(self, game):
        self.game = game
        self.scale_factor = 4.8
        self.raw_images = self.load_or_generate_sprites()

        self.scaled_images = [
            pygame.transform.scale(
                img,
                (int(img.get_width() * self.scale_factor), int(img.get_height() * self.scale_factor)),
            )
            for img in self.raw_images
        ]

        self.frame_index = 0
        self.num_frames = len(self.scaled_images)
        self.is_firing = False
        self.fire_timer = 0
        self.frame_duration = 100

        self.bob_timer = 0.0
        self.bob_x = 0
        self.bob_y = 0

    def load_or_generate_sprites(self):
        os.makedirs(ASSETS_WEAPON_DIR, exist_ok=True)
        images = []

        for i in range(4):
            path = os.path.join(ASSETS_WEAPON_DIR, f"shotgun_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
            else:
                img = generate_doom_shotgun_sprite(i)
                pygame.image.save(img, path)
            images.append(img)

        return images

    def fire(self):
        """Trigger blast, recoil, sound effect, and hitscan damage."""
        if not self.is_firing:
            self.is_firing = True
            self.frame_index = 1
            self.fire_timer = pygame.time.get_ticks()
            if hasattr(self.game, "sound"):
                self.game.sound.play_shot()
            if hasattr(self.game, "enemy_manager"):
                self.game.enemy_manager.process_shot(self.game.player)

    def update(self):
        now = pygame.time.get_ticks()

        if self.is_firing:
            # Synchronize visual cadence to audio: flash (120ms), recoil drop (240ms), pump reload (500ms)
            durations = {1: 120, 2: 240, 3: 500}
            cur_duration = durations.get(self.frame_index, self.frame_duration)

            if now - self.fire_timer > cur_duration:
                self.fire_timer = now
                self.frame_index += 1
                if self.frame_index == 3 and hasattr(self.game, "sound"):
                    self.game.sound.play_pump()
                elif self.frame_index >= self.num_frames:
                    self.frame_index = 0
                    self.is_firing = False

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
            self.bob_x = int(math.sin(self.bob_timer) * 9)
            self.bob_y = int(abs(math.cos(self.bob_timer)) * 14)
        else:
            self.bob_x = int(self.bob_x * 0.8)
            self.bob_y = int(self.bob_y * 0.8)

    def draw(self, screen: pygame.Surface):
        current_surf = self.scaled_images[self.frame_index]
        x = HALF_WIDTH - current_surf.get_width() // 2 + self.bob_x
        y = HEIGHT - current_surf.get_height() + self.bob_y + 15
        screen.blit(current_surf, (x, y))
