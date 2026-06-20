import pygame
import math
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FONT_NAME, FONT_SIZE_SMALL,
    FONT_SIZE_MEDIUM, FONT_SIZE_LARGE, FONT_SIZE_XLARGE, FONT_SIZE_TITLE,
    PANEL_BG_COLOR, PANEL_BORDER_COLOR, PANEL_HIGHLIGHT_COLOR,
    PANEL_SHADOW_COLOR, PANEL_RADIUS, BUTTON_BG, BUTTON_BORDER,
    BUTTON_HOVER_BORDER, BUTTON_HOVER_BG, BUTTON_RADIUS,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_ACCENT,
    draw_rounded_rect, hsv_to_rgb
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

    @classmethod
    def clear(cls):
        cls._fonts = {}


class Panel:
    def __init__(self, rect, bg_color=None, border_color=None,
                 radius=None, shadow=True):
        self.rect = pygame.Rect(rect)
        self.bg_color = bg_color or PANEL_BG_COLOR
        self.border_color = border_color or PANEL_BORDER_COLOR
        self.radius = radius if radius is not None else PANEL_RADIUS
        self.shadow = shadow
        self.alpha = 0
        self.target_alpha = 255
        self.fade_speed = 8
        self.time = 0.0
        self.anim_offset = 0
        self.target_offset = 0

    def set_fade(self, target):
        self.target_alpha = target

    def is_visible(self):
        return self.alpha > 5

    def update(self, dt):
        self.time += dt
        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + self.fade_speed * dt * 60)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - self.fade_speed * dt * 60)

        if self.anim_offset < self.target_offset:
            self.anim_offset += (self.target_offset - self.anim_offset) * dt * 10
        elif self.anim_offset > self.target_offset:
            self.anim_offset += (self.target_offset - self.anim_offset) * dt * 10

    def draw(self, surface):
        if self.alpha <= 0:
            return

        rect = self.rect.copy()
        anim_offset_int = int(self.anim_offset)
        rect.y += anim_offset_int

        if self.shadow:
            shadow_rect = rect.copy()
            shadow_rect.y += 4
            s = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            shadow_alpha = int(max(0, min(60, PANEL_SHADOW_COLOR[3] * (self.alpha / 255))))
            pygame.draw.rect(s, (*PANEL_SHADOW_COLOR[:3], shadow_alpha),
                           (0, 0, shadow_rect.width, shadow_rect.height),
                           border_radius=self.radius)
            surface.blit(s, shadow_rect.topleft)

        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg = self.bg_color
        if len(bg) == 4:
            bg_alpha = int(bg[3] * (self.alpha / 255))
            draw_color = (*bg[:3], bg_alpha)
        else:
            draw_color = bg

        pygame.draw.rect(s, draw_color, (0, 0, rect.width, rect.height),
                         border_radius=self.radius)

        if self.border_color:
            bc = self.border_color
            if len(bc) == 4:
                b_alpha = int(bc[3] * (self.alpha / 255))
                border_draw = (*bc[:3], b_alpha)
            else:
                border_draw = bc
            pygame.draw.rect(s, border_draw, (0, 0, rect.width, rect.height),
                           max(1, int(1.5)), border_radius=self.radius)

        highlight_rect = pygame.Rect(0, 0, rect.width, rect.height // 3)
        hc = PANEL_HIGHLIGHT_COLOR
        h_alpha = int(hc[3] * (self.alpha / 255))
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        for y in range(highlight_rect.height):
            t = 1 - y / highlight_rect.height
            a = int(h_alpha * t * 0.5)
            if a > 0:
                pygame.draw.line(highlight_surf, (*hc[:3], a),
                               (0, y), (highlight_rect.width, y))
        s.blit(highlight_surf, (0, 0))

        surface.blit(s, rect.topleft)


class Button:
    def __init__(self, rect, text, font_size=None, on_click=None,
                 bg_color=None, border_color=None,
                 hover_border_color=None, hover_bg_color=None,
                 text_color=None):
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

        self.hover = False
        self.hover_progress = 0.0
        self.click_scale = 1.0
        self.target_click_scale = 1.0
        self.alpha = 0
        self.target_alpha = 255
        self.fade_speed = 8
        self.time = 0.0
        self.anim_offset = 0
        self.target_offset = 0

    def set_fade(self, target):
        self.target_alpha = target

    def handle_event(self, event):
        if self.alpha < 50:
            return False

        pos = event.pos if hasattr(event, 'pos') else None

        if event.type == pygame.MOUSEMOTION:
            was_hover = self.hover
            self.hover = self.rect.collidepoint(event.pos)
            return was_hover != self.hover

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.target_click_scale = 0.92
                if self.on_click:
                    self.on_click()
                return True

        return False

    def update(self, dt):
        self.time += dt

        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + self.fade_speed * dt * 60)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - self.fade_speed * dt * 60)

        target_progress = 1.0 if self.hover else 0.0
        self.hover_progress += (target_progress - self.hover_progress) * dt * 12
        self.hover_progress = max(0, min(1, self.hover_progress))

        self.click_scale += (self.target_click_scale - self.click_scale) * dt * 20
        if abs(self.click_scale - 1.0) < 0.01:
            self.click_scale = 1.0
            self.target_click_scale = 1.0

        if self.anim_offset < self.target_offset:
            self.anim_offset += (self.target_offset - self.anim_offset) * dt * 10
        elif self.anim_offset > self.target_offset:
            self.anim_offset += (self.target_offset - self.anim_offset) * dt * 10

    def draw(self, surface):
        if self.alpha <= 0:
            return

        scale = self.click_scale
        scaled_w = int(self.rect.width * scale)
        scaled_h = int(self.rect.height * scale)
        scaled_x = self.rect.centerx - scaled_w // 2
        scaled_y = self.rect.centery - scaled_h // 2 + int(self.anim_offset)

        rect = pygame.Rect(scaled_x, scaled_y, scaled_w, scaled_h)

        bg_color = lerp_color_tuple(self.bg_color[:3], self.hover_bg_color[:3],
                                    self.hover_progress)
        border_color = lerp_color_tuple(
            (*self.border_color[:3],),
            (*self.hover_border_color[:3],),
            self.hover_progress
        )

        bg_alpha = int(self.bg_color[3] * (self.alpha / 255))

        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*bg_color, bg_alpha),
                        (0, 0, rect.width, rect.height),
                        border_radius=BUTTON_RADIUS)

        b_alpha = int(255 * (self.alpha / 255)) if len(self.border_color) == 3 else \
                  int(self.border_color[3] * (self.alpha / 255))
        pygame.draw.rect(s, (*border_color[:3], b_alpha),
                        (0, 0, rect.width, rect.height),
                        max(1, int(2 + self.hover_progress)), border_radius=BUTTON_RADIUS)

        if self.hover_progress > 0.01:
            glow_alpha = int(40 * self.hover_progress * (self.alpha / 255))
            glow_color = self.hover_border_color[:3]
            for r in range(4, 0, -1):
                g_a = glow_alpha // (5 - r)
                pygame.draw.rect(s, (*glow_color, g_a),
                               (-r, -r, rect.width + r * 2, rect.height + r * 2),
                               max(1, int(1.5)), BUTTON_RADIUS + r)

        text_color = lerp_color_tuple(
            self.text_color[:3],
            self.hover_text_color[:3],
            self.hover_progress
        )
        text_alpha = int(255 * (self.alpha / 255))

        font = FontCache.get(self.font_size)
        text = font.render(self.text, True, (*text_color, text_alpha))
        text_rect = text.get_rect(center=(rect.width // 2, rect.height // 2))

        s.blit(text, text_rect)
        surface.blit(s, rect.topleft)


class TextLabel:
    def __init__(self, text, font_size, color=None, center=None,
                 topleft=None, midtop=None, topright=None):
        self.text = text
        self.font_size = font_size
        self.color = color or TEXT_PRIMARY
        self.center = center
        self.topleft = topleft
        self.midtop = midtop
        self.topright = topright
        self.alpha = 255
        self.target_alpha = 255
        self.time = 0.0
        self.pulse = 0.0

    def set_fade(self, target):
        self.target_alpha = target

    def update(self, dt):
        self.time += dt
        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + 10 * dt * 60)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - 10 * dt * 60)
        self.pulse += dt * 2

    def draw(self, surface, text_override=None):
        text = text_override or self.text
        font = FontCache.get(self.font_size)
        color = self.color
        if len(color) == 3:
            color = (*color, int(self.alpha))
        else:
            color = (*color[:3], int(color[3] * self.alpha / 255))

        rendered = font.render(text, True, color[:3])
        rendered.set_alpha(color[3])

        if self.center:
            rect = rendered.get_rect(center=self.center)
        elif self.topleft:
            rect = rendered.get_rect(topleft=self.topleft)
        elif self.midtop:
            rect = rendered.get_rect(midtop=self.midtop)
        elif self.topright:
            rect = rendered.get_rect(topright=self.topright)
        else:
            rect = rendered.get_rect()

        surface.blit(rendered, rect)
        return rect


