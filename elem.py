class ElemError(Exception):
    """Error in Elem object."""
    pass

class AlreadySearched(Exception):
    """Island search already performed for this node."""
    pass

class BusTypeObserver(object):
    """An observer to notify swing holder when a bus becomes swing bus."""
    def __init__(self, default=None):
        self._default = default

    def __get__(self, inst, cls):
        if inst is None:
            raise AttributeError("Cannot get class attribute!.")
        try:
            return inst._bustype
        except AttributeError:
            inst._bustype = self._default

        return inst._bustype

    def __set__(self, inst, value):
        if inst is None:
            raise AttributeError("Cannot set class attribute!!") 
        # don't compute if this value is the same as the original.
        if inst.bustype == value:
            return

        inst._bustype = value
        # notify the swing holder.
        try:
            SwingHolder(inst)
        except ElemError:
            pass

class SwingHolder(object):
    """Singleton class to make global availability to the swing
    bus."""
    _shared_state = {}
    _swing = None

    def __init__(self, swing=None):
        """Can update the swing bus by passing swing bus here."""
        self.__dict__ = self._shared_state

        # validate that passed bus is a swing bus.
        try:
            if swing.bustype == 1:
                pass
            else:
                if swing.name == self._swing.name:
                    self._swing = None
                raise ElemError("Bus is not swing bus type")
        except AttributeError:
            # check if we were passed default value or some random object type.
            if swing is not None:
                raise ElemError("Got %s, wanted BusElem type" % type(swing))

        try:
            if self._swing.bustype == 1 and swing is not None:
                # can't have two swing buses at this stage!
                self._swing.bustype = 2
        except AttributeError:
            pass

        # update swing bus if passed a new bus.
        self._swing = swing or self._swing

    def active_nodes(self):
        """Return a list of all the active nodes."""

        reg = Register()
        # begin a new search, clear last search results.
        reg.clear()

        try:
            self._swing.island_search()
        except AttributeError:
            raise ElemError("Error no swing bus set!")

        # island search is now complete, return a list of connected.
        return reg.get_nodes()

class Register(object):
    """On island lookup, register search results to prevent 
        multiple look ups for the same node."""
    _shared_state = {}
    _nodes = []

    def __init__(self):
        """Borg singleton pattern."""
        self.__dict__ = self._shared_state

    def clear(self):
        """new island search, clear previous results."""
        self._nodes = []

    def register(self, node):
        """Add node to searched list. If node exists in list raise
        AlreadySearched, call register before computing search."""
        if node in self._nodes:
            raise AlreadySearched("Already searched node.")
        self._nodes.append(node)

    def remove(self, node):
        """Attempt to remove a node from the searched list."""
        try:
            self._nodes.remove(node)
        except ValueError:
            pass

    def get_nodes(self):
        return self._nodes

class Elem(object):
    """Base element class."""
    # default bus-type is None.
    # this attribute is used during island lookup.
    bustype = BusTypeObserver()

    # attribute to indicate if this node is connected 
    #  through the network to a swing bus. update using the
    #  island_search method.
    _connected = False

    name = 'default'
    def __repr__(self):
        return "<Elem object name: %s>" % self.name

    def decommission(self):
        """
        Remove connections to other elems.
        Remove element from service.
        """
        del(self.elems)

    def connect(self, elems):
        """
        Create connection to other elems.
        """
        # discard elements already connected to this object.
        new_elems = set(elem for elem in elems
                            if not elem in self._elems)

        self.elems = self.elems + list(new_elems)
        # call connect for each of the new elems.
        for elem in new_elems:
            elem.connect([self])

    def disconnect(self, other):
        """Disconnect an Elem object from self."""
        try:
            self._elems.remove(other)
        except ValueError:
            # tried to disconnect an element that wasn't in list.
            pass

    def island_search(self):
        """Begin a search to determine if this node is connected
        to a type 1 bus.""" 

        reg = Register()
        # register self before performing search.
        try:
            reg.register(self)
        except AlreadySearched:
            return

        # if a LineElem self.bustype = None.
        if self.bustype is None:
            # if this line is not connected at both ends, disconnect.
            if len(self._elems) < self._maxelems:
                reg.remove(self)
                return

        # now propagate search.
        for elem in self._elems:
            elem.island_search()

