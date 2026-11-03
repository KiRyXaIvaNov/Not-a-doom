"""
DDA (Digital Differential Analyzer) Raycasting engine for Not-a-Doom.
Calculates wall hits, distances, texture coordinates, projection heights,
and maintains a 1D Z-depth buffer for 2.5D sprite occlusion.
"""
import math
from src.settings import (
    FOV,
    HALF_FOV,
    NUM_RAYS,
    DELTA_ANGLE,
    MAX_DEPTH,
    SCREEN_DIST,
    SCALE,
    HALF_HEIGHT,
)


class RayCasting:
    def __init__(self, game):
        self.game = game
        self.ray_casting_result = []
        self.depth_buffer = [MAX_DEPTH] * NUM_RAYS

    def update(self):
        self.ray_cast()

    def ray_cast(self):
        """Execute DDA algorithm across the entire player Field of View."""
        self.ray_casting_result.clear()

        ox, oy = self.game.player.pos
        map_x, map_y = int(ox), int(oy)
        ray_angle = self.game.player.angle - HALF_FOV + 0.0001

        for ray in range(NUM_RAYS):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            delta_dist_x = abs(1.0 / (cos_a if cos_a != 0 else 1e-6))
            delta_dist_y = abs(1.0 / (sin_a if sin_a != 0 else 1e-6))

            if cos_a < 0:
                step_x = -1
                side_dist_x = (ox - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1.0 - ox) * delta_dist_x

            if sin_a < 0:
                step_y = -1
                side_dist_y = (oy - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1.0 - oy) * delta_dist_y

            side = 0
            cur_map_x, cur_map_y = map_x, map_y
            depth = 0.0
            texture_id = 1

            while depth < MAX_DEPTH:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    cur_map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    cur_map_y += step_y
                    side = 1

                wall_val = self.game.map.get_wall(cur_map_x, cur_map_y)
                if wall_val > 0:
                    texture_id = wall_val
                    break

            if side == 0:
                depth = (cur_map_x - ox + (1 - step_x) / 2) / (cos_a if cos_a != 0 else 1e-6)
                wall_x = oy + depth * sin_a
            else:
                depth = (cur_map_y - oy + (1 - step_y) / 2) / (sin_a if sin_a != 0 else 1e-6)
                wall_x = ox + depth * cos_a

            wall_x -= math.floor(wall_x)

            # Fish-eye correction relative to player heading
            depth *= math.cos(self.game.player.angle - ray_angle)

            # Record in depth buffer for sprite Z-testing
            self.depth_buffer[ray] = depth

            # Projection calculations
            proj_height = SCREEN_DIST / (depth + 0.0001)

            # Store result for rendering
            self.ray_casting_result.append(
                (depth, proj_height, texture_id, wall_x, ray, side)
            )

            ray_angle += DELTA_ANGLE

    def cast_single_ray(self, ox: float, oy: float, ray_angle: float) -> tuple[float, float, float]:
        """Cast a single ray through the map and return (euclidean_dist, hit_x, hit_y)."""
        map_x, map_y = int(ox), int(oy)
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        delta_dist_x = abs(1.0 / (cos_a if cos_a != 0 else 1e-6))
        delta_dist_y = abs(1.0 / (sin_a if sin_a != 0 else 1e-6))

        if cos_a < 0:
            step_x = -1
            side_dist_x = (ox - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - ox) * delta_dist_x

        if sin_a < 0:
            step_y = -1
            side_dist_y = (oy - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - oy) * delta_dist_y

        cur_map_x, cur_map_y = map_x, map_y
        depth = 0.0
        side = 0

        while depth < MAX_DEPTH:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                cur_map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                cur_map_y += step_y
                side = 1

            if self.game.map.get_wall(cur_map_x, cur_map_y) > 0:
                break

        if side == 0:
            depth = (cur_map_x - ox + (1 - step_x) / 2) / (cos_a if cos_a != 0 else 1e-6)
        else:
            depth = (cur_map_y - oy + (1 - step_y) / 2) / (sin_a if sin_a != 0 else 1e-6)

        hit_x = ox + depth * cos_a
        hit_y = oy + depth * sin_a
        return depth, hit_x, hit_y
