"""
Intended to be the top level for
PowerSim. This is the top level parent.
"""
import sys
import pygame
import threading
import time
import random
import Queue
from collections import defaultdict

from pygame.locals import *

from constants import *

import controller

class Master(object):
    """
    Top level parent object.
    Maintains the pygame program.
    """
    def __init__(self, size=None):
        """Initialise the PowerSim game."""
        # enable a large buffer to stop crackle in the sound.
        pygame.mixer.pre_init(44100, -16, 2, 1024 * 6)
        pygame.init()


        # set the screen size.
        self.size = size or SCREEN_SIZE

        # initialise the screen and background.
        self.window = pygame.display.set_mode(self.size)
        self.screen = pygame.display.get_surface()
        # background is used to 'clear' the screen between frames.
        self.background = pygame.Surface(self.size).convert()
        self.background.fill(GREY)
        self.screen.blit(self.background, (0, 0))
        pygame.display.flip()

        # add a clock.
        self.clock = pygame.time.Clock()

        # children threads.
        self.children = []

        # listening children.
        self.listening = []

        # create the controller.
        self.c = controller.Controller()

        self.c.register('exit', self.stop)
        self.c.register('pause', self.pause_child)

    def mainloop(self):
        """Maintain the children and event queue."""
        self.running = True
        while self.running:
            self.clock.tick(FPS)

            self.prune()

            self.events()

            self.redraw()

    def prune(self):
        """remove all dead children from children and listening."""
        for child in reversed(self.children):
            if not child.running.isSet():
                self.children.remove(child)
                try:
                    self.listening.remove(child)
                except ValueError:
                    pass
                # now fill over their empty space with background.
                topleft = child.topleft
                area = pygame.Rect(topleft, child.size)
                self.screen.blit(self.background, topleft, area)
                pygame.display.update([area])

    def events(self):
        """tend to the event queue, pass events to global controller."""
        for event in pygame.event.get():
            # pass the event to children.
            if event.type == QUIT:
                self.c.send('exit', event)

            for child, types in self.listening:
                if not child.pause.isSet():
                # dont send events to suspended children.
                    continue
                elif event.type in types:
                    child.events.put(event)

    def redraw(self):
        """check each of the children to see if they have a surface to
        publish and publish it."""
        # a list of dirty rectangles to redraw.
        dirty = []
        for child in self.children:
            if not child.pause.isSet():
                # if the child is paused don't redraw.
                continue

            # request a redraw from the child.
            try:
                surface = child.redraw()
            except NoUpdate:
                continue

            topleft = child.topleft
            area = surface.get_rect(topleft=topleft)
            # draw over screen with background first.
            self.screen.blit(self.background, topleft, area)
            self.screen.blit(surface, topleft)

            # create a kind of 'dirty' list to redraw.
            dirty.append(area)

        pygame.display.update(dirty)

    def stop(self, event):
        # exit the main loop.
        self.running = False

        for thread in self.children:
            thread.stop()
            thread.join()


    def pause_child(self, pause):
        pause()

    def listen(self, child, types):
        """Notify parent that this child is listening for the listed event
        types."""
        self.listening.append((child, types))

    def add_child(self, Child, *args, **kws):
        newchild = Child(parent=self, controller=self.c, *args, **kws)
        newchild.setDaemon(True)
        # child begins in a paused state.
        newchild.start()

        self.children.append(newchild)
        return newchild

    def reserve(self, child, topleft, size):
        """Child makes a request to reserve some surface space for it's
        blitting. Attempt to give child as much space as possible with top left
        as specified."""
        # current parent total size.
        p_xlen, p_ylen = self.size

        # child x and y size request.
        c_xlen, c_ylen = size
        c_x, c_y = topleft

        # limit child topleft to (0, 0) cannot be negative.
        a_x, a_y = max(c_x, 0), max(c_y, 0)

        # allowable x and y lengths.
        a_xlen = min(p_xlen, a_x + c_xlen) - a_x
        a_ylen = min(p_ylen, a_y + c_ylen) - a_y

        # normalise the size w.r.t zero. Child could request topleft outside
        # allowable area.
        a_xlen = max(a_xlen, 0)
        a_ylen = max(a_ylen, 0)

        # create a surface and return it to the child. Also register this
        # child's size and topleft.
        childsurface = pygame.Surface((a_xlen, a_ylen)).convert()

        child.topleft = (a_x, a_y)
        child.size = (a_xlen, a_ylen)

        return childsurface

class FakeSemaphore(object):
    def __init__(self, *args):
        pass
    def acquire(self):
        pass
    def release(self):
        pass

