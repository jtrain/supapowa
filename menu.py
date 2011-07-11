"""
Contains definition of all available menus.
"""
import pygame
from pygame.locals import *

from constants import *
from master import BaseChild
from menuitem import MenuItem
from unique import Unique
from font import small_font

class LevelMenu(BaseChild):
    def init(self, levels, prev=None, **kws):
        X, Y = SCREEN_SIZE
        w, h = (100, 300)
        # topleft.
        x, y = ((X - w) / 2, (Y - h) / 2)
        self.surface = self.parent.reserve(child=self,
                topleft=(x, y), size=(w,h))
        self.parent.listen(self, (KEYDOWN, MOUSEBUTTONDOWN))

        self.surface.fill(WHITE)

        self.buttons = pygame.sprite.Group()

        self.levels = {}

        # save the previous menu.
        self.prev = prev

        if prev:
            back = MenuItem(parent=self, controller=self.controller,
                    text='back', containers=[self.buttons])
            back.topleft = (20, 20)
            self.bind('button', self.on_back, back)
            h = 60
        else:
            h = 20

        # set up each of the buttons.
        for level in levels:
            b = MenuItem(parent=self, controller=self.controller,
                    text=level.name, containers=[self.buttons],
                    maxwidth=10)
            b.topleft = (20, h)
            h += b.size[1] + 20
            self.bind('button', self.on_button, b)
            # now map the button to the level.
            self.levels[id(b)] = level

        # add a select button.
        select = MenuItem(parent=self, controller=self.controller,
                text='ok!', containers=[self.buttons])
        select.topleft = (20, h)
        self.bind('select_level', self.on_select, select)

        # description boxes.
        self.active_desc = 'None'

    def on_select(self, button_id):
        """Assume that user has selected a level."""
        for level in self.levels.values():
            if level.name in self.active_desc:
                break
        else:
            # none found.
            return

        # create the game for now and pass it the level.
        import powersim
        Game = powersim.Game
        # XXX note that here we could define a 'prev' for the game
        # to come back to on 'ESC' event.

        child = self.parent.add_child(Game, level=level, prev=self.prev)
        child.resume()

        # play nice and suspend myself.
        self.stop()

    def on_back(self, button_id):
        # stop myself and reanimate former.
        self.prev.resume()
        self.stop()

    def stop(self):
        self.kill_desc()
        self._stop()

    def kill_desc(self):
        # kill any currently active description.
        self.controller.send(self.active_desc, None)
        self.active_desc = 'None'

    def on_button(self, button_id):
        # get the clicked button.
        try:
            level = self.levels[button_id]
        except KeyError:
            return

        # remove any other description box.
        self.kill_desc()

        # get a unique name to register to close the description box.
        unique = Unique()
        close_name = unique.generate(level.name)
        self.active_desc = close_name

        # should now create a co-menu with the description.
        child = self.parent.add_child(DescriptionBox, text=level.description,
                closename=close_name)
        child.resume()

    def _redraw(self):
        self.buttons.update()
        self.buttons.draw(self.surface)
        return self.surface

    def _loop(self, events):
        for event in events:

            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                if not pos in self:
                    return

                localpos = self.localise(pos)

                # was click in a button?
                for b in self.buttons:
                    b.click(localpos)


class DescriptionBox(BaseChild):
    """Defines a space that a paragraph or so of text can be displayed.
    Is cleaned up through registration of self with the controller."""
    def init(self, text, closename, **kws):
        # request some space from the parent.
        self.txt_surface = small_font(text or 'default', TEXT_COL,
                width=20)

        self.surface = self.parent.reserve(child=self,
                        topleft=(500, 100), size=self.txt_surface.get_size())

        self.controller.register(closename, self.on_close)

    def _redraw(self):
        self.surface.fill(BLUE)
        self.surface.blit(self.txt_surface, (0, 0))
        return self.surface

    def on_close(self, *args):
        self.stop()
