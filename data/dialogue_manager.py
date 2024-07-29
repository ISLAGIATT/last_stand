import pygame
import time


class DialogueManager:
    def __init__(self, font, wrap_width=200):
        self.dialogue_active = False
        self.dialogue_texts = []
        self.dialogue_start_time = None
        self.npc_dialogue_start_time = None
        self.font = font
        self.dialogue_index = 0
        self.wrap_width = wrap_width  # Width of the dialogue bubble in pixels
        self.stand_position = (0, 0)
        self.callback = None  # Add a callback attribute

        self.player_dialogue_active = False
        self.player_dialogue_texts = []
        self.player_dialogue_start_time = None
        self.player_npc_dialogue_start_time = None

        self.enemy_dialogue_active = False
        self.enemy_dialogue_texts = []
        self.enemy_dialogue_start_time = None
        self.enemy_npc_dialogue_start_time = None

    def start_dialogue(self, texts, start_time, stand_position, callback=None, source="player"):
        if source == "player":
            self.player_dialogue_texts = [self.wrap_text(text) for text in texts]
            self.player_dialogue_start_time = start_time
            self.player_npc_dialogue_start_time = start_time + 2  # NPC dialogue starts 2 seconds later
            self.player_dialogue_active = True
            self.dialogue_index = 0  # Reset dialogue_index when starting new dialogue
            self.stand_position = stand_position  # Position of the stand that triggered the dialogue
            self.callback = callback  # Store the callback
        # elif source == "enemy":
        #     self.enemy_dialogue_texts = [self.wrap_text(text) for text in texts]
        #     self.enemy_dialogue_start_time = start_time
        #     self.enemy_npc_dialogue_start_time = start_time + 2  # NPC dialogue starts 2 seconds later
        #     self.enemy_dialogue_active = True
        #     self.dialogue_index = 0  # Reset dialogue_index when starting new dialogue
        #     self.stand_position = stand_position  # Position of the stand that triggered the dialogue
        #     self.callback = callback  # Store the callback

    def wrap_text(self, text):
        """Wrap text to fit within the specified wrap width in pixels."""
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            # Add the next word and a space to the current line
            test_line = ' '.join(current_line + [word])
            # Render the test line to get its width
            test_surface = self.font.render(test_line, True, (255, 255, 255))
            test_width = test_surface.get_width()

            if test_width > self.wrap_width:
                # If the test line is too wide, add the current line to lines and start a new line
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)

        # Add the last line to lines
        lines.append(' '.join(current_line))
        return '\n'.join(lines)

    def draw_dialogue_bubble(self, surface, text, pos, color):
        """Draws a dialogue bubble with the given text at the specified position."""
        lines = text.split('\n')
        max_line_width = max(self.font.size(line)[0] for line in lines)
        total_height = len(lines) * self.font.get_linesize()

        padding = 10
        bubble_width = max_line_width + 2 * padding
        bubble_height = total_height + 2 * padding

        bubble_rect = pygame.Rect(pos[0] - bubble_width // 2, pos[1] - bubble_height, bubble_width, bubble_height)
        pygame.draw.rect(surface, (0, 0, 0), bubble_rect)
        pygame.draw.rect(surface, (0, 200, 0), bubble_rect, 2)  # Black border

        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, color)
            surface.blit(line_surface,
                         (bubble_rect.x + padding, bubble_rect.y + padding + i * self.font.get_linesize()))

    def draw_dialogue(self, surface, camera_offset, player_position, npc_text_color=(255, 0, 0),
                      npc_visible_duration=2):
        current_time = time.time()

        if self.player_dialogue_active and self.player_dialogue_texts:
            player_dialogue_duration = 2  # Duration for each dialogue to be visible

            dialogue_texts = self.player_dialogue_texts
            total_dialogue_count = len(dialogue_texts)
            elapsed_time = current_time - self.player_dialogue_start_time
            current_dialogue_index = int(elapsed_time // player_dialogue_duration)

            if current_dialogue_index < total_dialogue_count:
                is_npc = (current_dialogue_index % 2 == 1)  # NPC dialogues are at odd indices
                dialogue_text = dialogue_texts[current_dialogue_index]

                if is_npc:
                    self.draw_dialogue_bubble(surface, dialogue_text, (
                        self.stand_position[0] - camera_offset[0], self.stand_position[1] - camera_offset[1] + 150),
                                              npc_text_color)
                else:
                    self.draw_dialogue_bubble(surface, dialogue_text, (
                        player_position[0] - camera_offset[0], player_position[1] - camera_offset[1] - 50), (0, 255, 0))
            else:
                self.player_dialogue_active = False
                if self.callback:  # Call the callback if it exists
                    self.callback()

        # if self.enemy_dialogue_active and self.enemy_dialogue_texts:
        #     enemy_dialogue_duration = 2  # Duration for enemy dialogue to be visible
        #     npc_dialogue_start_delay = 2  # Delay before NPC dialogue starts
        #
        #     # Draw enemy dialogue above the stand
        #     if current_time - self.enemy_dialogue_start_time < enemy_dialogue_duration:
        #         self.draw_dialogue_bubble(surface, self.enemy_dialogue_texts[0], (self.stand_position[0] - camera_offset[0], self.stand_position[1] - camera_offset[1] - 100), (255, 0, 0))
        #
        #     # Draw NPC dialogue above the stand
        #     if len(self.enemy_dialogue_texts) > 1 and current_time >= self.enemy_npc_dialogue_start_time and current_time - self.enemy_npc_dialogue_start_time < npc_visible_duration:
        #         self.draw_dialogue_bubble(surface, self.enemy_dialogue_texts[1], (self.stand_position[0] - camera_offset[0], self.stand_position[1] - camera_offset[1] - 150), npc_text_color)
        #     elif len(self.enemy_dialogue_texts) > 1 and current_time - self.enemy_npc_dialogue_start_time >= npc_visible_duration:
        #         self.enemy_dialogue_active = False
        #         if self.callback:  # Call the callback if it exists
        #             self.callback()

