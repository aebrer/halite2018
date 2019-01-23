import hlt
from hlt import config, strategies, spawner, ships, tactics, pathfinding, entity, positionals, constants
import logging, time, os
from itertools import product
import pandas as pd
from scipy import signal
import numpy as np


# logging.info("Initializing:")
config.load_constants()

for param in hlt.control.dyno:
    for timepoint in hlt.control.dyno[param]:
        logging.info(f"0\t{param}\t{timepoint}\t{hlt.control.dyno[param][timepoint]}")

# logging.info("Creating target df:")
hlt.control.all_pos = list()
for x, y in product(range(hlt.control.game.game_map.height), range(hlt.control.game.game_map.height)):
    hlt.control.all_pos.append([x, y, None])
    hlt.control.is_target[positionals.Position(x, y)] = False
hlt.control.target_df = pd.DataFrame(hlt.control.all_pos, columns=['x', 'y', ''])
hlt.control.target_df = hlt.control.target_df.set_index(['x', 'y'], drop=True)
# logging.info("Filling in all scores:")
search_start_time = time.time()
hlt.control.target_df = hlt.control.target_df.apply(tactics.get_target_score, axis=1)
hlt.control.initial_halite = hlt.control.current_halite
# logging.info(f"{hlt.control.target_df.head()}")
# logging.info(f"Finished score calculations in {time.time() - search_start_time} seconds.")
# for (i, score) in hlt.control.target_df.iteritems():
#     logging.info(f"\n@{i[0]},{i[1]},{score},raw\n")
myarr = hlt.control.target_df.unstack()
r = list(range(hlt.control.kernel_radius, 0, -1)) + [0] + list(range(1, hlt.control.kernel_radius))
kernel = [[hlt.control.target_scaling ** (i+j) for j in r] for i in r]
# logging.info(f"{myarr}")
grad = signal.convolve2d(myarr, kernel, boundary='symm', mode='same')
new_df = pd.DataFrame(grad).stack().reindex_like(hlt.control.target_df)
# logging.info(f"{new_df.unstack()}")
# logging.info(f"{new_df}")
hlt.control.target_df = new_df
# for (i, score) in hlt.control.target_df.iteritems():
#     logging.info(f"\n@{i[0]},{i[1]},{score},conv\n")
# logging.info(f"{hlt.control.target_df}")

hlt.control.game.ready("highlander")  # Respond with your name

