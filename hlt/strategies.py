import hlt
from . import constants, config
import logging
from numpy import percentile, tanh


def build_dropoff_check():
    good = False
    if not (hlt.control.building_dropoff or hlt.control.never_dropoff):
        if hlt.control.progress_ratio < hlt.control.dropoff_spawn_pr_limit:
            # don't want to spend too long having a ship waiting for the right amount of halite to build
            if hlt.control.game.me.halite_amount > ((constants.DROPOFF_COST * 1.0) + constants.SHIP_COST):
                if len(hlt.control.game.me.get_dropoffs()) < hlt.control.max_dropoffs_allowed:
                    if hlt.control.ships_at_max >= hlt.control.dropoff_threshold:
                        good = True
    return good


def scale_constants():

    def s(a, z):
        a = float(a)
        z = float(z)
        if a > z:
            v = a - (a - z) * hlt.control.progress_ratio
        else:
            v = (z - a) * hlt.control.progress_ratio + a
        return v

    def fs(a, z):
        a = float(a)
        z = float(z)
        if a > z:
            v = a - (a - z) * (hlt.control.progress_ratio ** (1/2))
        else:
            v = (z - a) * (hlt.control.progress_ratio ** (1/2)) + a
        return v

    def vfs(a, z):
        a = float(a)
        z = float(z)
        if a > z:
            v = a - (a - z) * (hlt.control.progress_ratio ** 0.3)
        else:
            v = (z - a) * (hlt.control.progress_ratio ** 0.3) + a
        return v

    def ss(a, z):
        a = float(a)
        z = float(z)
        pr = hlt.control.progress_ratio
        q = (0.5 + (0.5 * tanh((pr * 5) - 2.5))) * (pr / (pr + 0.000001))
        if a > z:
            v = a - (a - z) * q
        else:
            v = (z - a) * q + a
        return v

    # dynamic constants
    d = hlt.control.dyno
    hlt.control.minimum_halite_percentile = ss(
        d["minimum_halite_percentile"]["a"],
        d["minimum_halite_percentile"]["z"]
    )
    # logging.info(f"DEBUG - minimum_halite_percentile: {hlt.control.minimum_halite_percentile}")

    hlt.control.minimum_target_percentile = ss(
        d["minimum_target_percentile"]["a"],
        d["minimum_target_percentile"]["z"]
    )
    # logging.info(f"DEBUG - minimum_target_percentile: {hlt.control.minimum_target_percentile}")

    hlt.control.dropoff_threshold = round(s(d["dropoff_threshold"]["a"], d["dropoff_threshold"]["z"]))
    # logging.info(f"DEBUG - dropoff_threshold: {hlt.control.dropoff_threshold}")

    hlt.control.spaces_per_all_ships = ss(d["spaces_per_all_ships"]["a"], d["spaces_per_all_ships"]["z"])
    # logging.info(f"DEBUG - spaces_per_ship: {hlt.control.spaces_per_ship}")

    hlt.control.ship_spawn_space_cutoff = min(
        hlt.control.ship_spawn_space_cutoff, (hlt.control.num_eligible_spaces / float(hlt.control.spaces_per_all_ships))
    )

    hlt.control.maximum_kamakazi_limit = round(s(d["maximum_kamakazi_limit"]["a"], d["maximum_kamakazi_limit"]["z"]))
    # logging.info(f"DEBUG - maximum_kamakazi_limit: {hlt.control.maximum_kamakazi_limit}")

    hlt.control.enemy_ship_target_min = round(s(d["enemy_ship_target_min"]["a"], d["enemy_ship_target_min"]["z"]))
    # logging.info(f"DEBUG - enemy_ship_target_min: {hlt.control.enemy_ship_target_min}")

    hlt.control.ship_harvest_threshold = round(fs(d["ship_harvest_threshold"]["a"], d["ship_harvest_threshold"]["z"]))
    # logging.info(f"DEBUG - ship_harvest_threshold: {hlt.control.ship_harvest_threshold}")

    hlt.control.target_scaling = fs(d["target_scaling"]["a"], d["target_scaling"]["z"])
    # logging.info(f"DEBUG - target_scaling: {hlt.control.target_scaling}")

    hlt.control.kernel_radius = round(vfs(d["kernel_radius"]["a"], d["kernel_radius"]["z"]))
    # logging.info(f"DEBUG - kernel_radius: {hlt.control.kernel_radius}")

    hlt.control.temperature = s(d["temperature"]["a"], d["temperature"]["z"])
    # logging.info(f"DEBUG - temperature: {hlt.control.temperature}")

    hlt.control.dropoff_distance_factor = vfs(d["dropoff_distance_factor"]["a"], d["dropoff_distance_factor"]["z"])
    # logging.info(f"DEBUG - dropoff_distance_factor: {hlt.control.dropoff_distance_factor}")

    hlt.control.target_percentile_cutoff = fs(d["target_percentile_cutoff"]["a"], d["target_percentile_cutoff"]["z"])
    # logging.info(f"DEBUG - target_percentile_cutoff: {hlt.control.target_percentile_cutoff}")

    hlt.control.self_distance_factor = vfs(d["self_distance_factor"]["a"], d["self_distance_factor"]["z"])
    # logging.info(f"DEBUG - self_distance_factor: {hlt.control.self_distance_factor}")

    hlt.control.weak_ship_visibility = round(fs(d["weak_ship_visibility"]["a"], d["weak_ship_visibility"]["z"]))
    # logging.info(f"DEBUG - weak_ship_visibility: {hlt.control.weak_ship_visibility}")

    hlt.control.weaker_ship_visibility = round(fs(d["weaker_ship_visibility"]["a"], d["weaker_ship_visibility"]["z"]))
    # logging.info(f"DEBUG - weak_ship_visibility: {hlt.control.weak_ship_visibility}")

    hlt.control.minimum_halite_to_collect = percentile(
        hlt.control.all_halite_amounts, hlt.control.minimum_halite_percentile
    ) + 1
    logging.info(f"{hlt.control.game.turn_number}\tcollect_percentile\t{hlt.control.minimum_halite_percentile}")
    logging.info(f"{hlt.control.game.turn_number}\tcollect_minimum\t{hlt.control.minimum_halite_to_collect}")

    hlt.control.minimum_target = percentile(
        hlt.control.all_halite_amounts, hlt.control.minimum_target_percentile
    ) + 1
    logging.info(f"{hlt.control.game.turn_number}\ttarget_percentile\t{hlt.control.minimum_target_percentile}")
    logging.info(f"{hlt.control.game.turn_number}\ttarget_minimum\t{hlt.control.minimum_target}")

    return 1

