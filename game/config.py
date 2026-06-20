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
FONT_SIZE_SMALL = 22
FONT_SIZE_MEDIUM = 34
FONT_SIZE_LARGE = 56
FONT_SIZE_XLARGE = 84
FONT_SIZE_TITLE = 110

PANEL_BG_COLOR = (8, 8, 14, 200)
PANEL_BORDER_COLOR = (255, 255, 255, 30)
PANEL_HIGHLIGHT_COLOR = (255, 255, 255, 12)
PANEL_SHADOW_COLOR = (0, 0, 0, 80)
PANEL_RADIUS = 16

BUTTON_BG = (12, 12, 22, 220)
BUTTON_BORDER = (255, 255, 255, 50)
BUTTON_HOVER_BORDER = (0, 220, 255, 220)
BUTTON_HOVER_BG = (18, 18, 35, 230)
BUTTON_RADIUS = 14

TEXT_PRIMARY = (230, 230, 245)
TEXT_SECONDARY = (130, 140, 165)
TEXT_ACCENT = (0, 220, 255)
TEXT_DIM = (60, 65, 80)

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


def generate_gradient(width, height, top_color, bottom_color):
    surface = pygame.Surface((width, height))
    for y in range(height):
        t = y / height
        color = lerp_color(top_color, bottom_color, t)
        pygame.draw.line(surface, color, (0, y), (width, y))
    return surface
