import pygame
import math
import sys
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE, GRID_COLS, GRID_ROWS,
    BG_TOP, BG_BOTTOM, DIFFICULTIES, SEGMENT_RADIUS,
    generate_gradient, load_high_scores, save_high_scores, hsv_to_rgb,
    draw_rounded_rect
)
from snake import Snake
from food import Food
from effects import ParticleSystem, BackgroundEffect
from sounds import SoundManager
from ui import (
    StartMenu, PauseMenu, GameOverMenu, HUD
)


class GameManager:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('SNAKE - NEON EDITION')
        pygame.display.set_icon(self._create_icon())
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'
        self.difficulty = 'Normal'
        self.score = 0
        self.high_scores = load_high_scores()
        self.current_difficulty = DIFFICULTIES['Normal']

        self.sound_manager = SoundManager()
        self._difficulty_color = self.current_difficulty['color']
        self.particles = ParticleSystem()
        self.background = BackgroundEffect()
        self.bg_gradient = generate_gradient(
            SCREEN_WIDTH, SCREEN_HEIGHT, BG_TOP, BG_BOTTOM
        )
        self.grid_surface = self._create_grid_surface()

        self.snake = Snake()
        self.food = Food()
        self.food.spawn(self.snake.get_occupied_set())

        self.start_menu = StartMenu(self.screen, self)
        self.pause_menu = PauseMenu(self.screen, self)
        self.game_over_menu = GameOverMenu(self.screen, self)
        self.hud = HUD(self.screen, self)

        self.time = 0.0
        self.game_over_timer = 0
        self.showing_game_over = False

        self.sound_manager.start_music()

    def _create_icon(self):
        icon = pygame.Surface((32, 32))
        icon.fill((5, 5, 5))
        pygame.draw.circle(icon, (0, 200, 255), (16, 16), 12)
        pygame.draw.circle(icon, (100, 255, 200), (16, 16), 6)
        return icon

    def _create_grid_surface(self):
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            alpha = 15 if x % (CELL_SIZE * 4) == 0 else 8
            pygame.draw.line(s, (30, 30, 50, alpha), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            alpha = 15 if y % (CELL_SIZE * 4) == 0 else 8
            pygame.draw.line(s, (30, 30, 50, alpha), (0, y), (SCREEN_WIDTH, y))
        return s

    def start_game(self):
        self.difficulty = self.difficulty if hasattr(self, 'difficulty') else 'Normal'
        self.current_difficulty = DIFFICULTIES[self.difficulty]
        self.score = 0
        self.game_over_timer = 0
        self.showing_game_over = False

        speed = self.current_difficulty['speed']
        self._difficulty_color = self.current_difficulty['color']
        self.snake = Snake(speed=speed)
        self.food = Food()
        self.food.spawn(self.snake.get_occupied_set())
        self.particles.clear()

        self.state = 'playing'

    def toggle_pause(self):
        if self.state == 'playing':
            self.state = 'paused'
            self.pause_menu.show()
        elif self.state == 'paused':
            self.state = 'playing'
            self.pause_menu.hide()

    def game_over(self):
        self.state = 'game_over'
        self.game_over_timer = 0.3
        self.showing_game_over = False
        self.sound_manager.play_sfx('game_over')

        diff = self.difficulty
        hs = self.high_scores.get(diff, 0)
        new_high = self.score > hs
        if new_high:
            self.high_scores[diff] = self.score
            save_high_scores(self.high_scores)

        self.game_over_menu.show(new_high)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        self.toggle_pause()
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.set_direction((0, -1))
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.set_direction((0, 1))
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.set_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.set_direction((1, 0))
                elif self.state == 'paused':
                    if event.key == pygame.K_ESCAPE:
                        self.toggle_pause()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == 'menu':
                    self.start_menu.handle_event(event)
                elif self.state == 'paused':
                    self.pause_menu.handle_event(event)
                elif self.state == 'game_over':
                    self.game_over_menu.handle_event(event)

            if event.type == pygame.MOUSEMOTION:
                if self.state == 'menu':
                    self.start_menu.handle_event(event)
                elif self.state == 'paused':
                    self.pause_menu.handle_event(event)
                elif self.state == 'game_over':
                    self.game_over_menu.handle_event(event)

    def update(self, dt):
        self.time += dt
        self.background.update(dt)

        if self.state == 'menu':
            self.start_menu.update(dt)
            self.food.update(dt)
            self.food.color_phase += dt * 0.2

        elif self.state == 'playing':
            self.snake.update(dt)
            self.food.update(dt)
            self.hud.update(dt)

            head = self.snake.get_head_pos()
            if head == self.food.grid_pos:
                self.score += 10
                self.snake.grow()
                self.sound_manager.play_sfx('eat')
                fx, fy = self.food.get_pixel_pos()
                self.particles.emit(fx, fy, self.food.get_current_color())
                self.food.spawn(self.snake.get_occupied_set())
                if self.score % (self.current_difficulty['interval'] * 10) == 0:
                    self.snake.speed += self.current_difficulty['increment']

            if self.snake.check_wall_collision() or self.snake.check_self_collision():
                self.game_over()

            self.particles.update(dt)

        elif self.state == 'paused':
            self.pause_menu.update(dt)
            self.hud.update(dt)

        elif self.state == 'game_over':
            if self.game_over_timer > 0:
                self.game_over_timer -= dt
            else:
                self.showing_game_over = True
            self.particles.update(dt)
            self.game_over_menu.update(dt)

    @property
    def difficulty_color(self):
        return self._difficulty_color

    @difficulty_color.setter
    def difficulty_color(self, val):
        self._difficulty_color = val

    def draw_grid(self):
        self.screen.blit(self.grid_surface, (0, 0))

    def draw(self):
        self.screen.blit(self.bg_gradient, (0, 0))
        self.background.draw(self.screen)
        self.background.draw_waves(self.screen, self.time)

        if self.state == 'menu':
            self.draw_grid()
            self.food.draw(self.screen)
            self.start_menu.draw()

        elif self.state == 'playing':
            self.draw_grid()
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.particles.draw(self.screen)
            self.hud.draw()

        elif self.state == 'paused':
            self.draw_grid()
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            self.particles.draw(self.screen)
            self.hud.draw()

            dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            dim_surf.set_alpha(120)
            dim_surf.fill((0, 0, 0))
            self.screen.blit(dim_surf, (0, 0))

            self.pause_menu.draw()

        elif self.state == 'game_over':
            self.draw_grid()
            self.food.draw(self.screen)
            if self.game_over_timer <= 0:
                dim_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                dim_surf.set_alpha(140)
                dim_surf.fill((0, 0, 0))
                self.screen.blit(dim_surf, (0, 0))
            self.particles.draw(self.screen)
            if self.showing_game_over:
                self.game_over_menu.draw()

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)
            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
