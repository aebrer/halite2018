import hlt
from . import tactics, positionals, pathfinding, strategies, constants
import random
import logging


def get_role(ship):

    game_map = hlt.control.game.game_map

    old_role = hlt.control.ship_role[ship.id]

    # first check if we should build a dropoff
    if strategies.build_dropoff_check():
        # logging.info("dropoff {}".format(ship))
        # only want to make the closest ship the builder
        pot_do = game_map.normalize(tactics.get_pot_dropoff_loc())
        if pot_do is None:
            hlt.control.never_dropoff = True
        else:
            d = game_map.calculate_distance(game_map.normalize(ship.position), pot_do)
            best_ship = ship
            for other_ship in hlt.control.ships:
                d2 = game_map.calculate_distance(game_map.normalize(other_ship.position), pot_do)
                if d2 < d:
                    best_ship = other_ship
                    d = d2
            # logging.info("{},{}".format(ship, best_ship))
            hlt.control.building_dropoff = True
            hlt.control.ship_role[best_ship.id] = "builder"
            hlt.control.ship_target_loc[best_ship.id] = pot_do  # where to build

    if ship.id not in hlt.control.ship_drop_loc:
        hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)

    # then check all the ship logic
    if hlt.control.suicide:
        hlt.control.ship_role[ship.id] = "suicide"
    elif game_map.calculate_distance(ship.position, hlt.control.ship_drop_loc[ship.id]) >= (constants.MAX_TURNS - hlt.control.game.turn_number) - 10:
        if ship.halite_amount >= 100:
            hlt.control.ship_role[ship.id] = "suicide"
    elif hlt.control.ship_role[ship.id] == "suicide":
        pass
    elif hlt.control.ship_role[ship.id] == "new":
        # logging.info("new {}".format(ship))
        # collector by default
        hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)
        target = tactics.get_target(ship)
        hlt.control.ship_target_loc[ship.id] = target
        hlt.control.ship_role[ship.id] = "collector"
        # otherwise, drop off the goods
        if ship.halite_amount >= hlt.control.ship_harvest_threshold:
            hlt.control.ship_role[ship.id] = "harvester"
            hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)

    elif hlt.control.ship_role[ship.id] == "collector":
        if ship.halite_amount >= hlt.control.ship_harvest_threshold:
            # logging.info("becoming harvester")
            hlt.control.ship_role[ship.id] = "harvester"
            hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)
            hlt.control.ship_target_loc[ship.id] = hlt.control.ship_drop_loc[ship.id]
        elif hlt.control.ship_target_loc[ship.id] is None:
            target = tactics.get_target_weak(ship)
            hlt.control.ship_target_loc[ship.id] = target
        elif game_map[hlt.control.ship_target_loc[ship.id]].halite_amount <= hlt.control.minimum_halite_to_collect:
            # get a new target
            target = tactics.get_target_weak(ship)
            hlt.control.ship_target_loc[ship.id] = target

    elif hlt.control.ship_role[ship.id] == "harvester":
        # logging.info("harvester {}".format(ship))
        # if dropped off the goods
        if game_map.normalize(ship.position) == hlt.control.ship_drop_loc[ship.id]:
            # logging.info("getting new target (was a harvester)")
            hlt.control.ship_role[ship.id] = "collector"
            target = tactics.get_target(ship)
            hlt.control.ship_target_loc[ship.id] = target
    elif hlt.control.ship_role[ship.id] == "builder":
        pass
    else:
        hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)
        target = tactics.get_target(ship)
        hlt.control.ship_target_loc[ship.id] = target
        hlt.control.ship_role[ship.id] = "collector"

    # new_role = hlt.control.ship_role[ship.id]
    #
    # if old_role != new_role:
    #      logging.info("Ship {} has changed roles, from {} to {}.".format(ship.id, old_role, new_role))


