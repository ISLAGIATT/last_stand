import pygame
import sys


class TitleScreen:
    def __init__(self, screen, font, width, height):
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.padding = 10
        self.title_font = pygame.font.SysFont("Courier", 42, bold=True)
        self.subtitle_font = pygame.font.SysFont("Courier", 36)
        self.title_image = pygame.image.load('images/title.png').convert_alpha()  # Path to your title image
        title_image_width = width - 2 * self.padding
        title_image_height = (height * 2 // 3) - self.padding
        self.title_image = pygame.transform.scale(self.title_image, (title_image_width, title_image_height))
        self.title_text = self.title_font.render('The Last Stand', True, (255, 255, 255))
        self.start_text = self.subtitle_font.render('Press any key to start', True, (255, 255, 255))
        self.title_music = 'audio/title_track.ogg'  # Path to your title music file
        pygame.mixer.init()
        pygame.mixer.music.load(self.title_music)
        pygame.mixer.music.play(-1)  # Loop the music

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title_image, (self.padding, self.padding))
        self.screen.blit(self.title_text, (self.width // 2 - self.title_text.get_width() // 2, self.height * 2 // 3 + 40))
        self.screen.blit(self.start_text, (self.width // 2 - self.start_text.get_width() // 2, self.height * 2 // 3 + 100))
        pygame.display.flip()

    def stop_music(self):
        pygame.mixer.music.fadeout(1000)  # Fade out music over 1 second

    def show(self):
        waiting_for_start = True
        while waiting_for_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting_for_start = False
            self.draw()

class InstructionsScreen:
    def __init__(self, screen, font, width, height):
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.padding = 20
        self.instructions = [
            "Instructions:",
            "1. Use arrow keys to move your character.",
            "2. Interact with stands to gain control.",
            "3. Sabotage enemy stands to gain an advantage.",
            "4. Avoid enemies and obstacles.",
            "5. First to control all stands wins.",
            "Press ESC to return to the title screen."
        ]
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)

    def draw(self):
        self.screen.fill(self.bg_color)
        y = self.padding
        for line in self.instructions:
            text = self.font.render(line, True, self.text_color)
            self.screen.blit(text, (self.padding, y))
            y += text.get_height() + self.padding
        pygame.display.flip()

    def show(self):
        showing_instructions = True
        while showing_instructions:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing_instructions = False
            self.draw()


class GameOverScreen:
    def __init__(self, screen, font, player_score, opponent_score, width, height):
        self.screen = screen
        self.font = font
        self.game_over_font = pygame.font.SysFont("Arial", 36, "bold")
        self.player_score = player_score
        self.opponent_score = opponent_score
        self.width = width
        self.height = height
        self.padding = 10
        self.game_over_image = pygame.image.load('images/game_over.png').convert_alpha()
        game_over_image_width = width - 2 * self.padding
        game_over_image_height = (height * 2 // 3) - self.padding
        self.game_over_image = pygame.transform.scale(self.game_over_image,
                                                      (game_over_image_width, game_over_image_height))

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game_over_image, (self.padding, self.padding))

        game_over_text = self.game_over_font.render('Game Over', False, (255, 255, 255))
        player_score_text = self.font.render(f'Player Score: ${self.player_score:.2f}', True, (255, 255, 255))
        opponent_score_text = self.font.render(f'Opponent Score: ${self.opponent_score:.2f}', True, (255, 255, 255))

        if self.player_score > self.opponent_score:
            winner_text = self.font.render('You Win!', True, (0, 255, 0))
        elif self.player_score < self.opponent_score:
            winner_text = self.font.render('You Lose!', True, (255, 0, 0))
        else:
            winner_text = self.font.render('It\'s a Tie!', True, (255, 255, 0))

        self.draw_text_with_background(game_over_text,
                                       (self.width // 2 - game_over_text.get_width() // 2, self.height // 3))
        self.draw_text_with_background(player_score_text,
                                       (self.width // 2 - player_score_text.get_width() // 2, 600))
        self.draw_text_with_background(opponent_score_text,
                                       (self.width // 2 - opponent_score_text.get_width() // 2, 600 + 50))
        self.draw_text_with_background(winner_text,
                                       (self.width // 2 - winner_text.get_width() // 2, 600 + 100))

        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    pygame.quit()
                    sys.exit()

    def draw_text_with_background(self, text_surface, position):
        rect = text_surface.get_rect(topleft=position).inflate(10, 10)
        pygame.draw.rect(self.screen, (0, 0, 0), rect)
        self.screen.blit(text_surface, position)
