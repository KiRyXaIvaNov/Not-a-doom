"""
3D World Renderer for Not-a-Doom.
Handles skybox scrolling, distance fog/shading, wall projection, 2.5D sprite occlusion, and HUD overlays.
"""
import math
import pygame
from src.settings import (
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
)


class Renderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.textures = game.textures
        self.sky_offset = 0
        self.font_large = pygame.font.SysFont("impact", 48)
        self.font_small = pygame.font.SysFont("arial", 20, bold=True)

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
        """Render textured 3D wall slices with hardware clipping and instant O(1) pre-shaded texture lookup."""
        for depth, proj_height, texture_id, wall_x, ray, side in self.game.raycasting.ray_casting_result:
            depth_factor = 1.0 / (1.0 + depth * depth * 0.04)
            side_factor = 0.75 if side == 1 else 1.0
            brightness = max(0.1, min(1.0, depth_factor * side_factor))

            texture = self.textures.get_shaded_texture(texture_id, brightness)
            col_x = int(wall_x * (TEXTURE_SIZE - 1))

            if proj_height < HEIGHT:
                slice_height = int(proj_height)
                screen_y = HALF_HEIGHT - slice_height // 2
                wall_slice = texture.subsurface(col_x, 0, 1, TEXTURE_SIZE)
                wall_column = pygame.transform.scale(wall_slice, (SCALE, slice_height))
            else:
                slice_height = HEIGHT
                screen_y = 0
                texture_height_factor = HEIGHT / proj_height
                sub_y = int((1.0 - texture_height_factor) * 0.5 * TEXTURE_SIZE)
                sub_h = int(texture_height_factor * TEXTURE_SIZE)
                sub_y = max(0, min(TEXTURE_SIZE - 1, sub_y))
                sub_h = max(1, min(TEXTURE_SIZE - sub_y, sub_h))
                wall_slice = texture.subsurface(col_x, sub_y, 1, sub_h)
                wall_column = pygame.transform.scale(wall_slice, (SCALE, HEIGHT))

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
                sx = map_x + int(sp.x * scale)
                sy = map_y + int(sp.y * scale)
                color = (0, 255, 200) if sp.name == "portal" else (50, 220, 50) if sp.name == "barrel" else (220, 50, 50) if sp.name == "medkit" else (200, 150, 50)
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
            flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((220, 20, 20, alpha))
            self.screen.blit(flash_surf, (0, 0))

    def draw_hud(self):
        """Draw player health bar and numerical status at top-left."""
        if not hasattr(self.game, 'player'):
            return
        hp = self.game.player.hp
        max_hp = self.game.player.max_hp

        # HUD Panel background
        panel_w, panel_h = 220, 52
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((14, 14, 20, 210))
        self.screen.blit(panel_surf, (16, 16))

        # Health Text
        text_col = (50, 220, 80) if hp > 50 else (240, 200, 40) if hp > 25 else (240, 50, 50)
        hp_text = self.font_small.render(f"HEALTH: {hp}%", True, text_col)
        self.screen.blit(hp_text, (26, 20))

        # Health bar background
        bar_x, bar_y = 26, 44
        bar_w, bar_h = 196, 14
        pygame.draw.rect(self.screen, (40, 40, 48), (bar_x, bar_y, bar_w, bar_h))

        # Health bar fill
        fill_w = int((hp / max_hp) * bar_w)
        if fill_w > 0:
            bar_col = (40, 200, 60) if hp > 50 else (230, 180, 40) if hp > 25 else (220, 30, 30)
            pygame.draw.rect(self.screen, bar_col, (bar_x, bar_y, fill_w, bar_h))

        # Border
        pygame.draw.rect(self.screen, (100, 100, 120), (bar_x, bar_y, bar_w, bar_h), 1)

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
        sub2 = self.font_small.render("Press Q to Quit", True, (200, 200, 200))

        self.screen.blit(title, title.get_rect(center=(HALF_WIDTH, HALF_HEIGHT - 40)))
        self.screen.blit(sub1, sub1.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 20)))
        self.screen.blit(sub2, sub2.get_rect(center=(HALF_WIDTH, HALF_HEIGHT + 55)))

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
        self.draw_hud()
        self.draw_minimap()

        if hasattr(self.game, 'victory') and self.game.victory:
            self.draw_victory_screen()
        elif hasattr(self.game, 'player') and not self.game.player.alive:
            self.draw_death_screen()
        elif not self.game.mouse_grabbed:
            self.draw_pause_overlay()
