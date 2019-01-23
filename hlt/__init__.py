#!/usr/bin/env python

from . import commands, entity, game_map, networking, constants, AI, config, pathfinding, ships, spawner, strategies, tactics
from .networking import Game
from .positionals import Direction, Position

control = AI.Controller()
control.game = Game()
