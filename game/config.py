import pygame
import json
import os
from pathlib import Path

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

CELL_SIZE = 24
GRID_COLS = SCREEN_WIDTH // CELL_SIZE
GRID_ROWS = SCREEN_HEIGHT // CELL_SIZE

BG_TOP = (5, 5, 5)
BG_BOTTOM = (17, 17, 17)

GRID_LINE_COLOR = (25, 25, 35)
GRID_LINE_ALPHA = 30

INITIAL_SPEED = 5
SPEED_INCREMENT = 0.4
SPEED_INTERVAL = 5

SEGMENT_SPACING = CELL_SIZE * 0.85
SEGMENT_RADIUS = int(CELL_SIZE * 0.4)
GLOW_RADIUS_OUTER = int(CELL_SIZE * 1.2)
GLOW_RADIUS_INNER = int(CELL_SIZE * 0.7)
GLOW_ALPHA_OUTER = 40
GLOW_ALPHA_INNER = 80

DIFFICULTIES = {
    'Easy': {'speed': 3.5, 'increment': 0.3, 'interval': 7, 'color': (0, 255, 100)},
    'Normal': {'speed': 5.5, 'increment': 0.5, 'interval': 5, 'color': (0, 200, 255)},
    'Hard': {'speed': 8.0, 'increment': 0.7, 'interval': 3, 'color': (255, 50, 50)},
}

EAT_PARTICLE_COUNT = 30
BG_PARTICLE_COUNT = 60
BG_WAVE_COUNT = 4

FONT_NAME = 'Segoe UI'
FONT_SIZE_SMALL = 18
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 48
FONT_SIZE_XLARGE = 72
FONT_SIZE_TITLE = 96

PANEL_BG_COLOR = (10, 10, 15, 180)
PANEL_BORDER_COLOR = (255, 255, 255, 25)
PANEL_HIGHLIGHT_COLOR = (255, 255, 255, 15)
PANEL_SHADOW_COLOR = (0, 0, 0, 60)
PANEL_RADIUS = 16

BUTTON_BG = (15, 15, 25, 200)
BUTTON_BORDER = (255, 255, 255, 40)
BUTTON_HOVER_BORDER = (0, 200, 255, 200)
BUTTON_HOVER_BG = (20, 20, 35, 220)
BUTTON_RADIUS = 12

TEXT_PRIMARY = (220, 220, 240)
TEXT_SECONDARY = (140, 140, 160)
TEXT_ACCENT = (0, 200, 255)

HIGH_SCORE_FILE = Path(__file__).parent / 'highscores.json'


def load_high_scores():
    if HIGH_SCORE_FILE.exists():
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {'Easy': 0, 'Normal': 0, 'Hard': 0}


def save_high_scores(scores):
    with open(HIGH_SCORE_FILE, 'w') as f:
        json.dump(scores, f, indent=2)


def hsv_to_rgb(h, s, v):
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c
    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    return (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_rounded_rect(surface, rect, color, radius, border_width=0, border_color=None):
    if len(color) == 4:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    else:
        s = pygame.Surface((rect.width, rect.height))
        s.set_colorkey((0, 0, 0))

    r = min(radius, min(rect.width, rect.height) // 2)
    pygame.draw.rect(s, color, (0, 0, rect.width, rect.height), border_radius=r)

    if border_width > 0 and border_color:
        pygame.draw.rect(s, border_color, (0, 0, rect.width, rect.height),
                         border_width, border_radius=r)

    surface.blit(s, rect.topleft)


def draw_rounded_rect_alpha(surface, rect, color, radius):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    s.set_alpha(color[3] if len(color) == 4 else 255)
    r = min(radius, min(rect.width, rect.height) // 2)
    pygame.draw.rect(s, color[:3], (0, 0, rect.width, rect.height), border_radius=r)
    surface.blit(s, rect.topleft)


def generate_gradient(width, height, top_color, bottom_color):
    surface = pygame.Surface((width, height))
    for y in range(height):
        t = y / height
        color = lerp_color(top_color, bottom_color, t)
        pygame.draw.line(surface, color, (0, y), (width, y))
    return surface
