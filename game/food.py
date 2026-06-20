import pygame
import math
import random
from config import CELL_SIZE, GRID_COLS, GRID_ROWS, hsv_to_rgb


class Food:
    def __init__(self):
        self.grid_pos = (0, 0)
        self.time = 0.0
        self.pulse_phase = 0.0
        self.color_phase = 0.0
        self.spawn_scale = 0.0
        self.spawning = True
        self.spawn_duration = 0.3

    def spawn(self, occupied_set=None):
        available = []
        for x in range(1, GRID_COLS - 1):
            for y in range(1, GRID_ROWS - 1):
                if occupied_set is None or (x, y) not in occupied_set:
                    available.append((x, y))

        if available:
            self.grid_pos = random.choice(available)
            self.spawning = True
            self.spawn_scale = 0.0

    def get_pixel_pos(self):
        return (
            self.grid_pos[0] * CELL_SIZE + CELL_SIZE / 2,
            self.grid_pos[1] * CELL_SIZE + CELL_SIZE / 2
        )

    def get_current_color(self):
        hue = (self.color_phase * 360) % 360
        return hsv_to_rgb(hue, 0.9, 1.0)

    def update(self, dt):
        self.time += dt
        self.pulse_phase += dt * 3
        self.color_phase += dt * 0.15

        if self.spawning:
            self.spawn_scale = min(1.0, self.spawn_scale + dt / self.spawn_duration)
            if self.spawn_scale >= 1.0:
                self.spawning = False

    def draw(self, surface):
        px, py = self.get_pixel_pos()
        color = self.get_current_color()

        if self.spawning:
            scale = self.spawn_scale
        else:
            pulse = math.sin(self.pulse_phase) * 0.08 + 0.92
            scale = pulse

        base_radius = CELL_SIZE * 0.35 * scale
        glow_radius = int(CELL_SIZE * 0.8 * scale)

        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        for r in range(glow_radius, 0, -2):
            alpha = int(60 * (r / glow_radius))
            pygame.draw.circle(glow_surf, (*color[:3], alpha),
                               (glow_radius, glow_radius), r)
        surface.blit(glow_surf, (int(px - glow_radius), int(py - glow_radius)),
                     special_flags=pygame.BLEND_ALPHA_SDL2)

        pygame.draw.circle(surface, (*color[:3], 255),
                           (int(px), int(py)), int(base_radius))

        highlight_color = tuple(min(255, c + 80) for c in color[:3])
        pygame.draw.circle(surface, (*highlight_color, 200),
                           (int(px - base_radius * 0.25), int(py - base_radius * 0.25)),
                           int(base_radius * 0.4))

        inner_glow = tuple(max(0, c - 40) for c in color[:3])
        pygame.draw.circle(surface, (*inner_glow, 100),
                           (int(px), int(py)), int(base_radius * 0.7), 2)

    def get_rect(self):
        px, py = self.get_pixel_pos()
        r = CELL_SIZE * 0.35
        return pygame.Rect(px - r, py - r, r * 2, r * 2)
