from tiletypes import Tiledict

class AddUnitEvent(object):
    """Add a unit after a given number of ticks."""
    def __init__(self, ticks, Unit, pos=None):
        """ticks - number of ticks to wait before adding unit."""
        self.Unit = Tiledict.get(Unit)
        self.pos = pos
        self.ticks = ticks
        self.active = True

    def update(self, level, game):
        # check how many ticks have elapsed.
        ticks = level.ticks
        if ticks > self.ticks and self.active:
            # run event.
            self.active = False # expire event so it doesn't run again.
            unit = self.Unit()
            if self.pos:
                unit.set_xy(self.pos)
                game.mesh.addtile(unit, self.pos)

from gamestate import GameState

class MakeSwing(object):
    """make an existing unit a swing unit."""
    def __init__(self, ticks, name):
        self.ticks = ticks
        self.name = name
        self.active = True

    def update(self, level, game):
        ticks = level.ticks
        if ticks > self.ticks and self.active:
            self.active = False
            gs = GameState()
            gs.edit_tile('Coal1', dict(bustype=1))

class MakePopup(object):
    """Confront the user with a paragraph in a popup box."""
    def __init__(self, ticks, heading, txt):
        self.ticks = ticks
        self.heading = heading
        self.txt = txt
        self.active = True

    def update(self, level, game):
        ticks = level.ticks
        if ticks > self.ticks and self.active:
            self.active = False
            game.make_popup(self.heading, self.txt)

def make_namedclass_filter(name):
    def isnamedclass(obj):
        'check that obj has the same class name as specified'
        return obj.lower() == name.lower()
    return isnamedclass

class Condition(object):
    def met(self, *args, **kwargs):
        return not self.active

class CheckTypeBuilt(Condition):
    'Purpose is to check a number of given types are built.'
    def __init__(self, number, buildtype):
        'buildtype is the name of the object we need number of'
        self._number = number
        name = Tiledict.get(buildtype).__name__
        self._buildfilter = make_namedclass_filter(name)
        self.active = True

    def met(self, level, game):
        'Check there is a given number of the type we want built.'
        members = game.getmembers()
        names = [m.__class__.__name__ for m in members]
        if len(filter(self._buildfilter, names)) >= self._number:
            return True
        return False











