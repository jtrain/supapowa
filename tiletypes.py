import pygame

import tileobject
from constants import *

__all__ = ['Grasstile', 'Linetile', 'Coaltile', 'Tiledict', 'Watertile',
        'Windfarmtile', 'Loadtile', 'SynconTile']

class Windfarmtile(tileobject.BusTile):
    def __init__(self, *args):
        tileobject.BusTile.__init__(self, (0,0), [], 
                TILE_HEIGHT, 'windfarm.png', (1,1))
        self.type = 'Windfarm'
        self.name = 'Wind Farm'
        self.paragraph = """
With a massive installed
capacity, this windfarm looks
great on paper.
"""
        self.info = dict(pgen=0.5)


class Watertile(tileobject.Tile):
    def __init__(self, *args):
        tileobject.Tile.__init__(self, (0,0), [], 
                TILE_HEIGHT, 'water.png', (1,1))
        self.type = 'Water'
        self.name = 'Mighty River'
        self.paragraph = """
The mighty river may
choose it's own direction. 
Only 8 glasses per day allowed.
"""

class Grasstile(tileobject.Tile):
    def __init__(self, *args):
        tileobject.Tile.__init__(self, (0,0), [], 
                TILE_HEIGHT, 'grass.png', (1,1))
        self.type = 'Grass'
        self.name = 'Grassy Noll'
        self.paragraph = """
The Grassy Noll,
The lawn of Australia's 
favourite son. Our Shannon"""
               
class Linetile(tileobject.LineTile):
    def __init__(self, *args):
        tileobject.LineTile.__init__(self, (0,0), [], 
                TILE_HEIGHT, 'line.png', (1,1))
        self.type = 'line'
        self.name = 'Power Line'
        self.paragraph = """
It is a power line
of undisclosed size.
Is it 330kV?."""
        self.info = dict(pflow=None, qflow=None)

class Loadtile(tileobject.BusTile):
    def __init__(self, *args):
        tileobject.BusTile.__init__(self, (0,0), [], 
                TILE_HEIGHT, 'load.png', (1,1))
        self.type = 'load'
        self.name = 'User Load'
        self.paragraph = """
Someone is cookin'
Somebudy is coolin'
Usin thair voltz."""
        self.info = dict(pload=1, qload=0.2)

class SynconTile(tileobject.BusTile):
    def __init__(self, *args):
        tileobject.BusTile.__init__(self, (0,0), [], 
                        TILE_HEIGHT, 'syncon.png', (1,1))
        self.type = 'sync'
        self.name = 'Synchronous Condensor'
        self.paragraph = """
Synchronous Condenser
The poor man's SVC."""
        self.info = dict(bustype=2)


class Coaltile(tileobject.BusTile):
    def __init__(self, *args):
        tileobject.BusTile.__init__(self, (0,0), [], 
                TILE_HEIGHT, 'coal.png', (1,1))
        self.type = 'Coal'
        self.name = 'Coal PS'
        self.paragraph = """
The backbone of the power
system. Coal, just one 
lump is enough to grant
one child's christmas wish."""
        self.info = dict(pgen=1, qgen=0.2)

Tiledict = {'Grass': Grasstile, 'Coal': Coaltile, 'Line': Linetile, 
        'Windfarm': Windfarmtile, 'Load': Loadtile, 'Sync': SynconTile}