class BaseChild(threading.Thread):
    """Defines an empty Null child."""
    def __init__(self, parent, controller, *args, **kws):
        threading.Thread.__init__(self)
        self.running = threading.Event()
        self.pause = threading.Event()
        self.parent = parent
        self.controller = controller

        # define a queue.
        self.events = Queue.Queue()

        # define a mapping between object_id and callable fn.
        self._bound = defaultdict(set)

        # create a clock to limit the FPS.
        self.clock = pygame.time.Clock()
        self.init(**kws)

        # create a 'screen' lock in effect around loop.
        self.looplock = FakeSemaphore(1)#threading.Semaphore(1)
        self.drawlock = FakeSemaphore(1)#threading.Semaphore(0)

    def init(self, **kws):
        """A do nothing initialisation function called from baseclass
        __init__."""
        pass

    def run(self):
        self.running.set()
        while True:
            # halt here if paused.
            self.pause.wait()

            # check if process is terminated.
            if not self.running.isSet():
                break

            # get all the events.
            events = []
            while not self.events.empty():
                events.append(self.events.get())

            # executed once per loop.
            self.looplock.acquire()
            try:
                self._loop(events)
            finally:
                self.drawlock.release()

            self.clock.tick(FPS)

    def redraw(self):
        self.drawlock.acquire()
        try:
            screen = self._redraw()
            return screen
        finally:
            self.looplock.release()

    def _redraw(self):
        raise NoUpdate("BaseChild does not redraw!")

    def _loop(self, events):
        time.sleep(1.0/FPS)
        time.sleep(1.0/FPS)

    def stop(self):
        """Override this function to hook into the
        stop sequence. Ensure you call _stop at the end."""
        self._stop()

    def _stop(self):
        self.resume()
        self.running.clear()

    def suspend(self):
        self.pause.clear()

    def resume(self):
        self.pause.set()

    def bind(self, name, fn, obj):
        """registers with the controller to listen for
        'name' events. matches the recieved event with id(obj)
        and calls the mapped fn."""
        self.controller.register(name, self._event)
        self._bound[id(obj)].update([fn])

    def _event(self, object_id):
        """
        called by the controller function when a registered
        event is sent. object_id was mapped earlier with the appropriate
        function call."""

        # do not complete request if we are paused.
        if not self.pause.isSet():
            return

        try:
            fns = self._bound[object_id]
        except KeyError:
            pass
        else:
            for fn in fns:
                fn(object_id)

    def reserve(self, child, topleft, size):
        """Child makes a request to reserve some surface space for it's
        blitting. Attempt to give child as much space as possible with top left
        as specified."""
        # current parent total size.
        p_xlen, p_ylen = self.size

        # child x and y size request.
        c_xlen, c_ylen = size
        c_x, c_y = topleft

        # limit child topleft to (0, 0) cannot be negative.
        a_x, a_y = max(c_x, 0), max(c_y, 0)

        # allowable x and y lengths.
        a_xlen = min(p_xlen, a_x + c_xlen) - a_x
        a_ylen = min(p_ylen, a_y + c_ylen) - a_y

        # normalise the size w.r.t zero. Child could request topleft outside
        # allowable area.
        a_xlen = max(a_xlen, 0)
        a_ylen = max(a_ylen, 0)

        # create a surface and return it to the child. Also register this
        # child's size and topleft.
        childsurface = pygame.Surface((a_xlen, a_ylen)).convert()

        child.topleft = (a_x, a_y)
        child.size = (a_xlen, a_ylen)

        return childsurface

    def __contains__(self, pos):
        x, y = self.localise(pos)
        if x < 0 or y < 0:
            return False
        x_size, y_size = self.size
        if x > x_size or y > y_size:
            return False
        return True

    def localise(self, pos):
        # user clicked at absolute position a,b.
        a, b = pos
        x, y = self.topleft
        return (a - x, b - y)

class NoUpdate(Exception):
    pass

class MovingObjectChild(BaseChild):
    """defines a child that produces an image of a moving block."""
    def init(self, **kws):
        # request some surface space from the parent, specify topleft and size.
        self.surface = self.parent.reserve(child=self,
                                            topleft=(0, 0), size=(100, 100))
        self.events = Queue.Queue()
        self.parent.listen(self, (KEYDOWN,))

    def _redraw(self):
        # return a surface to blit.
        colour = random.choice([RED, BLUE, GREEN, WHITE])
        self.surface.fill(colour)
        return self.surface

from menuitem import MenuItem

class Menu(BaseChild):
    """Defines a menu object, Menus have a plain background and
    a few 'buttons' and accept mouse and keyboard input."""
    def init(self, **kws):
        # request some surface space from the parent.
        X, Y = SCREEN_SIZE
        self.surface = self.parent.reserve(child=self,
                               topleft=(X/2 - 50, Y/2 - 50), size=(100, 100))
        self.events = Queue.Queue()
        self.parent.listen(self, (KEYDOWN, MOUSEBUTTONDOWN))

        self.surface.fill(WHITE)

        buttons = ['Play Game!', 'Exit Game!']
        self.buttons = pygame.sprite.Group()

        # set up the buttons.
        play = MenuItem(parent=self, controller=self.controller,
                text=buttons[0], containers=[self.buttons])
        play.topleft = (20, 20)
        quit_ = MenuItem(parent=self, controller=self.controller,
                text=buttons[1], containers=[self.buttons])
        quit_.topleft = (20, 60)

        # bind button state to an event.
        self.bind('button', self.on_play, play)
        self.bind('button', self.on_quit, quit_)

    def _on_play(self, event):
        import powersim
        Game = powersim.Game
        child = self.parent.add_child(Game)
        child.resume()

    def on_play(self, event):
        """Show the user a level select Menu."""
        from menu import LevelMenu

        # import the levels.
        import level
        c = self.controller
        levels = [
                    level.Level1(c),
                    level.Level2(c),
                    level.Level3(c)
                ]
        child = self.parent.add_child(LevelMenu, levels=levels,
                prev=self) # menus have a 'prev' to go back.
        child.resume()

        # be good and suspend myself.
        self.suspend()

    def on_quit(self, event):
        print "quit!"
        self.controller.send('exit', None)

    def _loop(self, events):
        # called per frame.
        for event in events:

            if event.type == MOUSEBUTTONDOWN:
                pos = event.pos
                # check to see if click was on us.
                if not pos in self:
                    return

                # localise pos to this child.
                localpos = self.localise(pos)

                # was click in a button?
                for b in self.buttons:
                    b.click(localpos)

    def _redraw(self):
        # return a surface to blit.
        self.buttons.update()
        self.buttons.draw(self.surface)
        return self.surface

if __name__ == '__main__':
    c = controller.Controller()
    c.setDaemon(True)
    c.start()

    m = Master()
    # start a child.
    kid3 = m.add_child(Menu)
    kid3.resume()

    # start the master.
    m.mainloop()