def get_command(ship):

    game_map = hlt.control.game.game_map

    # if sitting on the dropoff point, get the fuck out of the way
    if ship.position in hlt.control.my_dropoffs:
        # logging.info(f"{hlt.control.ship_target_loc[ship.id]}")
        target = tactics.get_target(ship)
        hlt.control.ship_target_loc[ship.id] = target
        move = pathfinding.empty_navigate(ship, hlt.control.ship_target_loc[ship.id])
        hlt.control.coms.append(ship.move(move))
        return 1

    elif hlt.control.ship_role[ship.id] == "harvester":
        # logging.info(f"Ship {ship.id} is a harvester who is moving toward the dropoff.")
        move = pathfinding.empty_navigate(ship, hlt.control.ship_drop_loc[ship.id])
        hlt.control.coms.append(ship.move(move))
        return 1

    elif hlt.control.ship_role[ship.id] == "collector":
        # if at target location
        if game_map.normalize(ship.position) == game_map.normalize(hlt.control.ship_target_loc[ship.id]):
            # if lots of halite, wait and collect halite
            if game_map[hlt.control.ship_target_loc[ship.id]].halite_amount > hlt.control.minimum_halite_to_collect:
                if not (hlt.control.unsafe_locs[ship.position] or
                        game_map[ship.position].is_occupied):
                    if pathfinding.area_is_occupied_by_enemy(ship.position, ship=ship):
                        if ship.halite_amount >= 300:
                            move = pathfinding.energy_move(ship)
                            hlt.control.coms.append(ship.move(move))
                            return 1
                        else:
                            # logging.info(f"ship {ship.id} is waiting here, thinks it's safe")
                            hlt.control.coms.append(ship.move(positionals.Direction.Still))
                            hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
                            hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
                            return 1
                    else:
                        # logging.info(f"ship {ship.id} is waiting here, thinks it's safe")
                        hlt.control.coms.append(ship.move(positionals.Direction.Still))
                        hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
                        hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
                        return 1
                else:
                    move = pathfinding.energy_move(ship)
                    hlt.control.coms.append(ship.move(move))
                    return 1
            # if not a lot of halite, get a new target
            elif game_map[hlt.control.ship_target_loc[ship.id]].halite_amount <= hlt.control.minimum_halite_to_collect:
                # logging.info("getting a new target in the command place {}".format(ship))
                target = tactics.get_target_weak(ship)
                hlt.control.ship_target_loc[ship.id] = target
                move = pathfinding.empty_navigate(ship, target)
                hlt.control.coms.append(ship.move(move))
                return 1
            else:
                # logging.info(f"ship {ship.id} is energy moving due to being pushed here")
                move = pathfinding.energy_move(ship)
                hlt.control.coms.append(ship.move(move))
                return 1

        elif game_map[ship.position].halite_amount >= hlt.control.minimum_target:
            if not (hlt.control.unsafe_locs[ship.position] or
                    game_map[ship.position].is_occupied):
                if pathfinding.area_is_occupied_by_enemy(ship.position, ship=ship):
                    if ship.halite_amount >= 300:
                        move = pathfinding.energy_move(ship)
                        hlt.control.coms.append(ship.move(move))
                        return 1
                    else:
                        # logging.info(f"ship {ship.id} is waiting here, thinks it's safe")
                        hlt.control.coms.append(ship.move(positionals.Direction.Still))
                        hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
                        hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
                        return 1
                else:
                    # logging.info(f"ship {ship.id} is waiting here, thinks it's safe")
                    hlt.control.coms.append(ship.move(positionals.Direction.Still))
                    hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
                    hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
                    return 1
            else:
                move = pathfinding.energy_move(ship)
                hlt.control.coms.append(ship.move(move))
                return 1
        # not at collection target, so go there
        else:
            # logging.info(f"{hlt.control.ship_target_loc[ship.id]}")
            move = pathfinding.empty_navigate(ship, hlt.control.ship_target_loc[ship.id])
            hlt.control.coms.append(ship.move(move))
            return 1

    elif hlt.control.ship_role[ship.id] == "builder":
        # logging.info("Double checking dropoff:")
        # get a new target
        if tactics.dropoff_still_good_check(hlt.control.ship_target_loc[ship.id]):
            if game_map.normalize(ship.position) == hlt.control.ship_target_loc[ship.id]:
                # logging.info("Same place for some fucking reason")
                if hlt.control.game.me.halite_amount > constants.DROPOFF_COST + constants.SHIP_COST:
                    hlt.control.coms.append(ship.make_dropoff())
                    return 1
                elif not (hlt.control.unsafe_locs[game_map.normalize(ship.position)] or
                        game_map[ship.position].is_occupied):
                    hlt.control.coms.append(ship.move(positionals.Direction.Still))
                    hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
                    hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
                    return 1
                else:
                    move = pathfinding.energy_move(ship)
                    hlt.control.coms.append(ship.move(move))
                    return 1
            else:
                move = pathfinding.empty_navigate(ship, hlt.control.ship_target_loc[ship.id])
                hlt.control.coms.append(ship.move(move))
                return 1
        else:
            # you don't get to be a builder anymore
            hlt.control.ship_role[ship.id] = "collector"
            target = tactics.get_target_weak(ship)
            hlt.control.ship_target_loc[ship.id] = target
            move = pathfinding.empty_navigate(ship, hlt.control.ship_target_loc[ship.id])
            hlt.control.coms.append(ship.move(move))
            return 1

    elif hlt.control.ship_role[ship.id] == "suicide":
        hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)
        unnormal_pot_posis = ship.position.get_surrounding_cardinals()
        pot_posis = [hlt.control.game.game_map.normalize(pot_pos) for pot_pos in unnormal_pot_posis]
        if hlt.control.ship_drop_loc[ship.id] in pot_posis:
            direcs = game_map.get_unsafe_moves(ship.position, hlt.control.ship_drop_loc[ship.id])
            hlt.control.coms.append(ship.move(direcs[0]))
            return 1
        else:
            move = pathfinding.empty_navigate(ship, hlt.control.ship_drop_loc[ship.id])
            hlt.control.coms.append(ship.move(move))
            return 1
    else:
        move = pathfinding.energy_move(ship)
        hlt.control.coms.append(ship.move(move))
        return 1

    return 0
