import pygame

from constants import *
from sprite import *
from math import tan, pi

from textentry import PermaText
from icontypes import Sellicon, Swingicon
from panel import Panel
from gamestate import GameState

__all__ = ['Tile']

class Tile(Sprite):
    """
    Makes a hexagonal tile
       ***     ^
      *   *    | h
       ***     _
       |-|
        s

    h = s_prime + s + s_prime
    """
    def __init__(self, pos, containers, height_width, image, num_pics = (1,1)): 
        self.containers = containers
        self.size = height_width, height_width

        self.h = height_width
        self.a = height_width * HEX_A
        self.b = height_width * HEX_B
        self.s = height_width * HEX_S

        Sprite.__init__(self, pos, containers, image, num_pics)

        self.name = 'default'
        self.redraw()
        self.kill()

        # default information about the tile.
        self.info = None

        # current warning level.
        self._warning = False
        self._online = True

    def set_xy(self, location):
        self.location = location

    def set_name(self, (from_name, to_name)):
        if self.name == from_name:
            self.name = to_name

    def set_offline(self, offline):
        """Set the element status to offline and 
        change the border colours to yellow."""
        if offline and self._online:
            self.colour = self.colours[BUTTON_OFF] = WARNING_OFFLINE
            self.redraw()
            self._warning = False
        elif not offline and not self._online:
            self.colour = self.colours[BUTTON_OFF] = TRANSPARENT
            self.redraw()

        self._online = not offline
    def set_info(self, info):
        """Accepts a record tuple for a line or bus, and updates info accordingly.
        Can accept a NoneType object, this signifies that the element is offline.
        Set the status to offline and change border colour to yellow."""
        #TODO: can place this information in a BUS/LINE subclass ..
        # unpack the info record.
        if info is None:
            self.info.update(status='offline')
            return self.set_offline(True)
        
        # turn off any online/offline warnings that were present.
        self.set_offline(False)

        mytype, name, payload = info

        def unity(value, tol=0.02):
            return abs(value - 1) < tol

        def rating(value, lim=1.05):
            return abs(value) <= lim

        if mytype is 'line':
            # unpack the payload.
            pflow, qflow, from_name, to_name = payload
            self.info.update(pflow=pflow, qflow=qflow, from_name=from_name,
                            to_name=to_name, status='online')

            # if pflow or qflow are not near unity and this is a new warning.
            if (not rating(pflow) or not rating(qflow)) and not self._warning:
                self.setwarning(True)
            elif rating(pflow) and rating(qflow) and self._warning:
                self.setwarning(False)
      
        else:
            # unpack the bus payload.
            volt, ang, pgen, qgen, pload, qload, bustype = payload 
            self.info.update(volt=volt, ang=ang, pgen=pgen, qgen=qgen, 
                                pload=pload, qload=qload, status='online',
                                bustype=bustype)

            # determine if we need to reset the warning level.
            if (not unity(volt) or not rating(pgen)) and not self._warning:
                self.setwarning(True)
            elif unity(volt) and rating(pgen) and self._warning: 
                self.setwarning(False)

    def redraw(self):
        #draw image onto a surface
        surf = pygame.Surface(self.size)
        surf.fill(TRANSPARENT)
        inner_img = Sprite._Sprite__rendercontent(self, surf)
        
        #make a mask to cover the surface
        mask = self.__makemask()
        maskrect = mask.get_rect()
        maskrect.topleft = self.pos

        #blit the mask onto the image
        inner_img.blit(mask, (0,0))
        inner_img.set_colorkey(TRANSPARENT)
        
        #draw bounding box
        self.__drawpoly(inner_img, colour=self.colour, linewidth = 2)
        self.image = inner_img
        self.rect = maskrect
    
    def __makemask(self):
        #first make a soon-to-be transparent background
        surf = pygame.Surface(self.size)
        surf.fill(TRANSPARENT)

        #now draw a filled polygon onto background
        surf = self.__drawpoly(surf)
        return surf

    def setwarning(self, on):
        """Set the warning level on for this tile.
        Args:
            on - True for set warning to on, False for turn off warnings.
        """
        self._warning = on
        if on:
            self.colour = self.colours[BUTTON_OFF] = WARNING_UNSELECTED
            self.colours[BUTTON_ON] = WARNING_SELECTED
        else:
            self.colour = self.colours[BUTTON_OFF] = TRANSPARENT
            self.colours[BUTTON_ON] = DULL_GREY
        self.redraw()

    def __drawpoly(self, surface, colour=PSEUDO_TRANSPARENT, linewidth = 0):
        H = round(self.h - 1)
        S = round(self.s)
        A = round(self.a)
        B = round(self.b)

        a = (1, A)
        b = (B, 2*A)
        c = (H - B, 2*A)
        d = (H - 1, A)
        e = (H - B, 1)
        f = (B, 1)
        points = [a,b,c,d,e,f]

        if linewidth < 1:
            pygame.draw.polygon(surface, colour, points, linewidth)
        else:
            pygame.draw.polygon(surface, colour, points, linewidth)
            #pygame.draw.aalines(surface, colour, True, points, True)
        if colour == PSEUDO_TRANSPARENT:
            surface.set_colorkey(PSEUDO_TRANSPARENT)

        return surface

class BusTile(Tile):
    def _makepanel(self):
        # make a text entry box.
        def renamer(txt):
            gs = GameState()
            gs.rename(self.name, txt)

            # now rename the panel.
            p.clear_yrange(((5,10), (100, 25)))
            p.make_heading((5, 10), self.name)

        te = PermaText((250, 20), [self.containers], renamer,
                heading='Rename.')

        def set_swing(name):
            gs = GameState()
            gs.edit_tile(name, dict(bustype=1))

        sell = Sellicon(None, self.mesh, self)
        swing = Swingicon(set_swing, self.name)
        p = Panel([], (0,0), SUB_PANEL_SIZE)
        p.object = self
        p.make_heading((5,10), self.name)
        if self.info is None:
            p.make_text((5,70), self.paragraph)
        else:
            txt = dict2txt(self.info)
            p.make_text((5,70), txt)
        p.add_icon((30,40), sell)
        p.add_icon((70,40), swing)
        p.add_dynamic_panel((150,40), te, 'text')
        p.show_panel('text')
        return p

class LineTile(Tile):
    def _makepanel(self):
        # make a text entry box.
        def renamer(txt):
            gs = GameState()
            gs.rename(self.name, txt)

            # now rename the panel.
            p.clear_yrange(((5,10), (100, 25)))
            p.make_heading((5, 10), self.name)

        te = PermaText((250, 20), [self.containers], renamer,
                heading='Rename.')

        sell = Sellicon(None, self.mesh, self)
        p = Panel([], (0,0), SUB_PANEL_SIZE)
        p.object = self
        p.make_heading((5,10), self.name)
        if self.info is None:
            p.make_text((5,70), self.paragraph)
        else:
            txt = dict2txt(self.info)
            p.make_text((5,70), txt)
        p.add_icon((30,40), sell)
        p.add_dynamic_panel((100,40), te, 'text')
        p.show_panel('text')
        return p

def dict2txt(info):
    paragraph = ''
    for i, key in enumerate(sorted(info.keys())):
        if info[key] is None:
            continue
        if i % 3 == 0:
            paragraph += '\n-----\n'
        try:
            paragraph += '%(key)s: %(value)+.2f   ' % dict(
                                            key=key, value=info[key])
        except TypeError:
            value = info[key]
            if len(value) > 7:
                value = value[:7] + '-'
            paragraph += '%(key)s: %(value)s   ' % dict(
                                            key=key, value=value)
    return paragraph
