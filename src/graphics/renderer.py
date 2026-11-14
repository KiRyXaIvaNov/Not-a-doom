"""
3D World Renderer for Not-a-Doom.
Handles skybox scrolling, distance fog/shading, wall projection, 2.5D sprite occlusion, and HUD overlays.
"""
import math
import pygame
from src.core.settings import (
    WIDTH,
    HEIGHT,
    HALF_WIDTH,
    HALF_HEIGHT,
    FLOOR_COLOR,
    SCALE,
    TEXTURE_SIZE,
    WHITE,
    RED,
    GREEN,
    HUD_HEIGHT,
)
from src.graphics.face import DoomFace


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.textures = game.textures
        self.sky_offset = 0
        self.font_large = pygame.font.SysFont("impact", 48)
        self.font_small = pygame.font.SysFont("arial", 20, bold=True)
        self.font_hud_big = pygame.font.SysFont("impact", 42)
        self.font_hud_label = pygame.font.SysFont("arial", 13, bold=True)
        self.font_hud_arms = pygame.font.SysFont("impact", 32)
        self.font_hud_ammo = pygame.font.SysFont("consolas", 14, bold=True)

        self.doom_face = DoomFace(game)
        self.hud_bg = self._create_hud_background()
        self.damage_flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.damage_flash_surf.fill((220, 20, 20))
        self.heal_flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.heal_flash_surf.fill((40, 220, 90))

    def draw_background(self):
        """Draw panoramic scrolling sky and dark retro floor."""
        self.sky_offset = -int((self.game.player.angle / math.tau) * WIDTH) % WIDTH
        self.screen.blit(self.textures.sky, (self.sky_offset, 0))
        self.screen.blit(self.textures.sky, (self.sky_offset - WIDTH, 0))

        # Dark floor
        pygame.draw.rect(
            self.screen,
            FLOOR_COLOR,
            (0, HALF_HEIGHT, WIDTH, HALF_HEIGHT),
        )

    def render_walls(self):
        """Render textured 3D wall slices with sub-pixel stability and instant O(1) pre-shaded texture lookup."""
        for depth, proj_height, texture_id, wall_x, ray, side in self.game.raycasting.ray_casting_result:
            depth_factor = 1.0 / (1.0 + depth * depth * 0.04)
            side_factor = 0.75 if side == 1 else 1.0
            brightness = max(0.1, min(1.0, depth_factor * side_factor))

            texture = self.textures.get_shaded_texture(texture_id, brightness)

            # Uniform texture column mapping across [0..TEXTURE_SIZE)
            col_x = int(wall_x * TEXTURE_SIZE) % TEXTURE_SIZE

            # Direct full-column scaling: eliminates integer subsurface crop jitter (sawtooth wavy artifact).
            # Enforce even slice height to lock center to HALF_HEIGHT and remove 0.5px odd/even parity oscillation.
            # Safe upper bound prevents out-of-memory allocations during collision edge cases.
            slice_height = max(2, min(int(proj_height), 5000))
            if slice_height % 2 != 0:
                slice_height += 1
            screen_y = HALF_HEIGHT - slice_height // 2

            wall_slice = texture.subsurface(col_x, 0, 1, TEXTURE_SIZE)
            wall_column = pygame.transform.scale(wall_slice, (SCALE, slice_height))

            screen_x = ray * SCALE
            self.screen.blit(wall_column, (screen_x, screen_y))

    def draw_crosshair(self):
        """Draw minimalist classic shooter crosshair in center."""
        cx, cy = HALF_WIDTH, HALF_HEIGHT
        size = 6
        gap = 3
        pygame.draw.line(self.screen, (0, 255, 0), (cx - size - gap, cy), (cx - gap, cy), 2)
        pygame.draw.line(self.screen, (0, 255, 0), (cx + gap, cy), (cx + size + gap, cy), 2)
        pygame.draw.line(self.screen, (0, 255, 0), (cx, cy - size - gap), (cx, cy - gap), 2)
        pygame.draw.line(self.screen, (0, 255, 0), (cx, cy + gap), (cx, cy + size + gap), 2)

    def draw_minimap(self):
        """Draw semi-transparent 2D radar minimap with wall markers and prop icons."""
        scale = 6
        map_w = self.game.map.cols * scale
        map_h = self.game.map.rows * scale
        pad = 12
        map_x = WIDTH - map_w - pad
        map_y = pad

        # Background panel
        bg_surf = pygame.Surface((map_w + 4, map_h + 4), pygame.SRCALPHA)
        bg_surf.fill((10, 10, 15, 180))
        self.screen.blit(bg_surf, (map_x - 2, map_y - 2))

        # Walls
        for (gx, gy) in self.game.map.world_map:
            rect = (map_x + gx * scale, map_y + gy * scale, scale, scale)
            pygame.draw.rect(self.screen, (100, 100, 120), rect)

        # Props on minimap
        if hasattr(self.game, 'sprite_manager'):
            for sp in self.game.sprite_manager.sprite_list:
                if getattr(sp, 'is_picked_up', False):
                    continue
                sx = map_x + int(sp.x * scale)
                sy = map_y + int(sp.y * scale)
                color = (0, 255, 200) if sp.name == "portal" else ((70, 70, 70) if getattr(sp, "is_exploded", False) else (50, 220, 50)) if sp.name == "barrel" else (220, 50, 50) if sp.name == "medkit" else (200, 150, 50)
                rad = 3 if sp.name == "portal" else 2
                pygame.draw.circle(self.screen, color, (sx, sy), rad)

        # Enemies on minimap (pulsing demonic red markers)
        if hasattr(self.game, 'enemy_manager'):
            pulse = (math.sin(pygame.time.get_ticks() * 0.007) + 1.0) * 0.5
            rad = int(2.5 + pulse * 1.5)
            for en in self.game.enemy_manager.enemies:
                if en.alive:
                    ex = map_x + int(en.x * scale)
                    ey = map_y + int(en.y * scale)
                    pygame.draw.circle(self.screen, (255, 30, 40), (ex, ey), rad)
                    pygame.draw.circle(self.screen, (255, 220, 220), (ex, ey), 1)
                elif en.is_dead or en.is_dying:
                    ex = map_x + int(en.x * scale)
                    ey = map_y + int(en.y * scale)
                    pygame.draw.circle(self.screen, (100, 15, 15), (ex, ey), 2)

        # Projectiles on minimap (flying orange plasma dots)
        if hasattr(self.game, 'projectile_manager'):
            for proj in self.game.projectile_manager.projectiles:
                if proj.alive:
                    fx = map_x + int(proj.x * scale)
                    fy = map_y + int(proj.y * scale)
                    pygame.draw.circle(self.screen, (255, 140, 20), (fx, fy), 2)

        # Player icon & direction line
        px = map_x + int(self.game.player.x * scale)
        py = map_y + int(self.game.player.y * scale)
        pygame.draw.circle(self.screen, (0, 255, 255), (px, py), 3)

        dir_len = 10
        end_x = px + int(math.cos(self.game.player.angle) * dir_len)
        end_y = py + int(math.sin(self.game.player.angle) * dir_len)
        pygame.draw.line(self.screen, (255, 255, 0), (px, py), (end_x, end_y), 2)

    def draw_damage_flash(self):
        """Draw full-screen red damage flash with smooth alpha fade."""
        if hasattr(self.game, 'player') and self.game.player.damage_alpha > 0.0:
            alpha = int(min(255, self.game.player.damage_alpha))
            self.damage_flash_surf.set_alpha(alpha)
            self.screen.blit(self.damage_flash_surf, (0, 0))

    def draw_heal_flash(self):
        """Draw soothing green/gold screen tint on health pickup."""
        if hasattr(self.game, 'player') and getattr(self.game.player, 'heal_alpha', 0.0) > 0.0:
            alpha = int(min(255, self.game.player.heal_alpha))
            self.heal_flash_surf.set_alpha(alpha)
            self.screen.blit(self.heal_flash_surf, (0, 0))

    def _create_hud_background(self) -> pygame.Surface:
        """Pre-bake metallic stone status bar base texture and beveled inset frames."""
        surf = pygame.Surface((WIDTH, HUD_HEIGHT))
        surf.fill((52, 54, 58))

        # 3D Top bevel
        pygame.draw.line(surf, (125, 130, 140), (0, 0), (WIDTH, 0), 2)
        pygame.draw.line(surf, (85, 90, 98), (0, 2), (WIDTH, 2), 1)
        pygame.draw.line(surf, (38, 40, 44), (0, 3), (WIDTH, 3), 1)
        pygame.draw.line(surf, (18, 18, 20), (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1), 1)

        def draw_inset_box(rect, bg_col=(18, 18, 22)):
            x, y, w, h = rect
            pygame.draw.rect(surf, bg_col, rect)
            pygame.draw.line(surf, (12, 12, 15), (x, y), (x + w - 1, y), 2)
            pygame.draw.line(surf, (12, 12, 15), (x, y), (x, y + h - 1), 2)
            pygame.draw.line(surf, (85, 90, 100), (x, y + h - 1), (x + w - 1, y + h - 1), 1)
            pygame.draw.line(surf, (85, 90, 100), (x + w - 1, y), (x + w - 1, y + h - 1), 1)

        def draw_divider(x):
            pygame.draw.line(surf, (22, 23, 26), (x, 0), (x, HUD_HEIGHT), 2)
            pygame.draw.line(surf, (90, 95, 105), (x + 2, 0), (x + 2, HUD_HEIGHT), 1)

        # Dividers
        draw_divider(180)
        draw_divider(420)
        draw_divider(576)
        draw_divider(702)
        draw_divider(942)

        # Inset boxes for content
        draw_inset_box((14, 10, 152, 50))    # AMMO
        draw_inset_box((194, 10, 212, 50))   # HEALTH
        draw_inset_box((434, 10, 130, 50))   # ARMS
        draw_inset_box((596, 6, 88, 76), bg_col=(14, 14, 18))  # FACE
        draw_inset_box((716, 10, 212, 50))   # ARMOR
        draw_inset_box((954, 8, 314, 72))    # AMMO TABLE

        # Static section labels
        lbl_ammo = self.font_hud_label.render("AMMO", True, (160, 165, 175))
        surf.blit(lbl_ammo, lbl_ammo.get_rect(center=(90, 72)))

        lbl_health = self.font_hud_label.render("HEALTH", True, (160, 165, 175))
        surf.blit(lbl_health, lbl_health.get_rect(center=(300, 72)))

        lbl_arms = self.font_hud_label.render("ARMS", True, (160, 165, 175))
        surf.blit(lbl_arms, lbl_arms.get_rect(center=(499, 72)))

        lbl_armor = self.font_hud_label.render("ARMOR", True, (160, 165, 175))
        surf.blit(lbl_armor, lbl_armor.get_rect(center=(822, 72)))

        return surf

    def draw_hud(self):
        """Draw authentic classic DOOM bottom status bar strip across full screen width."""
        hud_y = HEIGHT - HUD_HEIGHT
        self.screen.blit(self.hud_bg, (0, hud_y))

        # Update animated face
        self.doom_face.update()

        player = getattr(self.game, 'player', None)
        hp = player.hp if player else 100
        weapon = getattr(self.game, 'weapon', None)
        active_slot = getattr(weapon, 'slot', 1)

        # 1. AMMO: active weapon ammo placeholder (e.g. 50 for pistol, 16 for shotgun)
        ammo_count = 50 if active_slot == 1 else 16
        ammo_str = str(ammo_count)
        txt_sh = self.font_hud_big.render(ammo_str, True, (80, 8, 8))
        txt = self.font_hud_big.render(ammo_str, True, (225, 20, 20))
        self.screen.blit(txt_sh, txt_sh.get_rect(center=(90 + 2, hud_y + 35 + 2)))
        self.screen.blit(txt, txt.get_rect(center=(90, hud_y + 35)))

        # 2. HEALTH: actual player health percentage
        hp_str = f"{max(0, hp)}%"
        hp_col = (225, 20, 20) if hp > 25 else (255, 30, 30)
        hp_sh = self.font_hud_big.render(hp_str, True, (80, 8, 8))
        hp_txt = self.font_hud_big.render(hp_str, True, hp_col)
        self.screen.blit(hp_sh, hp_sh.get_rect(center=(300 + 2, hud_y + 35 + 2)))
        self.screen.blit(hp_txt, hp_txt.get_rect(center=(300, hud_y + 35)))

        # 3. ARMS: weapon slots as digits (1: Pistol, 2: Shotgun)
        # Slot 1
        s1_box = pygame.Rect(442, hud_y + 13, 52, 44)
        s1_bg = (30, 28, 20) if active_slot == 1 else (20, 20, 22)
        pygame.draw.rect(self.screen, s1_bg, s1_box)
        pygame.draw.rect(self.screen, (70, 65, 50) if active_slot == 1 else (40, 40, 45), s1_box, 1)
        s1_col = (255, 235, 40) if active_slot == 1 else (105, 95, 80)
        s1_txt = self.font_hud_arms.render("1", True, s1_col)
        self.screen.blit(s1_txt, s1_txt.get_rect(center=s1_box.center))

        # Slot 2
        s2_box = pygame.Rect(504, hud_y + 13, 52, 44)
        s2_bg = (30, 28, 20) if active_slot == 2 else (20, 20, 22)
        pygame.draw.rect(self.screen, s2_bg, s2_box)
        pygame.draw.rect(self.screen, (70, 65, 50) if active_slot == 2 else (40, 40, 45), s2_box, 1)
        s2_col = (255, 235, 40) if active_slot == 2 else (105, 95, 80)
        s2_txt = self.font_hud_arms.render("2", True, s2_col)
        self.screen.blit(s2_txt, s2_txt.get_rect(center=s2_box.center))

        # 4. FACE: animated Doom Marine face
        face_surf = self.doom_face.get_surface()
        self.screen.blit(face_surf, (608, hud_y + 8))

        # 5. ARMOR: 100% placeholder
        arm_str = "100%"
        arm_sh = self.font_hud_big.render(arm_str, True, (80, 8, 8))
        arm_txt = self.font_hud_big.render(arm_str, True, (225, 20, 20))
        self.screen.blit(arm_sh, arm_sh.get_rect(center=(822 + 2, hud_y + 35 + 2)))
        self.screen.blit(arm_txt, arm_txt.get_rect(center=(822, hud_y + 35)))

        # 6. AMMO TABLE: breakdown of ammo reserves
        ammo_rows = [
            ("BULL", "50", "200"),
            ("SHEL", "16", "50"),
            ("RCKT", "0", "50"),
            ("CELL", "0", "300"),
        ]
        for idx, (lbl_txt, cur_v, max_v) in enumerate(ammo_rows):
            ry = hud_y + 13 + idx * 17
            t_lbl = self.font_hud_ammo.render(lbl_txt, True, (225, 195, 45))
            self.screen.blit(t_lbl, (970, ry))

            t_cur = self.font_hud_ammo.render(cur_v.rjust(3), True, (255, 240, 70))
            self.screen.blit(t_cur, (1050, ry))

            t_sl = self.font_hud_ammo.render("/", True, (140, 145, 155))
            self.screen.blit(t_sl, (1120, ry))

            t_max = self.font_hud_ammo.render(max_v.rjust(3), True, (255, 240, 70))
            self.screen.blit(t_max, (1160, ry))

    def draw_death_screen(self):
        """Show dramatic retro Game Over overlay when player dies."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((120, 10, 15, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("YOU DIED", True, (255, 30, 40))
        sub = self.font_small.render("Press R to Respawn", True, (240, 240, 240))

        self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 30)))
        self.screen.blit(sub, sub.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 25)))

    def draw_victory_screen(self):
        """Show retro DOOM-style intermission victory screen with level stats."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 28, 20, 220))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("LEVEL COMPLETED!", True, (255, 215, 0))
        self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 120)))

        # Stats calculation
        total_demons = len(self.game.enemy_manager.enemies)
        dead_demons = sum(1 for e in self.game.enemy_manager.enemies if e.is_dead or not e.alive)
        kill_pct = int((dead_demons / total_demons * 100)) if total_demons else 100

        lines = [
            f"KILLS: {dead_demons} / {total_demons} ({kill_pct}%)",
            f"TIME: {self.game.elapsed_time_str}",
            f"HEALTH REMAINING: {self.game.player.hp}%",
        ]

        y_offset = HALF_HEIGHT - 35
        for line in lines:
            rendered = self.font_small.render(line, True, (230, 245, 235))
            self.screen.blit(rendered, rendered.get_rect(center=(HALF_WIDTH, y_offset)))
            y_offset += 40

        prompt = self.font_small.render("PRESS ENTER OR SPACE TO PLAY AGAIN", True, (0, 255, 200))
        self.screen.blit(prompt, prompt.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 120)))

    def draw_pause_overlay(self):
        """Darken screen and show pause instructions."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title = self.font_large.render("PAUSED", True, (255, 215, 0))
        sub1 = self.font_small.render("Press ESC or Click to Resume", True, (240, 240, 240))
        sub_wpn = self.font_small.render("1: Pistol | 2: Shotgun | Q / Wheel: Switch Weapon", True, (255, 215, 80))
        sub2 = self.font_small.render("Press F2 for Level Editor", True, (255, 200, 50))
        sub3 = self.font_small.render("Press F11 for Fullscreen", True, (0, 220, 255))
        sub4 = self.font_small.render("Press Q to Quit", True, (200, 200, 200))

        self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 80)))
        self.screen.blit(sub1, sub1.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 25)))
        self.screen.blit(sub_wpn, sub_wpn.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 5)))
        self.screen.blit(sub2, sub2.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 35)))
        self.screen.blit(sub3, sub3.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 65)))
        self.screen.blit(sub4, sub4.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 95)))

    def draw(self):
        self.draw_background()
        self.render_walls()

        # Render 2.5D billboard sprites with Z-buffer depth test
        if hasattr(self.game, 'sprite_manager'):
            self.game.sprite_manager.render(self.screen)

        # Render 3D blood splatters and sparks with Z-buffer depth test
        if hasattr(self.game, 'particle_manager'):
            self.game.particle_manager.render(self.screen)

        self.draw_crosshair()

        # Draw weapon in foreground
        if hasattr(self.game, 'weapon'):
            self.game.weapon.draw(self.screen)

        self.draw_damage_flash()
        self.draw_heal_flash()
        self.draw_hud()
        self.draw_minimap()

        if hasattr(self.game, 'victory') and self.game.victory:
            self.draw_victory_screen()
        elif hasattr(self.game, 'player') and not self.game.player.alive:
            self.draw_death_screen()
        elif not self.game.mouse_grabbed:
            self.draw_pause_overlay()
