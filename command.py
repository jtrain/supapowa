from elem import ElemError
class _Command(object):
    """Base class to issue commands."""
    def __init__(self, **kwargs):
        # save the parameters to be used later.
        self.attributes = kwargs

    def _operate(self, elem, context):
        """Command objects override this member."""
        pass

class _ConnectCommand(_Command):
    """Base class for connecting elements to the power system."""
    def _operate(self, elem, context):
        """Add the generic element to the context's list."""
        attr = self.attributes

        connect_names = attr['connections'] or []
        # get the objects represented by the connected names.
        connections = [context._getname(name) for name in connect_names]

        # get a list of elems that I am supposed to connect to.
        cached = context._getmap(attr['name'])
        # remove any NoneType connections (placeholders?).XXX Does this occur?
        cached_connections = [obj for obj in cached if obj is not None]
        
        # cache the ones that were not yet instantiated.
        for name, obj in zip(connect_names, connections):
            if obj is None:
                # this connection failed because 'name' was not
                #  yet instantiated so register myself as wanting to connect
                #  to name.
                context._addmap(mapfrom=name, mapto=attr['name'])

        # remove None Type connections.
        connections = [item for item in connections if item is not None]
        connections += cached_connections

        # connect the line to each of the named connections.
        for element in connections:
            try:
                # try to connect each element on an individual basis.
                elem.connect([element])
            except ElemError:
                pass
        context._addelem(attr['name'], elem) 

class _OperationCreateBus(_ConnectCommand):
    """Create a new bus, using the provided parameters."""
    def operate(self, context):
        """Carry out operation given the context. I.e context
        may provide a set/create/change bus method."""

        # create the new bus.
        attr = self.attributes
        newbus = context.BusType(pgen=attr['pgen'], 
                qgen=attr['qgen'], pload=attr['pload'], qload=attr['qload'],
                bustype=attr['bustype'], name=attr['name'])

        try:
            self._operate(newbus, context)
        except ElemError:
            # ignore cases were invalid connections were attempted.
            pass

class _OperationCreateLine(_ConnectCommand):
    """Create a new line, using the provided parameters."""
    def operate(self, context):
        """Carry out operation given the context. I.e context
        may provide a set/create/change line method."""

        # create the new line.
        attr = self.attributes
        newline = context.LineType(name=attr['name'])

        try:
            self._operate(newline, context)
        except ElemError:
            pass

class _OperationDecommission(_Command):
    """Decommission the given element."""
    def operate(self, context):
        """Decommission the given element, given the context passed."""

        name = self.attributes['name']

        try:
            context._decommission(name)
        except AttributeError:
            # no such 'name' in context.
            pass

class _OperationRenameElement(_Command):
    """Rename the element, from_name, to_name."""
    def operate(self, context):
        """rename the element 'from_name' to 'to_name'
        Assumes that the keys 'from_name' and 'to_name' were
        passed in the creation of this object."""

        from_name = self.attributes['from_name']
        to_name = self.attributes['to_name']

        context._rename(from_name, to_name)

class _OperationSetSolutionCallback(_Command):
    """Set a callback that is called with the new netlist details
    on valid powerflow solution.

    format of callback should be a record (tuple):
    (recordtype, element_name, (*payload))

    where payload is a variable length payload and it's contents for 
    the two defined recordtypes are:
    recordtype: bus
        *payload = (pgen, qgen, pload, qload, volt, ang)
    recordtype: line
        *payload = (pflow, qflow, from_name, to_name)
    
    """

    def operate(self, context):
        fn = self.attributes['fn']
        context._solution_callback = fn


class _OperationEditElement(_Command):
    """Update the attributes on a given element
    with the ones in the changes dict."""

    def operate(self, context):
        name = self.attributes['name']
        changes = self.attributes['changes']
        context._edit_elem(name, changes)
