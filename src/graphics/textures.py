"""
Procedural retro texture generator for Not-a-Doom.
Generates classic DOOM-style textures in code with zero external asset dependencies.
Includes pre-baked 16-level lighting maps (authentic DOOM colormap architecture).
"""
import pygame
import numpy as np
import os
from src.core.settings import TEXTURE_SIZE, WIDTH, HALF_HEIGHT, ASSETS_TEXTURES_DIR

NUM_LIGHT_LEVELS = 16


def create_brick_texture() -> pygame.Surface:
    """Procedurally create retro reddish-brown brick wall."""
    size = TEXTURE_SIZE
    arr = np.zeros((size, size, 3), dtype=np.uint8)

    # Base brick color variation
    base_r, base_g, base_b = 140, 50, 40
    noise = np.random.randint(-15, 15, (size, size, 3))
    arr[:, :] = np.clip([base_r, base_g, base_b] + noise, 0, 255)

    # Mortar lines (horizontal every 32px, vertical staggered)
    mortar_color = [60, 55, 50]
    row_height = 32
    brick_width = 64

    for y in range(0, size, row_height):
        arr[y : y + 3, :] = mortar_color
        offset = (brick_width // 2) if (y // row_height) % 2 else 0
        for x in range(offset, size, brick_width):
            arr[y : y + row_height, x : x + 3] = mortar_color

    # Add bevel highlights and shadows
    for y in range(0, size, row_height):
        arr[min(y + 3, size - 1), :] = np.clip(arr[min(y + 3, size - 1), :] + 25, 0, 255)
        arr[max(y - 1, 0), :] = np.clip(arr[max(y - 1, 0), :] - 30, 0, 255)

    return pygame.surfarray.make_surface(arr.swapaxes(0, 1))


def create_stone_texture() -> pygame.Surface:
    """Procedurally create gray medieval stone dungeon blocks."""
    size = TEXTURE_SIZE
    arr = np.zeros((size, size, 3), dtype=np.uint8)

    base = 110
    noise = np.random.randint(-20, 20, (size, size, 1))
    arr[:, :, :] = np.clip(base + noise, 0, 255)

    # Large stone grid (64x64)
    groove_color = [35, 35, 38]
    block_size = 64
    for y in range(0, size, block_size):
        arr[y : y + 4, :] = groove_color
        offset = (block_size // 2) if (y // block_size) % 2 else 0
        for x in range(offset, size, block_size):
            arr[y : y + block_size, x : x + 4] = groove_color

    return pygame.surfarray.make_surface(arr.swapaxes(0, 1))


def create_tech_texture() -> pygame.Surface:
    """Procedurally create sci-fi metal tech panel with glowing cyan circuits."""
    size = TEXTURE_SIZE
    arr = np.zeros((size, size, 3), dtype=np.uint8)

    # Dark blue-gray steel panel
    arr[:, :] = [55, 60, 70]
    noise = np.random.randint(-8, 8, (size, size, 3))
    arr[:, :] = np.clip(arr + noise, 0, 255)

    # Panel border rivets
    rivet_color = [180, 190, 200]
    for pos in [16, size - 16]:
        arr[pos - 2 : pos + 2, 16 : size - 16 : 32] = rivet_color
        arr[16 : size - 16 : 32, pos - 2 : pos + 2] = rivet_color

    # Glowing cyan conduit / energy line in center
    cyan_glow = [0, 220, 255]
    arr[size // 2 - 4 : size // 2 + 4, 24 : size - 24] = cyan_glow
    arr[24 : size - 24, size // 2 - 4 : size // 2 + 4] = cyan_glow

    # Center power core
    center = size // 2
    r = 20
    y, x = np.ogrid[:size, :size]
    mask = (x - center) ** 2 + (y - center) ** 2 <= r ** 2
    arr[mask] = [0, 255, 220]

    return pygame.surfarray.make_surface(arr.swapaxes(0, 1))


def create_hazard_texture() -> pygame.Surface:
    """Procedurally create industrial yellow-and-black hazard warning stripes."""
    size = TEXTURE_SIZE
    arr = np.zeros((size, size, 3), dtype=np.uint8)

    stripe_width = 32
    for y in range(size):
        for x in range(size):
            if ((x + y) // stripe_width) % 2 == 0:
                arr[y, x] = [230, 185, 20]
            else:
                arr[y, x] = [25, 25, 30]

    noise = np.random.randint(-15, 15, (size, size, 3))
    arr[:, :] = np.clip(arr + noise, 0, 255)

    return pygame.surfarray.make_surface(arr.swapaxes(0, 1))


def create_sky_surface() -> pygame.Surface:
    """Create panoramic atmospheric red/dark doom sky gradient."""
    sky_width = WIDTH * 2
    sky_height = HALF_HEIGHT
    surf = pygame.Surface((sky_width, sky_height))

    for y in range(sky_height):
        t = y / sky_height
        r = int(120 * (1 - t) + 20 * t)
        g = int(20 * (1 - t) + 10 * t)
        b = int(30 * (1 - t) + 40 * t)
        pygame.draw.line(surf, (r, g, b), (0, y), (sky_width, y))

    return surf


class TextureManager:
    """Holds and caches textures with pre-baked light levels for zero runtime multiplication overhead."""
    def __init__(self):
        os.makedirs(ASSETS_TEXTURES_DIR, exist_ok=True)
        self.raw_textures = {
            1: self._load_or_create_texture(1, "1.png", "brick.png", create_brick_texture),
            2: self._load_or_create_texture(2, "2.png", "stone.png", create_stone_texture),
            3: self._load_or_create_texture(3, "3.png", "tech.png", create_tech_texture),
            4: self._load_or_create_texture(4, "4.png", "hazard.png", create_hazard_texture),
        }
        self.sky = self._load_or_create_sky()
        self.shaded_textures = {}
        self._bake_lightmaps()

    def _load_or_create_texture(self, tex_id: int, filename: str, alt_name: str, generator_func) -> pygame.Surface:
        for name in [filename, alt_name]:
            path = os.path.join(ASSETS_TEXTURES_DIR, name)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    if img.get_size() != (TEXTURE_SIZE, TEXTURE_SIZE):
                        img = pygame.transform.scale(img, (TEXTURE_SIZE, TEXTURE_SIZE))
                    return img
                except Exception:
                    pass
        surf = generator_func()
        try:
            save_path = os.path.join(ASSETS_TEXTURES_DIR, filename)
            pygame.image.save(surf, save_path)
        except Exception:
            pass
        return surf

    def _load_or_create_sky(self) -> pygame.Surface:
        target_w = WIDTH * 2
        target_h = HALF_HEIGHT
        path = os.path.join(ASSETS_TEXTURES_DIR, "sky.png")
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                if img.get_size() != (target_w, target_h):
                    img = pygame.transform.scale(img, (target_w, target_h))
                return img
            except Exception:
                pass
        surf = create_sky_surface()
        try:
            pygame.image.save(surf, path)
        except Exception:
            pass
        return surf

    def _bake_lightmaps(self):
        """Pre-shade textures into 16 discrete light levels and pre-slice 256 vertical 1px columns."""
        self.pre_sliced_columns = {}
        for tex_id, surface in self.raw_textures.items():
            self.shaded_textures[tex_id] = []
            self.pre_sliced_columns[tex_id] = []
            for level in range(NUM_LIGHT_LEVELS):
                ratio = level / (NUM_LIGHT_LEVELS - 1)
                brightness = max(0.12, ratio)
                val = int(255 * brightness)
                shaded = surface.copy()
                shaded.fill((val, val, val), special_flags=pygame.BLEND_MULT)
                self.shaded_textures[tex_id].append(shaded)
                # Pre-slice 256 vertical 1px columns for zero-allocation O(1) render lookup
                cols = tuple(shaded.subsurface((x, 0, 1, TEXTURE_SIZE)) for x in range(TEXTURE_SIZE))
                self.pre_sliced_columns[tex_id].append(cols)

    def get_texture(self, texture_id: int) -> pygame.Surface:
        return self.raw_textures.get(texture_id, self.raw_textures[1])

    def set_texture(self, tex_id: int, surface: pygame.Surface):
        """Set or update a texture dynamically and rebake its lightmaps and column slices."""
        self.raw_textures[tex_id] = surface
        self.shaded_textures[tex_id] = []
        self.pre_sliced_columns[tex_id] = []
        for level in range(NUM_LIGHT_LEVELS):
            ratio = level / (NUM_LIGHT_LEVELS - 1)
            brightness = max(0.12, ratio)
            val = int(255 * brightness)
            shaded = surface.copy()
            shaded.fill((val, val, val), special_flags=pygame.BLEND_MULT)
            self.shaded_textures[tex_id].append(shaded)
            cols = tuple(shaded.subsurface((x, 0, 1, TEXTURE_SIZE)) for x in range(TEXTURE_SIZE))
            self.pre_sliced_columns[tex_id].append(cols)

    def get_shaded_texture(self, texture_id: int, brightness: float) -> pygame.Surface:
        """Instant O(1) table lookup of pre-shaded texture level."""
        levels = self.shaded_textures.get(texture_id, self.shaded_textures[1])
        idx = int(brightness * (NUM_LIGHT_LEVELS - 1))
        idx = max(0, min(NUM_LIGHT_LEVELS - 1, idx))
        return levels[idx]

    def get_column_slice(self, texture_id: int, brightness: float, col_x: int) -> pygame.Surface:
        """Instant O(1) lookup of pre-sliced, pre-shaded 1px texture column (zero allocation)."""
        levels = self.pre_sliced_columns.get(texture_id, self.pre_sliced_columns[1])
        idx = int(brightness * (NUM_LIGHT_LEVELS - 1))
        idx = max(0, min(NUM_LIGHT_LEVELS - 1, idx))
        return levels[idx][col_x]
