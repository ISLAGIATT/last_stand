import pygame
import random
import math

class RunningPerson:
    def __init__(self, x, y, size, speed):
        self.position = [x, y]
        self.size = size
        self.speed = speed
        self.direction = random.choice(['left', 'right'])
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frame_timer = 0

        # Define the animations dictionary here
        self.animations = {
            'right': [
                pygame.transform.scale(pygame.image.load(f'anim/running_kid/running_kid_side{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'left': [pygame.transform.flip(
                pygame.transform.scale(pygame.image.load(f'anim/running_kid/running_kid_side{i}.png').convert_alpha(),
                                       (self.size, self.size)), True, False) for i in range(1, 7)]
        }

        # Set the initial image
        self.image = self.animations[self.direction][0]

        self.target = self.get_random_target()

    def get_random_target(self):
        # Generate a random target off screen
        if self.direction == 'left':
            return [-self.size, self.position[1]]
        elif self.direction == 'right':
            return [2000 + self.size, self.position[1]]

    def move(self):
        if self.target:
            direction_x = self.target[0] - self.position[0]
            direction_y = self.target[1] - self.position[1]
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > self.speed:
                self.position[0] += (direction_x / distance) * self.speed
                self.position[1] += (direction_y / distance) * self.speed
            else:
                self.position = list(self.target)

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

    def is_off_screen(self, map_width, map_height):
        return self.position[0] < 0 or self.position[0] > map_width or self.position[1] < 0 or self.position[1] > map_height
