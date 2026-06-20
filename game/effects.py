import pygame
import math
import random
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BG_PARTICLE_COUNT, BG_WAVE_COUNT,
    EAT_PARTICLE_COUNT, CELL_SIZE, SEGMENT_RADIUS,
    GLOW_RADIUS_OUTER, GLOW_RADIUS_INNER, GLOW_ALPHA_OUTER, GLOW_ALPHA_INNER,
    lerp_color
)


class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime, size=4):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.trail = []
        self.max_trail = 5

    def update(self, dt):
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)

        speed_mult = 60.0
        self.x += self.vx * dt * speed_mult
        self.y += self.vy * dt * speed_mult
        self.vx *= 0.98
        self.vy *= 0.98
        self.vy += 0.5 * dt * speed_mult
        self.lifetime -= dt
        self.size *= 0.995

    def is_dead(self):
        return self.lifetime <= 0

    def draw(self, surface):
        alpha = max(0, int(255 * (self.lifetime / self.max_lifetime)))
        size = max(0.5, self.size * (self.lifetime / self.max_lifetime))

        for i, (tx, ty) in enumerate(self.trail):
            t_alpha = int(alpha * (i / len(self.trail)) * 0.3) if self.trail else 0
            t_size = size * (i / len(self.trail)) * 0.5 if self.trail else 0
            if t_size > 0.5 and t_alpha > 0:
                pygame.draw.circle(surface, (*self.color[:3], t_alpha),
                                   (int(tx), int(ty)), max(1, int(t_size)))

        glow_size = int(size * 3)
        if glow_size > 0 and alpha > 5:
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color[:3], alpha // 4),
                               (glow_size, glow_size), glow_size)
            surface.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)),
                         special_flags=pygame.BLEND_ALPHA_SDL2)

        if size > 0.5:
            pygame.draw.circle(surface, (*self.color[:3], alpha),
                               (int(self.x), int(self.y)), max(1, int(size)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=None):
        if count is None:
            count = EAT_PARTICLE_COUNT
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2
            lifetime = random.uniform(0.5, 1.5)
            size = random.uniform(2, 6)
            offset_x = x + random.uniform(-5, 5)
            offset_y = y + random.uniform(-5, 5)
            self.particles.append(Particle(
                offset_x, offset_y, vx, vy, color, lifetime, size
            ))

    def update(self, dt):
        self.particles = [p for p in self.particles if not p.is_dead()]
        for p in self.particles:
            p.update(dt)

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

    def clear(self):
        self.particles.clear()


class BackgroundEffect:
    def __init__(self):
        self.particles = []
        self.time = 0.0
        for _ in range(BG_PARTICLE_COUNT):
            self.particles.append({
                'x': random.uniform(0, SCREEN_WIDTH),
                'y': random.uniform(0, SCREEN_HEIGHT),
                'vx': random.uniform(-0.2, 0.2),
                'vy': random.uniform(-0.1, 0.1),
                'size': random.uniform(1, 3),
                'speed': random.uniform(0.2, 0.8),
                'phase': random.uniform(0, math.pi * 2),
                'alpha': random.uniform(20, 80),
            })

    def update(self, dt):
        self.time += dt
        for p in self.particles:
            p['x'] += p['vx'] * dt * 60
            p['y'] += p['vy'] * dt * 60
            p['alpha'] = 30 + 20 * math.sin(self.time * p['speed'] + p['phase'])
            p['size'] = 1 + math.sin(self.time * p['speed'] * 0.5 + p['phase']) * 0.5
            if p['x'] < -10:
                p['x'] = SCREEN_WIDTH + 10
            if p['x'] > SCREEN_WIDTH + 10:
                p['x'] = -10
            if p['y'] < -10:
                p['y'] = SCREEN_HEIGHT + 10
            if p['y'] > SCREEN_HEIGHT + 10:
                p['y'] = -10

    def draw(self, surface):
        for p in self.particles:
            alpha = max(0, min(255, int(p['alpha'])))
            if alpha > 5:
                size = max(0.5, p['size'])
                glow_surf = pygame.Surface((int(size * 8), int(size * 8)), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (100, 150, 255, alpha // 3),
                                   (int(size * 4), int(size * 4)), int(size * 4))
                surface.blit(glow_surf, (int(p['x'] - size * 4), int(p['y'] - size * 4)),
                             special_flags=pygame.BLEND_ALPHA_SDL2)
                pygame.draw.circle(surface, (150, 180, 255, alpha),
                                   (int(p['x']), int(p['y'])), max(1, int(size)))

    def draw_waves(self, surface, time):
        wave_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(BG_WAVE_COUNT):
            amplitude = 15 + i * 10
            frequency = 0.003 + i * 0.001
            wave_speed = 0.5 + i * 0.3
            phase = i * 1.5
            color = pygame.Color(0, 0, 0)
            color_hue = (time * 30 + i * 60) % 360
            color.hsla = (color_hue, 80, 50, 8 + i * 4)

            points = []
            for x in range(0, SCREEN_WIDTH + 20, 10):
                y = SCREEN_HEIGHT // 2 + amplitude * math.sin(
                    x * frequency + time * wave_speed + phase
                ) + amplitude * 0.5 * math.sin(
                    x * frequency * 0.7 + time * wave_speed * 0.7 + phase * 1.3
                )
                points.append((x, y))

            if len(points) > 1:
                for j in range(len(points) - 1):
                    thickness = 1 + math.sin(time + i + j * 0.01)
                    pygame.draw.line(wave_surf, color, points[j], points[j + 1],
                                     max(1, int(thickness * 1.5)))

        surface.blit(wave_surf, (0, 0), special_flags=pygame.BLEND_ALPHA_SDL2)


class SnakeGlowEffect:
    @staticmethod
    def draw_segment(surface, x, y, color, radius=None,
                     glow_outer=None, glow_inner=None):
        if radius is None:
            radius = SEGMENT_RADIUS
        if glow_outer is None:
            glow_outer = GLOW_RADIUS_OUTER
        if glow_inner is None:
            glow_inner = GLOW_RADIUS_INNER

        for glow_radius, glow_alpha, blur_steps in [
            (glow_outer, GLOW_ALPHA_OUTER, 8),
            (glow_inner, GLOW_ALPHA_INNER, 4),
        ]:
            glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            for s in range(blur_steps, 0, -1):
                r = glow_radius * s // blur_steps
                a = glow_alpha // (blur_steps - s + 1)
                pygame.draw.circle(glow_surf, (*color[:3], a),
                                   (glow_radius, glow_radius), r)
            surface.blit(glow_surf, (int(x - glow_radius), int(y - glow_radius)),
                         special_flags=pygame.BLEND_ALPHA_SDL2)

        pygame.draw.circle(surface, (*color[:3], 255),
                           (int(x), int(y)), int(radius * 0.9))

        highlight = pygame.Color(*color)
        h, s, v, a = highlight.hsla
        highlight.hsla = (h, s, min(100, v + 30), a)
        pygame.draw.circle(surface, highlight,
                           (int(x - radius * 0.2), int(y - radius * 0.2)),
                           int(radius * 0.5))
