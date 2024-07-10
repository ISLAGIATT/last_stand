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
        self.direction = 'right'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.frame_timer = 0
        self.moving = False
        self.movement_delay_active = False

        self.animations = {
            'walk_right': [
                pygame.transform.scale(pygame.image.load(f'anim/player/player_walk_side{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'walk_up': [
                pygame.transform.scale(pygame.image.load(f'anim/player/player_walk_up{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'walk_down': [
                pygame.transform.scale(pygame.image.load(f'anim/player/player_walk{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'walk_left': [pygame.transform.flip(
                pygame.transform.scale(pygame.image.load(f'anim/player/player_walk_side{i}.png').convert_alpha(),
                                       (self.size, self.size)), True, False) for i in range(1, 7)],
            'idle_right': [
                pygame.transform.scale(pygame.image.load(f'anim/player/player_idle_side{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'idle_up': [
                pygame.transform.scale(pygame.image.load(f'anim/player/player_idle_up{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'idle_down': [
                pygame.transform.scale(pygame.image.load(f'anim/player/player_idle{i}.png').convert_alpha(),
                                       (self.size, self.size)) for i in range(1, 7)],
            'idle_left': [pygame.transform.flip(
                pygame.transform.scale(pygame.image.load(f'anim/player/player_idle_side{i}.png').convert_alpha(),
                                       (self.size, self.size)), True, False) for i in range(1, 7)]
        }
        self.image = self.animations['idle_right'][0]  # Default frame

    def move(self, keys):
        self.moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.position[0] -= self.speed
            self.direction = 'left'
            self.moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.position[0] += self.speed
            self.direction = 'right'
            self.moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.position[1] -= self.speed
            self.direction = 'up'
            self.moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.position[1] += self.speed
            self.direction = 'down'
            self.moving = True

        # Keep player within map boundaries
        self.position[0] = max(0, min(self.position[0], self.map_width - self.size))
        self.position[1] = max(0, min(self.position[1], self.map_height - self.size))

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

    def draw(self, surface, camera_offset):
        self.update_animation()
        rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                           self.size)
        surface.blit(self.image, rect.topleft)
        return rect