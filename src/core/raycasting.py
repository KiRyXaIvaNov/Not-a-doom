"""
DDA (Digital Differential Analyzer) Raycasting engine for Not-a-Doom.
Calculates wall hits, distances, texture coordinates, projection heights,
and maintains a 1D Z-depth buffer for 2.5D sprite occlusion.
"""
import math
from src.core.settings import (
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
        self.scale = getattr(game, 'scale', SCALE)
        self.num_rays = getattr(game, 'num_rays', NUM_RAYS)
        self.delta_angle = getattr(game, 'delta_angle', DELTA_ANGLE)
        self.ray_casting_result = []
        self.depth_buffer = [MAX_DEPTH] * self.num_rays

    def set_quality(self, scale: int, num_rays: int, delta_angle: float):
        """Dynamically reconfigure raycasting density for graphics quality scaling."""
        self.scale = scale
        self.num_rays = num_rays
        self.delta_angle = delta_angle
        self.depth_buffer = [MAX_DEPTH] * self.num_rays

    def update(self):
        self.ray_cast()

    def ray_cast(self):
        """Execute optimized DDA algorithm across the entire player Field of View."""
        self.ray_casting_result.clear()

        ox, oy = self.game.player.pos
        map_x, map_y = int(ox), int(oy)
        player_angle = self.game.player.angle
        ray_angle = player_angle - HALF_FOV + 0.0001
        num_rays = self.num_rays
        delta_angle = self.delta_angle
        world_map_get = self.game.map.world_map.get
        depth_buffer = self.depth_buffer
        results = self.ray_casting_result

        for ray in range(num_rays):
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
                    depth = side_dist_x
                    side_dist_x += delta_dist_x
                    cur_map_x += step_x
                    side = 0
                else:
                    depth = side_dist_y
                    side_dist_y += delta_dist_y
                    cur_map_y += step_y
                    side = 1

                if depth >= MAX_DEPTH:
                    break

                wall_val = world_map_get((cur_map_x, cur_map_y), 0)
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
            depth *= math.cos(player_angle - ray_angle)

            # Record in depth buffer for sprite Z-testing
            depth_buffer[ray] = depth

            # Projection calculations
            proj_height = SCREEN_DIST / (depth + 0.0001)

            # Store result for rendering
            results.append(
                (depth, proj_height, texture_id, wall_x, ray, side)
            )

            ray_angle += delta_angle

    def cast_single_ray(self, ox: float, oy: float, ray_angle: float) -> tuple[float, float, float]:
        """Cast a single ray through the map and return (euclidean_dist, hit_x, hit_y)."""
        map_x, map_y = int(ox), int(oy)
        world_map_get = self.game.map.world_map.get
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
                depth = side_dist_x
                side_dist_x += delta_dist_x
                cur_map_x += step_x
                side = 0
            else:
                depth = side_dist_y
                side_dist_y += delta_dist_y
                cur_map_y += step_y
                side = 1

            if depth >= MAX_DEPTH:
                break

            if world_map_get((cur_map_x, cur_map_y), 0) > 0:
                break

        if side == 0:
            depth = (cur_map_x - ox + (1 - step_x) / 2) / (cos_a if cos_a != 0 else 1e-6)
        else:
            depth = (cur_map_y - oy + (1 - step_y) / 2) / (sin_a if sin_a != 0 else 1e-6)

        hit_x = ox + depth * cos_a
        hit_y = oy + depth * sin_a
        return depth, hit_x, hit_y
