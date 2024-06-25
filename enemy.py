import pygame
import random
import time
from stand import Stand, CookieGirl, HirableBully


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

    def set_target(self, stands):
        if stands:
            self.target_stand = random.choice(stands)
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

    def draw(self, surface, camera_offset):
        rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                           self.size)
        pygame.draw.rect(surface, (255, 0, 0), rect)  # Draw enemy as red square
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
