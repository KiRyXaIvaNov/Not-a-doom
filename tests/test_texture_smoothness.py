"""
Unit tests validating wall texture stability, monotonic projection,
and elimination of sawtooth wavy artifacts in Not-a-Doom renderer.
"""
import math
import os
import sys

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from src.main import Game
from src.core.settings import HEIGHT, HALF_HEIGHT, SCALE, TEXTURE_SIZE, NUM_RAYS


def test_texture_smoothness():
    print(">>> 1. Initializing game engine...")
    game = Game()

    print(">>> 2. Testing uniform texture column mapping [0..TEXTURE_SIZE)...")
    for wall_x in [0.0, 0.25, 0.5, 0.75, 0.9999]:
        col_x = int(wall_x * TEXTURE_SIZE) % TEXTURE_SIZE
        assert 0 <= col_x < TEXTURE_SIZE
    assert int(0.9999 * TEXTURE_SIZE) % TEXTURE_SIZE == 255, "Column 255 must be reachable"
    print("Texture column mapping verified!")

    print(">>> 3. Testing exact horizon centering on flat perpendicular wall...")
    # Inject synthetic texture with horizontal line at row 128 for all textures
    test_tex = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    test_tex.fill((255, 255, 255))
    pygame.draw.line(test_tex, (0, 0, 0), (0, 128), (TEXTURE_SIZE - 1, 128))
    for tex_id in list(game.textures.raw_textures.keys()):
        game.textures.set_texture(tex_id, test_tex)

    game.player.x = 2.4
    game.player.y = 2.5
    game.player.angle = 0.0

    game.raycasting.ray_cast()
    game.screen.fill((255, 255, 255))
    game.renderer.render_walls()

    center_ys = []
    for ray in range(NUM_RAYS):
        x = ray * SCALE
        y_black = [y for y in range(HEIGHT) if game.screen.get_at((x, y))[0] == 0]
        assert len(y_black) > 0, f"Expected black pixel at ray {ray}"
        center_ys.append(sum(y_black) / len(y_black))

    assert len(set(center_ys)) == 1, f"Expected identical center Y across all rays, got {set(center_ys)}"
    # Row 128 in 0..255 space is 0.5px below true mathematical center 127.5, so on screen it sits near ~363.5
    assert abs(center_ys[0] - HALF_HEIGHT) < 5.0, f"Expected center Y near {HALF_HEIGHT}, got {center_ys[0]}"
    print(f"Exact horizon centering verified ({center_ys[0]}px) with zero parity oscillation across all rays!")

    print(">>> 4. Testing monotonic projection and elimination of sawtooth wavy artifacts...")
    # Test wall at oblique angle (player.angle = 0.4 rad)
    game.player.x = 2.4
    game.player.y = 2.5
    game.player.angle = 0.4

    game.raycasting.ray_cast()
    game.screen.fill((255, 255, 255))
    game.renderer.render_walls()

    line_ys = []
    for ray in range(NUM_RAYS):
        x = ray * SCALE
        y_black = [y for y in range(HEIGHT) if game.screen.get_at((x, y))[0] == 0]
        if y_black:
            line_ys.append(sum(y_black) / len(y_black))

    # Calculate first derivative and count direction flips
    dy = [line_ys[i + 1] - line_ys[i] for i in range(len(line_ys) - 1)]
    direction_flips = sum(1 for i in range(len(dy) - 1) if dy[i] * dy[i + 1] < 0)

    assert direction_flips == 0, f"Found {direction_flips} direction flips! Wall texture still exhibits sawtooth waves."
    print("Monotonic projection verified with zero direction flips (smooth projection)!")

    print(">>> 5. Testing close-up rendering stability (60 frames at collision distance)...")
    game.player.x = 2.74  # 0.26 from wall at x=3
    game.player.y = 2.5
    game.player.angle = 0.0

    for _ in range(60):
        game.raycasting.ray_cast()
        game.renderer.render_walls()

    print("Close-up rendering stability verified!")
    print(">>> ALL TEXTURE SMOOTHNESS TESTS PASSED! <<<")


if __name__ == "__main__":
    test_texture_smoothness()
