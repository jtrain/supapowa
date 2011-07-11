#!/usr/bin/env python
import pygame
from pygame.locals import *
import sys
import Queue

from constants import *
from button import *
from sprite import *
from popup import *
from textentry import *
from icon import *
from icontypes import *
from panel import *
from tiletypes import *
from tileobject import *
from tilemesh import *

from gamestate import GameState
from textgrab import TextGrab, NoTextBox

from master import BaseChild

hex_size = 32

class Game(BaseChild):
    def init(self, level, prev, **kws):
        self.parent.listen(self, (KEYDOWN, KEYUP,
            MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION))
        self.screen = self.parent.reserve(child=self,
                topleft=(0, 0), size=(SCREEN_SIZE))

        self.prev = prev
        self.level = level

        self.background = pygame.Surface(SCREEN_SIZE).convert()
        self.background.fill(GREY)
        self.screen.blit(self.background, (0,0))

        self.all = pygame.sprite.RenderUpdates()
        self.buttons = pygame.sprite.Group()
        self.sprites = pygame.sprite.Group()
        self.popups = pygame.sprite.Group()
        self.textentry = pygame.sprite.Group()
        self.clock = pygame.time.Clock()

        self.pos = (100,100)

        # tracks the state of movement keys.
        self.keystate = {
                            K_UP: False,
                            K_DOWN: False,
                            K_LEFT: False,
                            K_RIGHT: False }

        p = Panel(self.all)
        p.show()
        p.make_heading((5,10))
        self.panel = p

        # define a method to update some game stats near the top of screen.
        def update_cash(new_value):
            """Updates the cash display near the top of screen."""
            pos = (50, 50)
            p.clear_yrange((pos, (100, 50)))
            txt = 'Cash: $%4d' % new_value
            p.make_text(pos, text=txt)

        gs = GameState()
        gs.register('cash', update_cash)

        members = {
                    'default': (Grasstile, ()), 
                    (2,1):(Watertile, ()), 
                    (1,1): (Watertile, ()),
                    (0,1): (Watertile, ()),
                    (3,0): (Watertile, ()),
                }
        self.mesh = Mesh([self.all], members, (20,12), pos = (30,30))
        self.mesh.set_panel(self.panel)
        self.mesh.show(self.all)

        myline = Lineicon(self.panel, self.mesh)
        self.panel.add_icon((25,100), myline)
        mycoal = Coalicon(self.panel, self.mesh)
        self.panel.add_icon((75,100), mycoal)
        mywind = Windfarmicon(self.panel, self.mesh)
        self.panel.add_icon((125,100), mywind)
        myload = Loadicon(self.panel, self.mesh)
        self.panel.add_icon((175,100), myload)
        mysync = Syncicon(self.panel, self.mesh)
        self.panel.add_icon((225,100), mysync)


        pygame.mixer.music.load('menu.ogg')
        # need to remove this at some stage. XXX
        global clicktrack
        clicktrack = Click_track()

    def _loop(self, events):
        gs = GameState()
        gs.tick()
        self.event(events)
        self.level.tick(self)

    def _redraw(self):
        self.screen = self.background.copy()
        self.all.update((pygame.mouse.get_pos(), clicktrack()), 'name' )
        dirty = self.all.draw(self.screen)

        # allow the text entry boxes and buttons to be highest layer.
        self.textentry.draw(self.screen)
        self.popups.draw(self.screen)
        self.buttons.draw(self.screen)
        return self.screen

    def make_popup(self, heading, txt):
        p = Popup(self.pos, heading, txt, [self.all, self.popups],
                [self.buttons, self.all])
        p.show()

    def getmembers(self):
        'return all the members of the mesh.'
        return self.mesh.active

    def event(self, events):
        for event in events:
            event = self.events.get()
            if event.type == QUIT:
                self.quit()
            elif event.type == KEYDOWN or event.type == KEYUP:
                self.keyevent(event)
            elif hasattr(event, 'pos'):
                self.mouseevent(event)
        self.keyrun()

    def keyevent(self, event):
        try:
            if event.type == KEYDOWN:
                # pass to the global text grabber.
                textentry = TextGrab()
                textentry.push(event.key)
                return
        except NoTextBox:
            pass

        # check for 'ESCAPE'. Pass control back to menu.
        if event.key == K_ESCAPE and event.type == KEYDOWN:
            self.prev.resume()
            self.stop()

        if event.key == K_x and event.type == KEYDOWN:
            t = Textentry(self.pos, [self.all, self.textentry], edit_elem,
                                num_chars=16)
            t.show()
        if event.key == K_t and event.type == KEYDOWN:
            p = Popup(self.pos, "heading", 'jervis \n test', self.all,
                    [self.buttons,self.all])
            p.show()
        elif event.key == K_g and event.type == KEYDOWN: #g: go play musics
            pygame.mixer.music.play()
        elif event.key == K_p and event.type == KEYDOWN: #p: pause musics
            pygame.mixer.music.pause()
        elif event.key == K_u and event.type == KEYDOWN: #u: unpause musics
            pygame.mixer.music.unpause()

        elif event.key == K_UP:
            self.keystate[K_UP] = event.type == KEYDOWN 

    def keyrun(self):
        try:
            if self.keystate[K_UP]:
                self.pos = (self.pos[0], (self.pos[1] - STEP) % SCREEN_SIZE[1])
        except KeyError:
            pass

    def mouseevent(self, event):
        if event.type == MOUSEMOTION:
            for sprite in self.buttons:
                if event.pos in sprite:
                    sprite.mouse_over(1)
                else:
                    sprite.mouse_over(0)
            for sprite in self.sprites:
                if event.pos in sprite:
                    sprite.mouse_over(1)
                else:
                    sprite.mouse_over(0)

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.all.update((pygame.mouse.get_pos(), (1,0,0)))
            elif event.button == 3:
                self.all.update((pygame.mouse.get_pos(), (0,0,1)))
            self.pos = event.pos
            for sprite in self.textentry:
                if not (event.pos in sprite):
                    sprite.close()
            for sprite in self.buttons:
                if sprite.get_state():
                   click = sprite.click(event.button) 
            for sprite in self.sprites:
                sprite.set_bounding(event.pos in sprite)
                if event.pos in sprite:
                    sprite.name = 'instance'
                    p = sprite.click(event.button)
                    if p:
                        self.panel.add_dynamic_panel((2,218), p, sprite.name)
                        self.panel.show_panel('instance')

    def quit(self):
        sys.exit()

    def __del__(self):
        pass

