"""
Weapon system and authentic classic Doom Super-Shotgun pixel-art for Not-a-Doom.
Includes seamless solid-underlay rendering (no transparent gaps) and PNG asset loading/saving.
"""
import os
import math
import pygame
from src.core.settings import (
    WIDTH,
    HEIGHT,
    HALF_WIDTH,
    ASSETS_WEAPON_DIR,
    SHOTGUN_MAX_RANGE,
    SHOTGUN_MIN_DAMAGE_RATIO,
    SHOTGUN_PELLETS,
    SHOTGUN_SPREAD,
    SHOTGUN_MIN_DAMAGE,
    SHOTGUN_MAX_DAMAGE,
    PISTOL_MAX_RANGE,
    PISTOL_MIN_DAMAGE_RATIO,
    PISTOL_PELLETS,
    PISTOL_SPREAD,
    PISTOL_MIN_DAMAGE,
    PISTOL_MAX_DAMAGE,
)

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


def generate_doom_pistol_sprite(frame_index: int) -> pygame.Surface:
    """
    Generate high-fidelity retro DOOM Pistol sprite (80x80).
    Frames:
      0: Idle aiming forward
      1: Firing blast with bright muzzle starburst & slide kick
      2: Recoil kick upward, slide blown back
      3: Slide returning forward, recovering to rest
    """
    w, h = 80, 80
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    recoil_y = 0
    if frame_index == 1:    # Blast & initial kick
        recoil_y = -7
    elif frame_index == 2:  # High recoil kick, slide back
        recoil_y = -11
    elif frame_index == 3:  # Slide cycling forward / recovery
        recoil_y = -4

    # Color Palette: Classic DOOM Steel, Polymer, and Combat Glove
    BLACK = (16, 17, 20)
    STEEL_LIGHT = (160, 168, 185)
    STEEL_HIGHLIGHT = (210, 218, 235)
    STEEL_MID = (100, 108, 122)
    STEEL_DARK = (62, 66, 76)
    STEEL_SHADOW = (38, 40, 48)

    GRIP_DARK = (24, 25, 28)
    GRIP_MID = (44, 46, 52)

    # Leather Combat Glove (Doomguy brown/tan leather with knuckle reinforcement)
    GLOVE_BASE = (145, 95, 55)
    GLOVE_LIGHT = (185, 130, 85)
    GLOVE_DARK = (95, 60, 35)
    GLOVE_SHADOW = (60, 38, 22)

    # Sleeve / Armor (Doom marine olive/gray combat fatigues)
    ARMOR_GREEN = (65, 78, 60)
    ARMOR_DARK = (42, 52, 38)

    # Gun geometry coordinates
    gun_top = 22 + recoil_y
    gun_bot = 42 + recoil_y
    gun_w = 7   # half width of slide (14px wide)

    # 1. Arm and wrist solid underlay
    arm_pts = [
        (cx - 16, h),
        (cx - 10, gun_bot + 16),
        (cx + 12, gun_bot + 16),
        (cx + 22, h)
    ]
    pygame.draw.polygon(surf, ARMOR_DARK, arm_pts)
    pygame.draw.polygon(surf, ARMOR_GREEN, [
        (cx - 14, h),
        (cx - 9, gun_bot + 18),
        (cx + 8, gun_bot + 18),
        (cx + 18, h)
    ])

    # 2. Glove hand holding grip
    glove_pts = [
        (cx - 9, gun_bot - 2),
        (cx + 8, gun_bot - 2),
        (cx + 12, gun_bot + 18),
        (cx - 12, gun_bot + 18)
    ]
    pygame.draw.polygon(surf, GLOVE_SHADOW, glove_pts)
    pygame.draw.polygon(surf, GLOVE_BASE, [
        (cx - 8, gun_bot),
        (cx + 7, gun_bot),
        (cx + 10, gun_bot + 16),
        (cx - 10, gun_bot + 16)
    ])

    # Knuckle guard / strap on glove
    pygame.draw.rect(surf, GLOVE_DARK, (cx - 7, gun_bot + 6, 14, 5))
    pygame.draw.line(surf, GLOVE_LIGHT, (cx - 7, gun_bot + 6), (cx + 6, gun_bot + 6), 1)

    # Fingers wrapped around grip
    for i in range(3):
        fy = gun_bot + 2 + i * 4
        pygame.draw.ellipse(surf, GLOVE_LIGHT, (cx + 3, fy, 7, 4))
        pygame.draw.ellipse(surf, GLOVE_DARK, (cx + 3, fy, 7, 4), 1)

    # Thumb on left side
    pygame.draw.ellipse(surf, GLOVE_LIGHT, (cx - 9, gun_bot + 1, 6, 8))
    pygame.draw.ellipse(surf, GLOVE_DARK, (cx - 9, gun_bot + 1, 6, 8), 1)

    # 3. Pistol Grip underlay & frame
    grip_pts = [
        (cx - 6, gun_bot - 4),
        (cx + 5, gun_bot - 4),
        (cx + 6, gun_bot + 14),
        (cx - 7, gun_bot + 14)
    ]
    pygame.draw.polygon(surf, GRIP_DARK, grip_pts)
    pygame.draw.polygon(surf, GRIP_MID, [
        (cx - 5, gun_bot - 3),
        (cx + 4, gun_bot - 3),
        (cx + 5, gun_bot + 12),
        (cx - 6, gun_bot + 12)
    ])

    # 4. Slide & Barrel (Solid Underlay)
    slide_pts = [
        (cx - gun_w - 1, gun_top - 1),
        (cx + gun_w + 1, gun_top - 1),
        (cx + gun_w + 1, gun_bot + 1),
        (cx - gun_w - 1, gun_bot + 1)
    ]
    pygame.draw.polygon(surf, STEEL_SHADOW, slide_pts)

    # Slide main body
    pygame.draw.rect(surf, STEEL_MID, (cx - gun_w, gun_top, gun_w * 2, gun_bot - gun_top))

    # Left slide bevel / highlight
    pygame.draw.rect(surf, STEEL_LIGHT, (cx - gun_w, gun_top, 4, gun_bot - gun_top))
    pygame.draw.line(surf, STEEL_HIGHLIGHT, (cx - gun_w + 1, gun_top + 1), (cx - gun_w + 1, gun_bot - 1), 1)

    # Top slide highlight line
    pygame.draw.line(surf, STEEL_HIGHLIGHT, (cx - gun_w + 1, gun_top), (cx + gun_w - 1, gun_top), 1)

    # Right slide shadow
    pygame.draw.rect(surf, STEEL_DARK, (cx + gun_w - 4, gun_top, 4, gun_bot - gun_top))
    pygame.draw.line(surf, STEEL_SHADOW, (cx + gun_w - 1, gun_top), (cx + gun_w - 1, gun_bot), 1)

    # Slide serrations (rear cocking grooves)
    for sy in range(gun_bot - 8, gun_bot - 2, 2):
        pygame.draw.line(surf, BLACK, (cx - gun_w + 1, sy), (cx + gun_w - 2, sy), 1)
        pygame.draw.line(surf, STEEL_LIGHT, (cx - gun_w + 1, sy + 1), (cx + gun_w - 2, sy + 1), 1)

    # Ejection Port / Chamber
    if frame_index in (1, 2):
        pygame.draw.rect(surf, BLACK, (cx - 2, gun_top + 4, 6, 7))
        pygame.draw.rect(surf, (210, 175, 50), (cx - 1, gun_top + 5, 4, 5))
    else:
        pygame.draw.rect(surf, STEEL_DARK, (cx - 2, gun_top + 4, 6, 6))
        pygame.draw.line(surf, BLACK, (cx - 2, gun_top + 4), (cx + 4, gun_top + 4), 1)

    # Front Sight Blade
    pygame.draw.rect(surf, BLACK, (cx - 1, gun_top - 3, 3, 3))
    pygame.draw.line(surf, STEEL_LIGHT, (cx, gun_top - 3), (cx, gun_top - 1), 1)

    # Rear Sight Notches
    pygame.draw.rect(surf, BLACK, (cx - 5, gun_bot - 3, 3, 3))
    pygame.draw.rect(surf, BLACK, (cx + 3, gun_bot - 3, 3, 3))

    # Barrel Muzzle Hole (Dark ellipse at top tip)
    pygame.draw.ellipse(surf, BLACK, (cx - 3, gun_top - 1, 6, 3))

    # Outer crisp pixel outlines
    pygame.draw.line(surf, BLACK, (cx - gun_w - 1, gun_top), (cx - gun_w - 1, gun_bot), 1)
    pygame.draw.line(surf, BLACK, (cx + gun_w + 1, gun_top), (cx + gun_w + 1, gun_bot), 1)
    pygame.draw.line(surf, BLACK, (cx - gun_w, gun_top - 1), (cx + gun_w, gun_top - 1), 1)

    # 5. Muzzle Flash (Frame 1 only)
    if frame_index == 1:
        fy = gun_top - 2
        outer_flash = [
            (cx, fy - 22),
            (cx - 5, fy - 14),
            (cx - 16, fy - 16),
            (cx - 11, fy - 7),
            (cx - 20, fy - 1),
            (cx - 10, fy + 3),
            (cx - 5, fy),
            (cx, fy - 3),
            (cx + 5, fy),
            (cx + 10, fy + 3),
            (cx + 20, fy - 1),
            (cx + 11, fy - 7),
            (cx + 16, fy - 16),
            (cx + 5, fy - 14),
        ]
        pygame.draw.polygon(surf, (255, 140, 25), outer_flash)

        inner_flash = [
            (cx, fy - 15),
            (cx - 4, fy - 10),
            (cx - 10, fy - 11),
            (cx - 7, fy - 4),
            (cx - 12, fy),
            (cx - 4, fy + 2),
            (cx, fy - 1),
            (cx + 4, fy + 2),
            (cx + 12, fy),
            (cx + 7, fy - 4),
            (cx + 10, fy - 11),
            (cx + 4, fy - 10),
        ]
        pygame.draw.polygon(surf, (255, 245, 90), inner_flash)
        pygame.draw.circle(surf, (255, 255, 255), (cx, fy - 4), 4)

    return surf


