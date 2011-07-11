import pygame

from constants import *
from icon import *
from panel import *

__all__ = ['Lineicon', 'Coalicon', 'Sellicon', 'Windfarmicon',
        'Loadicon', 'Syncicon', 'Swingicon', 'Renameicon']


class Baseicon():
    def __init__(self, panel, obj, num_pics, left_click, type):
        build = Buildicon(obj, num_pics, left_click, type)
        mypanel = self.makepanel()
        mypanel.add_icon((5,50), build)
        panel.add_dynamic_panel((2,218), mypanel, self.name)
    def makepanel(self):
        mypanel = Panel([], pos = (0,0), size = (PANEL_SIZE[0] - 4, 180))
        mypanel.make_heading((5,10), self.name)
        return mypanel

class Windfarmicon(Icon, Baseicon):
    def __init__(self, panel, mesh):
        default_init(self, 'windfarm.png', (1,1), \
                'blip.wav', 'Windfarm', panel, mesh.build_tile)

class Coalicon(Icon, Baseicon):
    def __init__(self, panel, mesh):
        default_init(self, 'coal.png', (1,1), 'blip.wav', 'Coal', panel, \
                mesh.build_tile)

class Lineicon(Icon, Baseicon):
    def __init__(self, panel, mesh):
        default_init(self, 'line.png', (1,1), 'blip.wav', 'Line', panel,
                mesh.build_tile)

class Loadicon(Icon, Baseicon):
    def __init__(self, panel, mesh):
        default_init(self, 'load.png', (1,1), 'blip.wav', 'Load', panel,
                mesh.build_tile)

class Syncicon(Icon, Baseicon):
    def __init__(self, panel, mesh):
        default_init(self, 'syncon.png', (1,1), 'blip.wav', 'Sync', panel,
                mesh.build_tile)

class Buildicon(Icon):
    def __init__(self, object, num_pics, left_click, type):
        Icon.__init__(self, (0,0), [], object, padding=(5,5), 
                sound=None, num_pics = num_pics)
        self.set_leftaction(left_click, type)

class Sellicon(Buildicon):
    def __init__(self, panel, mesh, host):
        Buildicon.__init__(self, 'sell.png', (1,1), mesh.sell_tile, host)

class Swingicon(Buildicon):
    def __init__(self, callback, name):
        Buildicon.__init__(self, 'make swing', (1,1), callback, name)

class Renameicon(Buildicon):
    def __init__(self, callback, name):
        Buildicon.__init__(self, 'rename', (1,1), callback, name)

def default_init(self, image, num_pics, sound, arg, panel, callback):
        Icon.__init__(self, (0,0), [], obj = image,\
                sound = sound, num_pics = num_pics)
        self.set_leftaction(panel.show_panel, arg)
        Baseicon.__init__(self, panel, image, num_pics, callback, arg)

