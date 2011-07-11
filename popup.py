
import pygame

from constants import *
from font import small_font, large_font
from button import *

__all__ = ['Popup']

class Popup(pygame.sprite.Sprite):
    def __init__(self, pos, heading, text, popup_container, button_container):
        pygame.sprite.Sprite.__init__(self, popup_container)

        self.container = popup_container
        self.pos = pos
        #make text 
        self.heading = large_font(heading, HEADING_COL, BUTTON_BACK)
        self.text = small_font(text, TEXT_COL, BUTTON_BACK)

        self.button_container = button_container
        #make button
        self.button = Exit_button((0,0), [button_container], self.close, 'exit')

        #make box
        height = self.heading.get_height() + self.text.get_height()
        width = max(self.heading.get_width() + self.button.image.get_width(), \
                self.text.get_width())

        rect = pygame.Rect((0,0), (width, height)).inflate(POPUP_PADDING, POPUP_PADDING)
        self.box = pygame.Surface(rect.size)
        self.box.fill(BUTTON_BACK)
        self.box.set_alpha(POPUP_ALPHA)
        inner = pygame.Surface((rect.width - 2, rect.height - 2))
        inner.fill(POPUP_INNER_BASE)
        inner.set_alpha(POPUP_ALPHA)
        self.box.blit(inner, (1,1))
        x, y = 5,5
        rect = self.box.blit(self.heading, (x,y))
        y += rect.height + 5
        self.box.blit(self.text, (x, y)) 
        x = self.box.get_width() - self.button.image.get_width() -5 + pos[0]
        y = 5 + pos[1]
        self.button.set_pos((x,y)) 
        self.image = self.box
        self.rect = pygame.Rect(pos, self.image.get_size())
        self.button.kill()
        self.kill()
        
    def show(self):
        self.button.add(self.button_container) 
        self.add(self.container)

    def close(self):
        self.button.kill()
        self.kill()
        


