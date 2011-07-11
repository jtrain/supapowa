import pygame
from constants import *

from button import *
from icon import *
from icontypes import *
from panel import *

from gamestate import GameState

__all__ = ['Sprite']

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, containers, image, num_pics = (1,1)):
        pygame.sprite.Sprite.__init__(self, containers)

        #load the image array
        self.imgs = load_img(image, num_pics)
        self.num_images = num_pics[0]*num_pics[1]
        self.img_index = 0 #currently indexed image
        
        self.pos = pos
        self.containers = containers
        self.colour = TRANSPARENT
        self.colours = {BUTTON_OFF: TRANSPARENT, \
                BUTTON_ON: DULL_GREY}
        self.current_state = BUTTON_OFF
        self.last_state = False
        self.redraw()

        self.paragraph = 'default sprite'
        self.kill()
        self.dirty = False

    def _makepanel(self):
        p = Panel([], (0,0), SUB_PANEL_SIZE)
        p.object = self
        p.make_heading((5,10), self.name)
        p.make_text((5,70), self.paragraph)
        return p

    def show(self, containers = None):
        if containers != None:
            self.containers = containers
        self.add(self.containers)

    def redraw(self):
        image, rect = self.__drawboundingbox(self.colour)
        self.image = image
        self.rect = rect

    def __drawsurface(self, colour = TRANSPARENT, size = SPRITE_SIZE):
        rect = pygame.Rect((0,0), size)

        sprite = pygame.Surface(rect.size)
        sprite.fill(colour)
        sprite.set_colorkey(TRANSPARENT)

        return sprite, rect

    def __drawboundingbox(self, colour = TRANSPARENT):
        outer, self.rect = self.__drawsurface()
        pygame.draw.rect(outer, colour, self.rect, 1)
        image = self.__rendercontent(outer)
        rect = image.get_rect()
        rect.topleft = self.pos

        return image, rect

    def __rendercontent(self, image):

        imagepos = self.imgs[self.img_index].get_rect(center = \
                (image.get_rect().centerx, image.get_rect().centery))
        image.blit(self.imgs[self.img_index], imagepos)
        return image

    def update(self, *args):
        if self.dirty:
            self.dirty = False
            self.redraw()

    def set_pos(self, pos):
        self.pos = pos
        self.rect.topleft = pos

    def increment_image(self, increment = 1):
        self.img_index = (self.img_index + increment) % self.num_images
        self.dirty = True

    def set_bounding(self, bounding):
        maybechange = False
        if bounding and self.current_state == BUTTON_ON:
            self.colour = DULL_WHITE
            maybechange = True
        elif bounding and self.current_state == BUTTON_OFF:
            self.colour = self.colours[self.current_state]
        else:
            self.colour = self.colours[self.current_state]
            maybechange = True
        if bounding != self.last_state and maybechange:
            if bounding == False:
                self.current_state = BUTTON_OFF
                self.colour = self.colours[self.current_state]
            self.dirty = True
            self.last_state = bounding

    def click(self, button):
        if button == 1:
            return self._makepanel()

    def __contains__(self, pos):
        return self.rect.collidepoint(pos)

    def mouse_over(self, new_state):
        #state = 1: on 0: off
        if self.last_state: #if bounding box on
            return
        if self.current_state != new_state:
            self.current_state = new_state
            self.colour = self.colours[new_state]
            self.dirty = True
            

