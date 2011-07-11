"""
Define network elements to communicate with PST.
"""

class DanglingLine(Exception):
    """Raised on a line with no start or end point."""
    pass

class LineElement():
    """Contains references to a from BusElement and a to
    BusElement."""
    def __init__(self, frm=None, to=None):
        self.set_from(frm)
        self.set_to(to)

    def set_from(self, frm):
        """Set the object that this line is connected to.
        Set to None for no object. Nominal sending end."""
        self._frm = frm
        frm.next_el = self

    def set_to(self, to):
        """Set the object that this line is connected to.
        Set to None for no object. Nominal recieving end."""
        self._to = to
        to.next_el = self

    def remove(self, obj):
        """Remove obj from to or from."""
        if self._frm is obj:
            self._frm = None
        elif self._to is obj:
            self._to = None

    def convert(self):
        """ Attempt to convert this line element into a PST type element."""
        res = 0.01
        reac = 0.05
        chrg = 0.05

        if self._from is None or self._to is None:
            raise DanglingLine(
                    "Could not add element missing start or end.")

        # get the from bus number and to bus number.
        frm = self._frm.get_busno()
        to = self._to.get_busno()
        
        line = [frm, to, res, reac, chrg, 1.0, 0.0]
        line_str = ','.join(line)
        return line_str

class BusRegister():
    """Register buses as they are connected using lines. 
    Buses are only assigned a bus number once they are connected."""
    _shared = {}
    _buses = {}
    _availableindex = None
    _max_index = 0
    def __init__(self):
        """Borg Type."""
        self.__dict__ = self._shared

    def register(self, bus):
        """Register the bus in a mapped object.
        As objects are removed, those indexes are placed
        into the available index.
        """
        if self._availableindex is None:
            self._buses[self._max_index] = bus
            self._max_index += 1
            # return the bus number for this bus.
            return self._max_index - 1

        # we have bus numbers that can be re-used.
        busno = self._availableindex.pop()
        self._buses[busno] = bus

        # check if there are no more re-usable bus numbers.
        if len(self._availableindex) == 0:
            self._availableindex = None
        return busno

    #def deregister

class BusElement():
    """Load type can be True (or False for generator)."""
    def __init__(self, p, q, load_type=False):
        self._p = p
        self._q = q
        self._loadtype = load_type
        # the next element (must be a LineEl).
        self._next = None

    def next_el():
        doc = "property to access the next element."
        def fget(self):
            return self._next

        def fset(self, value):
            # often used once the next property has been deleted.
            try:
                self._next.remove(self)
            except AttributeError:
                # Error when _next is a None object.
                pass
            self._next = value

        def fdel(self):
            # remove this bus element but warn next element of deletion.
            try:
                self._next.remove(self)
            except AttributeError:
                # Error when _next is a None object.
                pass
            del(self._next)
        return locals()
    # create a property next_el to refer to the next element.
    next_el = property(**next_el())

    def __del__(self):
        # define what occurs when this element is removed.

        # remove i.e notify next element that it is no longer referenced.
        del(self._next) 


    



