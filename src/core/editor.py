"""
In-game 2D Level Editor for Not-a-Doom.

Features:
- Real-time 16x16 2D interactive grid with DOOM texture miniature rendering
- Left-click drag to paint selected tiles/entities, Right-click to erase
- Complete entity palette: Player spawn, Exit portal, Demons, Barrels, Medkits, Pillars
- Wall textures palette: Brick (1), Stone (2), Tech (3), Blood (4), and Floor (0)
- Hotkeys: 1-4, 0, P, E, D, B, M, L, S (save), O (load), C (clear), F2/Enter (playtest)
- Instant zero-restart switch to 3D raycaster playtest with live reload
"""
import math
import pygame
from src.core.settings import (
    WIDTH,
    HEIGHT,
    DEFAULT_MAP_PATH,
)


class LevelEditor:
    def __init__(self, game):
        self.game = game

        # 16x16 Grid configuration
        self.cols = 16
        self.rows = 16
        self.cell_size = 40
        self.grid_x = 40
        self.grid_y = 40
        self.grid_w = self.cols * self.cell_size  # 640
        self.grid_h = self.rows * self.cell_size  # 640

        # Editor data state
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.player_spawn = [1.5, 1.5]
        self.portal = [14.5, 14.5]
        self.enemies: list[list[float]] = []
        self.barrels: list[list[float]] = []
        self.medkits: list[list[float]] = []
        self.pillars: list[list[float]] = []

        # Tool selection
        # Tools: 'wall_1', 'wall_2', 'wall_3', 'wall_4', 'floor',
        #        'player', 'portal', 'demon', 'barrel', 'medkit', 'pillar', 'erase'
        self.selected_tool = "wall_1"

        # Mouse painting state
        self.is_painting = False
        self.paint_button = 1  # 1 = LMB, 3 = RMB
        self.last_painted_cell = None

        # Status notification
        self.status_text = "LEVEL EDITOR READY | Press F2 / Enter to Playtest"
        self.status_color = (0, 255, 200)
        self.status_timer = 5000.0  # ms

        # Initialize fonts
        self.font_title = pygame.font.SysFont("impact", 26)
        if not self.font_title:
            self.font_title = pygame.font.SysFont("arial", 24, bold=True)
        self.font_section = pygame.font.SysFont("arial", 14, bold=True)
        self.font_btn = pygame.font.SysFont("arial", 13, bold=True)
        self.font_small = pygame.font.SysFont("arial", 12)
        self.font_micro = pygame.font.SysFont("arial", 10, bold=True)

        # Texture cache
        self.wall_thumbnails = {}
        self.btn_thumbnails = {}
        self._init_thumbnails()

        # UI Button rectangles
        self.buttons = []
        self._setup_ui_buttons()

        # Sync initial state from game map
        self.sync_from_map()

    def _init_thumbnails(self):
        """Prepare scaled thumbnail surfaces for grid and palette buttons."""
        if hasattr(self.game, "textures"):
            for tex_id in (1, 2, 3, 4):
                try:
                    raw = self.game.textures.get_texture(tex_id)
                    self.wall_thumbnails[tex_id] = pygame.transform.scale(raw, (self.cell_size, self.cell_size))
                    self.btn_thumbnails[tex_id] = pygame.transform.scale(raw, (30, 30))
                except Exception:
                    pass

    def _setup_ui_buttons(self):
        """Build interactive palette button rectangles in right panel."""
        self.buttons = []
        panel_x = 715

        # Wall tools (Row 1)
        wall_tools = [
            ("wall_1", "1:Brick", (160, 50, 40), 1),
            ("wall_2", "2:Stone", (110, 110, 110), 2),
            ("wall_3", "3:Tech", (40, 120, 160), 3),
            ("wall_4", "4:Blood", (150, 20, 20), 4),
            ("floor", "0:Floor", (45, 45, 52), None),
        ]
        btn_w, btn_h, gap = 98, 48, 8
        y = 110
        for i, (tool_id, label, color, tex_id) in enumerate(wall_tools):
            rect = pygame.Rect(panel_x + i * (btn_w + gap), y, btn_w, btn_h)
            self.buttons.append({
                "type": "tool",
                "tool": tool_id,
                "label": label,
                "rect": rect,
                "color": color,
                "tex_id": tex_id,
            })

        # Entity tools (Row 2)
        entity_tools = [
            ("player", "P:Player", (0, 200, 255)),
            ("portal", "E:Exit", (50, 220, 90)),
            ("demon", "D:Demon", (230, 40, 40)),
            ("barrel", "B:Barrel", (60, 180, 50)),
            ("medkit", "M:Medkit", (240, 240, 240)),
            ("pillar", "L:Pillar", (130, 130, 140)),
        ]
        ent_w, ent_h, ent_gap = 81, 44, 7
        y = 205
        for i, (tool_id, label, color) in enumerate(entity_tools):
            rect = pygame.Rect(panel_x + i * (ent_w + ent_gap), y, ent_w, ent_h)
            self.buttons.append({
                "type": "tool",
                "tool": tool_id,
                "label": label,
                "rect": rect,
                "color": color,
                "tex_id": None,
            })

        # Action Buttons
        y = 300
        # Playtest button (large, prominent)
        self.buttons.append({
            "type": "action",
            "action": "playtest",
            "label": "PLAYTEST 3D  [ENTER / F2]",
            "rect": pygame.Rect(panel_x, y, 260, 44),
            "color": (25, 140, 60),
            "hover_color": (35, 180, 80),
        })

        # Save & Load buttons
        self.buttons.append({
            "type": "action",
            "action": "save",
            "label": "SAVE MAP [S]",
            "rect": pygame.Rect(panel_x + 270, y, 120, 44),
            "color": (30, 90, 160),
            "hover_color": (40, 120, 210),
        })
        self.buttons.append({
            "type": "action",
            "action": "load",
            "label": "LOAD MAP [O]",
            "rect": pygame.Rect(panel_x + 400, y, 120, 44),
            "color": (110, 50, 150),
            "hover_color": (145, 65, 195),
        })

        # Utility Buttons (Row 4)
        y = 354
        self.buttons.append({
            "type": "action",
            "action": "clear",
            "label": "CLEAR INTERIOR [C]",
            "rect": pygame.Rect(panel_x, y, 160, 34),
            "color": (140, 40, 40),
            "hover_color": (180, 50, 50),
        })
        self.buttons.append({
            "type": "tool",
            "tool": "erase",
            "label": "ERASE TOOL [X / RMB]",
            "rect": pygame.Rect(panel_x + 170, y, 175, 34),
            "color": (180, 100, 30),
            "hover_color": (220, 130, 40),
        })

    def set_status(self, text: str, color: tuple[int, int, int] = (0, 255, 200), duration_ms: float = 4000.0):
        """Display an informational notification banner."""
        self.status_text = text
        self.status_color = color
        self.status_timer = duration_ms

    def sync_from_map(self):
        """Pull current level geometry and entities from the game's Map instance."""
        if not hasattr(self.game, "map"):
            return
        data = self.game.map.get_data()
        self.grid = [row[:] for row in data.get("grid", [])]
        self.player_spawn = list(data.get("player_spawn", [1.5, 1.5]))
        self.portal = list(data.get("portal", [14.5, 14.5]))
        self.enemies = [list(e) for e in data.get("enemies", [])]
        self.barrels = [list(b) for b in data.get("barrels", [])]
        self.medkits = [list(m) for m in data.get("medkits", [])]
        self.pillars = [list(p) for p in data.get("pillars", [])]

    def apply_to_game(self):
        """Send edited grid and entity positions to the game engine."""
        data = {
            "grid": [row[:] for row in self.grid],
            "player_spawn": list(self.player_spawn),
            "portal": list(self.portal),
            "enemies": [list(e) for e in self.enemies],
            "barrels": [list(b) for b in self.barrels],
            "medkits": [list(m) for m in self.medkits],
            "pillars": [list(p) for p in self.pillars],
        }
        self.game.map.set_data(data)
        if hasattr(self.game, "apply_editor_map"):
            self.game.apply_editor_map()

    def save_map(self, path: str = None) -> bool:
        """Serialize current editor data to JSON file."""
        self.apply_to_game()
        filepath = path or DEFAULT_MAP_PATH
        success = self.game.map.save_to_file(filepath)
        if success:
            self.set_status(f"MAP SAVED: {filepath}", (50, 255, 120))
        else:
            self.set_status(f"FAILED TO SAVE: {filepath}", (255, 60, 60))
        return success

    def load_map(self, path: str = None) -> bool:
        """Load level data from JSON file into editor."""
        filepath = path or DEFAULT_MAP_PATH
        success = self.game.map.load_from_file(filepath)
        if success:
            self.sync_from_map()
            self.set_status(f"MAP LOADED: {filepath}", (100, 220, 255))
        else:
            self.set_status(f"FAILED TO LOAD: {filepath}", (255, 60, 60))
        return success

    def clear_interior(self):
        """Reset interior tiles to open floor and remove all non-player/portal entities."""
        for y in range(self.rows):
            for x in range(self.cols):
                if x == 0 or x == self.cols - 1 or y == 0 or y == self.rows - 1:
                    self.grid[y][x] = 1
                else:
                    self.grid[y][x] = 0
        self.enemies.clear()
        self.barrels.clear()
        self.medkits.clear()
        self.pillars.clear()
        self.player_spawn = [1.5, 1.5]
        self.portal = [14.5, 14.5]
        self.set_status("Interior cleared. Outer walls & spawns retained.", (255, 200, 50))

    def _remove_entities_at(self, gx: int, gy: int, keep_player: bool = False, keep_portal: bool = False):
        """Remove any entities residing within the specified grid cell."""
        self.enemies = [e for e in self.enemies if int(e[0]) != gx or int(e[1]) != gy]
        self.barrels = [b for b in self.barrels if int(b[0]) != gx or int(b[1]) != gy]
        self.medkits = [m for m in self.medkits if int(m[0]) != gx or int(m[1]) != gy]
        self.pillars = [p for p in self.pillars if int(p[0]) != gx or int(p[1]) != gy]

        if not keep_player and self.player_spawn and int(self.player_spawn[0]) == gx and int(self.player_spawn[1]) == gy:
            self.player_spawn = None

        if not keep_portal and self.portal and int(self.portal[0]) == gx and int(self.portal[1]) == gy:
            self.portal = None

    def paint_cell(self, gx: int, gy: int, button: int = 1):
        """Paint or erase a tile/entity at grid cell coordinates."""
        if not (0 <= gx < self.cols and 0 <= gy < self.rows):
            return

        is_outer_border = (gx == 0 or gx == self.cols - 1 or gy == 0 or gy == self.rows - 1)

        # Right click or 'erase' tool
        if button == 3 or self.selected_tool == "erase":
            # If an entity is here, remove it first
            has_ent = False
            if (self.player_spawn and int(self.player_spawn[0]) == gx and int(self.player_spawn[1]) == gy) or \
               (self.portal and int(self.portal[0]) == gx and int(self.portal[1]) == gy) or \
               any(int(e[0]) == gx and int(e[1]) == gy for e in self.enemies) or \
               any(int(b[0]) == gx and int(b[1]) == gy for b in self.barrels) or \
               any(int(m[0]) == gx and int(m[1]) == gy for m in self.medkits) or \
               any(int(p[0]) == gx and int(p[1]) == gy for p in self.pillars):
                has_ent = True
                self._remove_entities_at(gx, gy)
                self.set_status(f"Removed entity at ({gx}, {gy})", (255, 180, 50), 2000)

            # If no entity, clear wall to floor (outer border protected)
            if not has_ent:
                if is_outer_border:
                    self.set_status("Outer border wall cannot be erased!", (255, 80, 80), 2000)
                else:
                    self.grid[gy][gx] = 0
            return

        # Painting Wall Tiles
        if self.selected_tool.startswith("wall_"):
            wall_id = int(self.selected_tool.split("_")[1])
            self._remove_entities_at(gx, gy)
            self.grid[gy][gx] = wall_id

        elif self.selected_tool == "floor":
            if is_outer_border:
                self.set_status("Outer border must remain a solid wall!", (255, 80, 80), 2000)
            else:
                self._remove_entities_at(gx, gy)
                self.grid[gy][gx] = 0

        # Placing Entities (Player, Portal, Demon, Barrel, Medkit, Pillar)
        else:
            if is_outer_border:
                self.set_status("Entities cannot be placed on outer boundary!", (255, 80, 80), 2000)
                return

            # Clear wall to floor so entity has walkable ground
            self.grid[gy][gx] = 0
            self._remove_entities_at(gx, gy)

            cx = gx + 0.5
            cy = gy + 0.5

            if self.selected_tool == "player":
                self.player_spawn = [cx, cy]
                self.set_status(f"Player spawn set to ({gx}, {gy})", (0, 240, 255), 2500)

            elif self.selected_tool == "portal":
                self.portal = [cx, cy]
                self.set_status(f"Exit portal set to ({gx}, {gy})", (50, 255, 100), 2500)

            elif self.selected_tool == "demon":
                self.enemies.append([cx, cy])
                self.set_status(f"Demon placed at ({gx}, {gy}) [Total: {len(self.enemies)}]", (255, 80, 80), 2500)

            elif self.selected_tool == "barrel":
                self.barrels.append([cx, cy])
                self.set_status(f"Toxic barrel placed at ({gx}, {gy}) [Total: {len(self.barrels)}]", (80, 220, 80), 2500)

            elif self.selected_tool == "medkit":
                self.medkits.append([cx, cy])
                self.set_status(f"Medkit placed at ({gx}, {gy}) [Total: {len(self.medkits)}]", (240, 240, 240), 2500)

            elif self.selected_tool == "pillar":
                self.pillars.append([cx, cy])
                self.set_status(f"Pillar placed at ({gx}, {gy}) [Total: {len(self.pillars)}]", (180, 180, 190), 2500)

    def handle_event(self, event: pygame.event.Event):
        """Process mouse clicks, keyboard hotkeys and UI button interactions."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if event.button in (1, 3):
                # Check UI buttons click
                if event.button == 1:
                    for btn in self.buttons:
                        if btn["rect"].collidepoint(mx, my):
                            if btn["type"] == "tool":
                                self.selected_tool = btn["tool"]
                                self.set_status(f"Selected Tool: {btn['label']}", (255, 220, 100), 2000)
                                return
                            elif btn["type"] == "action":
                                self._trigger_action(btn["action"])
                                return

                # Check grid click
                if self.grid_x <= mx < self.grid_x + self.grid_w and self.grid_y <= my < self.grid_y + self.grid_h:
                    gx = (mx - self.grid_x) // self.cell_size
                    gy = (my - self.grid_y) // self.cell_size
                    self.is_painting = True
                    self.paint_button = event.button
                    self.last_painted_cell = (gx, gy)
                    self.paint_cell(gx, gy, event.button)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                self.is_painting = False
                self.last_painted_cell = None

        elif event.type == pygame.MOUSEMOTION:
            if self.is_painting:
                mx, my = event.pos
                if self.grid_x <= mx < self.grid_x + self.grid_w and self.grid_y <= my < self.grid_y + self.grid_h:
                    gx = (mx - self.grid_x) // self.cell_size
                    gy = (my - self.grid_y) // self.cell_size
                    if (gx, gy) != self.last_painted_cell:
                        self.last_painted_cell = (gx, gy)
                        self.paint_cell(gx, gy, self.paint_button)

        elif event.type == pygame.KEYDOWN:
            # Hotkeys for tools & actions
            if event.key == pygame.K_1:
                self.selected_tool = "wall_1"
                self.set_status("Tool: 1 (Brick Wall)", (255, 180, 50), 2000)
            elif event.key == pygame.K_2:
                self.selected_tool = "wall_2"
                self.set_status("Tool: 2 (Stone Wall)", (200, 200, 200), 2000)
            elif event.key == pygame.K_3:
                self.selected_tool = "wall_3"
                self.set_status("Tool: 3 (Tech Panel)", (50, 180, 255), 2000)
            elif event.key == pygame.K_4:
                self.selected_tool = "wall_4"
                self.set_status("Tool: 4 (Blood Wall)", (255, 60, 60), 2000)
            elif event.key in (pygame.K_0, pygame.K_BACKSPACE):
                self.selected_tool = "floor"
                self.set_status("Tool: 0 (Floor / Empty)", (180, 180, 180), 2000)
            elif event.key == pygame.K_p:
                self.selected_tool = "player"
                self.set_status("Tool: P (Player Spawn)", (0, 220, 255), 2000)
            elif event.key == pygame.K_e:
                self.selected_tool = "portal"
                self.set_status("Tool: E (Exit Portal)", (50, 255, 100), 2000)
            elif event.key == pygame.K_d:
                self.selected_tool = "demon"
                self.set_status("Tool: D (Demon Spawn)", (255, 80, 80), 2000)
            elif event.key == pygame.K_b:
                self.selected_tool = "barrel"
                self.set_status("Tool: B (Toxic Barrel)", (80, 220, 80), 2000)
            elif event.key == pygame.K_m:
                self.selected_tool = "medkit"
                self.set_status("Tool: M (Medkit)", (240, 240, 240), 2000)
            elif event.key == pygame.K_l:
                self.selected_tool = "pillar"
                self.set_status("Tool: L (Stone Pillar)", (180, 180, 190), 2000)
            elif event.key == pygame.K_x:
                self.selected_tool = "erase"
                self.set_status("Tool: X (Erase)", (255, 140, 40), 2000)
            elif event.key == pygame.K_s:
                self.save_map()
            elif event.key == pygame.K_o:
                self.load_map()
            elif event.key == pygame.K_c:
                self.clear_interior()
            elif event.key in (pygame.K_RETURN, pygame.K_F2, pygame.K_ESCAPE):
                self._trigger_action("playtest")

    def _trigger_action(self, action: str):
        """Execute toolbar action."""
        if action == "playtest":
            if not self.player_spawn:
                self.set_status("CANNOT PLAY: Player spawn is missing! Press 'P' to place one.", (255, 50, 50), 4000)
                return
            if not self.portal:
                self.set_status("WARNING: Exit portal is missing! Press 'E' to place exit.", (255, 160, 40), 3000)
            self.apply_to_game()
            self.game.close_editor(apply=True)
        elif action == "save":
            self.save_map()
        elif action == "load":
            self.load_map()
        elif action == "clear":
            self.clear_interior()

    def update(self):
        """Update editor timers and dynamic state."""
        if self.status_timer > 0:
            self.status_timer -= self.game.delta_time

    def draw(self, screen: pygame.Surface):
        """Render the complete level editor UI."""
        screen.fill((16, 17, 22))

        self._draw_grid(screen)
        self._draw_hud(screen)

    def _draw_grid(self, screen: pygame.Surface):
        """Render the 16x16 grid canvas with textured tiles, entities, and hover highlights."""
        mx, my = pygame.mouse.get_pos()
        hover_gx = (mx - self.grid_x) // self.cell_size
        hover_gy = (my - self.grid_y) // self.cell_size
        on_grid = (0 <= hover_gx < self.cols and 0 <= hover_gy < self.rows and
                   self.grid_x <= mx < self.grid_x + self.grid_w and
                   self.grid_y <= my < self.grid_y + self.grid_h)

        # Coordinate rulers (column labels top, row labels left)
        for i in range(self.cols):
            cx = self.grid_x + i * self.cell_size + self.cell_size // 2
            txt = self.font_micro.render(str(i), True, (100, 110, 125))
            screen.blit(txt, txt.get_rect(center=(cx, self.grid_y - 12)))

        for j in range(self.rows):
            cy = self.grid_y + j * self.cell_size + self.cell_size // 2
            txt = self.font_micro.render(str(j), True, (100, 110, 125))
            screen.blit(txt, txt.get_rect(center=(self.grid_x - 14, cy)))

        # Outer grid border frame
        pygame.draw.rect(
            screen,
            (70, 75, 90),
            (self.grid_x - 2, self.grid_y - 2, self.grid_w + 4, self.grid_h + 4),
            2,
            border_radius=4,
        )

        # Grid cells
        for j in range(self.rows):
            for i in range(self.cols):
                rect = pygame.Rect(
                    self.grid_x + i * self.cell_size,
                    self.grid_y + j * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                wall_val = self.grid[j][i]

                # Draw floor or wall texture
                if wall_val == 0:
                    pygame.draw.rect(screen, (28, 30, 36), rect)
                else:
                    if wall_val in self.wall_thumbnails:
                        screen.blit(self.wall_thumbnails[wall_val], rect.topleft)
                    else:
                        colors = {1: (160, 50, 40), 2: (110, 110, 110), 3: (40, 120, 160), 4: (150, 20, 20)}
                        pygame.draw.rect(screen, colors.get(wall_val, (80, 80, 80)), rect)

                # Thin grid cell border
                pygame.draw.rect(screen, (48, 52, 64), rect, 1)

        # Render Entities
        self._draw_entities(screen)

        # Hover cell indicator
        if on_grid:
            h_rect = pygame.Rect(
                self.grid_x + hover_gx * self.cell_size,
                self.grid_y + hover_gy * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            pygame.draw.rect(screen, (255, 230, 80), h_rect, 2)

    def _draw_entities(self, screen: pygame.Surface):
        """Draw player spawn, exit portal, demons, barrels, medkits and pillars on the grid."""
        # 1. Barrels
        for b in self.barrels:
            gx, gy = int(b[0]), int(b[1])
            cx = self.grid_x + gx * self.cell_size + self.cell_size // 2
            cy = self.grid_y + gy * self.cell_size + self.cell_size // 2
            pygame.draw.circle(screen, (30, 140, 45), (cx, cy), 13)
            pygame.draw.circle(screen, (80, 255, 60), (cx, cy), 11)
            pygame.draw.circle(screen, (15, 60, 20), (cx, cy), 5)
            lbl = self.font_micro.render("B", True, (255, 255, 255))
            screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # 2. Pillars
        for p in self.pillars:
            gx, gy = int(p[0]), int(p[1])
            cx = self.grid_x + gx * self.cell_size + self.cell_size // 2
            cy = self.grid_y + gy * self.cell_size + self.cell_size // 2
            pygame.draw.circle(screen, (120, 120, 130), (cx, cy), 13)
            pygame.draw.circle(screen, (70, 70, 80), (cx, cy), 10)
            lbl = self.font_micro.render("PIL", True, (220, 220, 230))
            screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # 3. Medkits
        for m in self.medkits:
            gx, gy = int(m[0]), int(m[1])
            rx = self.grid_x + gx * self.cell_size + 8
            ry = self.grid_y + gy * self.cell_size + 8
            pygame.draw.rect(screen, (235, 235, 240), (rx, ry, 24, 24), border_radius=3)
            pygame.draw.rect(screen, (50, 50, 60), (rx, ry, 24, 24), 1, border_radius=3)
            # Red cross
            cx = rx + 12
            cy = ry + 12
            pygame.draw.rect(screen, (220, 20, 30), (cx - 7, cy - 2, 14, 4))
            pygame.draw.rect(screen, (220, 20, 30), (cx - 2, cy - 7, 4, 14))

        # 4. Demons (Cacodemons)
        for e in self.enemies:
            gx, gy = int(e[0]), int(e[1])
            cx = self.grid_x + gx * self.cell_size + self.cell_size // 2
            cy = self.grid_y + gy * self.cell_size + self.cell_size // 2
            pygame.draw.circle(screen, (180, 25, 25), (cx, cy), 14)
            pygame.draw.circle(screen, (240, 50, 50), (cx, cy), 12)
            # Demon eye
            pygame.draw.circle(screen, (50, 10, 10), (cx, cy - 2), 6)
            pygame.draw.circle(screen, (255, 215, 0), (cx, cy - 2), 3)
            lbl = self.font_micro.render("DEM", True, (255, 255, 255))
            screen.blit(lbl, lbl.get_rect(center=(cx, cy + 6)))

        # 5. Exit Portal
        if self.portal:
            gx, gy = int(self.portal[0]), int(self.portal[1])
            cx = self.grid_x + gx * self.cell_size + self.cell_size // 2
            cy = self.grid_y + gy * self.cell_size + self.cell_size // 2
            pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1.0) * 0.5
            rad = int(12 + pulse * 3)
            pygame.draw.circle(screen, (20, 80, 40), (cx, cy), rad + 2)
            pygame.draw.circle(screen, (40, 230, 100), (cx, cy), rad)
            pygame.draw.circle(screen, (200, 255, 220), (cx, cy), max(2, rad - 6))
            lbl = self.font_micro.render("EXIT", True, (0, 40, 10))
            screen.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # 6. Player Spawn
        if self.player_spawn:
            gx, gy = int(self.player_spawn[0]), int(self.player_spawn[1])
            cx = self.grid_x + gx * self.cell_size + self.cell_size // 2
            cy = self.grid_y + gy * self.cell_size + self.cell_size // 2
            pygame.draw.circle(screen, (0, 140, 180), (cx, cy), 15)
            pygame.draw.circle(screen, (0, 230, 255), (cx, cy), 13)
            # Arrow indicator
            arrow_pts = [(cx + 10, cy), (cx + 3, cy - 5), (cx + 3, cy + 5)]
            pygame.draw.polygon(screen, (255, 255, 255), arrow_pts)
            lbl = self.font_micro.render("P", True, (0, 30, 50))
            screen.blit(lbl, lbl.get_rect(center=(cx - 3, cy)))

    def _draw_hud(self, screen: pygame.Surface):
        """Render titles, active tool banner, buttons, statistics, instructions, and status bar."""
        panel_x = 715
        mx, my = pygame.mouse.get_pos()

        # Title Header
        title = self.font_title.render("NOT-A-DOOM LEVEL EDITOR", True, (255, 215, 0))
        screen.blit(title, (panel_x, 35))
        sub = self.font_small.render("Paint 2D maps and test instantly in 3D (Press F2 or Enter)", True, (160, 170, 185))
        screen.blit(sub, (panel_x, 68))

        # Section 1 Header: WALL TILES
        sec1 = self.font_section.render("WALL TEXTURES & FLOOR:", True, (210, 220, 235))
        screen.blit(sec1, (panel_x, 90))

        # Section 2 Header: ENTITIES
        sec2 = self.font_section.render("ENTITIES & ITEMS:", True, (210, 220, 235))
        screen.blit(sec2, (panel_x, 185))

        # Section 3 Header: ACTIONS
        sec3 = self.font_section.render("ACTIONS & TOOLS:", True, (210, 220, 235))
        screen.blit(sec3, (panel_x, 278))

        # Draw all Buttons
        for btn in self.buttons:
            rect = btn["rect"]
            is_hovered = rect.collidepoint(mx, my)
            is_selected = (btn.get("tool") == self.selected_tool)

            bg_color = btn.get("hover_color", btn["color"]) if is_hovered else btn["color"]

            pygame.draw.rect(screen, bg_color, rect, border_radius=5)

            # Draw thumbnail preview if available
            tex_id = btn.get("tex_id")
            if tex_id and tex_id in self.btn_thumbnails:
                t_surf = self.btn_thumbnails[tex_id]
                screen.blit(t_surf, (rect.x + 5, rect.y + (rect.height - 30) // 2))
                txt_x = rect.x + 40
            else:
                txt_x = rect.x + 8

            # Highlight selected tool with glowing gold border
            if is_selected:
                pygame.draw.rect(screen, (255, 225, 60), rect, 3, border_radius=5)
            elif is_hovered:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=5)
            else:
                pygame.draw.rect(screen, (60, 65, 80), rect, 1, border_radius=5)

            # Label text
            txt_color = (255, 255, 255)
            lbl = self.font_btn.render(btn["label"], True, txt_color)
            if tex_id:
                screen.blit(lbl, (txt_x, rect.centery - lbl.get_height() // 2))
            else:
                screen.blit(lbl, lbl.get_rect(center=rect.center))

        # Section 4: Map Statistics & Validation Box
        stats_y = 405
        stats_rect = pygame.Rect(panel_x, stats_y, 525, 74)
        pygame.draw.rect(screen, (24, 26, 34), stats_rect, border_radius=6)
        pygame.draw.rect(screen, (55, 60, 75), stats_rect, 1, border_radius=6)

        p_status = "OK" if self.player_spawn else "MISSING [P]!"
        p_color = (0, 240, 255) if self.player_spawn else (255, 60, 60)
        e_status = "OK" if self.portal else "MISSING [E]!"
        e_color = (60, 240, 110) if self.portal else (255, 140, 40)

        s_line1 = f"Player: {p_status}   |   Exit Portal: {e_status}"
        s_line2 = f"Demons: {len(self.enemies)}   |   Barrels: {len(self.barrels)}   |   Medkits: {len(self.medkits)}   |   Pillars: {len(self.pillars)}"

        t_s1 = self.font_section.render(s_line1, True, (230, 230, 240))
        t_s2 = self.font_small.render(s_line2, True, (180, 190, 205))
        screen.blit(t_s1, (panel_x + 12, stats_y + 12))
        screen.blit(t_s2, (panel_x + 12, stats_y + 42))

        # Section 5: Cheat Sheet Controls
        guide_y = 490
        guide_lines = [
            "CONTROLS CHEAT SHEET:",
            "  * LMB / Drag: Paint selected wall or place entity",
            "  * RMB / Drag: Erase wall or remove entity",
            "  * 1, 2, 3, 4, 0: Wall textures (Brick, Stone, Tech, Blood) & Floor",
            "  * P, E, D, B, M, L: Player, Exit, Demon, Barrel, Medkit, Pillar",
            "  * S: Save map to level1.json   |   O: Reload from disk",
            "  * F2 or ENTER: Switch to 3D Game Playtest   |   F11: Fullscreen",
        ]
        gy = guide_y
        for i, line in enumerate(guide_lines):
            col = (255, 215, 0) if i == 0 else (150, 160, 175)
            font = self.font_section if i == 0 else self.font_small
            t = font.render(line, True, col)
            screen.blit(t, (panel_x + 4, gy))
            gy += 20

        # Section 6: Status Bar Notification Banner
        sb_rect = pygame.Rect(panel_x, 642, 525, 38)
        pygame.draw.rect(screen, (22, 24, 32), sb_rect, border_radius=5)
        pygame.draw.rect(screen, (50, 55, 70), sb_rect, 1, border_radius=5)

        # Coordinate tracker info
        mx, my = pygame.mouse.get_pos()
        gx = (mx - self.grid_x) // self.cell_size
        gy = (my - self.grid_y) // self.cell_size
        if 0 <= gx < self.cols and 0 <= gy < self.rows and self.grid_x <= mx < self.grid_x + self.grid_w and self.grid_y <= my < self.grid_y + self.grid_h:
            coord_str = f"Grid: ({gx}, {gy})"
        else:
            coord_str = "Grid: (--)"

        t_coord = self.font_small.render(coord_str, True, (130, 140, 155))
        screen.blit(t_coord, (panel_x + 440, 652))

        # Status text with timer
        if self.status_timer > 0:
            status_rendered = self.font_btn.render(self.status_text, True, self.status_color)
            screen.blit(status_rendered, (panel_x + 12, 652))
        else:
            default_status = self.font_small.render(f"Active Tool: {self.selected_tool.upper()}", True, (160, 170, 185))
            screen.blit(default_status, (panel_x + 12, 652))