def lerp_color_tuple(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


class MenuManager:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.gm = game_manager
        self.time = 0.0
        self.active_panel = None
        self.buttons = []
        self.labels = []
        self.transition_alpha = 0
        self.transition_target = 0
        self.transition_speed = 12
        self.transition_callback = None

    def fade_to(self, target, callback=None):
        self.transition_target = target
        self.transition_callback = callback

    def update(self, dt):
        self.time += dt
        if self.transition_alpha < self.transition_target:
            self.transition_alpha = min(self.transition_target,
                                        self.transition_alpha + self.transition_speed * dt * 60)
            if self.transition_alpha >= self.transition_target and self.transition_callback:
                cb = self.transition_callback
                self.transition_callback = None
                cb()
        elif self.transition_alpha > self.transition_target:
            self.transition_alpha = max(self.transition_target,
                                        self.transition_alpha - self.transition_speed * dt * 60)

    def draw_transition(self):
        if self.transition_alpha > 0:
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            s.set_alpha(min(255, int(self.transition_alpha)))
            s.fill((0, 0, 0))
            self.screen.blit(s, (0, 0))


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
        self.fade_in_done = False

        title_panel = Panel(pygame.Rect(
            SCREEN_WIDTH // 2 - 250, 100, 500, 120
        ))
        title_panel.set_fade(255)
        self.panels.append(title_panel)

        self.title_label = TextLabel(
            'SNAKE', FONT_SIZE_TITLE, TEXT_ACCENT,
            center=(SCREEN_WIDTH // 2, 160)
        )
        self.subtitle_label = TextLabel(
            'NEON EDITION', FONT_SIZE_LARGE, TEXT_SECONDARY,
            center=(SCREEN_WIDTH // 2, 200)
        )

        start_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 120, 320, 240, 55),
            'START GAME', FONT_SIZE_LARGE,
            on_click=self._on_start
        )
        self.buttons.append(start_btn)

        diff_panel = Panel(pygame.Rect(
            SCREEN_WIDTH // 2 - 200, 410, 400, 80
        ))
        self.panels.append(diff_panel)
        self.diff_label = TextLabel(
            'DIFFICULTY', FONT_SIZE_SMALL, TEXT_SECONDARY,
            midtop=(SCREEN_WIDTH // 2, 418)
        )
        self.labels.append(self.diff_label)

        difficulties = ['Easy', 'Normal', 'Hard']
        btn_width = 110
        total_width = len(difficulties) * btn_width + (len(difficulties) - 1) * 15
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        for i, diff in enumerate(difficulties):
            btn = Button(
                pygame.Rect(start_x + i * (btn_width + 15), 440, btn_width, 40),
                diff.upper(), FONT_SIZE_SMALL,
                on_click=lambda d=diff: self._select_difficulty(d)
            )
            self.difficulty_buttons.append(btn)

        self.buttons.extend(self.difficulty_buttons)
        self._select_difficulty('Normal')

        # Music toggle
        self.music_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 120, 530, 240, 45),
            'MUSIC: ON', FONT_SIZE_MEDIUM,
            on_click=self._toggle_music
        )
        self.buttons.append(self.music_btn)

        # SFX toggle
        self.sfx_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 120, 590, 240, 45),
            'SFX: ON', FONT_SIZE_MEDIUM,
            on_click=self._toggle_sfx
        )
        self.buttons.append(self.sfx_btn)

        self.high_score_label = TextLabel(
            '', FONT_SIZE_SMALL, TEXT_SECONDARY,
            center=(SCREEN_WIDTH // 2, 660)
        )
        self.labels.append(self.high_score_label)

        self.credit_label = TextLabel(
            'PREMIUM NEON EDITION', FONT_SIZE_SMALL, TEXT_SECONDARY,
            center=(SCREEN_WIDTH // 2, 720)
        )
        self.labels.append(self.credit_label)

    def _on_start(self):
        self.gm.sound_manager.play_sfx('click')
        self.gm.start_game()

    def _select_difficulty(self, diff):
        self.selected_difficulty = diff
        self.gm.difficulty = diff
        self.gm.sound_manager.play_sfx('click')
        for btn in self.difficulty_buttons:
            if btn.text == diff.upper():
                btn.border_color = self.gm.difficulty_color
                btn.hover_border_color = self.gm.difficulty_color
            else:
                btn.border_color = BUTTON_BORDER
                btn.hover_border_color = BUTTON_HOVER_BORDER

    def _toggle_music(self):
        enabled = self.gm.sound_manager.toggle_music()
        self.music_btn.text = f'MUSIC: {"ON" if enabled else "OFF"}'

    def _toggle_sfx(self):
        enabled = self.gm.sound_manager.toggle_sfx()
        self.sfx_btn.text = f'SFX: {"ON" if enabled else "OFF"}'

    def update(self, dt):
        self.time += dt
        for panel in self.panels:
            panel.update(dt)
        for btn in self.buttons:
            btn.update(dt)
        for label in self.labels:
            label.update(dt)

        hs = self.gm.high_scores.get(self.selected_difficulty, 0)
        self.high_score_label.text = f'HIGH SCORE ({self.selected_difficulty.upper()}): {hs}'

    def draw(self):
        for panel in self.panels:
            panel.draw(self.screen)
        self.title_label.draw(self.screen)
        self.subtitle_label.draw(self.screen)
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

    def reset(self):
        self.time = 0.0


class PauseMenu:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.gm = game_manager
        self.time = 0.0
        self.buttons = []
        self.labels = []

        overlay_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 150, 400, 300)
        self.overlay = Panel(overlay_rect)
        self.panels = [self.overlay]

        self.title = TextLabel(
            'PAUSED', FONT_SIZE_XLARGE, TEXT_ACCENT,
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90)
        )
        self.labels.append(self.title)

        resume_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20, 200, 45),
            'RESUME', FONT_SIZE_LARGE, on_click=self._on_resume
        )
        self.buttons.append(resume_btn)

        restart_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 45),
            'RESTART', FONT_SIZE_LARGE, on_click=self._on_restart
        )
        self.buttons.append(restart_btn)

        menu_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 45),
            'MAIN MENU', FONT_SIZE_LARGE, on_click=self._on_menu
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
        self.new_high_score = False

        overlay_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 180, 500, 360)
        self.overlay = Panel(overlay_rect)
        self.panels = [self.overlay]

        self.title = TextLabel(
            'GAME OVER', FONT_SIZE_XLARGE, (255, 60, 60),
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)
        )
        self.labels.append(self.title)

        self.score_label = TextLabel(
            '', FONT_SIZE_LARGE, TEXT_PRIMARY,
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)
        )
        self.labels.append(self.score_label)

        self.high_score_label = TextLabel(
            '', FONT_SIZE_MEDIUM, TEXT_ACCENT,
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        )
        self.labels.append(self.high_score_label)

        restart_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 40, 200, 45),
            'PLAY AGAIN', FONT_SIZE_LARGE, on_click=self._on_restart
        )
        self.buttons.append(restart_btn)

        menu_btn = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 45),
            'MAIN MENU', FONT_SIZE_LARGE, on_click=self._on_menu
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
        self.score_label.text = f'SCORE: {self.gm.score}'
        if self.new_high_score:
            self.high_score_label.text = f'NEW HIGH SCORE! ({diff.upper()})'
        else:
            self.high_score_label.text = f'HIGH SCORE ({diff.upper()}): {hs}'

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


