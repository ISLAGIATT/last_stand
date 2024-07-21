import random
import time
import pygame

from message_box import MessageBox
from player import Player
from running_person import RunningPerson


def blink_color(color, start_time):
    elapsed = time.time() - start_time
    if int(elapsed * 5) % 2 == 0:  # Blinks every 0.2 seconds
        return color
    else:
        return (0, 0, 0)  # Blinking effect


class Stand:
    next_id = 1  # Class-level attribute to keep track of the next ID to assign

    def __init__(self, x, y, size, color, image_path="images/stand_200px.png"):
        self.id = Stand.next_id
        Stand.next_id += 1
        self.position = [x, y]
        self.size = size
        self.color = color
        self.image_path = image_path
        self.player_image_path = "images/stand_player.png"
        self.enemy_image_path = "images/stand_enemy.png"
        self.contact_image_path = "images/home_base_occupied.png"
        self.inactive_image_path = 'images/stand_inactive.gif'

        self.image = pygame.image.load(image_path) if image_path else None

        # Load default image
        self.image = pygame.image.load(image_path) if image_path else None
        if self.image:
            self.image = pygame.transform.scale(self.image, (size, size))

        # Load contact image
        self.contact_image = pygame.image.load(self.contact_image_path) if self.contact_image_path else None
        if self.contact_image:
            self.contact_image = pygame.transform.scale(self.contact_image, (size, size))

        # Load player-controlled image
        self.player_image = pygame.image.load(self.player_image_path) if self.player_image_path else None
        if self.player_image:
            self.player_image = pygame.transform.scale(self.player_image, (size, size))

        # Load enemy-controlled image
        self.enemy_image = pygame.image.load(self.enemy_image_path) if self.enemy_image_path else None
        if self.enemy_image:
            self.enemy_image = pygame.transform.scale(self.enemy_image, (size, size))

        # Load inactive image
        self.inactive_image = pygame.image.load(self.inactive_image_path) if self.inactive_image_path else None
        if self.inactive_image:
            self.inactive_image = pygame.transform.scale(self.inactive_image, (size, size))

        # Create shadow surface
        self.shadow = pygame.Surface((size, size // 2), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow, (0, 0, 0, 100), self.shadow.get_rect())

        self.message_box = None
        self.encounter_triggered = False
        self.controlled_by_player = False # for draw method
        self.controlled_by_enemy = False # for draw method
        self.inactive = False # for failed sabotage draw method
        self.encounter_type = None
        self.sabotage_required = False
        self.blink_start_time = None
        self.encounter_completed = False  # Flag to indicate if encounter dialogue has completed
        self.is_sabotage_target = False  # Mark if this stand is the target for sabotage
        self.running_persons = []  # List to store running persons
        self.sabotage_alpha = 255  # Initial alpha value for the stand image
        self.sabotage_alpha_direction = -5  # Direction for alpha change

    def update_running_persons(self, map_width, map_height):
        self.running_persons = [person for person in self.running_persons if not person.is_off_screen(map_width, map_height)]
        for person in self.running_persons:
            person.move()

    def draw_running_persons(self, surface, camera_offset):
        for person in self.running_persons:
            person.draw(surface, camera_offset)

    def set_home_stand_image(self, in_contact):
        if in_contact and self.contact_image:
            self.image = self.contact_image
        else:
            self.image = pygame.image.load(self.image_path)
            if self.image:
                self.image = pygame.transform.scale(self.image, (self.size, self.size))

    def draw(self, surface, camera_offset):
        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size, self.size)

        # Blit the shadow
        shadow_offset = (0 + 5, self.size // 1.66)  # Adjust shadow position
        surface.blit(self.shadow, (stand_rect.topleft[0] + shadow_offset[0], stand_rect.topleft[1] + shadow_offset[1]))

        if self.inactive:
            image = self.inactive_image
        elif self.controlled_by_player:
            image = self.player_image
        elif self.controlled_by_enemy:
            image = self.enemy_image
        else:
            image = self.image

        if image:
            if self.is_sabotage_target:
                self.sabotage_alpha += self.sabotage_alpha_direction
                if self.sabotage_alpha <= 100 or self.sabotage_alpha >= 255:
                    self.sabotage_alpha_direction *= -1

                temp_image = image.copy()
                temp_image.fill((255, 255, 255, self.sabotage_alpha), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(temp_image, stand_rect.topleft)
            else:
                surface.blit(image, stand_rect.topleft)
        else:
            pygame.draw.rect(surface, self.color, stand_rect)

        return stand_rect

    def handle_collision(self, player_rect, camera_offset, player, dialogue_manager, game_state_manager, player_cup, message_box):
        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size,
                                 self.size)
        if player_rect.colliderect(stand_rect):
            if game_state_manager.got_pee and game_state_manager.sabotage_in_progress and game_state_manager.sabotage_stand_id == self.id:
                self.complete_sabotage(player, dialogue_manager, game_state_manager, player_cup, message_box)
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

    def complete_sabotage(self, player, dialogue_manager, game_state_manager, player_cup, message_box):
        cookie_girl_penalty = 30 if player.has_cookie_girl else 0
        roll = random.randint(1, 100)
        sabotage_failed = roll <= cookie_girl_penalty
        sabotage_movement_delay = 3.5

        if sabotage_failed:
            print(f"{roll} out of 100")
            self.encounter_triggered = True  # Make it off-limits
            self.inactive = True
            dialogue_texts = ["Drink up!", "Oh that's disgusting. I'm telling!"]

            def update_message_box():
                if player.has_cookie_girl:
                    message_box.add_message("Girl scout has left.")
                    player.has_cookie_girl = False
                    print("Failure due to the cookie girl penalty.")
                message_box.add_message("Sabotage failed! Girl Scout ratted you out!")

            dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                            source="player")
        else:
            success_chance = 50  # Adjust success chance as needed
            sabotage_result = random.randint(1, 100) < success_chance

            if sabotage_result:
                # Disable player movement for 4 seconds
                game_state_manager.encounter_triggered_by_player = True
                game_state_manager.player_movement_delay = time.time() + sabotage_movement_delay

                def update_message_box():
                    message_box.add_message("Sabotage successful! This stand is now under your control.")
                    running_person = RunningPerson(self.position[0], self.position[1], 25, 5)
                    self.controlled_by_player = True
                    self.color = (0, 200, 0)  # Change to green
                    self.running_persons.append(running_person)

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
                    self.inactive = True

                dialogue_texts = ["Drink up, buddy...", "No way am I drinking that."]
                dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                source="player")

        game_state_manager.complete_sabotage(player_cup)

        def update_running_persons(self):
            for person in self.running_persons:
                person.move()

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
                    self.color = (0, 255, 0)  # Change to green

                    def update_message_box():
                        message_box.add_message("You took control of this stand.")
                        # Add running person animation
                        running_person = RunningPerson(self.position[0], self.position[1], 25, entity.speed)
                        self.running_persons.append(running_person)
                        self.controlled_by_player = True

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

                        def update_message_box():
                            message_box.add_message("You won the fight! This stand is now under your control.")
                            running_person = RunningPerson(self.position[0], self.position[1], 25,
                                                           entity.speed)
                            self.running_persons.append(running_person)
                            if bully_bonus > 0 and base_success_chance < roll <= success_chance:
                                entity.hirable_bullies -= 1
                                message_box.add_message("The bully announces he is leaving.")
                                print("The bully won the fight for you and left.")
                            self.controlled_by_player = True

                    else:
                        self.sabotage_required = True
                        game_state_manager.start_sabotage(self)
                        # Disable player movement for 2 seconds
                        game_state_manager.encounter_triggered_by_player = True
                        game_state_manager.player_movement_delay = time.time() + encounter_2_failure_movement_delay
                        dialogue_texts = ["Ow. Sucker punch me? I'll be back."]

                        def update_message_box():
                            message_box.add_message("You lost the fight. Return to this stand with some foul-tasting lemonade!")
                            self.is_sabotage_target = True
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
                    game_state_manager.sabotage_stand_id = self.id

                    # Disable player movement for 4 seconds
                    game_state_manager.encounter_triggered_by_player = True
                    game_state_manager.player_movement_delay = time.time() + encounter_3_movement_delay

                    dialogue_texts = [
                        "This is mine now.", "Back off, my dad's a cop.", "Psh. I'll be back"]

                    def update_message_box():
                        message_box.add_message(
                            "You need to sabotage this stand. Go to a quiet place to get the foul-smelling lemonade.")
                        self.is_sabotage_target = True
                        game_state_manager.start_sabotage(self)

                    dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                    source="player")
                else:
                    # enabling sabotage for enemy player being saved for later

                    # encounter_3_movement_delay = 3.5
                    # self.color = (128, 128, 128)  # Grey for sabotage
                    # game_state_manager.start_sabotage(self)
                    # game_state_manager.sabotage_stand_id = self.id
                    # self.is_sabotage_target = True
                    # game_state_manager.encounter_triggered_by_enemy = True
                    # game_state_manager.enemy_movement_delay = time.time() + encounter_3_movement_delay
                    # dialogue_texts = None
                    #
                    # def update_message_box():
                    #     message_box.add_message(
                    #         "The enemy needs to sabotage a stand. They will return to their home stand to get the foul-smelling lemonade.")
                    #
                    # dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                    #                                 source="enemy")
                    pass

    def finalize_encounter(self):
        if self.pending_control == "player":
            self.controlled_by_player = True
            self.color = (0, 200, 0)  # Change to green
        elif self.pending_control == "enemy":
            self.controlled_by_enemy = True
            self.color = (255, 0, 0)  # Change to red
        self.encounter_completed = True

    @classmethod
    def is_valid_position(cls, x, y, stands, min_distance=400, player_pos=None, enemy_pos=None, safe_distance=300):
        for stand in stands:
            dist = ((x - stand.position[0]) ** 2 + (y - stand.position[1]) ** 2) ** 0.5
            if dist < min_distance:
                return False

        if player_pos:
            player_dist = ((x - player_pos[0]) ** 2 + (y - player_pos[1]) ** 2) ** 0.5
            if player_dist < safe_distance:
                return False

        if enemy_pos:
            enemy_dist = ((x - enemy_pos[0]) ** 2 + (y - enemy_pos[1]) ** 2) ** 0.5
            if enemy_dist < safe_distance:
                return False

        return True

    @classmethod
    def generate_random_stands(cls, num_random_stands, num_cookie_girls, num_bullies, map_width, map_height, player_pos,
                               enemy_pos):
        opp_stands = []
        while len(opp_stands) < num_random_stands:
            x, y = random.randint(0, map_width), random.randint(0, map_height)
            if cls.is_valid_position(x, y, opp_stands, player_pos=player_pos, enemy_pos=enemy_pos):
                opp_stands.append(cls(x, y, 75, (255, 100, 0)))  # change stand image size here

        for _ in range(num_cookie_girls):
            while True:
                x, y = random.randint(0, map_width), random.randint(0, map_height)
                if cls.is_valid_position(x, y, opp_stands, player_pos=player_pos, enemy_pos=enemy_pos):
                    opp_stands.append(CookieGirl(x, y))
                    break

        for _ in range(num_bullies):
            while True:
                x, y = random.randint(0, map_width), random.randint(0, map_height)
                if cls.is_valid_position(x, y, opp_stands, player_pos=player_pos, enemy_pos=enemy_pos):
                    opp_stands.append(HirableBully(x, y))
                    break
        return opp_stands


