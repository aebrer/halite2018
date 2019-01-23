import hlt
from . import positionals, constants, tactics
import random
import logging


def empty_navigate(ship, destination):
    """
    Returns a singular safe move towards the destination.

    :param ship: The ship to move.
    :param destination: Ending position
    :return: A direction.
    """
    # logging.info(f"Ship {ship.id} is looking for empty positions.")

    game_map = hlt.control.game.game_map

    if destination is None:
        # logging.info(f"DEBUG - Ship {ship} has no destination.")
        if hlt.control.ship_role[ship.id] == "harvester":
            hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)
            destination = hlt.control.ship_drop_loc[ship.id]
        else:
            destination = tactics.get_target_weak(ship)
            hlt.control.ship_target_loc[ship.id] = destination

    if destination is None:
        # logging.info(f"DEBUG - Ship {ship} STILL has no destination.")
        destination = tactics.get_target_weaker(ship)
        hlt.control.ship_target_loc[ship.id] = destination

    if destination is None:
        # logging.info(f"DEBUG - Ship {ship} is lost af.")
        hlt.control.ship_role[ship.id] = "harvester"
        return energy_move(ship)

    game_map = hlt.control.game.game_map

    if ship.id in hlt.control.ship_role:
        if hlt.control.ship_role[ship.id] == "harvester":
            if game_map[ship.position].halite_amount >= hlt.control.minimum_target:
                if ship.halite_amount < hlt.control.ship_harvest_threshold:
                    if not (hlt.control.unsafe_locs[game_map.normalize(ship.position)] or
                            area_is_occupied_by_enemy(game_map.normalize(ship.position), ship=ship) or
                            game_map[ship.position].is_occupied):
                        hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
                        hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
                        return positionals.Direction.Still

    # No need to normalize destination, since get_unsafe_moves
    # does that
    directions = game_map.get_unsafe_moves(ship.position, destination)
    best_pos = None
    best_dir = None

    # can't afford to move off this space if true
    can_move = ship.halite_amount >= game_map[ship.position].halite_amount / constants.MOVE_COST_RATIO

    if ship.id not in hlt.control.ship_drop_loc:
        hlt.control.ship_drop_loc[ship.id] = tactics.get_drop_loc(ship)

    if can_move:
        for direc in directions:
            pot_pos = ship.position.directional_offset(direc)
            pot_pos = game_map.normalize(pot_pos)
            if not (pot_pos == hlt.control.game.me.shipyard.position and hlt.control.spawning):
                # if dropoff is blocked by enemy ship, destroy it
                if not (hlt.control.unsafe_locs[pot_pos] or
                        area_is_occupied_by_enemy(pot_pos, ship=ship) or
                        game_map[pot_pos].is_occupied):
                    if best_pos is not None:
                        if game_map[pot_pos].halite_amount <= game_map[best_pos].halite_amount:
                            best_pos = pot_pos
                            best_dir = direc
                    else:
                        best_pos = pot_pos
                        best_dir = direc
                elif pot_pos in hlt.control.close_adj_posis and game_map[pot_pos].is_occupied:
                    if game_map[pot_pos].ship.owner != hlt.control.game.me.id:
                        best_pos = pot_pos
                        best_dir = direc

        if best_pos is not None:
            hlt.control.unsafe_locs[best_pos] = True
            # logging.info(f"{ship}, {best_pos}")
            # logging.info(f"{game_map[best_pos].is_occupied}")
            return best_dir

        else:
            return energy_move(ship)
    else:
        hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
        hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
        return positionals.Direction.Still


def safe_moves(ship):

    game_map = hlt.control.game.game_map
    # logging.info(f"Ship {ship.id} is looking for energy positions.")

    unnormal_posis = ship.position.get_surrounding_cardinals()
    posis = [hlt.control.game.game_map.normalize(pos) for pos in unnormal_posis]
    safe_posis = list()
    for pot_pos in posis:
        if not (pot_pos == hlt.control.game.me.shipyard.position and hlt.control.spawning):
            if not (hlt.control.unsafe_locs[pot_pos] or
                    area_is_occupied_by_enemy(pot_pos, ship=ship) or
                    game_map[pot_pos].is_occupied):
                    safe_posis.append(pot_pos)
    if not safe_posis:
        safe_posis.append(game_map.normalize(ship.position))
        hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)

    # logging.info("{}".format(safe_posis))

    # if game_map.normalize(ship.position) in safe_posis:
    #     return [game_map.normalize(ship.position)]
    # else:
    return safe_posis


