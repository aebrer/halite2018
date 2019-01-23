import hlt
from . import positionals, pathfinding, constants
import logging, time


def calculate_s(pos):

    game_map = hlt.control.game.game_map
    me = hlt.control.game.me

    s = 0.0  # initial score

    h = float(game_map[pos].halite_amount)  # halite on this position
    hlt.control.current_halite += h
    s += h

    d = float(game_map.calculate_distance(pos, me.shipyard.position))  # distance to closest dropoff
    for do in hlt.control.my_dropoffs:
        do_d = float(game_map.calculate_distance(pos, do))
        # if this dropoff is closer than the previous one, go there instead
        if do_d < d:
            d = do_d

    s = s * (hlt.control.dropoff_distance_factor ** d)

    return s


def get_target_score(row):

    # logging.info(f"{row.name}")

    x = row.name[0]
    y = row.name[1]

    game_map = hlt.control.game.game_map
    pos = game_map.normalize(positionals.Position(x, y))

    return calculate_s(pos)


def get_target(ship):
    """
    Used to determine a new target for a ship, to collect from.
    :param hlt.control:
    :param ship:
    :return:
    """

    tg_st = time.time()
    best_score = 0.0
    target = None

    scaled = list()
    for (i, score) in hlt.control.ship_tar_df.iteritems():
        # logging.info(f"{row}")
        tx = i[0]
        ty = i[1]
        tpos = positionals.Position(tx, ty)
        # if this potential target is not already a target for another ship
        d = hlt.control.game.game_map.calculate_distance(ship.position, tpos)
        new_score = hlt.control.self_distance_factor ** d
        if not hlt.control.game.game_map[tpos].has_structure:
            if new_score > best_score:
                if hlt.control.game.game_map[tpos].halite_amount > hlt.control.minimum_target:
                    scaled.append([tx, ty, new_score])
                    best_score = new_score

    for x, y, score in reversed(scaled):
        tpos = positionals.Position(x, y)
        if not hlt.control.is_target[tpos]:
            # logging.info(f"Got target for ship {ship} in {time.time() - tg_st} seconds.")
            target = tpos
            return target

    return target


def get_target_weak(ship):
    """
    Used to determine a new target for a ship, to collect from, nearby.
    :param hlt.control:
    :param ship:
    :return:
    """

    game_map = hlt.control.game.game_map
    pos = ship.position
    target_pos = None
    # best_s = 0.0
    pot_tars = list()

    for dx in range(-1 * hlt.control.weak_ship_visibility, hlt.control.weak_ship_visibility + 1):
        for dy in range(-1 * hlt.control.weak_ship_visibility, hlt.control.weak_ship_visibility + 1):
            new_pos = game_map.normalize(positionals.Position(pos.x + dx, pos.y + dy))
            # logging.info(f"{game_map.width},{game_map.height},{positionals.Position(pos.x + dx, pos.y + dy)}, {new_pos}")
            if game_map[new_pos].halite_amount > hlt.control.minimum_target:
                if not hlt.control.game.game_map[new_pos].has_structure:
                    # try:
                    # logging.info(f"{new_pos.x},{new_pos.y}, {hlt.control.target_df[0,0]}")
                    s = hlt.control.target_df[new_pos.x, new_pos.y]
                    # logging.info(f"{s}")
                    s *= (hlt.control.self_distance_factor ** (abs(dx) + abs(dy)))
                    # if s >= best_s:
                    #     best_s = s
                    pot_tars.append([new_pos, s])

    pot_tars.sort(key=lambda x: x[1], reverse=True)

    # logging.info(f"{pot_tars}")
    for new_pos, s in pot_tars:
        if not hlt.control.is_target[new_pos]:
            target_pos = new_pos
            return target_pos

    if target_pos is None:
        # logging.info(f"Couldn't find target position with get_target_weak.")
        target_pos = get_target(ship)

    return target_pos