class CookieGirl(Stand):
    def __init__(self, x, y, size=75, image_path="images/cookie_girl_70px.png"):
        super().__init__(x, y, size, (255, 0, 255))  # Example color: Magenta
        self.controlled_by_enemy = False
        self.controlled_by_player = False
        self.frame_index = 0
        self.animation_speed = .05
        self.frame_timer = 0
        self.hired = False  # To track if the cookie girl has been hired

        # Load animation frames and scale them to the desired size
        self.animations = [
            pygame.transform.scale(pygame.image.load(f'anim/cookie_girl/cookie_girl{i}.png').convert_alpha(),
                                   (self.size, self.size)) for i in range(1, 5)]
        self.image = self.animations[0]  # Default frame

        self.image_size = self.image.get_size()
        self.shadow = self.create_ovular_shadow(self.image, (0, 0, 0, 100))  # Create an ovular shadow with 100 alpha

    def create_ovular_shadow(self, image, shadow_color):
        shadow = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(0, 0, image.get_width(), image.get_height())
        ellipse_rect = pygame.Rect(0, 0, image.get_width() * 0.6, image.get_height() * 0.3)
        ellipse_rect.center = (shadow_rect.centerx - 10, shadow_rect.centery + 15)  # Adjust x, y position here
        pygame.draw.ellipse(shadow, shadow_color, ellipse_rect)
        return shadow

    def update_animation(self):
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations)
            self.image = self.animations[self.frame_index]

    def draw(self, surface, camera_offset):
        if self.hired:
            return  # Do not draw if the cookie girl is hired

        self.update_animation()

        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1],
                                 self.image_size[0], self.image_size[1])

        # Draw shadow first
        shadow_offset = (30, self.image_size[1] * 0.3)  # Adjust shadow position here
        shadow_pos = (stand_rect.topleft[0] + shadow_offset[0], stand_rect.topleft[1] + shadow_offset[1])
        surface.blit(self.shadow, shadow_pos)

        # Draw the sprite image
        surface.blit(self.image, stand_rect.topleft)

        overlay_surface = pygame.Surface(self.image_size, pygame.SRCALPHA)
        surface.blit(overlay_surface, stand_rect.topleft)

    def apply_effect(self, player):
        if not self.controlled_by_enemy:
            player.score_rate += 0.05
            player.has_cookie_girl = True

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
                self.apply_effect(entity)
                entity.has_cookie_girl = True  # Set the flag indicating the player has a cookie girl

                dialogue_texts = [
                    "Come sell some cookies for me",
                    "Ugh. Only because I feel sorry for you."
                ]

                def update_message_box():
                    message_box.add_message("Player hired a Girl Scout")
                    self.hired = True

                dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                                source="player")
            else:
                self.pending_control = "enemy"
                self.controlled_by_enemy = True
                self.hired = True
                entity.has_cookie_girl = True  # Set the flag indicating the enemy has a cookie girl
                message_box.add_message("The enemy hired a Girl Scout")


