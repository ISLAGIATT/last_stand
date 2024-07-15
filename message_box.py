import pygame
import time

class MessageBox:
    def __init__(self, width, height, screen_width, screen_height, font, max_messages=10):
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = font
        self.max_messages = max_messages
        self.messages = []  # List of tuples (message, timestamp, blink)
        self.background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.background.fill((0, 0, 0, 150))  # Black with 150/255 transparency
        self.line_height = self.font.get_height()
        self.vertical_padding = 5  # Padding above and below each line of text
        self.bottom_padding = 10  # Padding at the bottom of the message box

    def add_message(self, message, blink=False):
        current_time = time.time()
        # Split message into lines that fit within the message box width
        words = message.split(' ')
        lines = []
        current_line = '•'  # Start the first line with a bullet point
        for word in words:
            if self.font.size(current_line + ' ' + word)[0] < self.width - 20:  # Adjust for padding
                current_line += ' ' + word if current_line.strip() else word
            else:
                lines.append((current_line, current_time, blink))
                current_line = word  # No bullet point for wrapped lines
        if current_line:
            lines.append((current_line, current_time, blink))

        # Add lines to messages
        self.messages.extend(lines)

        # Remove oldest messages if necessary
        self.clear_old_messages(current_time)

    def clear_old_messages(self, current_time):
        # Remove messages older than 5 seconds
        self.messages = [(msg, timestamp, blink) for msg, timestamp, blink in self.messages if current_time - timestamp <= 5]

        # Ensure the message box does not exceed max height
        while len(self.messages) * (self.line_height + 2 * self.vertical_padding) > self.height - self.bottom_padding:
            self.messages.pop(0)

    def draw(self, surface):
        current_time = time.time()
        self.clear_old_messages(current_time)
        x_position = (self.screen_width - self.width) // 2
        y_position = self.screen_height - self.height - 50  # 50-pixel buffer at the bottom
        surface.blit(self.background, (x_position, y_position))
        for i, (message, timestamp, blink) in enumerate(self.messages):
            color = self.get_blink_color() if blink else (255, 255, 255)
            text_surface = self.font.render(message, True, color)
            y_offset = y_position + 10 + i * (self.line_height + 2 * self.vertical_padding)
            surface.blit(text_surface, (x_position + 10, y_offset + self.vertical_padding))

    def get_blink_color(self):
        elapsed = time.time() - self.messages[0][1]  # Use the timestamp of the first message
        cycle_time = 0.25  # Change color every 0.5 seconds
        cycle_phase = (elapsed % (cycle_time * 3)) / cycle_time
        if cycle_phase < 1:
            return (255, 0, 0)  # Red
        elif cycle_phase < 2:
            return (0, 0, 255)  # Blue
        else:
            return (255, 255, 255)  # White
