import random
import pygame
import math

class Path:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def draw(self, surface, camera_offset):
        start_pos = (self.start[0] - camera_offset[0], self.start[1] - camera_offset[1])
        end_pos = (self.end[0] - camera_offset[0], self.end[1] - camera_offset[1])
        pygame.draw.line(surface, (128, 128, 128), start_pos, end_pos, 5)

    @staticmethod
    def generate_paths(stands):
        paths = []
        num_paths = len(stands)
        for i in range(num_paths):
            start = stands[i].position
            end = stands[(i + 1) % num_paths].position
            path_segment = Path.generate_intermediate_path(start, end)
            paths.append(Path(*path_segment))
        return paths

    @staticmethod
    def generate_intermediate_path(start, end):
        # Generate a path segment that doesn't fully connect the stands
        mid_x = (start[0] + end[0]) // 2 + random.randint(-100, 100)
        mid_y = (start[1] + end[1]) // 2 + random.randint(-100, 100)
        return (start, (mid_x, mid_y))

    @staticmethod
    def is_player_on_path(player_pos, paths, player_size):
        player_x, player_y = player_pos
        for path in paths:
            distance = Path.point_to_segment_distance(player_x, player_y, path.start[0], path.start[1], path.end[0], path.end[1])
            if distance <= player_size / 2:
                return True
        return False

    @staticmethod
    def point_to_segment_distance(px, py, x1, y1, x2, y2):
        line_mag = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if line_mag < 0.000001:
            return math.sqrt((px - x1) ** 2 + (py - y1) ** 2)
        u1 = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (line_mag ** 2)
        u = max(0, min(1, u1))
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        return math.sqrt((px - ix) ** 2 + (py - iy) ** 2)