class HirableBully(Stand):
    def __init__(self, x, y):
        super().__init__(x, y, 75, (0, 0, 255))  # Example color: Blue
        self.controlled_by_enemy = False
        self.controlled_by_player = False
        self.frame_index = 0
        self.animation_speed = 0.10
        self.frame_timer = 0
        self.hired = False
        self.animations = [pygame.transform.scale(pygame.image.load(f'anim/bully/bully{i}.png').convert_alpha(), (self.size, self.size)) for i in range(1, 6)]
        self.image = self.animations[0]  # Default frame

    def apply_effect(self, player, game_state_manager):
        if not self.controlled_by_enemy:
            player.hirable_bullies += 1
            game_state_manager.opponent_score_rate = max(0.00, game_state_manager.opponent_score_rate - 0.05)
            print(
                f"Bully added. Opponent score rate decreased by 0.05. Current opponent score rate: {game_state_manager.opponent_score_rate}")

    def update_animation(self):
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.animations)
            self.image = self.animations[self.frame_index]

    def draw(self, surface, camera_offset):
        if self.hired:
            return  # Do not draw if the bully is hired

        self.update_animation()

        # Blit the shadow
        stand_rect = pygame.Rect(self.position[0] - camera_offset[0], self.position[1] - camera_offset[1], self.size, self.size)
        shadow_offset = (0 + 5, self.size // 1.66)  # Adjust shadow position
        surface.blit(self.shadow, (stand_rect.topleft[0] + shadow_offset[0], stand_rect.topleft[1] + shadow_offset[1]))

        # Blit the animation frame
        surface.blit(self.image, stand_rect.topleft)

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
                # message_box.add_message("Player hired a bully")

                def update_message_box():
                    message_box.add_message("Player hired a bully")
                    self.hired = True
            else:
                self.pending_control = "enemy"
                self.controlled_by_enemy = True
                # self.color = (255, 0, 0)  # Change to red
                entity.has_bully = True
                self.hired = True

                def update_message_box():
                    message_box.add_message("The enemy hired a bully")

            dialogue_manager.start_dialogue(dialogue_texts, time.time(), self.position, update_message_box,
                                            source="player" if isinstance(entity, Player) else "enemy")

    def bully_steal_check(self, entity, message_box):
        if entity.has_bully:
            if random.randint(1, 100) == 1:  # 1 in 100 chance every frame
                stolen_amount = entity.score * 0.33
                entity.score -= stolen_amount
                print(f"The bully stole 33% of {entity}'s score! You lost ${stolen_amount:.2f}.")
                message_box.add_message(f"The bully stole ${stolen_amount:.2f} from {entity}!")
