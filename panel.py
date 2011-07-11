import pygame
from pygame.locals import *

from constants import *
from icon import *
from font import *

__all__ = ['Panel']

class Panel(pygame.sprite.Sprite):
    def __init__(self, containers, pos = PANEL_POS, size = PANEL_SIZE):
        pygame.sprite.Sprite.__init__(self, containers)

        self.child_groups = pygame.sprite.RenderUpdates()
        self.buttons = pygame.sprite.Group()
        self.panels = pygame.sprite.Group()

        self.dynamic_panels = {}
        self.pos = pos
        self.size = size
        self.containers = containers
        image, self.rect = self.__make_panel()
        self.image = pygame.Surface(size)
        self.image.blit(image, (0,0))
        
        self.showing_dynamic = False
        self.kill()

    def __make_panel(self):
        panel = pygame.Surface(self.size)
        panel.fill(PANEL_BORDER)
        
        inner = pygame.Surface((self.size[0] - 2, self.size[1] - 2))
        inner.fill(PANEL_BACK)
        panel.blit(inner, (1,1))
    
        self.panel = panel
        rect = pygame.Rect(self.pos, self.size)

        return panel, rect

    def make_heading(self, pos, text='powersim.'):
        self._heading = large_font(text, HEADING_COL, PANEL_BACK)
        self.panel.blit(self._heading, pos)
        self.image.blit(self.panel, (0,0))

    def make_text(self, pos, text = 'default'):
        paragraph = small_font(text, DULL_WHITE, PANEL_BACK)
        self.panel.blit(paragraph, pos)
        self.image.blit(self.panel, (0,0))

    def clear_yrange(self, (topleft, size)):
        """clears a section of background the size of rect."""
        blank_panel = pygame.Surface(size)
        blank_panel.fill(PANEL_BACK)
        self.panel.blit(blank_panel, topleft)

    def show(self, containers=None):
        try:
            if containers != None:
                self.containers = containers
        except:
            pass
        self.add(self.containers)

    def close(self):
        self.kill()
        for panel in self.panels:
            panel.close()

    def set_pos(self, pos):
        self.pos = pos
        self.rect.topleft = pos

    def add_icon(self, pos, icon):
        self.__add_object(pos, icon, self.buttons)

    def add_dynamic_panel(self, pos, panel, name):
        self.dynamic_panels[name] = panel
        self.__add_object(pos, panel, self.panels)
        panel.kill()

    def show_panel(self, name):
        try:
            for panel in self.panels:
                panel.kill()
            panel = self.dynamic_panels[name]
            panel.show([self.child_groups, self.panels])
            self.showing_dynamic = True
        except Exception, msg:
            print msg

    def __add_object(self, pos, obj, containers):
        obj.set_pos(pos)
        obj.show([self.child_groups, containers])

    def update(self,*args, **kwargs):
        try:
            mouse = self.__mouseevent(args[0])
        except KeyError:
            pass
        for panel in self.panels:
            if not panel.alive():
                panel.close()

        self.child_groups.clear(self.image, self.panel)
        self.child_groups.update(mouse)
        self.child_groups.draw(self.image)
        self.showing_dynamic = False

    def __contains__(self, pos):
        return self.rect.collidepoint(pos)

    def __mouseevent(self, mouse):
        """
        mouse object:
        tuple(tuple(x,y), tuple(m1,m2,m3))
        """
        rawpos, button_state = mouse
        left, middle, right = button_state

        #get pos relative to panel
        pos = self.__relativepos(rawpos) 

        if not (rawpos in self): #if pos not on panel
            self.__mousedown(left, right, pos)
            return (pos,button_state) #do nothing

        if not self.__mousedown(left, right, pos):
            self.__mouseover(pos) 

        return (pos, button_state)
        
    def __mouseover(self, pos):
        for button in self.buttons:
            if pos in button:
                button.mouse_over(1)
            else:
                button.mouse_over(0)

    def __mousedown(self, left, right, pos):
        if left: #if left click
            index = 1
        elif right: #if right click
            index = 3
        else: #return false if no clicks
            return False

        for panel in self.panels:
            if not pos in panel and not self.showing_dynamic:
                panel.close()
        for button in self.buttons:
            if button.get_state():
                click = button.click(index)

        return True

    def __relativepos(self, pos):
        pos_x = pos[0] - self.pos[0]
        pos_y = pos[1] - self.pos[1]
        return (pos_x, pos_y)

