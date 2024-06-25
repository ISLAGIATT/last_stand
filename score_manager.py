import pygame
import time

from stand import CookieGirl, HirableBully

class ScoreManager:
    def __init__(self, player, enemy, font, stands_font, time_limit=2 * 60 * 1000):
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

    def calculate_score_rates(self, opp_stands):
        player_stands_controlled = sum(
            1 for stand in opp_stands if stand.controlled_by_player and not isinstance(stand, (CookieGirl, HirableBully)))
        enemy_stands_controlled = sum(
            1 for stand in opp_stands if stand.controlled_by_enemy and not isinstance(stand, (CookieGirl, HirableBully)))

        # Changes highlighted
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
            1 for stand in opp_stands if stand.controlled_by_player and not isinstance(stand, (CookieGirl, HirableBully)))
        enemy_stands_controlled = sum(
            1 for stand in opp_stands if stand.controlled_by_enemy and not isinstance(stand, (CookieGirl, HirableBully)))

        player_score_text = self.font.render(f'Player: ${self.player_score:.2f}', True, (255, 255, 255))
        player_stands_text = self.stands_font.render(f'Stands Controlled: {player_stands_controlled}', True, (255, 255, 255))
        player_score_rate_text = self.font.render(f'Score Rate: {self.player.score_rate:.2f}', True, (255, 255, 255))

        opponent_score_text = self.font.render(f'Opponent: ${self.opponent_score:.2f}', True, (255, 255, 255))
        enemy_stands_text = self.stands_font.render(f'Stands Controlled: {enemy_stands_controlled}', True, (255, 255, 255))
        enemy_score_rate_text = self.font.render(f'Score Rate: {self.enemy.score_rate:.2f}', True, (255, 255, 255))

        screen.blit(player_score_text, (10, 10))
        screen.blit(player_stands_text, (10, 40))
        screen.blit(player_score_rate_text, (10, 70))

        screen.blit(opponent_score_text, (width - opponent_score_text.get_width() - 10, 10))
        screen.blit(enemy_stands_text, (width - enemy_stands_text.get_width() - 10, 40))
        screen.blit(enemy_score_rate_text, (width - enemy_score_rate_text.get_width() - 10, 70))

        if self.player.has_bully:
            pygame.draw.circle(screen, (0, 0, 255), (10, 110), 10)  # Blue circle for bully
        if self.player.has_cookie_girl:
            pygame.draw.circle(screen, (255, 0, 255), (10, 140), 10)  # Magenta circle for cookie girl
        if self.enemy.has_bully:
            pygame.draw.circle(screen, (0, 0, 255), (width - 10, 110), 10)  # Blue circle for enemy bully
        if self.enemy.has_cookie_girl:
            pygame.draw.circle(screen, (255, 0, 255), (width - 10, 140), 10)  # Magenta circle for enemy cookie girl

        # Timer
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        remaining_time = max(0, self.time_limit - elapsed_time)
        timer_text = self.font.render(f'Time: {remaining_time // 1000}', True, (255, 255, 255))
        screen.blit(timer_text, (width // 2 - timer_text.get_width() // 2, + 20))

    def reset(self):
        self.player_score = 0.0
        self.opponent_score = 0.0
        self.start_time = pygame.time.get_ticks()
