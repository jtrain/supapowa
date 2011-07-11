"""
Level: A base class for providing scripting
and leveling capabilities for the game.

A level provides a name and description (for
identifing purposes in a menu situation.)

A tick method that is called once per frame, this
is used by the level to check if conditions have been met,
And if new events should occur.

"""
from itertools import count
import levelevents as levent

class Level(object):
    name = "Default Level"
    description = """Default Description."""
    events = []
    conditions = []
    _count = count()
    _ticks = 0
    def __init__(self, controller):
        self.controller = controller

    def ticks():
        def fget(self):
            return self._ticks
        def fset(self, value):
            self._ticks = self._count.next()
        return locals()
    ticks = property(**ticks())

    def tick(self, game):
        """Called once per frame, it gives the level object
        a chance to check all conditions and events."""

        # increment tick.
        self.ticks = 'tick'

        # check if all conditions have been met.
        if all(condition.met(self, game) for condition in self.conditions):
            self.controller.send('level_complete', self.name)

        # check if any events should be run.
        for event in self.events:
            # run in the context of the game.
            event.update(self, game)

class Level1(Level):
    name = "Level 1"
    description = """An introduction to PowerSim."""
    events = [levent.AddUnitEvent(0, 'Coal', (5, 5)),
              levent.AddUnitEvent(0, 'Line', (5, 6)),
              levent.AddUnitEvent(0, 'Line', (5, 8)),
              levent.AddUnitEvent(0, 'Load', (5, 9)),
              levent.AddUnitEvent(0, 'Coal', (5, 7)),
              levent.MakeSwing(0, 'Coal1'),
              levent.MakePopup(5, 'Welcome', "Thanks for playing!\n"
                  "A small power system has been set up for you.\n"
                  "Your objective is to add an additional 2 coal \n"
                  "power stations.")]
    conditions = [levent.CheckTypeBuilt(4, 'Coal')]

class Level2(Level):
    name = "Level 2 - The Age of Wind."
    description = """Build up a wind empire."""

class Level3(Level):
    name = "Free Play"
    description = """The world is yours, manage the grid."""

