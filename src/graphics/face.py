"""
Authentic retro DOOM Marine Face generator and animation controller for Not-a-Doom.
Generates reactive pixel art faces responding to health, damage, and looking around.
"""
import random
import pygame


def generate_marine_face_surface(health: int, is_hurt: bool = False, glance: str = "center") -> pygame.Surface:
    """
    Procedurally draws an authentic retro DOOM Marine pixel art face (32x36 upscaled to 64x72).
    """
    w, h = 32, 36
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Color Palette: Retro DOOM Skin, Hair, and Blood tones
    SKIN_LIGHT = (235, 180, 135)
    SKIN_MID = (200, 140, 100)
    SKIN_SHADOW = (150, 100, 65)
    SKIN_DARK = (105, 65, 40)

    HAIR_DARK = (70, 42, 22)
    HAIR_MID = (105, 65, 35)
    HAIR_LIGHT = (140, 95, 55)

    EYE_WHITE = (235, 235, 240)
    EYE_PUPIL = (25, 35, 50)
    EYE_SHADOW = (120, 75, 50)

    BLOOD_RED = (185, 22, 26)
    BLOOD_DARK = (115, 12, 16)

    TEETH = (235, 230, 220)
    MOUTH_DARK = (60, 25, 25)

    is_dead = health <= 0

    if is_dead:
        # Slumped, lifeless head
        pygame.draw.rect(surf, (30, 20, 20), (6, 6, 20, 26))
        pygame.draw.rect(surf, (155, 125, 115), (7, 7, 18, 24))
        # Head wound & dripping blood
        pygame.draw.rect(surf, BLOOD_DARK, (9, 8, 8, 5))
        pygame.draw.rect(surf, BLOOD_RED, (10, 9, 6, 3))
        # Closed/slitted dead eyes
        pygame.draw.line(surf, (40, 20, 20), (10, 16), (13, 17), 1)
        pygame.draw.line(surf, (40, 20, 20), (18, 17), (21, 16), 1)
        # Blood pooling from mouth
        pygame.draw.rect(surf, BLOOD_DARK, (12, 23, 8, 5))
        pygame.draw.line(surf, BLOOD_RED, (14, 28), (14, 32), 2)
        return pygame.transform.scale(surf, (64, 72))

    # 1. Base Head Shape (Angular, iconic heroic jaw)
    pygame.draw.rect(surf, HAIR_DARK, (7, 2, 18, 9))
    pygame.draw.rect(surf, SKIN_SHADOW, (6, 9, 20, 17))
    pygame.draw.rect(surf, SKIN_MID, (7, 10, 18, 15))
    pygame.draw.rect(surf, SKIN_LIGHT, (8, 10, 16, 6))

    # Jawline taper
    pygame.draw.line(surf, SKIN_SHADOW, (7, 26), (11, 29), 1)
    pygame.draw.line(surf, SKIN_SHADOW, (24, 26), (20, 29), 1)
    pygame.draw.rect(surf, SKIN_MID, (11, 26, 10, 4))
    # Chin cleft
    pygame.draw.line(surf, SKIN_DARK, (16, 27), (16, 29), 1)

    # 2. Crew Cut Hair Texture
    pygame.draw.rect(surf, HAIR_MID, (8, 3, 16, 6))
    pygame.draw.rect(surf, HAIR_LIGHT, (10, 3, 12, 2))
    hair_strands = [(8, 8), (11, 9), (14, 8), (17, 9), (20, 8), (23, 8)]
    for sx, sy in hair_strands:
        pygame.draw.line(surf, HAIR_DARK, (sx, sy - 2), (sx, sy), 1)

    # 3. Ears
    pygame.draw.rect(surf, SKIN_SHADOW, (5, 13, 2, 6))
    pygame.draw.rect(surf, SKIN_SHADOW, (25, 13, 2, 6))
    pygame.draw.line(surf, SKIN_DARK, (5, 15), (5, 17), 1)
    pygame.draw.line(surf, SKIN_DARK, (26, 15), (26, 17), 1)

    # 4. Eyebrows
    if is_hurt:
        # Angled pained brow
        pygame.draw.line(surf, HAIR_DARK, (8, 12), (13, 14), 2)
        pygame.draw.line(surf, HAIR_DARK, (23, 12), (18, 14), 2)
    else:
        # Determined flat/slight furrow
        pygame.draw.line(surf, HAIR_DARK, (9, 13), (14, 13), 2)
        pygame.draw.line(surf, HAIR_DARK, (18, 13), (23, 13), 2)

    # 5. Eyes with glance direction
    pupil_ox = 0
    if glance == "left":
        pupil_ox = -1
    elif glance == "right":
        pupil_ox = 1

    if is_hurt:
        # Squinting pain eyes
        pygame.draw.line(surf, EYE_SHADOW, (9, 15), (13, 16), 2)
        pygame.draw.line(surf, EYE_SHADOW, (22, 15), (18, 16), 2)
        pygame.draw.circle(surf, EYE_PUPIL, (11 + pupil_ox, 15), 1)
        pygame.draw.circle(surf, EYE_PUPIL, (20 + pupil_ox, 15), 1)
    else:
        # Left eye
        pygame.draw.rect(surf, EYE_WHITE, (9, 15, 5, 3))
        pygame.draw.circle(surf, EYE_PUPIL, (11 + pupil_ox, 16), 1)
        pygame.draw.line(surf, EYE_SHADOW, (9, 14), (13, 14), 1)

        # Right eye
        pygame.draw.rect(surf, EYE_WHITE, (18, 15, 5, 3))
        pygame.draw.circle(surf, EYE_PUPIL, (20 + pupil_ox, 16), 1)
        pygame.draw.line(surf, EYE_SHADOW, (18, 14), (22, 14), 1)

    # 6. Nose
    pygame.draw.line(surf, SKIN_SHADOW, (15, 15), (15, 20), 1)
    pygame.draw.line(surf, SKIN_DARK, (14, 20), (17, 20), 1)
    pygame.draw.circle(surf, SKIN_LIGHT, (15, 19), 1)

    # 7. Mouth
    if is_hurt:
        # Grimacing mouth baring teeth
        pygame.draw.rect(surf, MOUTH_DARK, (12, 22, 8, 4))
        pygame.draw.rect(surf, TEETH, (13, 23, 6, 2))
        pygame.draw.line(surf, MOUTH_DARK, (15, 23), (15, 24), 1)
    elif health < 30:
        # Heavy ragged breath grimace
        pygame.draw.rect(surf, MOUTH_DARK, (12, 23, 8, 3))
        pygame.draw.line(surf, TEETH, (13, 23), (18, 23), 1)
    else:
        # Resolute mouth line
        pygame.draw.line(surf, SKIN_DARK, (12, 23), (19, 23), 2)
        pygame.draw.line(surf, SKIN_SHADOW, (11, 24), (13, 24), 1)
        pygame.draw.line(surf, SKIN_SHADOW, (18, 24), (20, 24), 1)

    # 8. Progressive Battle Scars & Blood
    if health < 75:
        # Forehead scratch
        pygame.draw.line(surf, BLOOD_RED, (19, 6), (22, 9), 1)
        pygame.draw.circle(surf, BLOOD_DARK, (20, 8), 1)

    if health < 50:
        # Blood on cheek
        pygame.draw.rect(surf, BLOOD_RED, (8, 19, 3, 3))
        pygame.draw.circle(surf, BLOOD_DARK, (9, 20), 1)

    if health < 25:
        # Bloody mouth drip & black eye
        pygame.draw.line(surf, BLOOD_RED, (14, 24), (14, 28), 1)
        pygame.draw.circle(surf, BLOOD_DARK, (14, 28), 1)
        pygame.draw.rect(surf, (80, 50, 70), (8, 14, 6, 2))

    return pygame.transform.scale(surf, (64, 72))


