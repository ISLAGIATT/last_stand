from stand import HirableBully

class GameStateManager:
    def __init__(self):
        self.sabotage_in_progress = False
        self.sabotage_start_time = None
        self.got_pee = False
        self.sabotage_stand_id = None
        self.opponent_score_rate = 0.10  # Initial opponent score rate
        self.fight_fail_sabotage = False
        self.player_movement_delay = 0
        self.enemy_movement_delay = 0  # Added variable to track enemy movement delay
        self.encounter_triggered_by_player = False  # Flag to track if the encounter was triggered by the player
        self.encounter_triggered_by_enemy = False  # Added flag to track if the encounter was triggered by the enemy

    def start_sabotage(self, stand):
        self.sabotage_in_progress = True
        self.sabotage_stand_id = stand.id

    def complete_sabotage(self, player_cup):
        self.sabotage_in_progress = False
        self.sabotage_start_time = None
        self.got_pee = False
        self.sabotage_stand_id = None
        player_cup.reset()

    def update_sabotage_start_time(self, time):
        self.sabotage_start_time = time

    def apply_bully_effects(self, player, opp_stands, message_box):
        for stand in opp_stands:
            if isinstance(stand, HirableBully) and stand.controlled_by_player:
                stand.bully_steal_check(player, message_box)
