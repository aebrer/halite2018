import hlt
from . import constants
import logging
import random


def load_constants():

    # fixed constants
    hlt.control.max_dropoffs_allowed = 4
    hlt.control.max_enemies_allowed_to_build = 4  # how many enemies are allowed in an area before it can't be a dropoff
    hlt.control.nearest_dropoff_dist_min = 15  # if there is a dropoff this close or closer, don't build here
    hlt.control.ship_spawn_pr_limit = 0.8
    hlt.control.dropoff_spawn_pr_limit = 0.75


    if hlt.control.game.game_map.height > 40:
        # dynamic constants - load first for game initialization
        hlt.control.dyno["minimum_halite_percentile"]["a"] = 40  # don't bother collecting from a tile with less than this
        hlt.control.dyno["minimum_halite_percentile"]["z"] = 1  # don't bother collecting from a tile with less than this
        hlt.control.dyno["minimum_target_percentile"]["a"] = 50  # don't bother collecting from a tile with less than this
        hlt.control.dyno["minimum_target_percentile"]["z"] = 17  # don't bother collecting from a tile with less than this
        hlt.control.dyno["dropoff_threshold"]["a"] = 5  # build a dropoff if this many ships are full at once
        hlt.control.dyno["dropoff_threshold"]["z"] = 20  # build a dropoff if this many ships are full at once
        hlt.control.dyno["spaces_per_all_ships"]["a"] = 6.0  # each ship is expected to lay claim to this many spaces
        hlt.control.dyno["spaces_per_all_ships"]["z"] = 32  # each ship is expected to lay claim to this many spaces
        hlt.control.dyno["maximum_kamakazi_limit"]["a"] = 10  # ship is nearly empty
        hlt.control.dyno["maximum_kamakazi_limit"]["z"] = 80  # ship is nearly empty
        hlt.control.dyno["enemy_ship_target_min"]["a"] = constants.MAX_HALITE * 1.0  # enemy has a lot of halite
        hlt.control.dyno["enemy_ship_target_min"]["z"] = constants.MAX_HALITE * 0.9  # enemy has a lot of halite
        hlt.control.dyno["ship_harvest_threshold"]["a"] = constants.MAX_HALITE * 0.86  # when to go to a dropoff with cargo
        hlt.control.dyno["ship_harvest_threshold"]["z"] = constants.MAX_HALITE * 0.93  # when to go to a dropoff with cargo
        hlt.control.dyno["target_scaling"]["a"] = 0.999  # scaling factor for number of steps away from target loc
        hlt.control.dyno["target_scaling"]["z"] = 0.95  # scaling factor for number of steps away from target loc
        hlt.control.dyno["kernel_radius"]["a"] = round(hlt.control.game.game_map.height / 16)
        hlt.control.dyno["kernel_radius"]["z"] = round(hlt.control.game.game_map.height / 4)
        hlt.control.dyno["temperature"]["a"] = 0.05
        hlt.control.dyno["temperature"]["z"] = 0.15
        hlt.control.dyno["dropoff_distance_factor"]["a"] = 0.95
        hlt.control.dyno["dropoff_distance_factor"]["z"] = 0.999
        hlt.control.dyno["target_percentile_cutoff"]["a"] = 0.6
        hlt.control.dyno["target_percentile_cutoff"]["z"] = 0.4
        hlt.control.dyno["self_distance_factor"]["a"] = 0.75
        hlt.control.dyno["self_distance_factor"]["z"] = 0.931
        hlt.control.dyno["weak_ship_visibility"]["a"] = 15
        hlt.control.dyno["weak_ship_visibility"]["z"] = 8
        hlt.control.dyno["weaker_ship_visibility"]["a"] = 3
        hlt.control.dyno["weaker_ship_visibility"]["z"] = 6
    else:
        hlt.control.dyno["minimum_halite_percentile"]["a"] = 40  # don't bother collecting from a tile with less than this
        hlt.control.dyno["minimum_halite_percentile"]["z"] = 1  # don't bother collecting from a tile with less than this
        hlt.control.dyno["minimum_target_percentile"]["a"] = 20  # don't bother collecting from a tile with less than this
        hlt.control.dyno["minimum_target_percentile"]["z"] = 15  # don't bother collecting from a tile with less than this
        hlt.control.dyno["dropoff_threshold"]["a"] = 5  # build a dropoff if this many ships are full at once
        hlt.control.dyno["dropoff_threshold"]["z"] = 10  # build a dropoff if this many ships are full at once
        hlt.control.dyno["spaces_per_all_ships"]["a"] = 5.0  # each ship is expected to lay claim to this many spaces
        hlt.control.dyno["spaces_per_all_ships"]["z"] = 32  # each ship is expected to lay claim to this many spaces
        hlt.control.dyno["maximum_kamakazi_limit"]["a"] = 10  # ship is nearly empty
        hlt.control.dyno["maximum_kamakazi_limit"]["z"] = 80  # ship is nearly empty
        hlt.control.dyno["enemy_ship_target_min"]["a"] = constants.MAX_HALITE * 1.0  # enemy has a lot of halite
        hlt.control.dyno["enemy_ship_target_min"]["z"] = constants.MAX_HALITE * 0.9  # enemy has a lot of halite
        hlt.control.dyno["ship_harvest_threshold"]["a"] = constants.MAX_HALITE * 0.86  # when to go to a dropoff with cargo
        hlt.control.dyno["ship_harvest_threshold"]["z"] = constants.MAX_HALITE * 0.93  # when to go to a dropoff with cargo
        hlt.control.dyno["target_scaling"]["a"] = 0.999  # scaling factor for number of steps away from target loc
        hlt.control.dyno["target_scaling"]["z"] = 0.95  # scaling factor for number of steps away from target loc
        hlt.control.dyno["kernel_radius"]["a"] = round(hlt.control.game.game_map.height / 32)
        hlt.control.dyno["kernel_radius"]["z"] = round(hlt.control.game.game_map.height / 8)
        hlt.control.dyno["temperature"]["a"] = 0.05
        hlt.control.dyno["temperature"]["z"] = 0.15
        hlt.control.dyno["dropoff_distance_factor"]["a"] = 0.95
        hlt.control.dyno["dropoff_distance_factor"]["z"] = 0.999
        hlt.control.dyno["target_percentile_cutoff"]["a"] = 0.6
        hlt.control.dyno["target_percentile_cutoff"]["z"] = 0.4
        hlt.control.dyno["self_distance_factor"]["a"] = 0.75
        hlt.control.dyno["self_distance_factor"]["z"] = 0.931
        hlt.control.dyno["weak_ship_visibility"]["a"] = 15
        hlt.control.dyno["weak_ship_visibility"]["z"] = 8
        hlt.control.dyno["weaker_ship_visibility"]["a"] = 2
        hlt.control.dyno["weaker_ship_visibility"]["z"] = 3

    d = hlt.control.dyno
    hlt.control.minimum_halite_percentile = hlt.control.dyno["minimum_halite_percentile"]["a"]
    hlt.control.minimum_target_percentile = hlt.control.dyno["minimum_target_percentile"]["a"]  # don't bother collecting from a tile with less than this
    hlt.control.minimum_target = hlt.control.dyno["minimum_target_percentile"]["a"]  # don't bother collecting from a tile with less than this
    hlt.control.minimum_halite_to_collect = d["minimum_halite_percentile"]["a"]
    hlt.control.dropoff_threshold = d["dropoff_threshold"]["a"]
    hlt.control.spaces_per_ship = d["spaces_per_ship"]["a"]
    hlt.control.spaces_per_all_ships = d["spaces_per_all_ships"]["a"]
    hlt.control.maximum_kamakazi_limit = d["maximum_kamakazi_limit"]["a"]
    hlt.control.enemy_ship_target_min = d["enemy_ship_target_min"]["a"]
    hlt.control.ship_harvest_threshold = d["ship_harvest_threshold"]["a"]
    hlt.control.target_scaling = d["target_scaling"]["a"]
    hlt.control.enemy_target_score_penalty = d["enemy_target_score_penalty"]["a"]
    hlt.control.self_target_score_penalty = d["self_target_score_penalty"]["a"]
    hlt.control.kernel_radius = d["kernel_radius"]["a"]
    hlt.control.temperature = d["temperature"]["a"]
    hlt.control.dropoff_distance_factor = d["dropoff_distance_factor"]["a"]
    hlt.control.target_percentile_cutoff = d["target_percentile_cutoff"]["a"]
    hlt.control.self_distance_factor = d["self_distance_factor"]["a"]
    hlt.control.weak_ship_visibility = d["weak_ship_visibility"]["a"]
    hlt.control.weaker_ship_visibility = d["weaker_ship_visibility"]["a"]
    hlt.control.ship_spawn_space_cutoff = 100000000000.0

    return 1


def set_progress_details():

    """
    Get the details about the current progress of the game.
    :return:
    """

    # time based progress
    lt = constants.MAX_TURNS
    ct = hlt.control.game.turn_number
    tr = float(ct) / float(lt)
    hlt.control.turn_ratio = tr

    # halite mining based progress
    ih = hlt.control.initial_halite
    ch = hlt.control.current_halite
    hr = float(ch) / float(ih)
    hlt.control.halite_ratio = hr
    ihr = 1.0 - hr

    # combined stats
    # pr = (tr * ihr) ** 0.5  # geometric mean
    pr = max(tr, ihr)
    hlt.control.progress_ratio = pr

    logging.info(f"{hlt.control.game.turn_number}\tturn_ratio\t{tr}")
    logging.info(f"{hlt.control.game.turn_number}\tprogress_ratio\t{pr}")
    logging.info(f"{hlt.control.game.turn_number}\thalite_ratio\t{hr}")



