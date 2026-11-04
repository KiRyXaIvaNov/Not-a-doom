"""
Map representation, grid system, and level serialization for Not-a-Doom.
"""
import json
import os
from src.core.settings import DEFAULT_MAP_PATH, ASSETS_MAPS_DIR

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

DEFAULT_LEVEL = {
    "grid": MAP_DATA,
    "player_spawn": [1.5, 1.5],
    "portal": [14.5, 14.5],
    "enemies": [
        [7.5, 4.5],
        [9.5, 3.5],
        [13.5, 10.5],
    ],
    "barrels": [
        [3.5, 1.5],
        [4.5, 1.5],
        [9.5, 5.5],
        [13.5, 13.5],
    ],
    "medkits": [
        [1.5, 3.5],
        [5.5, 5.5],
        [11.5, 1.5],
    ],
    "pillars": [
        [7.5, 1.5],
        [1.5, 7.5],
        [13.5, 5.5],
    ],
}


class Map:
    def __init__(self, map_path: str = None):
        self.map_path = map_path or DEFAULT_MAP_PATH
        self.mini_map = [row[:] for row in MAP_DATA]
        self.player_spawn = list(DEFAULT_LEVEL["player_spawn"])
        self.portal = list(DEFAULT_LEVEL["portal"])
        self.enemies = [list(p) for p in DEFAULT_LEVEL["enemies"]]
        self.barrels = [list(p) for p in DEFAULT_LEVEL["barrels"]]
        self.medkits = [list(p) for p in DEFAULT_LEVEL["medkits"]]
        self.pillars = [list(p) for p in DEFAULT_LEVEL["pillars"]]
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.world_map = {}

        if os.path.isfile(self.map_path):
            self.load_from_file(self.map_path)
        else:
            self._populate_world_map()
            # Ensure default level JSON is saved to disk
            self.save_to_file(self.map_path)

    def _populate_world_map(self):
        """Construct coordinate lookup table for fast collision and ray tests."""
        self.world_map = {}
        for j, row in enumerate(self.mini_map):
            for i, val in enumerate(row):
                if val:
                    self.world_map[(i, j)] = val

    def is_wall(self, x: int, y: int) -> bool:
        return (x, y) in self.world_map

    def get_wall(self, x: int, y: int) -> int:
        return self.world_map.get((x, y), 0)

    def set_data(self, data: dict):
        """Load grid and entity placements from a dictionary."""
        self.mini_map = [row[:] for row in data.get("grid", MAP_DATA)]
        self.rows = len(self.mini_map)
        self.cols = len(self.mini_map[0])
        self.player_spawn = list(data.get("player_spawn", DEFAULT_LEVEL["player_spawn"]))
        self.portal = list(data.get("portal", DEFAULT_LEVEL["portal"]))
        self.enemies = [list(p) for p in data.get("enemies", [])]
        self.barrels = [list(p) for p in data.get("barrels", [])]
        self.medkits = [list(p) for p in data.get("medkits", [])]
        self.pillars = [list(p) for p in data.get("pillars", [])]
        self._populate_world_map()

    def get_data(self) -> dict:
        """Serialize current grid and entities to a dictionary."""
        return {
            "grid": [row[:] for row in self.mini_map],
            "player_spawn": list(self.player_spawn),
            "portal": list(self.portal),
            "enemies": [list(p) for p in self.enemies],
            "barrels": [list(p) for p in self.barrels],
            "medkits": [list(p) for p in self.medkits],
            "pillars": [list(p) for p in self.pillars],
        }

    def save_to_file(self, filepath: str = None) -> bool:
        """Save level data to a JSON file with clean, human-readable formatting."""
        target_path = filepath or self.map_path
        try:
            os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
            data = self.get_data()
            grid_str = ",\n    ".join(json.dumps(row) for row in data["grid"])
            formatted_json = (
                "{\n"
                f'  "grid": [\n    {grid_str}\n  ],\n'
                f'  "player_spawn": {json.dumps(data["player_spawn"])},\n'
                f'  "portal": {json.dumps(data["portal"])},\n'
                f'  "enemies": {json.dumps(data["enemies"])},\n'
                f'  "barrels": {json.dumps(data["barrels"])},\n'
                f'  "medkits": {json.dumps(data["medkits"])},\n'
                f'  "pillars": {json.dumps(data["pillars"])}\n'
                "}\n"
            )
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(formatted_json)
            self.map_path = target_path
            return True
        except Exception as e:
            print(f"Error saving map: {e}")
            return False

    def load_from_file(self, filepath: str = None) -> bool:
        """Load level data from a JSON file."""
        target_path = filepath or self.map_path
        if not os.path.isfile(target_path):
            return False
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.set_data(data)
            self.map_path = target_path
            return True
        except Exception as e:
            print(f"Error loading map: {e}")
            return False