class BaseWeapon:
    """Base class for first-person handheld weapons."""
    def __init__(self, game):
        self.game = game
        self.frame_index = 0
        self.is_firing = False
        self.fire_timer = 0
        self.bob_timer = 0.0
        self.bob_x = 0
        self.bob_y = 0

    def update_bobbing(self):
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


class Shotgun(BaseWeapon):
    """Classic authentic Super Shotgun with dual barrels and heavy close-range spread."""
    def __init__(self, game):
        super().__init__(game)
        self.name = "SHOTGUN"
        self.slot = 2
        self.scale_factor = 4.8
        self.max_range = SHOTGUN_MAX_RANGE
        self.min_damage_ratio = SHOTGUN_MIN_DAMAGE_RATIO
        self.num_pellets = SHOTGUN_PELLETS
        self.spread = SHOTGUN_SPREAD
        self.min_damage = SHOTGUN_MIN_DAMAGE
        self.max_damage = SHOTGUN_MAX_DAMAGE

        self.raw_images = self.load_or_generate_sprites()
        self.scaled_images = [
            pygame.transform.scale(
                img,
                (int(img.get_width() * self.scale_factor), int(img.get_height() * self.scale_factor)),
            )
            for img in self.raw_images
        ]
        self.num_frames = len(self.scaled_images)
        self.frame_durations = {1: 120, 2: 240, 3: 500}

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
                self.game.enemy_manager.process_shot(self.game.player, weapon=self)

    def update(self):
        now = pygame.time.get_ticks()
        if self.is_firing:
            cur_duration = self.frame_durations.get(self.frame_index, 100)
            if now - self.fire_timer > cur_duration:
                self.fire_timer = now
                self.frame_index += 1
                if self.frame_index == 3 and hasattr(self.game, "sound"):
                    self.game.sound.play_pump()
                elif self.frame_index >= self.num_frames:
                    self.frame_index = 0
                    self.is_firing = False
        self.update_bobbing()