def get_target_weaker(ship):
    """
    Used to determine a new target for a ship, to collect from, nearby.
    :param hlt.control:
    :param ship:
    :return:
    """

    game_map = hlt.control.game.game_map
    pos = ship.position
    target_pos = None
    # best_s = 0.0
    pot_tars = list()

    for dx in range(-1 * hlt.control.weaker_ship_visibility, hlt.control.weaker_ship_visibility + 1):
        for dy in range(-1 * hlt.control.weaker_ship_visibility, hlt.control.weaker_ship_visibility + 1):
            new_pos = game_map.normalize(positionals.Position(pos.x + dx, pos.y + dy))
            # logging.info(f"{game_map.width},{game_map.height},{positionals.Position(pos.x + dx, pos.y + dy)}, {new_pos}")
            if game_map[new_pos].halite_amount > hlt.control.minimum_halite_to_collect:
                if not hlt.control.game.game_map[new_pos].has_structure:
                    # try:
                    # logging.info(f"{new_pos.x},{new_pos.y}, {hlt.control.target_df[0,0]}")
                    s = hlt.control.target_df[new_pos.x, new_pos.y]
                    # logging.info(f"{s}")
                    s *= (hlt.control.self_distance_factor ** (abs(dx) + abs(dy)))
                    # if s >= best_s:
                    #     best_s = s
                    pot_tars.append([new_pos, s])

    pot_tars.sort(key=lambda x: x[1], reverse=True)

    # logging.info(f"{pot_tars}")
    for new_pos, s in pot_tars:
        if not hlt.control.is_target[new_pos]:
            target_pos = new_pos
            return target_pos

    if target_pos is None:
        # logging.info(f"Couldn't find target position with get_target_weak.")
        target_pos = get_target(ship)

    return target_pos


def get_drop_loc(ship):

    game_map = hlt.control.game.game_map
    me = hlt.control.game.me

    d = game_map.calculate_distance(ship.position, me.shipyard.position)
    best_pos = me.shipyard.position  # by default, dropoff is shipyard
    for do in hlt.control.my_dropoffs:
        do_d = game_map.calculate_distance(ship.position, do)
        # if this dropoff is closer than the previous one, go there instead
        if do_d < d:
            d = do_d
            best_pos = do
    return game_map.normalize(best_pos)


def get_pot_dropoff_loc():
    """
    Used to determine a new target for a ship, to collect from.
    :param hlt.control:
    :param ship:
    :return:
    """
    game_map = hlt.control.game.game_map
    me = hlt.control.game.me
    df = hlt.control.target_df

    scaled = list()
    for (i, score) in df.iteritems():
        # logging.info(f"{row}")
        tx = i[0]
        ty = i[1]
        tpos = positionals.Position(tx, ty)
        d = float(game_map.calculate_distance(tpos, me.shipyard.position))  # distance to closest dropoff
        for do in hlt.control.my_dropoffs:
            do_d = float(game_map.calculate_distance(tpos, do))
            # if this dropoff is closer than the previous one, go there instead
            if do_d < d:
                d = do_d
        new_score = score / ((hlt.control.dropoff_distance_factor ** 0.5) ** d)
        # if hlt.control.unsafe_locs[tpos] or tpos in hlt.control.ship_target_loc.values():
        #     new_score = new_score ** (1/hlt.control.self_target_score_penalty)
        scaled.append([tx, ty, new_score])

    scaled.sort(key=lambda x: x[2], reverse=True)

    for x, y, score in scaled:
        tpos = positionals.Position(x, y)
        if not (tpos in hlt.control.blacklisted_dropoff_spots):
            if dropoff_still_good_check(tpos):
                target = positionals.Position(scaled[0][0], scaled[0][1])
                return target
            else:
                hlt.control.blacklisted_dropoff_spots.append(tpos)


def dropoff_still_good_check(pos):

    game_map = hlt.control.game.game_map
    good_pos = True
    me = hlt.control.game.me
    # how close to the nearest dropoff point
    d = game_map.calculate_distance(pos, me.shipyard.position)
    dropoffs = list()
    for pid in hlt.control.game.players:
        dropoffs += [do.position for do in hlt.control.game.players[pid].get_dropoffs()]
        dropoffs.append(hlt.control.game.players[pid].shipyard.position)
    for do in dropoffs:
        do_d = game_map.calculate_distance(pos, do)
        if do_d < d:
            d = do_d
    if d > hlt.control.nearest_dropoff_dist_min:
        area = pathfinding.get_area(pos, 2)
        occupation = 0
        for pos in area:
            if game_map[pos].is_occupied:
                if game_map[pos].ship.owner != hlt.control.game.me.id:
                    occupation += 1
            if occupation >= hlt.control.max_enemies_allowed_to_build:
                break
        if occupation >= hlt.control.max_enemies_allowed_to_build:
            good_pos = False
    else:
        good_pos = False

    if not good_pos:
        hlt.control.blacklisted_dropoff_spots.append(pos)

    return good_pos



