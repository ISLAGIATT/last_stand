import random
import time

import pygame

from player import Player


def blink_color(color, start_time):
    elapsed = time.time() - start_time
    if int(elapsed * 5) % 2 == 0:  # Blinks every 0.2 seconds
        return color
    else:
        return (0, 0, 0)  # Blinking effect

class BaseStand:
    next_id = 1  # Class-level attribute to keep track of the next ID to assign

    def __init__(self, x, y, size, color):
        self.id = BaseStand.next_id
        BaseStand.next_id += 1
        self.position = [x, y]
        self.size = size
        self.color = color
        self.message_box = None
        self.encounter_triggered = False
        self.controlled_by_player = False
        self.controlled_by_enemy = False
        self.encounter_type = None
        self.sabotage_required = False
        self.blink_start_time = None
        self.encounter_completed = False  # Flag to indicate if encounter dialogue has completed

    def draw(self, surface, camera_offset):
        if self.controlled_by_enemy:
            if self.blink_start_time is None:
                self.blink_start_time = time.time()
            color = blink_color((255, 0, 0), self.blink_start_time)
        else:
            color = self.color
        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size, self.size)
        pygame.draw.rect(surface, color, stand_rect)
        return stand_rect
class HirableBully(BaseStand):
    def __init__(self, x, y):
        super().__init__(x, y, 50, (0, 0, 255))  # Example color: Blue
        self.controlled_by_enemy = False
        self.controlled_by_player = False

    def apply_effect(self, player, game_state_manager):
        if not self.controlled_by_enemy:
            player.hirable_bullies += 1
            game_state_manager.opponent_score_rate = max(0.00, game_state_manager.opponent_score_rate - 0.05)
            print(
                f"Bully added. Opponent score rate decreased by 0.05. Current opponent score rate: {game_state_manager.opponent_score_rate}")

    def draw(self, surface, camera_offset):
        if self.controlled_by_enemy:
            color1 = (0, 0, 255)  # Blue
            color2 = (255, 0, 0)  # Red
            half_width = self.size // 2
            # Draw the left half in Blue
            pygame.draw.rect(surface, color1, (
                self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], half_width, self.size))
            # Draw the right half in Red
            pygame.draw.rect(surface, color2, (
                self.position[0] - camera_offset[0] + half_width, self.position[1] - camera_offset[1], half_width,
                self.size))
        elif self.controlled_by_player:
            color1 = (0, 0, 255)  # Blue
            color2 = (0, 255, 0)  # Green
            half_width = self.size // 2
            # Draw the left half in Blue
            pygame.draw.rect(surface, color1, (
                self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], half_width, self.size))
            # Draw the right half in Green
            pygame.draw.rect(surface, color2, (
                self.position[0] - camera_offset[0] + half_width, self.position[1] - camera_offset[1], half_width,
                self.size))
        else:
            super().draw(surface, camera_offset)

    def handle_encounter(self, entity, dialogue_manager, game_state_manager, message_box):
        if isinstance(entity, Player) and entity.has_bully:
            message_box.add_message("You already have a bully in your employ.")
            return
        elif not isinstance(entity, Player) and entity.has_bully:
            message_box.add_message("The enemy already has a bully in their employ.")
            return

        if not self.controlled_by_enemy and not self.controlled_by_player:
            self.encounter_completed = False  # Reset encounter completion flag
            dialogue_texts = [
                "Care to help me out? I'll make it worth your while.",
                "Yeah, we'll see about that..."
            ]
            if isinstance(entity, Player):
                self.pending_control = "player"
                self.controlled_by_player = True
                self.color = (0, 255, 0)  # Change to green
                self.apply_effect(entity, game_state_manager)
                entity.has_bully = True  # Set the flag indicating the player has a bully
                message_box.add_message("Player hired a bully")

                def update_message_box():
                    message_box.add_message("Player hired a bully")
            else:
                self.pending_control = "enemy"
                self.controlled_by_enemy = True
                self.color = (255, 0, 0)  # Change to red
                entity.has_bully = True

                def update_message_box():
                    message_box.add_message("The enemy hired a bully")

            dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                            source="player" if isinstance(entity, Player) else "enemy")

    def bully_steal_check(self, player, message_box):
        if random.randint(1, 200) == 1:  # 1 in 200 chance
            stolen_amount = player.score * 0.33
            player.score -= stolen_amount
            print(f"The bully stole 33% of your score! You lost ${stolen_amount:.2f}.")
            message_box.add_message(f"The bully stole ${stolen_amount:.2f} from you!")

    def handle_opponent_capture(self, stand, dialogue_manager, game_state_manager, message_box):
        dialogue_texts = [
            "A bully is capturing this stand for you!",
        ]
        dialogue_manager.start_dialogue(dialogue_texts, time.time(), stand.position,
                                        lambda: message_box.add_message("A bully is capturing this stand for you!"),
                                        source="enemy")
        stand.handle_encounter(self, dialogue_manager, game_state_manager, message_box)


class CookieGirl(BaseStand):
    def __init__(self, x, y):
        super().__init__(x, y, 50, (255, 0, 255))  # Example color: Magenta
        self.controlled_by_enemy = False
        self.controlled_by_player = False

    def apply_effect(self, player):
        if not self.controlled_by_enemy:
            player.score_rate += 0.05
            player.has_cookie_girl = True

    def draw(self, surface, camera_offset):
        if self.controlled_by_enemy:
            color1 = (255, 0, 255)  # Magenta
            color2 = (255, 0, 0)  # Red
            half_width = self.size // 2
            # Draw the left half in Magenta
            pygame.draw.rect(surface, color1, (
                self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], half_width, self.size))
            # Draw the right half in Red
            pygame.draw.rect(surface, color2, (
                self.position[0] - camera_offset[0] + half_width, self.position[1] - camera_offset[1], half_width,
                self.size))
        elif self.controlled_by_player:
            color1 = (0, 255, 0)  # Green
            color2 = (255, 0, 255)  # Magenta
            half_width = self.size // 2
            # Draw the left half in Green
            pygame.draw.rect(surface, color1, (
                self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], half_width, self.size))
            # Draw the right half in Magenta
            pygame.draw.rect(surface, color2, (
                self.position[0] - camera_offset[0] + half_width, self.position[1] - camera_offset[1], half_width,
                self.size))
        else:
            super().draw(surface, camera_offset)

    def handle_encounter(self, entity, dialogue_manager, game_state_manager, message_box):
        if isinstance(entity, Player) and entity.has_cookie_girl:
            message_box.add_message("You already have a Girl Scout working with you.")
            return
        elif not isinstance(entity, Player) and entity.has_cookie_girl:
            message_box.add_message("The enemy already has a Girl Scout working with them.")
            return

        if not self.controlled_by_enemy and not self.controlled_by_player:
            self.encounter_completed = False  # Reset encounter completion flag
            if isinstance(entity, Player):
                self.pending_control = "player"
                self.controlled_by_player = True
                self.color = (0, 255, 0)  # Change to green
                self.apply_effect(entity)
                entity.has_cookie_girl = True  # Set the flag indicating the player has a cookie girl

                dialogue_texts = [
                    "Come sell some cookies for me",
                    "Ugh. Only because I feel sorry for you."
                ]

                def update_message_box():
                    message_box.add_message("Player hired a Girl Scout")
                dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                source="player")
            else:
                self.pending_control = "enemy"
                self.controlled_by_enemy = True
                self.color = (255, 0, 0)  # Change to red
                entity.has_cookie_girl = True  # Set the flag indicating the enemy has a cookie girl
                message_box.add_message("The enemy hired a Girl Scout")
