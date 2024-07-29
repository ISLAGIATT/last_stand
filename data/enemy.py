import pygame
import random
import time
from data.stand import Stand, CookieGirl, HirableBully


class Enemy:
    def __init__(self, x, y, size, speed):
        self.position = [x, y]
        self.size = size
        self.speed = speed
        self.target = None
        self.target_stand = None
        self.score_rate = 0.05  # Score increment per stand per second
        self.has_cookie_girl = False
        self.has_bully = False
        self.hirable_bullies = 0  # Adding the attribute
        self.cookie_girls = 0  # Adding the attribute
        self.stands_controlled = 0  # Adding the attribute
        self.score = 0
        self.last_score_update_time = time.time()
        self.direction = 'right'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frame_timer = 0
        self.moving = False

        self.animations = {
            'walk_right': [
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_walk_side{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'walk_up': [
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_walk_up{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'walk_down': [
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_walk{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'walk_left': [pygame.transform.flip(
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_walk_side{i}.png').convert_alpha(),
                                       (self.size, self.size)), True, False) for i in range(1, 7)],
            'idle_right': [
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_idle_side{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'idle_up': [
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_idle_up{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'idle_down': [
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_idle{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'idle_left': [pygame.transform.flip(
                pygame.transform.scale(pygame.image.load(f'data/anim/enemy/enemy_idle_side{i}.png').convert_alpha(),
                                       (self.size, self.size)), True, False) for i in range(1, 7)]
        }
        self.image = self.animations['idle_right'][0]  # Default frame

    def set_idle(self):
        self.moving = False
        if self.direction == 'left':
            self.image = pygame.transform.flip(self.animations['idle_right'][self.frame_index], True, False)
        elif self.direction == 'right':
            self.image = self.animations['idle_right'][self.frame_index]
        elif self.direction == 'up':
            self.image = self.animations['idle_up'][self.frame_index]
        elif self.direction == 'down':
            self.image = self.animations['idle_down'][self.frame_index]

    def update_animation(self):
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            animation_key = f'walk_{self.direction}' if self.moving else f'idle_{self.direction}'
            self.frame_index = (self.frame_index + 1) % len(self.animations[animation_key])
            self.image = self.animations[animation_key][self.frame_index]

    def set_target(self, stands):
        available_stands = [stand for stand in stands if not stand.controlled_by_player and not stand.controlled_by_enemy]
        if available_stands:
            self.target_stand = random.choice(available_stands)
            self.target = self.target_stand.position

    def move(self):
        if self.target:
            target_x, target_y = self.target
            dx = target_x - self.position[0]
            dy = target_y - self.position[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance < self.speed:
                self.position[0] = target_x
                self.position[1] = target_y
                self.target = None
            else:
                self.position[0] += self.speed * dx / distance
                self.position[1] += self.speed * dy / distance
                self.moving = True

    def draw(self, surface, camera_offset):
        self.update_animation()
        rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                           self.size)
        surface.blit(self.image, rect.topleft)
        return rect

    def handle_collision(self, player_rect, camera_offset, player, dialogue_manager, game_state_manager, opp_stands,
                         cookie_girls, bullies, surface, message_box):
        enemy_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                                 self.size)

        for stand in opp_stands:
            stand.handle_enemy_collision(enemy_rect, camera_offset, self, dialogue_manager, game_state_manager,
                                         message_box)

        for stand in cookie_girls:
            stand.handle_enemy_collision(enemy_rect, camera_offset, self, dialogue_manager, game_state_manager,
                                         message_box)

        for stand in bullies:
            stand.handle_enemy_collision(enemy_rect, camera_offset, self, dialogue_manager, game_state_manager,
                                         message_box)

    def update_score(self, stands):
        current_time = time.time()
        time_diff = current_time - self.last_score_update_time
        if time_diff >= 1:  # Update score every second
            stands_controlled = sum(1 for stand in stands if stand.controlled_by_enemy)
            self.score += stands_controlled * self.score_rate * time_diff
            self.last_score_update_time = current_time
