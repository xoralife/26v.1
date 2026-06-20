import pygame
import math
from collections import deque
from config import (
    CELL_SIZE, GRID_COLS, GRID_ROWS, SEGMENT_RADIUS,
    INITIAL_SPEED, SPEED_INCREMENT, SPEED_INTERVAL,
    hsv_to_rgb
)
from effects import SnakeGlowEffect


class Snake:
    def __init__(self, start_pos=None, length=3, speed=None):
        self.grid_positions = deque()
        self.prev_grid_positions = deque()
        self.move_progress = 0.0
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.speed = speed if speed else INITIAL_SPEED
        self.base_speed = self.speed
        self.grow_count = 0
        self.food_eaten = 0
        self.moved = False
        self.time = 0.0

        if start_pos is None:
            start_pos = (GRID_COLS // 2, GRID_ROWS // 2)

        for i in range(length):
            pos = (start_pos[0] - i, start_pos[1])
            self.grid_positions.append(pos)
            self.prev_grid_positions.append(pos)

    def set_direction(self, new_dir):
        dx, dy = new_dir
        cdx, cdy = self.direction
        if (dx, dy) != (-cdx, -cdy) and (dx, dy) != (cdx, cdy):
            self.next_direction = (dx, dy)

    def grow(self):
        self.grow_count += 1

    def get_head_pos(self):
        return self.grid_positions[0]

    def check_self_collision(self):
        head = self.grid_positions[0]
        for i in range(1, len(self.grid_positions)):
            if self.grid_positions[i] == head:
                return True
        return False

    def check_wall_collision(self):
        x, y = self.grid_positions[0]
        return x < 0 or x >= GRID_COLS or y < 0 or y >= GRID_ROWS

    def update(self, dt):
        self.time += dt
        self.move_progress += self.speed * dt

        moved_this_frame = False

        if self.move_progress >= 1.0:
            self.move_progress -= 1.0
            self.direction = self.next_direction

            self.prev_grid_positions = self.grid_positions.copy()

            head = self.grid_positions[0]
            new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
            self.grid_positions.appendleft(new_head)

            if self.grow_count > 0:
                self.grow_count -= 1
            else:
                self.grid_positions.pop()

            self.food_eaten += 1
            if self.food_eaten % SPEED_INTERVAL == 0:
                self.speed += SPEED_INCREMENT

            moved_this_frame = True
            self.moved = True

        return moved_this_frame

    def reset_progress(self):
        self.move_progress = 0.0
        self.prev_grid_positions = self.grid_positions.copy()

    def get_visual_position(self, index):
        if index >= len(self.grid_positions):
            return (0, 0)

        t = self.move_progress
        curr = self.grid_positions[index]
        prev = self.prev_grid_positions[index] if index < len(self.prev_grid_positions) else curr

        if prev == curr:
            px = curr[0] * CELL_SIZE + CELL_SIZE / 2
            py = curr[1] * CELL_SIZE + CELL_SIZE / 2
        else:
            px = (prev[0] + (curr[0] - prev[0]) * t) * CELL_SIZE + CELL_SIZE / 2
            py = (prev[1] + (curr[1] - prev[1]) * t) * CELL_SIZE + CELL_SIZE / 2

        return (px, py)

    def get_segment_color(self, index, total):
        hue = (self.time * 60 + index * (360 / max(total, 1))) % 360
        return hsv_to_rgb(hue, 0.85, 0.95)

    def draw(self, surface):
        total_segments = len(self.grid_positions)
        for i in range(total_segments - 1, -1, -1):
            x, y = self.get_visual_position(i)
            color = self.get_segment_color(i, total_segments)
            SnakeGlowEffect.draw_segment(surface, x, y, color)

    def get_head_rect(self):
        x, y = self.get_visual_position(0)
        return pygame.Rect(
            x - SEGMENT_RADIUS, y - SEGMENT_RADIUS,
            SEGMENT_RADIUS * 2, SEGMENT_RADIUS * 2
        )

    def get_occupied_set(self):
        s = set()
        for pos in self.grid_positions:
            s.add((pos[0], pos[1]))
        return s

    def reset(self, start_pos=None, speed=None):
        self.grid_positions.clear()
        self.prev_grid_positions.clear()
        self.move_progress = 0.0
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.speed = speed if speed else self.base_speed
        self.grow_count = 0
        self.food_eaten = 0
        self.moved = False
        self.time = 0.0

        if start_pos is None:
            start_pos = (GRID_COLS // 2, GRID_ROWS // 2)

        for i in range(3):
            pos = (start_pos[0] - i, start_pos[1])
            self.grid_positions.append(pos)
            self.prev_grid_positions.append(pos)
