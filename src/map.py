"""
Map representation and grid system for Not-a-Doom.
"""

# Map layout:
# 0 = empty space
# 1 = brick wall
# 2 = stone wall
# 3 = tech panel
# 4 = blood wall / hazard
_ = 0

MAP_DATA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 0, 1, 0, 3, 3, 3, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 1, 0, 3, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1],
    [1, 0, 0, 0, 4, 4, 0, 0, 2, 2, 2, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 1],
    [1, 0, 3, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 3, 0, 3, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]


class Map:
    def __init__(self):
        self.mini_map = MAP_DATA
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.world_map = {}
        self._populate_world_map()

    def _populate_world_map(self):
        """Construct coordinate lookup table for fast collision and ray tests."""
        for j, row in enumerate(self.mini_map):
            for i, val in enumerate(row):
                if val:
                    self.world_map[(i, j)] = val

    def is_wall(self, x: int, y: int) -> bool:
        return (x, y) in self.world_map

    def get_wall(self, x: int, y: int) -> int:
        return self.world_map.get((x, y), 0)