class Pistol(BaseWeapon):
    """Accurate semi-automatic handgun with pinpoint accuracy and long range."""
    def __init__(self, game):
        super().__init__(game)
        self.name = "PISTOL"
        self.slot = 1
        self.scale_factor = 4.8
        self.max_range = PISTOL_MAX_RANGE
        self.min_damage_ratio = PISTOL_MIN_DAMAGE_RATIO
        self.num_pellets = PISTOL_PELLETS
        self.spread = PISTOL_SPREAD
        self.min_damage = PISTOL_MIN_DAMAGE
        self.max_damage = PISTOL_MAX_DAMAGE

        self.raw_images = self.load_or_generate_sprites()
        self.scaled_images = [
            pygame.transform.scale(
                img,
                (int(img.get_width() * self.scale_factor), int(img.get_height() * self.scale_factor)),
            )
            for img in self.raw_images
        ]
        self.num_frames = len(self.scaled_images)
        self.frame_durations = {1: 80, 2: 120, 3: 130}

    def load_or_generate_sprites(self):
        os.makedirs(ASSETS_WEAPON_DIR, exist_ok=True)
        images = []
        for i in range(4):
            path = os.path.join(ASSETS_WEAPON_DIR, f"pistol_{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
            else:
                img = generate_doom_pistol_sprite(i)
                pygame.image.save(img, path)
            images.append(img)
        return images

    def fire(self):
        """Trigger pistol gunshot, sound effect, and pinpoint hitscan damage."""
        if not self.is_firing:
            self.is_firing = True
            self.frame_index = 1
            self.fire_timer = pygame.time.get_ticks()
            if hasattr(self.game, "sound"):
                self.game.sound.play_pistol_shot()
            if hasattr(self.game, "enemy_manager"):
                self.game.enemy_manager.process_shot(self.game.player, weapon=self)

    def update(self):
        now = pygame.time.get_ticks()
        if self.is_firing:
            cur_duration = self.frame_durations.get(self.frame_index, 90)
            if now - self.fire_timer > cur_duration:
                self.fire_timer = now
                self.frame_index += 1
                if self.frame_index >= self.num_frames:
                    self.frame_index = 0
                    self.is_firing = False
        self.update_bobbing()


# Backward compatibility alias
Weapon = Shotgun
