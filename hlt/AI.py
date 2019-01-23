class NestedDict(dict):
    def __missing__(self, key):
        self[key] = NestedDict()
        return self[key]

    def __str__(self):
        string = "\nNestedDict::{"

        for key in self.keys():
            if type(self[key]) == NestedDict:
                string = string + "\n\n\t" + str(key) + ":"
                string = string + "\n\t" + str(self[key])
            else:
                string = string + "\n\t" + str(key) + ":"
                string = string + "\t\t" + str(self[key])
        return string + "}"


class Controller:
    """
    This object is used to store all the system variables that need to be modified across contexts.
    See init.py for more.
    """
    def __init__(self):
        self.ship_role = dict()
        self.ship_drop_loc = dict()
        self.ship_pos_hist = dict()
        self.ship_target_loc = dict()
        self.coms = list()
        self.unsafe_locs = dict()
        self.building_dropoff = False
        self.ships = list()
        self.game = None
        self.initial_halite = 0.0
        self.current_halite = 0.0
        self.spawning = False
        self.current_ship_locs = list()
        self.ships_at_max = 0
        self.never_dropoff = False
        self.num_eligible_spaces = 0
        self.end_game_triggered = False
        self.seed = 0
        self.target_df = None
        self.blacklisted_dropoff_spots = list()
        self.all_pos = list()
        self.turn_ratio = 0.0
        self.halite_ratio = 0.0
        self.progress_ratio = 0.0
        self.dyno = NestedDict()
        self.suicide = False
        self.ship_tar_df = None
        self.adj_posis = list()
        self.all_halite_amounts = list()
        self.is_target = dict()
        self.my_dropoffs = list()
        self.total_ships = 0
        self.mean_ships_per_player = 0

