import pygame
import time
import random

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
        self.particles = []

    def start(self):
        if not self.active and not self.full:
            self.start_time = time.time()
            self.active = True

    def draw(self, surface):
        if not self.active and not self.full:
            return

        if self.start_time:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.duration:
                elapsed_time = self.duration
                self.active = False
                self.full = True

        fill_height = self.height if self.full else int((elapsed_time / self.duration) * self.height)
        cup_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        fill_rect = pygame.Rect(self.x, self.y + self.height - fill_height, self.width, fill_height)

        # Draw cup border
        pygame.draw.rect(surface, (255, 255, 255), cup_rect, 2)

        # Draw the stream effect pouring into the cup
        if not self.full:
            self.generate_particles()
            self.update_particles()
            self.draw_particles(surface, fill_rect)

        # Draw filled part
        pygame.draw.rect(surface, (255, 255, 0), fill_rect)

    def generate_particles(self):
        if len(self.particles) < 20:  # Limit the number of particles
            self.particles.append([self.x + self.width // 2, self.y, random.randint(-2, 2), random.randint(2, 5)])

    def update_particles(self):
        for particle in self.particles:
            particle[1] += particle[3]  # Move particle downwards
            if particle[1] > self.y + self.height:  # Remove particle if it reaches the bottom of the cup
                self.particles.remove(particle)

    def draw_particles(self, surface, fill_rect):
        for particle in self.particles:
            pygame.draw.circle(surface, (255, 255, 0), (particle[0], particle[1]), 2)
            if particle[1] > fill_rect.top:
                self.particles.remove(particle)

    def reset(self):
        self.start_time = None
        self.active = False
        self.full = False
        self.particles = []

    def update_position(self, x, y):
        self.x = x
        self.y = y
