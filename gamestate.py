"""A controller module to keep game state,
and maintain callbacks."""
from collections import defaultdict

from observer import Observer
from powersystem import PowerSystem

import random

def curry(fn, arg):
    """Return a new function that calls function 'fn' always with 
    arg as the first argument."""
    def newfn(*args, **kws):
        return fn(arg, *args, **kws)
    return newfn

class Dispatch(object):
    """A callable class that can handle events. I.e handle
    people registering for events and callbacks notifying of events."""
    _dispatch = defaultdict(list)
    def __init__(self):
        pass

    def __call__(self, name, *args):
        """Send the arguments to all listeners that have registered for
        events with name 'name'."""
        listeners = self._dispatch[name]
        for listener in listeners:
            listener(*args)

    def register(self, name, fn):
        """Register for events with name 'name', and provide a function
        that can accept any number of arguments."""
        self._dispatch[name] += [fn]

    def deregister(self, name):
        """remove the registration for name."""
        try:
            del(self._dispatch[name])
        except KeyError:
            pass

    def listeners(self, name):
        """return a list of all the listeners for a particular name."""
        return self._dispatch.get(name, [])

    def names(self):
        """Return a list of all the registered events."""
        return self._dispatch.keys()

class DefaultTile(Exception):
    """Raised when user attempts to register a default tile."""

class GameState(object):
    """A global game state object. 
    Registers events and callbacks to notify the view 
    when the data has changed."""

    # global game state uses singleton 'Borg' pattern.
    _shared_state = {}

    # define class data descriptors for game state variables.
    cash = Observer(curry(Dispatch(), 'cash'), default=1000)

    # define the powersystem object, this maintains the netlist and
    #  solves for powerflow.
    ps = PowerSystem()
    ps.setDaemon(True)
    ps.start()

    _dispatch = Dispatch()

    _nameregister = defaultdict(int)

    def __init__(self):
        self.__dict__ = self._shared_state

        self.ps.set_solution_callback(self._solver_callback)

    def _solver_callback(self, records):
        """Called when the solver reaches a solution with the updated
        record list in tuples."""
        el = ElemRegister()
        for record in records:
            self._dispatch(record[1], record)

            # notify that this element has been updated.
            el.poke(record[1])

        self._records = records
    
    def register(self, name, fn):
        self._dispatch.register(name, fn)

    def add_tile(self, tiletype, info, connections=None):
        if info is None:
            raise DefaultTile("Cannot register a default tile!")

        self._nameregister[tiletype] += 1

        # remove some of the cash level.
        self.cash -= 50

        # create this tile's name.
        name = tiletype + str(self._nameregister[tiletype])

        # now register this tile with the solver.
        if tiletype is 'line':
            self.ps.add_line(name, connections=connections)
        else:
            self.ps.add_bus(name, connections=connections, **info)

        # for some added fun, reg windfarms for gen changes.
        if 'wind' in tiletype.lower():
            wc = WindChange()
            wc.register(name, info['pgen'])

        # register this element with the ElemRegister.
        el = ElemRegister()
        el.register(name)
        return name

    def edit_tile(self, name, changes):
        """update the element attributes with the ones in the changes
        dictionary."""
        self.ps.edit_elem(name, changes)

    def remove_tile(self, name):
        """remove the tile of name 'name' from the powersystem."""
        if name in self._dispatch.names():
            self.ps.decommission_element(name)
            self.cash += 25

            wc = WindChange()
            wc.remove(name)
            er = ElemRegister()
            er.remove(name)

    def rename(self, from_name, to_name):
        """rename an element from name to name. 
        Does not rename if an existing element already has name."""
        # if the name is already registered, don't proceed.
        if to_name in self._dispatch.names():
            return
        self.ps.rename_element(from_name, to_name)

        # take care of registration.
        listeners = self._dispatch.listeners(from_name)
        for listener in listeners:
            # also notify these listeners of a change.
            self._dispatch.register(to_name, listener)

        # anyone that has registered to be notified of name changes.
        self._dispatch('rename', (from_name, to_name))
        self._dispatch.deregister(from_name)

        # now update the wind change and element track objects.
        wc = WindChange()
        size = wc.remove(from_name)
        if size:
            wc.register(to_name, size)

        er = ElemRegister()
        status = er.remove(from_name)
        er.register(to_name, status)

    def tick(self):
        """Called on each iteration through the game loop.
        This function is used to increment game logic such as cash levels
        and other house keeping tasks."""

        # access cash amount forces a callback on initial access.
        self.cash

        # a scheme to determine disconnected nodes.
        el = ElemRegister()
        offline = el.status()

        for element in offline:
            self._dispatch(element, None)

        # a scheme to change windfarm output randomly.
        #  in practice I would like output to change 1 every 20 seconds.
        wc = WindChange()
        wc.shuffle()

class WindChange(object):
    """Allows the wind to change and set the wind farm output
    randomly. Call periodically."""
    _shared_state = {}
    _windfarms = {}
    def __init__(self):
        self.__dict__ = self._shared_state

    def register(self, name, size):
        self._windfarms[name] = size

    def remove(self, name):
        try:
            size = self._windfarms[name]
            del(self._windfarms[name])
            return size
        except KeyError:
            pass

    def shuffle(self):
        """Calculate a probability of wind change for each windfarm.
        If wind changes, calculate the new output level."""
        for farm, size in self._windfarms.items():
            windchange = random.choice(xrange(20)) 
            if windchange:
                continue
            # select a random value from weibull distribution
            #  with lambda = 0.3 and k = 1.
            output = random.weibullvariate(0.3, 1) * size

            gs = GameState()
            gs.edit_tile(farm, dict(pgen=output))

            # only change a single windfarm at a time.
            break

class ElemRegister(object):
    """Keep a track of all online elements."""
    _shared_state = {}
    _elements = {}
    def __init__(self):
        self.__dict__ = self._shared_state

    def register(self, name, status=False):
        self._elements[name] = status

    def remove(self, name):
        try:
            status = self._elements[name]
            del(self._elements[name])
            return status
        except KeyError:
            pass

    def poke(self, name):
        """the passed argument was updated, 
        set it's status to online."""
        try:
            self._elements[name] = True
        except KeyError:
            pass
        
    def status(self):
        """returns all of the elements that have not set
        their status to online since the last check."""
        offline = [name for name in self._elements if 
                            self._elements[name] == False]
        # reset the list.
        for name in self._elements:
            self._elements[name] = False

        return offline


