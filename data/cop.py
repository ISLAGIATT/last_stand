import pygame
import random


class Cop:
    def __init__(self, map_width, map_height, size=100, speed=3):
        self.size = size
        self.speed = speed
        self.position = [random.randint(0, map_width), random.randint(0, map_height)]
        self.color = (0, 0, 255)
        self.active = False
        self.direction = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frame_timer = 0

        # Load animation frames and scale them to the desired size
        self.animations = {
            'down': [self.load_image(f'data/anim/cop/cop_down{i}.png') for i in range(1, 9)],
            'up': [self.load_image(f'data/anim/cop/cop_up{i}.png') for i in range(1, 9)],
            'right': [self.load_image(f'data/anim/cop/cop_side{i}.png') for i in range(1, 9)],
            'left': [pygame.transform.flip(self.load_image(f'data/anim/cop/cop_side{i}.png'), True, False) for i in range(1, 9)]
        }
        self.image = self.animations['down'][0]  # Default frame

    def load_image(self, path):
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (self.size, self.size))

    def activate(self):
        self.active = True

    def move(self, player_position):
        direction_x = player_position[0] - self.position[0]
        direction_y = player_position[1] - self.position[1]

        if abs(direction_x) > abs(direction_y):
            if direction_x > 0:
                self.position[0] += self.speed
                self.direction = 'right'
            else:
                self.position[0] -= self.speed
                self.direction = 'left'
        else:
            if direction_y > 0:
                self.position[1] += self.speed
                self.direction = 'down'
            else:
                self.position[1] -= self.speed
                self.direction = 'up'

    def update_animation(self):
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
            self.image = self.animations[self.direction][self.frame_index]

    def draw(self, surface, camera_offset):
        self.update_animation()
        rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size, self.size)
        surface.blit(self.image, rect.topleft)

    def check_collision(self, player_position, player_size):
        player_rect = pygame.Rect(player_position[0], player_position[1], player_size, player_size)
        cop_rect = pygame.Rect(self.position[0], self.position[1], self.size, self.size)
        return player_rect.colliderect(cop_rect)
