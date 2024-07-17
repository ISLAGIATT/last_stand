import pygame
import random
import time

from cop import Cop
from cup import CountdownCup
from customer import Customer
from dialogue_manager import DialogueManager
from enemy import Enemy
from game_state_manager import GameStateManager
from map_object import MapObject
from message_box import MessageBox
from paths import Path
from player import Player
from score_manager import ScoreManager
from screens import TitleScreen, GameOverScreen
from stand import Stand, CookieGirl, HirableBully

pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1000, 800
MAP_WIDTH, MAP_HEIGHT = 2500, 2500
FPS = 60

# Colors
BRIGHT_GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF)
pygame.display.set_caption('The Last Stand')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
stands_font = pygame.font.Font(None, 24)

# Title Screen
title_screen = TitleScreen(screen, font, WIDTH, HEIGHT)
title_screen.show()  # Display the title screen

# Fade out title screen music
title_screen.stop_music()

# Load background image and convert
background_image = pygame.image.load('images/grass_v2.png').convert()
tile_width = background_image.get_width()
tile_height = background_image.get_height()

# FPS counter
pygame.font.init()
fps_font = pygame.font.Font(None, 36)

# Timer variables
start_time = pygame.time.get_ticks()
time_limit = 1.5 * 60 * 1000  # 2 minutes in milliseconds

