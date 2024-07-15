import pygame
import time

class CountdownCup:
    def __init__(self, x, y, width, height, duration):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.duration = duration
        self.start_time = None
        self.active = False
        self.full = False

    def start(self):
        if not self.active and not self.full:
            self.start_time = time.time()
            self.active = True

    def draw(self, surface, x_offset=0, y_offset=0):
        if not self.active and not self.full:
            return

        if self.start_time:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.duration:
                elapsed_time = self.duration
                self.active = False
                self.full = True  # Keep the cup full after the duration

        fill_height = self.height if self.full else int((elapsed_time / self.duration) * self.height)
        cup_rect = pygame.Rect(self.x + x_offset, self.y + y_offset, self.width, self.height)
        fill_rect = pygame.Rect(self.x + x_offset, self.y + y_offset + self.height - fill_height, self.width,
                                fill_height)

        pygame.draw.rect(surface, (255, 255, 255), cup_rect, 2)  # Draw cup border
        pygame.draw.rect(surface, (255, 255, 0), fill_rect)  # Draw filled part

    def reset(self):
        self.start_time = None
        self.active = False
        self.full = False

    def update_position(self, x, y):
        self.x = x
        self.y = y
