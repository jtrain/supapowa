"""
A module to bridge between the object representation of 
elements and the matrix representation required by a 
typical solver.
"""

from collections import defaultdict
from numpy import matrix

class InvalidSwingBus(AttributeError):
    """Raised on swingbus object that does not implement
    Desired interface."""
    pass

class NoSolution(ArithmeticError):
    """Raised on invalid solution, or solver failed
    at some point."""
    pass

class SolverBridge(object):
    def __init__(self, solver):
        """Initialise with an instantiated solver class.
        This class accepts a bus and a line matrix."""
        self._solver = solver

        # used to get the latest netlist.
        self._swingbus = None

        self._createstorage()

    def _createstorage(self):
        """Create the mapping attributes."""
        # a mapping between busnos and names.
        # lines are mapped by (to,frm) tuple.
        self._name2busnum = {}
        self._busnum2elem = {}
        self._line2elem = {}
        # XXX: Remove this not required.

    def swingbus():
        def fget(self):
            return self._swingbus

        def fset(self, swingbus):
            """Set swing bus checks swingbus
            implements interface before setting."""
            
            try:
                swingbus.active_nodes
            except AttributeError:
                msg = 'SwingBus object does not define active nodes'
                raise InvalidSwingBus(msg)
                        
            self._swingbus = swingbus
        return locals()
    swingbus = property(**swingbus())

    def solve(self):
        """Once swing bus has been set, this is called to
        send the netlist to the solver and update objects."""

        # create new mapped storages.
        self._createstorage()

        netlist = self.swingbus.active_nodes()
        # map all the buses in the netlist.

        busmatrix = []
        for i, element in enumerate(netlist):
            # first map all bus elements.

            if element._bustype is None:
                # check if a bus or line element.
                continue
        
            self._busnum2elem[i] = element
            self._name2busnum[element.name] = i

            busmatrix.append(element.tolist(i))

        # now map the line elements.
        linematrix = []
        for element in netlist:
            # check to see if it is a bus.
            if element._bustype is not None:
                continue

            # get connected buses.
            buses = element.elems

            # a tuple of the connected bus numbers. 
            nums = tuple(self._name2busnum[bus.name] 
                                    for bus in buses)

            self._line2elem[nums] = element

            linematrix.append(element.tolist(nums))

        busmatrix = matrix(busmatrix)
        linematrix = matrix(linematrix)

        try:
            # compute the solution and return as a system of arrays.
            busrows, linerows = self._solver(busmatrix, linematrix, 
                                        0.02, 15, 0.95, 1.05, 1, 'n', 1)
        except (ValueError, IndexError, TypeError, UnboundLocalError):
            # occurs when solver fails loudly.
            raise NoSolution("Solver failed to complete! No Solution")

        # update buses with recalculated values.
        for row in busrows:
            busobj = self._busnum2elem[int(row[0])]
            updatebus(busobj, row)

        # update lines with recalculated values.
        for row in linerows:
            frmto = (int(row[1]), int(row[2]))
            try:
                lineobj = self._line2elem[frmto]
            except KeyError:
                continue

            # store power flows as a direction from bus name to bus name.
            frm_name = self._busnum2elem[frmto[0]].name
            to_name = self._busnum2elem[frmto[1]].name
            # store as a nested tuple (p, q, from, to)
            lineobj.pqflow = (row[3], row[4], frm_name, to_name)

        return netlist

def updatebus(busobj, row):
    """Update the bus with the contents of the row.
    Could be implemented in the bus object."""
    busobj.voltage = row[1]
    busobj.angle = row[2]
    busobj.pgen = row[3]
    busobj.qgen = row[4]
    busobj.pload = row[5]
    busobj.qload = row[6]






        


