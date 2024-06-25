import pygame
import random


class Cop:
    def __init__(self, map_width, map_height, size=100, speed=3):
        self.size = size
        self.speed = speed
        self.position = [random.randint(0, map_width), random.randint(0, map_height)]
        self.color = (0, 0, 255)
        self.active = False

    def activate(self):
        self.active = True

    def move(self, player_position):
        if player_position[0] < self.position[0]:
            self.position[0] -= self.speed
        if player_position[0] > self.position[0]:
            self.position[0] += self.speed
        if player_position[1] < self.position[1]:
            self.position[1] -= self.speed
        if player_position[1] > self.position[1]:
            self.position[1] += self.speed

    def draw(self, surface, camera_offset):
        if self.active:
            cop_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size, self.size)
            pygame.draw.rect(surface, self.color, cop_rect)

    def check_collision(self, player_position, player_size):
        player_rect = pygame.Rect(player_position[0], player_position[1], player_size, player_size)
        cop_rect = pygame.Rect(self.position[0], self.position[1], self.size, self.size)
        return player_rect.colliderect(cop_rect)
