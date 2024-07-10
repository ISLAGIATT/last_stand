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
        self.direction = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frame_timer = 0

        # Load animation frames and scale them to the desired size
        self.animations = {
            'down': [self.load_image(f'anim/customer/customer_walk_down{i}.png') for i in range(1, 9)],
            'up': [self.load_image(f'anim/customer/customer_walk_up{i}.png') for i in range(1, 9)],
            'left': [self.load_image(f'anim/customer/customer_walk_left{i}.png') for i in range(1, 9)],
            'right': [self.load_image(f'anim/customer/customer_walk_right{i}.png') for i in range(1, 9)]
        }
        self.image = self.animations['down'][0]  # Default frame

    def load_image(self, path):
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (self.size, self.size))

    def get_new_target(self):
        potential_targets = [s for s in self.stands if s != self.stand]
        return random.choice(potential_targets).position

    def move(self):
        if self.target:
            direction_x = self.target[0] - self.position[0]
            direction_y = self.target[1] - self.position[1]
            distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance > self.speed:
                self.position[0] += (direction_x / distance) * self.speed
                self.position[1] += (direction_y / distance) * self.speed

                # Determine direction
                if abs(direction_x) > abs(direction_y):
                    if direction_x > 0:
                        self.direction = 'right'
                    else:
                        self.direction = 'left'
                else:
                    if direction_y > 0:
                        self.direction = 'down'
                    else:
                        self.direction = 'up'
            else:
                self.position = list(self.target)
                self.target = self.get_new_target()

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
