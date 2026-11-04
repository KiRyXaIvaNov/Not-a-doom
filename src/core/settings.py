"""
Game settings and constants for Not-a-Doom.
"""
import os
import math

# Project Directory & Asset Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ASSETS_MAPS_DIR = os.path.join(ASSETS_DIR, "maps")
DEFAULT_MAP_PATH = os.path.join(ASSETS_MAPS_DIR, "level1.json")
ASSETS_SOUND_DIR = os.path.join(ASSETS_DIR, "sound")
ASSETS_TEXTURES_DIR = os.path.join(ASSETS_DIR, "textures")
ASSETS_SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
ASSETS_ENEMY_DIR = os.path.join(ASSETS_SPRITES_DIR, "enemy")
ASSETS_WEAPON_DIR = os.path.join(ASSETS_SPRITES_DIR, "weapon")
ASSETS_PROPS_DIR = os.path.join(ASSETS_SPRITES_DIR, "props")
ASSETS_FIREBALL_PATH = os.path.join(ASSETS_SPRITES_DIR, "fireball.png")


# Window & Display
RES = WIDTH, HEIGHT = 1280, 720
HALF_WIDTH = WIDTH // 2
HALF_HEIGHT = HEIGHT // 2
FPS = 60

# Player settings
PLAYER_POS = 1.5, 1.5  # Starting position on the corridor (open space)
PLAYER_ANGLE = 0.0     # Initial facing angle in radians
PLAYER_SPEED = 0.004   # Movement speed
PLAYER_ROT_SPEED = 0.003 # Responsive keyboard arrow rotation speed
PLAYER_SIZE_SCALE = 60 # Collision box scale
MOUSE_SENSITIVITY = 0.002 # Snappy, comfortable mouse look sensitivity
MOUSE_MAX_REL = 40
MOUSE_BORDER_LEFT = 100
MOUSE_BORDER_RIGHT = WIDTH - MOUSE_BORDER_LEFT

# Camera & FOV
FOV = math.pi / 3       # 60 degrees field of view
HALF_FOV = FOV / 2
NUM_RAYS = WIDTH // 2   # Cast 1 ray per 2 pixels for performance balance
HALF_NUM_RAYS = NUM_RAYS // 2
DELTA_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 30          # Maximum view distance in grid units

# Screen Projection
SCREEN_DIST = HALF_WIDTH / math.tan(HALF_FOV)
SCALE = WIDTH // NUM_RAYS

# Textures
TEXTURE_SIZE = 256
HALF_TEXTURE_SIZE = TEXTURE_SIZE // 2

# Colors
FLOOR_COLOR = (35, 35, 35)
CEILING_COLOR = (20, 20, 25)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (0, 200, 0)
DARK_GRAY = (40, 40, 40)
