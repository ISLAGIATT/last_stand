import pygame
from abc import ABC, abstractmethod

class GameState(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def enter(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def update(self, events):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

class TitleState(GameState):
    def enter(self):
        pygame.mixer.init()
        pygame.mixer.music.load('music/title_track.ogg')
        pygame.mixer.music.play(-1)

    def exit(self):
        pygame.mixer.music.stop()

    def update(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.change_state('GameLoopState')
                elif event.key == pygame.K_i:
                    self.game.change_state('InstructionState')

    def draw(self, screen):
        screen.fill((0, 0, 0))
        title_text = self.game.font.render('The Last Stand', True, (255, 255, 255))
        start_text = self.game.font.render('Press Enter to Start', True, (255, 255, 255))
        instruction_text = self.game.font.render('Press I for Instructions', True, (255, 255, 255))
        screen.blit(title_text, (self.game.width // 2 - title_text.get_width() // 2, 200))
        screen.blit(start_text, (self.game.width // 2 - start_text.get_width() // 2, 300))
        screen.blit(instruction_text, (self.game.width // 2 - instruction_text.get_width() // 2, 400))

class InstructionState(GameState):
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game.change_state('TitleState')

    def draw(self, screen):
        screen.fill((0, 0, 0))
        instruction_text = self.game.font.render('Instructions: ...', True, (255, 255, 255))
        back_text = self.game.font.render('Press Enter to Go Back', True, (255, 255, 255))
        screen.blit(instruction_text, (self.game.width // 2 - instruction_text.get_width() // 2, 200))
        screen.blit(back_text, (self.game.width // 2 - back_text.get_width() // 2, 300))

class GameLoopState(GameState):
    def enter(self):
        # Initialize your game objects here
        pass

    def exit(self):
        pass

    def update(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.change_state('TitleState')

        # Update game objects here

    def draw(self, screen):
        screen.fill((0, 0, 0))
        # Draw game objects here

class GameOverState(GameState):
    def __init__(self, game, player_score, opponent_score):
        super().__init__(game)
        self.player_score = player_score
        self.opponent_score = opponent_score

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN:
                self.game.change_state('TitleState')

    def draw(self, screen):
        screen.fill((0, 0, 0))
        game_over_text = self.game.font.render('Game Over', True, (255, 255, 255))
        player_score_text = self.game.font.render(f'Player Score: ${self.player_score:.2f}', True, (255, 255, 255))
        opponent_score_text = self.game.font.render(f'Opponent Score: ${self.opponent_score:.2f}', True, (255, 255, 255))
        screen.blit(game_over_text, (self.game.width // 2 - game_over_text.get_width() // 2, 200))
        screen.blit(player_score_text, (self.game.width // 2 - player_score_text.get_width() // 2, 300))
        screen.blit(opponent_score_text, (self.game.width // 2 - opponent_score_text.get_width() // 2, 350))