class DoomFace:
    """Manages DOOM status bar face animations, glancing, and pain reactions."""
    def __init__(self, game):
        self.game = game
        self.glance = "center"
        self.next_glance_time = pygame.time.get_ticks() + random.randint(2500, 4500)
        self.glance_duration = 800
        self.glance_end_time = 0

        # Pre-bake face states for maximum performance (O(1) drawing)
        self.cache = {}
        health_tiers = [100, 65, 35, 15, 0]
        glances = ["center", "left", "right"]
        for ht in health_tiers:
            for hurt in [False, True]:
                for gl in glances:
                    key = (ht, hurt, gl)
                    self.cache[key] = generate_marine_face_surface(ht, hurt, gl)

    def _get_health_tier(self, hp: int) -> int:
        if hp <= 0:
            return 0
        if hp < 25:
            return 15
        if hp < 50:
            return 35
        if hp < 75:
            return 65
        return 100

    def update(self):
        now = pygame.time.get_ticks()

        # Handle random glancing left/right like classic Doomguy
        if self.glance != "center":
            if now >= self.glance_end_time:
                self.glance = "center"
                self.next_glance_time = now + random.randint(2500, 4500)
        else:
            if now >= self.next_glance_time:
                self.glance = random.choice(["left", "right"])
                self.glance_end_time = now + self.glance_duration

    def get_surface(self) -> pygame.Surface:
        player = getattr(self.game, "player", None)
        hp = player.hp if player else 100
        tier = self._get_health_tier(hp)

        is_hurt = False
        if player and getattr(player, "damage_alpha", 0.0) > 30.0:
            is_hurt = True

        key = (tier, is_hurt, self.glance if tier > 0 else "center")
        if key in self.cache:
            return self.cache[key]
        return self.cache.get((100, False, "center"))