class BusElem(Elem):
    """Bus element. Can connect to multiple LineElements."""
    def __init__(self, name, pgen=0, qgen=0, pload=0, qload=0, bustype=1):
        self.name = name
        self.pgen = pgen
        self.qgen = qgen
        self.pload = pload
        self.qload = qload
        # some default voltage and angle.
        self.voltage = 1
        self.angle = 0

        # check if created with a rubbish bustype.
        if bustype not in [1,2,3]:
            raise ElemError("Invalid bustype: %s must be 1, 2 or 3" % bustype)

        # an empty container to hold connected elements.
        self._elems = []
        # limit number of connected elements to a nominal 10.
        self._maxelems = 10
        # the bus type: 1 load P-Q, 2 generator P-V, 3 swing bus V-delta.
        self.bustype = bustype

    def elems():
        def fget(self):
            """get the connected elements."""
            return self._elems

        def fset(self, value):
            """check if number of elems exceeds maximum. Set if it doesn't."""
            try:
                if len(value) > self._maxelems:
                    # cannot set elems.
                    raise ElemError("Number of elements exceeds maximum.")

                # check if attempt is made to connect a non LineElem.
                for elem in value:
                    if not isinstance(elem, LineElem):
                        raise ElemError(
                            "Cannot connect instance of type %(badtype)r"
                            % dict(badtype=type(elem)))

                self._elems = value
                return 
            except AttributeError:
                # the value is not a sequence type or does not implement len.
                raise ElemError("Must pass a sequence of LineElems")

        def fdel(self):
            """remove all connections. connected elems must be notified."""
            for elem in self._elems:
                elem.disconnect(self)
            self._elems = []
        return locals()
    elems = property(**elems())

    def tolist(self, busno):
        """convert this element to a list representation.
        [busno, voltage, angle, pgen, qgen, pload, qload, 
        conductance, susceptance, bustype]"""
        cond = 0
        susc = 0
        return [busno, self.voltage, self.angle, self.pgen, 
                self.qgen, self.pload, self.qload, cond, susc, self.bustype]

    def torecord(self):
        """Return a record of the form:
        (recordtype, name, (volt, ang, pgen, qgen, pload, qload))
        """
        return (
                'bus', self.name, 
                    ( # payload.
                        self.voltage, self.angle, self.pgen,  
                        self.qgen, self.pload, self.qload, self.bustype 
                    )
                ) 

class LineElem(Elem):
    """Line element. Can connect to two BusElements."""
    def __init__(self, name):
        self.name = name
        # an empty container to hold connected elements.
        self._elems = []
        # limit number of connected elements to 2.
        self._maxelems = 2

        self.res = 0.005
        self.reac = 0.02
        self.charg = 0.1
        self.tap = 1
        self.phase = 0

        # stored as (p, q, from, to)
        self.pqflow = None
    def elems():
        def fget(self):
            """get the connected elements."""
            return self._elems

        def fset(self, value):
            """check if number of elems exceeds maximum. Set if it doesn't."""
            try:
                if len(value) > self._maxelems:
                    # cannot set elems.
                    raise ElemError("Number of elements exceeds maximum.")

                # check if attempt is made to connect a non BusElem.
                for elem in value:
                    if not isinstance(elem, BusElem):
                        raise ElemError(
                            "Cannot connect instance of type %(badtype)r"
                            % dict(badtype=type(elem)))
                self._elems = value
                return 
            except AttributeError:
                # the value is not a sequence type or does not implement len.
                raise ElemError("Must pass a sequence of BusElems")

        def fdel(self):
            """remove all connections. connected elems must be notified."""
            for elem in self._elems:
                elem.disconnect(self)
            self._elems = []
        return locals()
    elems = property(**elems())

    def tolist(self, from_to):
        frm, to = from_to

        return [frm, to, self.res, self.reac, 
                            self.charg, self.tap, self.phase]
    def torecord(self):
        """Return a record of the form:
        (recordtype, name, (pflow, qflow, from_name, to_name))
        """
        return ('line', self.name, self.pqflow)

    



    



