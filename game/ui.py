import pygame
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME, FONT_SIZE_SMALL,
    FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_XLARGE, FONT_SIZE_TITLE,
    PANEL_BG_COLOR, PANEL_BORDER_COLOR, PANEL_HIGHLIGHT_COLOR,
    PANEL_SHADOW_COLOR, PANEL_RADIUS, BUTTON_BG, BUTTON_BORDER,
    BUTTON_HOVER_BORDER, BUTTON_HOVER_BG, BUTTON_RADIUS,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_ACCENT, TEXT_DIM,
    hsv_to_rgb, lerp_color
)


class FontCache:
    _fonts = {}

    @classmethod
    def get(cls, size, bold=False, name=None):
        key = (name or FONT_NAME, size, bold)
        if key not in cls._fonts:
            try:
                font = pygame.font.SysFont(name or FONT_NAME, size, bold=bold)
            except:
                font = pygame.font.Font(None, size)
            cls._fonts[key] = font
        return cls._fonts[key]


class RoundedRect:
    @staticmethod
    def draw(surface, rect, color, radius, border_width=0, border_color=None):
        r = min(radius, min(rect.width, rect.height) // 2)
        pygame.draw.rect(surface, color, rect, border_radius=r)
        if border_width > 0 and border_color:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=r)

    @staticmethod
    def draw_alpha(surface, rect, color, radius):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        r = min(radius, min(rect.width, rect.height) // 2)
        pygame.draw.rect(s, color, (0, 0, rect.width, rect.height), border_radius=r)
        surface.blit(s, rect.topleft)


class GlowBorder:
    @staticmethod
    def draw(surface, rect, color, radius, width=2, glow_size=6):
        for i in range(glow_size, 0, -1):
            alpha = int(30 * (1 - i / glow_size))
            r = min(radius + i, min(rect.width, rect.height) // 2 + i)
            pygame.draw.rect(surface, (*color[:3], alpha),
                           rect.inflate(i * 2, i * 2), width, border_radius=r)
        pygame.draw.rect(surface, (*color[:3], min(255, color[3] if len(color) > 3 else 180)),
                       rect, width, border_radius=min(radius, min(rect.width, rect.height) // 2))


class Panel:
    def __init__(self, rect, bg_color=None, border_color=None,
                 radius=None, shadow=True):
        self.rect = pygame.Rect(rect)
        self.bg_color = bg_color or PANEL_BG_COLOR
        self.border_color = border_color or PANEL_BORDER_COLOR
        self.radius = radius if radius is not None else PANEL_RADIUS
        self.shadow_enabled = shadow
        self.alpha = 0
        self.target_alpha = 255
        self.fade_speed = 10
        self.time = 0.0
        self.anim_offset_y = 0
        self.target_offset_y = 0

    def set_fade(self, target):
        self.target_alpha = target

    def is_visible(self):
        return self.alpha > 5

    def update(self, dt):
        self.time += dt
        diff = self.target_alpha - self.alpha
        if abs(diff) > 1:
            self.alpha += diff * dt * 12
        else:
            self.alpha = self.target_alpha

        self.anim_offset_y += (self.target_offset_y - self.anim_offset_y) * dt * 10

    def draw(self, surface):
        if self.alpha <= 0:
            return

        rect = self.rect.copy()
        rect.y += int(self.anim_offset_y)

        alpha_mult = self.alpha / 255

        if self.shadow_enabled:
            shadow_rect = rect.copy()
            shadow_rect.y += 6
            s = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            sa = int(50 * alpha_mult)
            pygame.draw.rect(s, (*PANEL_SHADOW_COLOR[:3], sa),
                           (0, 0, shadow_rect.width, shadow_rect.height),
                           border_radius=self.radius)
            surface.blit(s, shadow_rect.topleft)

        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        bg = self.bg_color
        bg_alpha = int((bg[3] if len(bg) > 3 else 180) * alpha_mult)
        pygame.draw.rect(s, (*bg[:3], bg_alpha),
                        (0, 0, rect.width, rect.height),
                        border_radius=self.radius)

        if self.border_color:
            bc = self.border_color
            b_alpha = int((bc[3] if len(bc) > 3 else 180) * alpha_mult)
            pygame.draw.rect(s, (*bc[:3], b_alpha),
                           (0, 0, rect.width, rect.height),
                           max(1, int(1.5)), border_radius=self.radius)

        hc = PANEL_HIGHLIGHT_COLOR
        ha = int(hc[3] * alpha_mult)
        if ha > 2:
            hr = pygame.Rect(0, 0, rect.width, rect.height // 2)
            for y in range(hr.height):
                t = 1 - y / hr.height
                a = int(ha * t * 0.4)
                if a > 0:
                    pygame.draw.line(s, (*hc[:3], a), (0, y), (hr.width, y))

        surface.blit(s, rect.topleft)


class Button:
    def __init__(self, rect, text, font_size=None, on_click=None,
                 bg_color=None, border_color=None,
                 hover_border_color=None, hover_bg_color=None,
                 text_color=None, accent=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font_size = font_size or FONT_SIZE_MEDIUM
        self.on_click = on_click
        self.bg_color = bg_color or BUTTON_BG
        self.border_color = border_color or BUTTON_BORDER
        self.hover_border_color = hover_border_color or BUTTON_HOVER_BORDER
        self.hover_bg_color = hover_bg_color or BUTTON_HOVER_BG
        self.text_color = text_color or TEXT_PRIMARY
        self.hover_text_color = TEXT_ACCENT
        self.accent = accent

        self.hover = False
        self.hover_progress = 0.0
        self.click_scale = 1.0
        self.target_click_scale = 1.0
        self.alpha = 0
        self.target_alpha = 255
        self.fade_speed = 10
        self.time = 0.0
        self.anim_offset_y = 0
        self.target_offset_y = 0

    def set_fade(self, target):
        self.target_alpha = target

    def handle_event(self, event):
        if self.alpha < 30:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.target_click_scale = 0.92
                if self.on_click:
                    self.on_click()
                return True
        return False

    def update(self, dt):
        self.time += dt
        diff = self.target_alpha - self.alpha
        if abs(diff) > 1:
            self.alpha += diff * dt * 12
        else:
            self.alpha = self.target_alpha

        target_progress = 1.0 if self.hover else 0.0
        self.hover_progress += (target_progress - self.hover_progress) * dt * 15
        self.hover_progress = max(0, min(1, self.hover_progress))

        self.click_scale += (self.target_click_scale - self.click_scale) * dt * 25
        if abs(self.click_scale - 1.0) < 0.01:
            self.click_scale = 1.0
            self.target_click_scale = 1.0

        self.anim_offset_y += (self.target_offset_y - self.anim_offset_y) * dt * 10

    def draw(self, surface):
        if self.alpha <= 0:
            return

        alpha_mult = self.alpha / 255
        scale = self.click_scale
        sw = int(self.rect.width * scale)
        sh = int(self.rect.height * scale)
        sx = self.rect.centerx - sw // 2
        sy = self.rect.centery - sh // 2 + int(self.anim_offset_y)
        rect = pygame.Rect(sx, sy, sw, sh)

        r = BUTTON_RADIUS

        bg_color = (
            int(self.bg_color[0] + (self.hover_bg_color[0] - self.bg_color[0]) * self.hover_progress),
            int(self.bg_color[1] + (self.hover_bg_color[1] - self.bg_color[1]) * self.hover_progress),
            int(self.bg_color[2] + (self.hover_bg_color[2] - self.bg_color[2]) * self.hover_progress),
        )
        bc_color = (
            int(self.border_color[0] + (self.hover_border_color[0] - self.border_color[0]) * self.hover_progress),
            int(self.border_color[1] + (self.hover_border_color[1] - self.border_color[1]) * self.hover_progress),
            int(self.border_color[2] + (self.hover_border_color[2] - self.border_color[2]) * self.hover_progress),
        )

        bg_alpha = int(self.bg_color[3] * alpha_mult)
        border_alpha = int(255 * alpha_mult) if len(self.border_color) == 3 else \
                       int(self.border_color[3] * alpha_mult)

        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        if self.hover_progress > 0.01:
            glow_intensity = int(60 * self.hover_progress * alpha_mult)
            for i in range(5, 0, -1):
                ga = glow_intensity // (6 - i)
                gr = r + i
                pygame.draw.rect(s, (*bc_color[:3], ga),
                               (-i, -i, rect.width + i * 2, rect.height + i * 2),
                               border_radius=gr)

        pygame.draw.rect(s, (*bg_color, bg_alpha),
                        (0, 0, rect.width, rect.height),
                        border_radius=r)

        bw = max(1, int(2 + self.hover_progress * 1.5))
        pygame.draw.rect(s, (*bc_color[:3], border_alpha),
                        (0, 0, rect.width, rect.height),
                        bw, border_radius=r)

        txt_color = lerp_color(self.text_color[:3], self.hover_text_color[:3],
                               self.hover_progress)
        font = FontCache.get(self.font_size)
        text = font.render(self.text, True, txt_color)
        text.set_alpha(int(255 * alpha_mult))
        tr = text.get_rect(center=(rect.width // 2, rect.height // 2))
        s.blit(text, tr)
        surface.blit(s, rect.topleft)


class TextLabel:
    def __init__(self, text, font_size, color=None, center=None,
                 topleft=None, midtop=None, topright=None, midleft=None):
        self.text = text
        self.font_size = font_size
        self.color = color or TEXT_PRIMARY
        self.center = center
        self.topleft = topleft
        self.midtop = midtop
        self.topright = topright
        self.midleft = midleft
        self.alpha = 255
        self.target_alpha = 255
        self.time = 0.0

    def set_fade(self, target):
        self.target_alpha = target

    def update(self, dt):
        self.time += dt
        diff = self.target_alpha - self.alpha
        if abs(diff) > 1:
            self.alpha += diff * dt * 12
        else:
            self.alpha = self.target_alpha

    def draw(self, surface, text_override=None):
        text = text_override or self.text
        font = FontCache.get(self.font_size)
        alpha = int(self.alpha)
        rendered = font.render(text, True, self.color[:3])
        rendered.set_alpha(alpha)

        if self.center:
            rect = rendered.get_rect(center=self.center)
        elif self.topleft:
            rect = rendered.get_rect(topleft=self.topleft)
        elif self.midtop:
            rect = rendered.get_rect(midtop=self.midtop)
        elif self.topright:
            rect = rendered.get_rect(topright=self.topright)
        elif self.midleft:
            rect = rendered.get_rect(midleft=self.midleft)
        else:
            rect = rendered.get_rect()

        surface.blit(rendered, rect)
        return rect


class HUD:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.gm = game_manager
        self.time = 0.0

        bar_h = 56
        self.bar = Panel(pygame.Rect(0, 0, SCREEN_WIDTH, bar_h),
                        bg_color=(5, 5, 10, 180),
                        border_color=(255, 255, 255, 10),
                        radius=0, shadow=False)
        self.bar.set_fade(255)

        self.score_label = TextLabel('0', FONT_SIZE_LARGE, TEXT_ACCENT,
                                   topleft=(30, -2))
        self.score_prefix = TextLabel('SCORE', FONT_SIZE_SMALL, TEXT_SECONDARY,
                                    topleft=(30, 26))

        self.best_label = TextLabel('0', FONT_SIZE_LARGE, TEXT_PRIMARY,
                                  topright=(SCREEN_WIDTH - 30, -2))
        self.best_prefix = TextLabel('BEST', FONT_SIZE_SMALL, TEXT_SECONDARY,
                                   topright=(SCREEN_WIDTH - 30, 26))

        speed_x = SCREEN_WIDTH // 2
        self.speed_label = TextLabel('SPEED 1.0x', FONT_SIZE_MEDIUM, TEXT_DIM,
                                   center=(speed_x, 14))
        self.diff_label = TextLabel('NORMAL', FONT_SIZE_SMALL, TEXT_DIM,
                                  center=(speed_x, 38))

    def update(self, dt):
        self.time += dt
        self.bar.update(dt)
        self.score_label.update(dt)
        self.score_prefix.update(dt)
        self.best_label.update(dt)
        self.best_prefix.update(dt)
        self.speed_label.update(dt)
        self.diff_label.update(dt)

        self.score_label.text = str(self.gm.score)
        hs = self.gm.high_scores.get(self.gm.difficulty, 0)
        self.best_label.text = str(hs)
        speed_ratio = self.gm.snake.speed / self.gm.current_difficulty['speed']
        self.speed_label.text = f'SPEED {speed_ratio:.1f}x'
        self.diff_label.text = self.gm.difficulty.upper()

    def draw(self):
        self.bar.draw(self.screen)

        pygame.draw.line(self.screen, (*TEXT_ACCENT[:3], 30),
                        (0, 56), (SCREEN_WIDTH, 56), 1)

        self.score_prefix.draw(self.screen)
        self.score_label.draw(self.screen)
        self.best_prefix.draw(self.screen)
        self.best_label.draw(self.screen)
        self.speed_label.draw(self.screen)
        self.diff_label.draw(self.screen)


class StartMenu:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.gm = game_manager
        self.time = 0.0
        self.panels = []
        self.buttons = []
        self.labels = []
        self.difficulty_buttons = []
        self.selected_difficulty = 'Normal'
        self.orbit_angle = 0

        cx = SCREEN_WIDTH // 2

        self.title_label = TextLabel('SNAKE', FONT_SIZE_TITLE, TEXT_ACCENT,
                                   center=(cx, 155))
        self.subtitle_label = TextLabel('NEON EDITION', FONT_SIZE_MEDIUM, TEXT_SECONDARY,
                                      center=(cx, 210))

        start_btn = Button(
            pygame.Rect(cx - 180, 270, 360, 65),
            'START GAME', FONT_SIZE_LARGE,
            on_click=self._on_start, accent=True
        )
        self.buttons.append(start_btn)

        diff_panel = Panel(pygame.Rect(cx - 240, 370, 480, 95),
                          bg_color=(6, 6, 12, 170))
        self.panels.append(diff_panel)
        self.diff_label = TextLabel('DIFFICULTY', FONT_SIZE_SMALL, TEXT_SECONDARY,
                                  midtop=(cx, 378))
        self.labels.append(self.diff_label)

        difficulties = ['Easy', 'Normal', 'Hard']
        bw = 140
        gap = 16
        total = bw * 3 + gap * 2
        start_x = cx - total // 2
        for i, diff in enumerate(difficulties):
            btn = Button(
                pygame.Rect(start_x + i * (bw + gap), 420, bw, 38),
                diff.upper(), FONT_SIZE_SMALL,
                on_click=lambda d=diff: self._select_difficulty(d)
            )
            self.difficulty_buttons.append(btn)

        self.buttons.extend(self.difficulty_buttons)
        self._select_difficulty('Normal')

        sep_y = 530
        self.sep_label = TextLabel('───  SETTINGS  ───', FONT_SIZE_SMALL, TEXT_DIM,
                                 center=(cx, sep_y))
        self.labels.append(self.sep_label)

        self.music_btn = Button(
            pygame.Rect(cx - 140, 560, 280, 48),
            'MUSIC  ON', FONT_SIZE_MEDIUM,
            on_click=self._toggle_music
        )
        self.buttons.append(self.music_btn)

        self.sfx_btn = Button(
            pygame.Rect(cx - 140, 620, 280, 48),
            'SFX  ON', FONT_SIZE_MEDIUM,
            on_click=self._toggle_sfx
        )
        self.buttons.append(self.sfx_btn)

        self.high_score_label = TextLabel(
            '', FONT_SIZE_MEDIUM, TEXT_ACCENT,
            center=(cx, 695)
        )
        self.labels.append(self.high_score_label)

        self.credit_label = TextLabel(
            'SNAKE  ·  NEON  EDITION  ·  2026',
            FONT_SIZE_SMALL, TEXT_DIM,
            center=(cx, 760)
        )
        self.labels.append(self.credit_label)

    def _on_start(self):
        self.gm.sound_manager.play_sfx('click')
        self.gm.start_game()

    def _select_difficulty(self, diff):
        self.selected_difficulty = diff
        self.gm.difficulty = diff
        self.gm.sound_manager.play_sfx('click')
        dc = self.gm.difficulty_color
        for btn in self.difficulty_buttons:
            if btn.text == diff.upper():
                btn.border_color = (*dc, 220)
                btn.hover_border_color = (*dc, 255)
                btn.text_color = dc
            else:
                btn.border_color = BUTTON_BORDER
                btn.hover_border_color = BUTTON_HOVER_BORDER
                btn.text_color = TEXT_PRIMARY

    def _toggle_music(self):
        enabled = self.gm.sound_manager.toggle_music()
        self.music_btn.text = f'MUSIC  {"ON" if enabled else "OFF"}'

    def _toggle_sfx(self):
        enabled = self.gm.sound_manager.toggle_sfx()
        self.sfx_btn.text = f'SFX  {"ON" if enabled else "OFF"}'

    def update(self, dt):
        self.time += dt
        self.orbit_angle += dt * 0.8
        for panel in self.panels:
            panel.update(dt)
        for btn in self.buttons:
            btn.update(dt)
        for label in self.labels:
            label.update(dt)

        hs = self.gm.high_scores.get(self.selected_difficulty, 0)
        self.high_score_label.text = f'HIGH SCORE  ·  {hs}'

        hue = (self.time * 40) % 360
        color = hsv_to_rgb(hue, 0.9, 1.0)
        self.title_label.color = color

    def draw(self):
        cx = SCREEN_WIDTH // 2
        self.title_label.draw(self.screen)
        self.subtitle_label.draw(self.screen)

        for panel in self.panels:
            panel.draw(self.screen)

        for label in self.labels:
            label.draw(self.screen)

        self.draw_orbiting_dots(cx)

        for btn in self.buttons:
            btn.draw(self.screen)

    def draw_orbiting_dots(self, cx):
        t = self.time
        for i in range(6):
            angle = t * 0.6 + i * math.pi / 3
            x = cx + 300 * math.cos(angle)
            y = 155 + 80 * math.sin(angle * 0.7)
            hue = (t * 50 + i * 60) % 360
            color = hsv_to_rgb(hue, 0.9, 0.8)
            alpha = int(40 + 30 * math.sin(t + i))
            pygame.draw.circle(self.screen, (*color, alpha), (int(x), int(y)), 3)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def show(self):
        for btn in self.buttons:
            btn.set_fade(255)
        for panel in self.panels:
            panel.set_fade(255)
        for label in self.labels:
            label.set_fade(255)

    def hide(self):
        for btn in self.buttons:
            btn.set_fade(0)
        for panel in self.panels:
            panel.set_fade(0)
        for label in self.labels:
            label.set_fade(0)

    def reset(self):
        self.time = 0.0


class PauseMenu:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.gm = game_manager
        self.time = 0.0
        self.buttons = []
        self.labels = []
        self.panels = []

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        self.overlay = Panel(pygame.Rect(cx - 180, cy - 170, 360, 340),
                            bg_color=(6, 6, 12, 200))
        self.panels.append(self.overlay)

        self.title = TextLabel('PAUSED', FONT_SIZE_XLARGE, TEXT_ACCENT,
                             center=(cx, cy - 100))
        self.labels.append(self.title)

        resume_btn = Button(
            pygame.Rect(cx - 120, cy - 20, 240, 50),
            'RESUME', FONT_SIZE_LARGE,
            on_click=self._on_resume
        )
        self.buttons.append(resume_btn)

        restart_btn = Button(
            pygame.Rect(cx - 120, cy + 50, 240, 50),
            'RESTART', FONT_SIZE_LARGE,
            on_click=self._on_restart
        )
        self.buttons.append(restart_btn)

        menu_btn = Button(
            pygame.Rect(cx - 120, cy + 120, 240, 50),
            'MAIN MENU', FONT_SIZE_MEDIUM,
            on_click=self._on_menu
        )
        self.buttons.append(menu_btn)

    def _on_resume(self):
        self.gm.sound_manager.play_sfx('click')
        self.gm.toggle_pause()

    def _on_restart(self):
        self.gm.sound_manager.play_sfx('click')
        self.gm.start_game()

    def _on_menu(self):
        self.gm.sound_manager.play_sfx('click')
        self.gm.state = 'menu'

    def update(self, dt):
        self.time += dt
        for panel in self.panels:
            panel.update(dt)
        for btn in self.buttons:
            btn.update(dt)
        for label in self.labels:
            label.update(dt)

        hue = (self.time * 30) % 360
        self.title.color = hsv_to_rgb(hue, 0.8, 1.0)

    def draw(self):
        for panel in self.panels:
            panel.draw(self.screen)
        for label in self.labels:
            label.draw(self.screen)
        for btn in self.buttons:
            btn.draw(self.screen)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def show(self):
        for btn in self.buttons:
            btn.set_fade(255)
        for panel in self.panels:
            panel.set_fade(255)
        for label in self.labels:
            label.set_fade(255)

    def hide(self):
        for btn in self.buttons:
            btn.set_fade(0)
        for panel in self.panels:
            panel.set_fade(0)
        for label in self.labels:
            label.set_fade(0)


class GameOverMenu:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.gm = game_manager
        self.time = 0.0
        self.buttons = []
        self.labels = []
        self.panels = []
        self.new_high_score = False

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        self.overlay = Panel(pygame.Rect(cx - 220, cy - 190, 440, 380),
                            bg_color=(6, 6, 12, 200))
        self.panels.append(self.overlay)

        self.title = TextLabel('GAME OVER', FONT_SIZE_XLARGE, (255, 60, 60),
                             center=(cx, cy - 125))
        self.labels.append(self.title)

        self.score_label = TextLabel('', FONT_SIZE_LARGE, TEXT_PRIMARY,
                                   center=(cx, cy - 50))
        self.labels.append(self.score_label)

        self.high_score_label = TextLabel('', FONT_SIZE_MEDIUM, TEXT_ACCENT,
                                        center=(cx, cy - 5))
        self.labels.append(self.high_score_label)

        restart_btn = Button(
            pygame.Rect(cx - 140, cy + 55, 280, 55),
            'PLAY AGAIN', FONT_SIZE_LARGE,
            on_click=self._on_restart
        )
        self.buttons.append(restart_btn)

        menu_btn = Button(
            pygame.Rect(cx - 140, cy + 125, 280, 50),
            'MAIN MENU', FONT_SIZE_MEDIUM,
            on_click=self._on_menu
        )
        self.buttons.append(menu_btn)

    def _on_restart(self):
        self.gm.sound_manager.play_sfx('click')
        self.gm.start_game()

    def _on_menu(self):
        self.gm.sound_manager.play_sfx('click')
        self.gm.state = 'menu'

    def update(self, dt):
        self.time += dt
        for panel in self.panels:
            panel.update(dt)
        for btn in self.buttons:
            btn.update(dt)
        for label in self.labels:
            label.update(dt)

        diff = self.gm.difficulty
        hs = self.gm.high_scores.get(diff, 0)
        self.score_label.text = f'SCORE  {self.gm.score}'
        if self.new_high_score:
            pulse = abs(math.sin(self.time * 3))
            r = int(255 - (255 - 0) * pulse)
            g = int(255 - (255 - 200) * pulse)
            b = int(255 - (255 - 255) * pulse)
            self.high_score_label.color = (r, g, b)
            self.high_score_label.text = f'★  NEW HIGH SCORE  ★'
        else:
            self.high_score_label.text = f'HIGH SCORE  ·  {hs}'

        if self.new_high_score:
            hue = (self.time * 60) % 360
            self.title.color = hsv_to_rgb(hue, 0.9, 1.0)

    def draw(self):
        for panel in self.panels:
            panel.draw(self.screen)
        for label in self.labels:
            label.draw(self.screen)
        for btn in self.buttons:
            btn.draw(self.screen)

    def handle_event(self, event):
        for btn in self.buttons:
            btn.handle_event(event)

    def show(self, new_high=False):
        self.new_high_score = new_high
        for btn in self.buttons:
            btn.set_fade(255)
        for panel in self.panels:
            panel.set_fade(255)
        for label in self.labels:
            label.set_fade(255)

    def hide(self):
        for btn in self.buttons:
            btn.set_fade(0)
        for panel in self.panels:
            panel.set_fade(0)
        for label in self.labels:
            label.set_fade(0)
