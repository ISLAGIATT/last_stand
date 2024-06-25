import pygame
import random
import math

class Customer:
    def __init__(self, x, y, size, speed, stand, stands):
        self.position = [x, y]
        self.size = size
        self.speed = speed
        self.stand = stand
        self.stands = stands
        self.target = self.get_new_target()

    def get_new_target(self):
        potential_targets = [s for s in self.stands if s != self.stand]
        return random.choice(potential_targets).position

    def move(self):
        if self.target:
            direction_x = self.target[0] - self.position[0]
            direction_y = self.target[1] - self.position[1]
            distance = math.sqrt(direction_x**2 + direction_y**2)

            if distance > self.speed:
                self.position[0] += (direction_x / distance) * self.speed
                self.position[1] += (direction_y / distance) * self.speed
            else:
                self.position = list(self.target)
                self.target = self.get_new_target()

    def draw(self, surface, camera_offset):
        rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size, self.size)
        pygame.draw.rect(surface, (139, 69, 19), rect)  # Brown color for customers