def energy_move(ship):

    game_map = hlt.control.game.game_map
    me = hlt.control.game.me

    # logging.info(f"Ship {ship.id} is looking for energy positions.")
    # if you're here, you need to lose your target, because you might get stuck in a target loop
    if hlt.control.ship_role == "collector":
        hlt.control.ship_target_loc[ship.id] = None

    unnormal_posis = ship.position.get_surrounding_cardinals()
    posis = [hlt.control.game.game_map.normalize(pos) for pos in unnormal_posis]
    # can't afford to move off this space if true
    can_move = ship.halite_amount >= game_map[ship.position].halite_amount / constants.MOVE_COST_RATIO

    weighted_posis = list()
    if can_move:
        tx = ship.position.x
        ty = ship.position.y
        s = hlt.control.target_df[tx, ty] * 5.0
        if hlt.control.ship_role[ship.id] == "harvester":
            s *= -1
        # now scale to return to dropoffs
        # s = s * (1 - halite_ratio)
        # logging.info(f"Still: {s}")
        weighted_posis.append([ship.position, s])
        for pot_pos in posis:
            # logging.info(f"{row}")
            tx = pot_pos.x
            ty = pot_pos.y
            # if this potential target is not already a target for another ship
            # * (1.0/(hlt.control.self_target_score_penalty / hlt.control.target_scaling))
            s = hlt.control.target_df[tx, ty]
            if hlt.control.ship_role[ship.id] == "harvester":
                s *= -1
            # now scale to return to dropoffs
            # s = s * (halite_ratio + 0.001)

            # logging.info(f"{pot_pos}, {s}")
            weighted_posis.append([pot_pos, s])
    else:
        hlt.control.unsafe_locs[ship.position] = True
        hlt.control.game.game_map[ship.position].mark_unsafe(ship)
        return positionals.Direction.Still

    if hlt.control.ship_role[ship.id] == "harvester":
        weighted_posis.sort(key=lambda x: x[1], reverse=False)
    else:
        weighted_posis.sort(key=lambda x: x[1], reverse=True)
    # logging.info(f"{weighted_posis}")

    candidates = list()
    for i, pot_pos_pair in enumerate(weighted_posis):
        prob = hlt.control.temperature ** i
        pot_pos = pot_pos_pair[0]
        if not (pot_pos == hlt.control.game.me.shipyard.position and hlt.control.spawning):
            if not (hlt.control.unsafe_locs[pot_pos]
                    or game_map[pot_pos].is_occupied
                    or area_is_occupied_by_enemy(pot_pos, ship=ship)):
                if random.uniform(0, 1) <= prob:
                    candidates.append(pot_pos)

    # logging.info(f"Ship: {ship}, All candidates: {candidates}")

    if len(candidates) > 0:
        best_pos = random.choice(candidates)
        # logging.info(f"Best position: {best_pos}")
        if best_pos == ship.position:
            hlt.control.unsafe_locs[ship.position] = True
            hlt.control.game.game_map[game_map.normalize(best_pos)].mark_unsafe(ship)
            return positionals.Direction.Still
        else:
            best_dir = game_map.get_unsafe_moves(ship.position, best_pos)[0]
            # logging.info(f"{ship.position}, {best_dir}")
            hlt.control.unsafe_locs[game_map.normalize(best_pos)] = True
            hlt.control.game.game_map[game_map.normalize(best_pos)].mark_unsafe(ship)
            return best_dir
    else:
        safe_posis = safe_moves(ship)
        target_posi = game_map.normalize(random.choice(safe_posis))
        if target_posi != game_map.normalize(ship.position):
            best_dir = game_map.get_unsafe_moves(ship.position, target_posi)[0]
            hlt.control.unsafe_locs[game_map.normalize(
                positionals.Position.directional_offset(ship.position, best_dir))] = True
        else:
            best_dir = positionals.Direction.Still
            hlt.control.unsafe_locs[game_map.normalize(ship.position)] = True
            hlt.control.game.game_map[game_map.normalize(ship.position)].mark_unsafe(ship)
        return best_dir


def get_area(pos, r=3):
    pos = hlt.control.game.game_map.normalize(pos)
    area = list()
    for dx in range(-1 * r, r + 1):
        for dy in range(-1 * r, r + 1):
            area.append(hlt.control.game.game_map.normalize(positionals.Position(pos.x + dx, pos.y + dy)))
    return area


def get_area_value(pos, r=3):

    value = 0.0
    nearby = get_area(pos, r)

    for loc in nearby:
        cell = hlt.control.game.game_map[loc]
        value += cell.halite_amount

    return value, nearby


def area_is_occupied_by_enemy(pos, r=1, ship=None):
    game_map = hlt.control.game.game_map
    pos = hlt.control.game.game_map.normalize(pos)
    safe = True
    for dx in range(-1 * r, r + 1):
        for dy in range(-1 * r, r + 1):
            if abs(dx) + abs(dy) <= r:
                test_pos = game_map.normalize(positionals.Position(pos.x + dx, pos.y + dy))
                if test_pos in hlt.control.adj_posis:
                    pass
                elif game_map[test_pos].is_occupied:
                    if game_map[test_pos].ship.owner != hlt.control.game.me.id:
                        if ship is None:
                            safe = False
                        else:
                            if abs(dx) + abs(dy) == 0:  # never ACTUALLY crash into enemies intentionally
                                safe = False
                            else:
                                # logging.info(f"Ship {ship.id} sees an enemy. Owned by {game_map[test_pos].ship.owner}")
                                if game_map[test_pos].ship.halite_amount >= hlt.control.enemy_ship_target_min \
                                  and ship.halite_amount < hlt.control.maximum_kamakazi_limit:
                                    # logging.info(f"Ship {ship.id} is going to kamakazi.")
                                    # logging.info(f"{game_map[test_pos].ship.halite_amount}, {ship.halite_amount}")
                                    pass
                                else:
                                    safe = False
    return not safe


def adj_area_occupation(pos):
    game_map = hlt.control.game.game_map
    pos = hlt.control.game.game_map.normalize(pos)
    occupation = 0
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if abs(dx) + abs(dy) <= 2:
                test_pos = game_map.normalize(positionals.Position(pos.x + dx, pos.y + dy))
                if hlt.control.game.game_map[test_pos].is_occupied or hlt.control.unsafe_locs[test_pos]:
                    occupation += 1
    return occupation
