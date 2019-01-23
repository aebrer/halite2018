import hlt
from . import constants, entity, pathfinding
import logging


def spawn_check():

    game_map = hlt.control.game.game_map
    me = hlt.control.game.me

    safe = True
    if game_map[me.shipyard.position].is_occupied:
        safe = False
    if hlt.control.unsafe_locs[me.shipyard.position]:
        safe = False
    if pathfinding.adj_area_occupation(me.shipyard.position) >= 8:
        safe = False
    if pathfinding.area_is_occupied_by_enemy(me.shipyard.position):
        safe = False

    if len(hlt.control.game.players.values()) == 2:
        ship_num = (hlt.control.total_ships - len(hlt.control.ships)) * 2 + len(hlt.control.ships)
    else:
        ship_num = hlt.control.total_ships - len(hlt.control.ships)

    if hlt.control.progress_ratio < hlt.control.ship_spawn_pr_limit:
        if (
            ship_num < hlt.control.ship_spawn_space_cutoff
        ):
            if me.halite_amount >= constants.SHIP_COST:
                if safe:
                    if not hlt.control.building_dropoff:
                        return True
                    elif me.halite_amount >= constants.SHIP_COST + constants.DROPOFF_COST:
                        return True



    return False


def spawn():
    hlt.control.coms.append(hlt.control.game.me.shipyard.spawn())
    hlt.control.unsafe_locs[hlt.control.game.me.shipyard.position] = True
    hlt.control.spawning = True