def create_object(self, label, desc, num_pics = (1,1)):

    text_pos = (self.pos[0], self.pos[1] - 50)
    text = Textentry(text_pos, [self.all, self.textentry], desc, BUTTON_BACK, \
            [self.all, self.buttons], print_text)

    popup_pos = (self.pos[0] + 50, self.pos[1] + 50)
    popup = Popup(popup_pos, desc, 'this button \nrocks my jocks',\
            [self.all, self.popups], [self.all, self.buttons] )

    myicon = Icon(self.pos, [self.all, self.buttons], obj = label, \
            sound = 'blip.wav', num_pics = num_pics)
    myicon.set_leftaction(text.show)
    myicon.set_rightaction(popup.show)
    myicon.show()

class Click_track():
    def __init__(self):
        self.left = False
        self.middle = False
        self.right = False
        self.lstate = 0
        self.mstate = 0
        self.rstate = 0
    def __call__(self):
        left, middle, right = (0,0,0) 
        self.left, self.lstate = self.latch(self.left, left, self.lstate)
        self.middle, self.mstate = self.latch(self.middle, middle, self.mstate)
        self.right, self.rstate = self.latch(self.right, right, self.rstate)

        return self.left, self.middle, self.right

    def latch(self, oldstate, newstate, state):
        if state == 0:
            if oldstate == False and newstate == True:
                return True, 1
            else:
                return False, 0
        else:
            if newstate == 0:
                return False, 0
            else:
                return False, 1

def edit_elem(txt):
    """Change an element's attributes."""
    try:
        name, attr, value = txt.split()
        gs = GameState()
        gs.edit_tile(name, {attr: float(value)})
    except ValueError:
        pass

