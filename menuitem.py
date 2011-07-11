"""
A button-like menu item.

Accepts a parent.
Accepts text
to write on it's surface (can use wrap module.)
Has an off/on state.
Is a sprite.
"""

import pygame

from font import small_font
from constants import *

class MenuItem(pygame.sprite.Sprite):
    def __init__(self, parent, controller, text=None, containers=None,
            maxwidth=None):
        pygame.sprite.Sprite.__init__(self, containers or [])
        self.parent = parent
        self.controller = controller

        self.txt_surface = small_font(text or 'default', TEXT_COL,
                width=maxwidth or 50)

        # reserve some space from the parent.
        self.surface = self.parent.reserve(self, topleft=(-1, -1),
                                                size=(self.txt_surface.get_size()))

        self._colours = {True: BLUE, False: GREY}
        self._clicked = False

    def click(self, pos):
        clicked = pos in self
        # send an event if clicked.
        if clicked:
            self.controller.send('button', id(self))
        self._clicked = clicked
        return clicked

    def update(self):
        self.image = self.redraw()
        self.rect = pygame.Rect(self.topleft, self.size)

    def redraw(self):
        # return a representation of this button.
        self.surface.fill(self._colours[self._clicked])
        self.surface.blit(self.txt_surface, (0, 0))
        return self.surface

    def __contains__(self, pos):
        x, y = self.localise(pos)
        if x < 0 or y < 0:
            return False
        x_size, y_size = self.size
        if x > x_size or y > y_size:
            return False
        return True

    def localise(self, pos):
        a, b = pos
        x, y = self.topleft
        return (a - x, b - y)