# Instantiate game objects
game_state_manager = GameStateManager()
dialogue_manager = DialogueManager(font, wrap_width=200)
message_box = MessageBox(550, 175, WIDTH, HEIGHT, font)
enemy = Enemy(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT), 25, 4)
player = Player(WIDTH // 2, HEIGHT // 2, 50, 5, (255, 0, 0), MAP_WIDTH, MAP_HEIGHT)
home_stand = Stand(200, 300, 100, (0, 255, 0), 'images/home_base.png')
second_home_stand = Stand(2000, 1500, 100, (0, 255, 0), 'images/home_base.png')
player_cup = CountdownCup(home_stand.position[0] - 50, home_stand.position[1], 30, 100, 10)
score_manager = ScoreManager(player, enemy, font, stands_font, time_limit, player_cup)
cop = Cop(MAP_WIDTH, MAP_HEIGHT, size=60, speed=3)

# Generate stands
opp_stands = Stand.generate_random_stands(14, 2, 2, MAP_WIDTH, MAP_HEIGHT)

# Filter stands for path generation
opp_stand_positions = [stand for stand in opp_stands if not isinstance(stand, (CookieGirl, HirableBully))]

# Map objects
map_objects = [
    MapObject(1500, 1500, 30, (34, 139, 34)),
    MapObject(100, 1600, 40, (139, 69, 19))
]

camera_offset = [0, 0]

# Initialize home stand checks
last_update_time = pygame.time.get_ticks()
last_speed_increase_time = pygame.time.get_ticks()
home_encounter_triggered = False
time_at_home_stand = None
player_in_contact_with_home_stand = False
time_at_enemy_home_stand = None
# enemy_in_contact_with_home_stand = False

# Generate paths
paths = Path.generate_paths(opp_stand_positions)

# Generate customers
customers = []
for stand in opp_stand_positions:
    for _ in range(50 // len(opp_stand_positions)):  # Distribute 50 customers among stands
        x = random.randint(stand.position[0] - 200, stand.position[0] + 200)
        y = random.randint(stand.position[1] - 200, stand.position[1] + 200)
        customers.append(Customer(x, y, 50, 1, stand, opp_stand_positions))

# Set initial target for enemy
enemy.set_target(opp_stands + [cg for cg in opp_stands if isinstance(cg, CookieGirl)] + [hb for hb in opp_stands if isinstance(hb, HirableBully)])

def handle_home_collision():
    global time_at_home_stand, player_in_contact_with_home_stand
    if game_state_manager.sabotage_in_progress:
        if player_rect.colliderect(home_stand_rect):
            home_stand.set_home_stand_image(True)
            player_in_contact_with_home_stand = True
            if time_at_home_stand is None:
                time_at_home_stand = time.time()
                player_cup.start()
            elapsed_time = time.time() - time_at_home_stand
            if elapsed_time >= 10:
                message_box.add_message("You've got the foul-smelling lemonade. Go sabotage the enemy stand!")
                time_at_home_stand = None
                game_state_manager.got_pee = True
                player_in_contact_with_home_stand = False
        elif player_rect.colliderect(second_home_stand_rect):  # Check collision with second home stand
            second_home_stand.set_home_stand_image(True)
            player_in_contact_with_home_stand = True
            if time_at_home_stand is None:
                time_at_home_stand = time.time()
                player_cup.start()
            elapsed_time = time.time() - time_at_home_stand
            if elapsed_time >= 10:
                message_box.add_message("You've got the foul-smelling lemonade. Go sabotage the enemy stand!")
                time_at_home_stand = None
                game_state_manager.got_pee = True
                player_in_contact_with_home_stand = False
        else:
            home_stand.set_home_stand_image(False)
            second_home_stand.set_home_stand_image(False)  # Reset image for second home stand
            if not player_cup.full:
                time_at_home_stand = None
                player_cup.reset()
                player_in_contact_with_home_stand = False


def get_click_coordinates():
    mouse_pos = pygame.mouse.get_pos()
    world_pos = (mouse_pos[0] + camera_offset[0], mouse_pos[1] + camera_offset[1])
    print(f"Clicked at world coordinates: {world_pos}")


def draw_border(surface, camera_offset):
    points = [
        (0 - camera_offset[0], 0 - camera_offset[1]),
        (MAP_WIDTH - camera_offset[0], 0 - camera_offset[1]),
        (MAP_WIDTH - camera_offset[0], MAP_HEIGHT - camera_offset[1]),
        (0 - camera_offset[0], MAP_HEIGHT - camera_offset[1]),
        (0 - camera_offset[0], 0 - camera_offset[1])
    ]
    pygame.draw.lines(surface, BRIGHT_GREEN, False, points, 5)


def draw_background(surface, camera_offset, tile_image):
    tile_width = tile_image.get_width()
    tile_height = tile_image.get_height()
    start_x = max(int((camera_offset[0] - 1000) // tile_width), 0)
    end_x = min(int((camera_offset[0] + WIDTH + 1000) // tile_width) + 1, int((MAP_WIDTH + 2000) // tile_width))
    start_y = max(int((camera_offset[1] - 1000) // tile_height), 0)
    end_y = min(int((camera_offset[1] + HEIGHT + 1000) // tile_height) + 1, int((MAP_HEIGHT + 2000) // tile_height))
    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            surface.blit(tile_image, (x * tile_width - camera_offset[0], y * tile_height - camera_offset[1]))


def check_collision_with_customers(player_rect, customers, camera_offset):
    collision_detected = False
    for customer in customers:
        customer_rect = pygame.Rect(customer.position[0] - camera_offset[0], customer.position[1] - camera_offset[1], customer.size, customer.size)
        if player_rect.colliderect(customer_rect):
            collision_detected = True
    return collision_detected


# Display title screen
title_screen = TitleScreen(screen, font, WIDTH, HEIGHT)
title_screen.draw()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            get_click_coordinates()
        elif event.type == pygame.KEYDOWN and dialogue_manager.dialogue_active:
            if event.key == pygame.K_SPACE:
                dialogue_manager.dialogue_index += 1
                if dialogue_manager.dialogue_index >= len(dialogue_manager.dialogue_texts):
                    dialogue_manager.dialogue_active = False

    # Input
    keys = pygame.key.get_pressed()

    # Screen
    screen.fill((0, 0, 0))
    draw_background(screen, camera_offset, background_image)
    camera_offset = (player.position[0] - WIDTH // 2 + player.size // 2, player.position[1] - HEIGHT // 2 + player.size // 2)

    # Temp border
    draw_border(screen, camera_offset)

    # Player
    player_rect = pygame.Rect(player.position[0], player.position[1], player.size, player.size)
    # Enemy
    enemy_rect = enemy.draw(screen, camera_offset)

    # Handle player movement delays
    if time.time() > game_state_manager.player_movement_delay:
        if game_state_manager.encounter_triggered_by_player:
            game_state_manager.encounter_triggered_by_player = False  # Reset the flag
        player.move(keys)
    else:
        player.set_idle()
        player.update_animation()

    # Handle enemy movement
    if time.time() > game_state_manager.enemy_movement_delay:
        if game_state_manager.encounter_triggered_by_enemy:
            game_state_manager.encounter_triggered_by_enemy = False  # Reset the flag
        enemy.move()

    # Enemy pathfinding
    if not enemy.target:
        enemy.set_target(
            opp_stands + [cg for cg in opp_stands if isinstance(cg, CookieGirl)] + [hb for hb in opp_stands if isinstance(hb, HirableBully)])
    enemy.handle_collision(player_rect, camera_offset, player, dialogue_manager, game_state_manager, opp_stands,
                           [cg for cg in opp_stands if isinstance(cg, CookieGirl)],
                           [hb for hb in opp_stands if isinstance(hb, HirableBully)], screen, message_box)
    enemy.update_score(opp_stands)

    # Ensure only the target stand is highlighted for sabotage
    for stand in opp_stands:
        if stand.id == game_state_manager.sabotage_stand_id:
            stand.is_sabotage_target = True
        else:
            stand.is_sabotage_target = False

    # Scoring
    current_time = pygame.time.get_ticks()
    score_manager.update_scores(current_time, opp_stands, message_box)
    score_manager.calculate_score_rates(opp_stands)

    # Update the count of stands controlled by player and enemy, excluding Cookie Girls and Bullies
    player_stands_controlled = sum(
        1 for stand in opp_stands if stand.controlled_by_player and not isinstance(stand, (CookieGirl, HirableBully)))
    enemy_stands_controlled = sum(
        1 for stand in opp_stands if stand.controlled_by_enemy and not isinstance(stand, (CookieGirl, HirableBully)))

    # Draw paths
    for path in paths:
        path.draw(screen, camera_offset)
    if Path.is_player_on_path(player.position, paths, player.size):
        player.speed = 5.5  # Increase speed by 10%
    else:
        player.speed = 5

    player_rect = player.draw(screen, camera_offset)

    # Draw customers
    for customer in customers:
        customer.move()
        customer.draw(screen, camera_offset)

    # Draw stands
    home_stand_rect = home_stand.draw(screen, camera_offset)
    second_home_stand_rect = second_home_stand.draw(screen, camera_offset)
    for opp_stand in opp_stands:
        opp_stand.update_running_persons(MAP_WIDTH, MAP_HEIGHT)
        opp_stand.draw_running_persons(screen, camera_offset)
        opp_stand_rect = opp_stand.draw(screen, camera_offset)
        opp_stand.handle_collision(player_rect, camera_offset, player, dialogue_manager,
                                   game_state_manager, player_cup, message_box)

    # Draw obstacles (rocks)
    for obj in map_objects:
        obj.draw(screen, camera_offset)

    # Customer collision detection
    if check_collision_with_customers(player_rect, customers, camera_offset):
        player.speed = player.speed / 2  # Reduce speed by half if colliding with a customer
    else:
        player.speed = player.speed  # Restore original speed

    # Home Stand Collision handling
    handle_home_collision()

    # Pee logic
    if not game_state_manager.sabotage_in_progress and game_state_manager.got_pee:
        game_state_manager.complete_sabotage(player_cup)
    if game_state_manager.sabotage_in_progress or player_cup.full:
        player_cup.draw(screen)
    player_cup.update_position(home_stand.position[0] - 50, home_stand.position[1])

    # Cop Logic
    elapsed_time = current_time - start_time
    remaining_time = max(0, time_limit - elapsed_time)
    if remaining_time == 0 and not cop.active:
        cop.activate()
        last_speed_increase_time = current_time
        message_box.add_message("Time's up, here come the cops!", blink=True)
        print("Cop activated")
    if cop.active and current_time - last_speed_increase_time >= 10 * 1000:
        cop.speed += 1
        last_speed_increase_time = current_time
        print(f"Cop speed increased to {cop.speed}")
    if cop.active:
        cop.move(player.position)
        cop.draw(screen, camera_offset)
        if cop.check_collision(player.position, player.size):
            print("Game Over")
            running = False
            game_over_screen = GameOverScreen(screen, font, score_manager.player_score, score_manager.opponent_score, WIDTH, HEIGHT)
            game_over_screen.draw()

    # Draw dialogue
    dialogue_manager.draw_dialogue(screen, camera_offset, player.position, npc_text_color=(255, 255, 255), npc_visible_duration=2)

    # Draw stats
    score_manager.draw_scores(screen, WIDTH, HEIGHT, opp_stands)

    # Message box on top
    message_box.draw(screen)

    # FPS for debug
    fps = clock.get_fps()
    fps_text = fps_font.render(f'FPS: {int(fps)}', True, (255, 255, 255))
    screen.blit(fps_text, (10, HEIGHT - 40))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()