import pygame
import pygame.gfxdraw
import time

from stand import HirableBully, CookieGirl

def draw_rounded_rect(surface, rect, color, radius, alpha=150):
    rect = pygame.Rect(rect)
    color = (*color, alpha)  # Adding transparency to the color
    corner_radius = min(rect.width, rect.height) // radius  # ensure corner radius doesn't exceed rectangle size

    # Create a temporary surface with transparency
    alpha_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    alpha_surface = alpha_surface.convert_alpha()

    # Draw the four corners
    pygame.draw.circle(alpha_surface, color, (corner_radius, corner_radius), corner_radius)
    pygame.draw.circle(alpha_surface, color, (rect.width - corner_radius, corner_radius), corner_radius)
    pygame.draw.circle(alpha_surface, color, (corner_radius, rect.height - corner_radius), corner_radius)
    pygame.draw.circle(alpha_surface, color, (rect.width - corner_radius, rect.height - corner_radius), corner_radius)

    # Draw the rectangles to connect the corners
    pygame.draw.rect(alpha_surface, color, (corner_radius, 0, rect.width - 2 * corner_radius, rect.height))
    pygame.draw.rect(alpha_surface, color, (0, corner_radius, rect.width, rect.height - 2 * corner_radius))

    # Blit the temporary surface onto the main surface
    surface.blit(alpha_surface, rect.topleft)


class ScoreManager:
    def __init__(self, player, enemy, font, stands_font, time_limit, cup):
        self.cup = cup
        self.player = player
        self.enemy = enemy
        self.font = font
        self.stands_font = stands_font
        self.time_limit = time_limit
        self.start_time = pygame.time.get_ticks()
        self.player_score = 0.0
        self.opponent_score = 0.0
        self.last_update_time = pygame.time.get_ticks()

    def update_scores(self, current_time, opp_stands, message_box):
        if current_time - self.last_update_time >= 1000:
            self.player_score += self.player.score_rate
            self.player.score = self.player_score  # Update player's score
            self.opponent_score += self.enemy.score_rate
            self.last_update_time = current_time

            for stand in opp_stands:
                if isinstance(stand, HirableBully):
                    stand.bully_steal_check(self.player, message_box)
                    stand.bully_steal_check(self.enemy, message_box)

    def calculate_score_rates(self, opp_stands):
        player_stands_controlled = sum(
            1 for stand in opp_stands if stand.controlled_by_player and not isinstance(stand, (CookieGirl, HirableBully)))
        enemy_stands_controlled = sum(
            1 for stand in opp_stands if stand.controlled_by_enemy and not isinstance(stand, (CookieGirl, HirableBully)))

        self.player.score_rate = 0.05 * player_stands_controlled
        self.enemy.score_rate = 0.05 * enemy_stands_controlled

        if self.player.has_cookie_girl:
            self.player.score_rate += 0.05
        if self.player.has_bully:
            self.enemy.score_rate -= 0.05

        if self.enemy.has_cookie_girl:
            self.enemy.score_rate += 0.05
        if self.enemy.has_bully:
            self.player.score_rate -= 0.05

    def draw_scores(self, screen, width, height, opp_stands):
        player_stands_controlled = sum(
            1 for stand in opp_stands if
            stand.controlled_by_player and not isinstance(stand, (CookieGirl, HirableBully)))
        enemy_stands_controlled = sum(
            1 for stand in opp_stands if
            stand.controlled_by_enemy and not isinstance(stand, (CookieGirl, HirableBully)))

        player_score_text = self.font.render(f'Player: ${self.player_score:.2f}', True, (255, 255, 255))
        player_stands_text = self.stands_font.render(f'Stands Controlled: {player_stands_controlled}', True,
                                                     (255, 255, 255))
        player_score_rate_text = self.font.render(f'Score Rate: {self.player.score_rate:.2f}', True, (255, 255, 255))

        opponent_score_text = self.font.render(f'Opponent: ${self.opponent_score:.2f}', True, (255, 255, 255))
        enemy_stands_text = self.stands_font.render(f'Stands Controlled: {enemy_stands_controlled}', True,
                                                    (255, 255, 255))
        enemy_score_rate_text = self.font.render(f'Score Rate: {self.enemy.score_rate:.2f}', True, (255, 255, 255))

        alpha = 150  # Define the transparency level

        # Background for player score
        player_rect = pygame.Rect(5, 5, player_score_text.get_width() + 100,
                                  player_score_text.get_height() + 100)  # Increase width to accommodate the cup
        draw_rounded_rect(screen, player_rect, (0, 0, 0), 10, alpha)
        # Background for enemy score
        draw_rounded_rect(screen, pygame.Rect(width - opponent_score_text.get_width() - 15, 5,
                                              opponent_score_text.get_width() + 10,
                                              opponent_score_text.get_height() + 100), (0, 0, 0), 10, alpha)
        # Background for timer
        draw_rounded_rect(screen, pygame.Rect(width // 2 - 62, 5, 125, 35), (0, 0, 0), 10, alpha)

        # Blit texts
        screen.blit(player_score_text, (10, 10))
        screen.blit(player_stands_text, (10, 40))
        screen.blit(player_score_rate_text, (10, 70))

        screen.blit(opponent_score_text, (width - opponent_score_text.get_width() - 10, 10))
        screen.blit(enemy_stands_text, (width - enemy_stands_text.get_width() - 10, 40))
        screen.blit(enemy_score_rate_text, (width - enemy_score_rate_text.get_width() - 10, 70))

        if self.player.has_bully:
            pygame.draw.circle(screen, (0, 0, 255), (20, 110), 10)  # Blue circle for bully
        if self.player.has_cookie_girl:
            pygame.draw.circle(screen, (255, 0, 255), (50, 110), 10)  # Magenta circle for cookie girl
        if self.enemy.has_bully:
            pygame.draw.circle(screen, (0, 0, 255), (width - 20, 110), 10)  # Blue circle for enemy bully
        if self.enemy.has_cookie_girl:
            pygame.draw.circle(screen, (255, 0, 255), (width - 50, 110), 10)  # Magenta circle for enemy cookie girl

        # Timer
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        remaining_time = max(0, self.time_limit - elapsed_time)
        timer_text = self.font.render(f'Time: {remaining_time // 1000}', True, (255, 255, 255))
        screen.blit(timer_text, (width // 2 - timer_text.get_width() // 2, 10))

        # Draw the cup with right justification in the player score overlay
        cup_x_offset = player_rect.right - 40  # Adjust position as necessary
        self.cup.update_position(cup_x_offset, 10)
        self.cup.draw(screen)

    def reset(self):
        self.player_score = 0.0
        self.opponent_score = 0.0
        self.start_time = pygame.time.get_ticks()

    def reset(self):
        self.player_score = 0.0
        self.opponent_score = 0.0
        self.start_time = pygame.time.get_ticks()