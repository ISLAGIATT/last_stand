import pygame
class Player:
    def __init__(self, x, y, size, speed, color, map_width, map_height):
        self.position = [x, y]
        self.size = size
        self.speed = speed
        self.color = color
        self.map_width = map_width
        self.map_height = map_height
        self.has_cookie_girl = False
        self.has_bully = False
        self.score_rate = 0.05  # Example score rate
        self.cookie_girls = 0
        self.hirable_bullies = 0

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.position[0] = max(0, self.position[0] - self.speed)
        if keys[pygame.K_RIGHT]:
            self.position[0] = min(self.map_width - self.size, self.position[0] + self.speed)
        if keys[pygame.K_UP]:
            self.position[1] = max(0, self.position[1] - self.speed)
        if keys[pygame.K_DOWN]:
            self.position[1] = min(self.map_height - self.size, self.position[1] + self.speed)

    def draw(self, surface, camera_offset):
        rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size, self.size)
        pygame.draw.rect(surface, self.color, rect)
        return rect
