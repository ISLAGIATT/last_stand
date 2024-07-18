import pygame
import sys

def render_text_wrapped(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        width, _ = font.size(' '.join(current_line))
        if width > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]

    lines.append(' '.join(current_line))
    return [font.render(line, True, (255, 255, 255)) for line in lines]

class InstructionScreen:
    def __init__(self, screen, font, width, height):
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.running = True
        self.instruction_font = pygame.font.SysFont("Courier", 16, bold=True)

        # Load animations or images for each character and resize to 75px
        self.bully_images = [pygame.transform.scale(pygame.image.load(f'anim/bully/bully{i}.png').convert_alpha(), (75, 75)) for i in range(1, 6)]
        self.cookie_girl_images = [pygame.transform.scale(pygame.image.load(f'anim/cookie_girl/cookie_girl{i}.png').convert_alpha(), (75, 75)) for i in range(1, 5)]
        self.cop_images = [pygame.transform.scale(pygame.image.load(f'anim/cop/cop_down{i}.png').convert_alpha(), (75, 75)) for i in range(1, 7)]
        self.player_images = [pygame.transform.scale(pygame.image.load(f'anim/player/player_idle{i}.png').convert_alpha(), (75, 75)) for i in range(1, 7)]
        self.customer_images = [pygame.transform.scale(pygame.image.load(f'anim/customer/customer_walk_down{i}.png').convert_alpha(), (75, 75)) for i in range(1, 7)]
        self.stand_image = pygame.transform.scale(pygame.image.load('images/stand_200px.png').convert_alpha(), (75, 75))

        self.frame_index = 0
        self.animation_speed = 0.01
        self.frame_timer = 0

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Draw title
        title_text = self.font.render('Game Instructions', True, (255, 255, 255))
        self.screen.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 50))

        # Update animation frame index
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % max(len(self.bully_images), len(self.cookie_girl_images), len(self.cop_images), len(self.player_images), len(self.customer_images))

        # Characters and labels
        characters = [
            ('this is you', self.player_images),
            ('scare off rival lemonade stand owners!', [self.stand_image]),
            ('bullies can help in fights and make it harder for the other guy to make money, but will steal from you', self.bully_images),
            ('customers will slow you down', self.customer_images),
            ('girl scouts will sell cookies for you, but will rat you out if you get out of hand', self.cookie_girl_images),
            ('after the time limit is up, this guy will come shake you down', self.cop_images),
        ]

        y_start = 150
        y_offset = 100
        max_text_width = self.width - 250

        for i, (label, images) in enumerate(characters):
            x_position = 100 if i % 2 == 0 else self.width - 175  # Alternate left and right
            self.screen.blit(images[self.frame_index % len(images)], (x_position, y_start + i * y_offset))
            wrapped_text = render_text_wrapped(label, self.instruction_font, max_text_width)
            text_x_position = x_position + 100 if i % 2 == 0 else x_position - max(wrapped_text, key=lambda
                s: s.get_width()).get_width() - 25
            for j, line in enumerate(wrapped_text):
                self.screen.blit(line, (text_x_position, y_start + i * y_offset + 25 + j * 30))

        pygame.display.flip()

    def show(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False  # Exit to title screen

            self.draw()

class TitleScreen:
    def __init__(self, screen, font, width, height, instruction_screen):
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
        # self.start_text = self.subtitle_font.render('Press any key to start', True, (255, 255, 255))
        self.instruction_text = font.render('Instructions', True, (255, 255, 255))
        self.title_music = 'audio/title_track.ogg'  # Path to your title music file
        pygame.mixer.init()
        pygame.mixer.music.load(self.title_music)
        pygame.mixer.music.play(-1)  # Loop the music

        self.options = [
            ('Start Game', self.subtitle_font.render('Press any key to start', True, (255, 255, 255))),
            ('Instructions', self.subtitle_font.render('Instructions', True, (255, 255, 255)))
        ]
        self.current_option = 0
        self.instruction_screen = instruction_screen

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title_image, (self.padding, self.padding))
        self.screen.blit(self.title_text, (self.width // 2 - self.title_text.get_width() // 2, self.height * 2 // 3 + 40))
        # self.screen.blit(self.start_text, (self.width // 2 - self.start_text.get_width() // 2, self.height * 2 // 3 + 100))

        for i, (text, option_surface) in enumerate(self.options):
            color = (255, 255, 0) if i == self.current_option else (255, 255, 255)
            option_surface = self.subtitle_font.render(text, True, color)
            self.screen.blit(option_surface,
                             (self.width // 2 - option_surface.get_width() // 2, self.height * 2 // 3 + 100 + i * 40))
        pygame.display.flip()
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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.current_option = (self.current_option - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.current_option = (self.current_option + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.current_option == 0:
                            waiting_for_start = False
                        elif self.current_option == 1:
                            self.stop_music()
                            self.instruction_screen.show()
                            pygame.mixer.music.play(-1)  # Restart the title music
                            self.draw()  # Redraw title screen after returning from instructions
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if self.current_option == 0:
                            waiting_for_start = False
                        elif self.current_option == 1:
                            self.stop_music()
                            self.instruction_screen.show()
                            pygame.mixer.music.play(-1)  # Restart the title music
                            self.draw()  # Redraw title screen after returning from instructions

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