while True:
    # logging.info("New turn!")
    start_time = time.time()
    # logging.info("Updating:")
    hlt.control.num_eligible_spaces = 0
    hlt.control.game.update_frame()

    hlt.control.total_ships = 0
    ship_nums = list()
    for player in hlt.control.game.players.values():
        hlt.control.total_ships += len(player.get_ships())
        ship_nums.append(len(player.get_ships()))
    geometric_mean_ships = 1.0
    for num in ship_nums:
        geometric_mean_ships *= num
    hlt.control.mean_ships_per_player = geometric_mean_ships ** (1/len(hlt.control.game.players.values()))
    logging.info(f"{hlt.control.game.turn_number}\ttotal_ships\t{hlt.control.total_ships}")
    logging.info(f"{hlt.control.game.turn_number}\tmean_ships\t{hlt.control.mean_ships_per_player}")

    # scale all the constants based on game details
    # must be done before current halite is set, for efficiency, so it will actually be based on last turn
    config.set_progress_details()
    strategies.scale_constants()

    for tpos in hlt.control.ship_target_loc.values():
        hlt.control.is_target[tpos] = True

    hlt.control.current_halite = 0
    hlt.control.target_df = pd.DataFrame(hlt.control.all_pos, columns=['x', 'y', ''])
    hlt.control.target_df = hlt.control.target_df.set_index(['x', 'y'], drop=True)
    # logging.info("Filling in all scores:")
    hlt.control.target_df = hlt.control.target_df.apply(tactics.get_target_score, axis=1)
    # for (i, score) in hlt.control.target_df.iteritems():
    #     logging.info(f"\n@{i[0]},{i[1]},{score},raw,{hlt.control.game.turn_number}\n")
    # logging.info(f"{hlt.control.target_df.head()}")
    myarr = hlt.control.target_df.unstack()
    grad = signal.convolve2d(myarr, kernel, boundary='symm', mode='same')
    new_df = pd.DataFrame(grad).stack().reindex_like(hlt.control.target_df)
    hlt.control.target_df = new_df
    # for (i, score) in hlt.control.target_df.iteritems():
    #     logging.info(f"\n@{i[0]},{i[1]},{score},conv,{hlt.control.game.turn_number}\n")
    # logging.info(f"{hlt.control.target_df}")

    hlt.control.coms = list()  # command queue
    hlt.control.ships = hlt.control.game.me.get_ships()
    hlt.control.current_ship_locs = list()
    hlt.control.ships_at_max = 0

    # get all dropoff adjacent positions:
    dropoffs = [do.position for do in hlt.control.game.me.get_dropoffs()]
    dropoffs.append(hlt.control.game.me.shipyard.position)
    hlt.control.my_dropoffs = dropoffs

    hlt.control.adj_posis = list()
    for pos in hlt.control.my_dropoffs:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) <= 2:
                    test_pos = hlt.control.game.game_map.normalize(positionals.Position(pos.x + dx, pos.y + dy))
                    hlt.control.adj_posis.append(test_pos)
    hlt.control.close_adj_posis = list()
    for pos in hlt.control.my_dropoffs:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) <= 1:
                    test_pos = hlt.control.game.game_map.normalize(positionals.Position(pos.x + dx, pos.y + dy))
                    hlt.control.close_adj_posis.append(test_pos)
    # logging.info(f"{hlt.control.adj_posis }")

    if hlt.control.ships:
        ship_tar_df = hlt.control.target_df.copy()
        ship_tar_df = ship_tar_df.sort_values(ascending=False)
        cutoff = round((
                    (len(ship_tar_df.index) ** 2) * (
                        hlt.control.target_percentile_cutoff / len(hlt.control.ships)
                    )
        ))
        cutoff = max(len(hlt.control.ship_target_loc.values()) + 300, cutoff)
        # logging.info(f"{cutoff}")
        hlt.control.ship_tar_df = ship_tar_df.head(n=int(cutoff))

    # get ships at max
    for ship in hlt.control.ships:
        if ship.halite_amount >= hlt.control.minimum_halite_to_collect:
            hlt.control.ships_at_max += 1

    # logging.info("Getting Ship Roles:")
    builders = list()
    for ship in hlt.control.ships:
        if ship.id not in hlt.control.ship_role:
            hlt.control.ship_role[ship.id] = "new"
        ships.get_role(ship)
        if hlt.control.ship_role[ship.id] == "builder":
            builders.append(ship)
    if len(builders) >= 1:
        hlt.control.building_dropoff = True
    else:
        hlt.control.building_dropoff = False
    # logging.info("{}".format(time.time() - start_time))


    # spawn if needed, must be done after the ships locs list is populated
    hlt.control.spawning = False
    if spawner.spawn_check():
        # logging.info("Spawning.")
        spawner.spawn()

    logging.info(f"{hlt.control.game.turn_number}\tspawning\t{hlt.control.spawning}")

    # logging.info("Commanding Ships:")
    # get commands for each ship
    # command the harvesters first, as I care about them more
    unseen_shipsZ = list()
    unseen_shipsY = list()
    unseen_ships0 = list()
    unseen_ships1 = list()
    unseen_ships2 = list()
    unseen_ships3 = list()
    unseen_ships4 = list()

    for ship in hlt.control.ships:
        if ship.position in hlt.control.my_dropoffs:
            msg = ships.get_command(ship)
        else:
            unseen_shipsY.append(ship)
    for ship in unseen_shipsY:
        if ship.position in hlt.control.close_adj_posis and hlt.control.ship_target_loc[ship.id] not in hlt.control.close_adj_posis:
            msg = ships.get_command(ship)
        else:
            unseen_shipsZ.append(ship)
    for ship in unseen_shipsZ:
        if ship.position in hlt.control.adj_posis and hlt.control.ship_target_loc[ship.id] not in hlt.control.adj_posis:
            msg = ships.get_command(ship)
        else:
            unseen_ships0.append(ship)
    for ship in unseen_ships0:
        if hlt.control.ship_role[ship.id] == "builder":
            msg = ships.get_command(ship)
        else:
            unseen_ships1.append(ship)
    for ship in unseen_ships1:
        if hlt.control.ship_role[ship.id] == "harvester":
            msg = ships.get_command(ship)
        else:
            unseen_ships2.append(ship)
    for ship in unseen_ships2:
        if ship.position == hlt.control.ship_target_loc[ship.id]:
            msg = ships.get_command(ship)
        else:
            unseen_ships3.append(ship)
    for ship in unseen_ships3:
        msg = ships.get_command(ship)
    # logging.info("{}".format(time.time() - start_time))




    logging.info(f"{hlt.control.game.turn_number}\truntime\t{time.time() - start_time}")

    # logging.info("Ending Turn.")
    # Send your moves back to the game environment, ending this turn.
    hlt.control.game.end_turn(hlt.control.coms)