class HUD:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.gm = game_manager
        self.time = 0.0

        self.score_panel = Panel(pygame.Rect(20, 20, 280, 90))
        self.score_panel.set_fade(255)

        self.high_score_panel = Panel(pygame.Rect(20, 120, 280, 70))
        self.high_score_panel.set_fade(255)

        self.speed_panel = Panel(pygame.Rect(20, 200, 280, 60))
        self.speed_panel.set_fade(255)

        self.score_label = TextLabel(
            'SCORE: 0', FONT_SIZE_LARGE, TEXT_PRIMARY,
            topleft=(40, 35)
        )
        self.high_score_label = TextLabel(
            'BEST: 0', FONT_SIZE_MEDIUM, TEXT_SECONDARY,
            topleft=(40, 135)
        )
        self.speed_label = TextLabel(
            'SPEED: 1.0x', FONT_SIZE_SMALL, TEXT_SECONDARY,
            topleft=(40, 215)
        )

    def update(self, dt):
        self.time += dt
        self.score_panel.update(dt)
        self.high_score_panel.update(dt)
        self.speed_panel.update(dt)
        self.score_label.update(dt)
        self.high_score_label.update(dt)
        self.speed_label.update(dt)

        self.score_label.text = f'SCORE: {self.gm.score}'
        hs = self.gm.high_scores.get(self.gm.difficulty, 0)
        self.high_score_label.text = f'BEST: {hs}'
        speed_ratio = self.gm.snake.speed / self.gm.current_difficulty['speed']
        self.speed_label.text = f'SPEED: {speed_ratio:.1f}x'

    def draw(self):
        self.score_panel.draw(self.screen)
        self.high_score_panel.draw(self.screen)
        self.speed_panel.draw(self.screen)
        self.score_label.draw(self.screen)
        self.high_score_label.draw(self.screen)
        self.speed_label.draw(self.screen)
