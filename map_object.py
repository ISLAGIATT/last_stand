import pygame


class MapObject:
    def __init__(self, x, y, size, color):
        self.position = [x, y]
        self.size = size
        self.color = color

    def draw(self, surface, camera_offset):
        obj_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                               self.size)
        if obj_rect.colliderect(surface.get_rect()):  # Check if object is within the visible screen
            pygame.draw.rect(surface, self.color, obj_rect)
        return obj_rect
