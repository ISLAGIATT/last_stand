import random
import time
import pygame

from message_box import MessageBox
from player import Player


def blink_color(color, start_time):
    elapsed = time.time() - start_time
    if int(elapsed * 5) % 2 == 0:  # Blinks every 0.2 seconds
        return color
    else:
        return (0, 0, 0)  # Blinking effect


class Stand:
    next_id = 1  # Class-level attribute to keep track of the next ID to assign

    def __init__(self, x, y, size, color):
        self.id = Stand.next_id
        Stand.next_id += 1
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
        self.is_sabotage_target = False  # Mark if this stand is the target for sabotage

    def draw(self, surface, camera_offset):
        if self.controlled_by_enemy:
            if self.blink_start_time is None:
                self.blink_start_time = time.time()
            color = blink_color((255, 0, 0), self.blink_start_time)
        else:
            color = self.color
        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                                 self.size)
        pygame.draw.rect(surface, color, stand_rect)
        return stand_rect

    def handle_collision(self, player_rect, camera_offset, player, dialogue_manager, game_state_manager, player_cup,
                         enemy_cup, message_box):
        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                                 self.size)
        if player_rect.colliderect(stand_rect):
            if game_state_manager.got_pee and game_state_manager.sabotage_in_progress and game_state_manager.sabotage_stand_id == self.id:
                self.complete_sabotage(player, dialogue_manager, game_state_manager, player_cup, enemy_cup, message_box)
            elif not self.encounter_triggered and not game_state_manager.sabotage_in_progress:
                self.handle_encounter(player, dialogue_manager, game_state_manager, message_box)
                self.encounter_triggered = True

    def handle_enemy_collision(self, enemy_rect, camera_offset, enemy, dialogue_manager, game_state_manager,
                               message_box):
        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                                 self.size)
        if enemy_rect.colliderect(stand_rect):
            if not self.enemy_in_contact:
                self.handle_encounter(enemy, dialogue_manager, game_state_manager, message_box)
                self.enemy_in_contact = True
        else:
            self.enemy_in_contact = False

    def complete_sabotage(self, player, dialogue_manager, game_state_manager, player_cup, enemy_cup, message_box):
        cookie_girl_penalty = 30 if player.has_cookie_girl else 0
        roll = random.randint(1, 100)
        sabotage_failed = roll <= cookie_girl_penalty
        sabotage_movement_delay = 3.5

        if sabotage_failed:
            print(f"{roll} out of 100")
            self.encounter_triggered = True  # Make it off-limits
            dialogue_texts = ["Drink up!", "Oh that's disgusting. I'm telling!"]

            def update_message_box():
                if player.has_cookie_girl:
                    message_box.add_message("Girl scout has left.")
                    player.has_cookie_girl = False
                    print("Failure due to the cookie girl penalty.")
                message_box.add_message("Sabotage failed! This stand is now off-limits to you.")

            dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                            source="player")
        else:
            success_chance = 50  # Adjust success chance as needed
            sabotage_result = random.randint(1, 100) < success_chance

            if sabotage_result:
                self.controlled_by_player = True
                self.color = (0, 200, 0)  # Change to green
                # Disable player movement for 4 seconds
                game_state_manager.encounter_triggered_by_player = True
                game_state_manager.player_movement_delay = time.time() + sabotage_movement_delay

                def update_message_box():
                    message_box.add_message("Sabotage successful! This stand is now under your control.")

                dialogue_texts = ["Drink up, buddy...", "**URP** I gotta go home"]
                dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                source="player")
            else:
                self.encounter_triggered = True  # Make it off-limits
                # Disable player movement for 4 seconds
                game_state_manager.encounter_triggered_by_player = True
                game_state_manager.player_movement_delay = time.time() + sabotage_movement_delay

                def update_message_box():
                    message_box.add_message("Sabotage failed! This stand is now off-limits to you.")

                dialogue_texts = ["Drink up, buddy...", "No way am I drinking that."]
                dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                source="player")

        game_state_manager.complete_sabotage(player_cup, enemy_cup)

    def handle_encounter(self, entity, dialogue_manager, game_state_manager, message_box):
        if not self.controlled_by_enemy and not self.controlled_by_player:
            self.encounter_completed = False  # Reset encounter completion flag
            encounter_type = random.randint(1, 3)

            if encounter_type == 1:
                encounter_1_movement_delay = 3.5
                # Disable player movement for 4 seconds
                if isinstance(entity, Player):
                    game_state_manager.encounter_triggered_by_player = True
                    game_state_manager.player_movement_delay = time.time() + encounter_1_movement_delay
                else:
                    game_state_manager.encounter_triggered_by_enemy = True
                    game_state_manager.enemy_movement_delay = time.time() + encounter_1_movement_delay

                dialogue_texts = [
                    "Nice lemonade stand. Would be a shame if something happened to it.",
                    "Oh no! This took three weeks of allowance to build!",
                    "I'll take good care of it."
                ]
                if isinstance(entity, Player):
                    self.pending_control = "player"
                    self.controlled_by_player = True
                    self.color = (0, 255, 0)  # Change to green

                    def update_message_box():
                        message_box.add_message("You took control of this stand.")
                else:
                    self.pending_control = "enemy"
                    self.controlled_by_enemy = True
                    self.color = (255, 0, 0)  # Change to red

                    def update_message_box():
                        message_box.add_message("The enemy took control of this stand.")

                dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                source="player" if isinstance(entity, Player) else "enemy")

            elif encounter_type == 2:
                encounter_2_success_movement_delay = 5.5
                encounter_2_failure_movement_delay = 2
                base_success_chance = 50
                if isinstance(entity, Player):
                    bully_bonus = entity.hirable_bullies * 10
                    success_chance = base_success_chance + bully_bonus
                    roll = random.randint(1, 100)
                    fight_result = roll <= success_chance

                    if fight_result:
                        # Disable player movement for 6 seconds
                        game_state_manager.encounter_triggered_by_player = True
                        game_state_manager.player_movement_delay = time.time() + encounter_2_success_movement_delay
                        dialogue_texts = ["Don't make me come back there.", "You don't have the guts.", "**SMACK**"]
                        self.pending_control = "player"
                        self.controlled_by_player = True

                        def update_message_box():
                            message_box.add_message("You won the fight! This stand is now under your control.")
                            if bully_bonus > 0 and base_success_chance < roll <= success_chance:
                                entity.hirable_bullies -= 1
                                message_box.add_message("The bully announces he is leaving.")
                                print("The bully won the fight for you and left.")
                    else:
                        self.sabotage_required = True
                        game_state_manager.start_sabotage(self)
                        self.is_sabotage_target = True
                        # Disable player movement for 2 seconds
                        game_state_manager.encounter_triggered_by_player = True
                        game_state_manager.player_movement_delay = time.time() + encounter_2_failure_movement_delay
                        dialogue_texts = ["Ow. Sucker punch me? I'll be back."]

                        def update_message_box():
                            message_box.add_message("You lost the fight. You'll have to sabotage them next time.")
                else:
                    success_chance = base_success_chance
                    roll = random.randint(1, 100)
                    fight_result = roll <= success_chance

                    if fight_result:
                        dialogue_texts = None
                        self.pending_control = "enemy"
                        game_state_manager.encounter_triggered_by_enemy = True
                        game_state_manager.enemy_movement_delay = time.time() + encounter_2_success_movement_delay

                        def update_message_box():
                            message_box.add_message("The enemy won the fight and took control of a stand.")
                    else:
                        dialogue_texts = None
                        game_state_manager.encounter_triggered_by_enemy = True
                        game_state_manager.enemy_movement_delay = time.time() + encounter_2_failure_movement_delay

                        def update_message_box():
                            message_box.add_message("The enemy lost the fight.")

                if dialogue_texts:
                    dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                    source="player" if isinstance(entity, Player) else "enemy")
                else:
                    update_message_box()

            elif encounter_type == 3:
                if isinstance(entity, Player):
                    encounter_3_movement_delay = 3.5
                    # Initial encounter, no sabotage check yet
                    self.color = (255, 250, 205)
                    game_state_manager.start_sabotage(self)
                    game_state_manager.sabotage_stand_id = self.id
                    self.is_sabotage_target = True

                    # Disable player movement for 4 seconds
                    game_state_manager.encounter_triggered_by_player = True
                    game_state_manager.player_movement_delay = time.time() + encounter_3_movement_delay

                    dialogue_texts = [
                        "This is mine now.", "Back off, my dad's a cop.", "Psh. I'll be back"]

                    def update_message_box():
                        message_box.add_message(
                            "You need to sabotage this stand. Return to your home stand to get the foul-smelling lemonade.")
                    dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                    source="player")
                else:
                    encounter_3_movement_delay = 3.5
                    self.color = (128, 128, 128)  # Grey for sabotage
                    game_state_manager.start_sabotage(self)
                    game_state_manager.sabotage_stand_id = self.id
                    self.is_sabotage_target = True
                    game_state_manager.encounter_triggered_by_enemy = True
                    game_state_manager.enemy_movement_delay = time.time() + encounter_3_movement_delay
                    dialogue_texts = None

                    def update_message_box():
                        message_box.add_message(
                            "The enemy needs to sabotage a stand. They will return to their home stand to get the foul-smelling lemonade.")
                    dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                    source="enemy")

    def finalize_encounter(self):
        if self.pending_control == "player":
            self.controlled_by_player = True
            self.color = (0, 200, 0)  # Change to green
        elif self.pending_control == "enemy":
            self.controlled_by_enemy = True
            self.color = (255, 0, 0)  # Change to red
        self.encounter_completed = True

    @classmethod
    def is_valid_position(cls, x, y, stands, min_distance=400):
        for stand in stands:
            dist = ((x - stand.position[0]) ** 2 + (y - stand.position[1]) ** 2) ** 0.5
            if dist < min_distance:
                return False
        return True

    @classmethod
    def generate_random_stands(cls, num_random_stands, num_cookie_girls, num_bullies, map_width, map_height):
        opp_stands = []
        while len(opp_stands) < num_random_stands:
            x, y = random.randint(0, map_width), random.randint(0, map_height)
            if cls.is_valid_position(x, y, opp_stands):
                opp_stands.append(cls(x, y, 50, (255, 100, 0)))

        for _ in range(num_cookie_girls):
            while True:
                x, y = random.randint(0, map_width), random.randint(0, map_height)
                if cls.is_valid_position(x, y, opp_stands):
                    opp_stands.append(CookieGirl(x, y))
                    break

        for _ in range(num_bullies):
            while True:
                x, y = random.randint(0, map_width), random.randint(0, map_height)
                if cls.is_valid_position(x, y, opp_stands):
                    opp_stands.append(HirableBully(x, y))
                    break
        return opp_stands


class CookieGirl(Stand):
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


class HirableBully(Stand):
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
        if player.has_bully:
            if random.randint(1, 100) == 1:  # 1 in 100 chance every frame
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
