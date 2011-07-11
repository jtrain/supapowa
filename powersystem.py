import threading
import Queue
import time
from collections import defaultdict

# exceptions.
from elem import ElemError, AlreadySearched
# Element classes.
from elem import SwingHolder, BusElem, LineElem
# Solver Bridge.
from solverbridge import SolverBridge, NoSolution
# get the solver.
from solver import loadflow

from command import _OperationCreateLine, _OperationCreateBus
from command import _OperationDecommission, _OperationRenameElement
from command import _OperationSetSolutionCallback, _OperationEditElement

__all__ = ['PowerSystem']

class PowerSystemError(Exception):
    """Error in Power System Class."""
    pass

"""Bus Types:
    1: Swing bus
    2: Generator Bus (PV Bus)
    3: Load Bus (PQ Bus)
"""
        
class PowerSystem(threading.Thread):
    """An object to bridge the Mesh object - a graphical view, and the 
    strategy to calculate power flow."""
    def __init__(self, bustype=BusElem, linetype=LineElem):
        threading.Thread.__init__(self)
        # a threadsafe queue for communication with Mesh.
        self._queue = Queue.Queue(-1)
        # bus and line types can be set at startup.
        self.BusType = bustype
        self.LineType = linetype

        # keep a map of attempted connections.
        self._attempted = defaultdict(list)

        # active elements.
        self._elems = {}

        # thread running.
        self._running = False

        # current solution.
        # XXX Future versions may implement this as a property 
        # in order to place a mutex on its access.
        self.solution = False

        # set a default callback that can be overridden by client.
        def defaultcallback(self, *args, **kws):
            pass
        self._solution_callback = defaultcallback

    def add_bus(self, name, pgen=0, qgen=0, connections=None, 
                            pload=0, qload=0, bustype=None):
        """Creates a new bus object in the network, use the bustype 
        keyword to specify if type 1 (integer 1)."""
        if bustype not in [None, 1, 2, 3]:
            raise PowerSystemError("Invalid Bus Type.")
        
        if ((pgen or 1) < 0 or 
           (qgen or 1) < 0 or 
           (pload or 1) < 0 or 
           (qload or 1) < 0):
            raise PowerSystemError("Cannot have negative loads/gens.")

        # assign a bus type, generator or load bus.
        if bustype is None:
            # determine if generator or load bus.
            if pgen > 0 or qgen > 0:
                # assume greater than 0 for now, no consuming 'generators'.
                bustype = 2
            else:
                bustype = 3

        bus = _OperationCreateBus(name=name, pgen=pgen, qgen=qgen, pload=pload,
                connections=connections, qload=qload, bustype=bustype)

        self._queue.put(bus)

    def set_solution_callback(self, fn):
        """Enable other client classes to be notified of the changed
        netlist details after a solution."""

        cmd = _OperationSetSolutionCallback(fn=fn)
        self._queue.put(cmd)
        
    def add_line(self, name, connections=None):
        """Creates a new line object in the network."""

        line = _OperationCreateLine(name=name, connections=connections)

        self._queue.put(line)

    def rename_element(self, from_name, to_name):
        """Rename an existing element from name to name."""
        com = _OperationRenameElement(from_name=from_name, to_name=to_name)
        self._queue.put(com)
        
    def decommission_element(self, name):
        """Remove the element from the Power System."""
        com = _OperationDecommission(name=name)
        self._queue.put(com)

    def edit_elem(self, name, changes):
        """Edit the element given by name, with the 
        attribute changes in the changes dict."""
        com = _OperationEditElement(name=name, changes=changes)
        self._queue.put(com)

    def _edit_elem(self, name, changes):
        """Change the attributes on the element with the ones
        in the given change dictionary."""
        elem = self._getname(name)
        for change, value in changes.items():
            try:
                getattr(elem, change)
            except AttributeError:
                continue
            else:
                setattr(elem, change, value)

    def _addelem(self, name, elem):
        """Add a mapped reference to the element."""
        self._elems[name] = elem

    def _getname(self, name):
        """Return the object mapped by name."""
        return self._elems.get(name)

    def _addmap(self, mapfrom, mapto):
        """Each key will return a list of elems that failed to connect
        to this elem."""
        self._attempted[mapfrom] += [mapto]

    def _getmap(self, name):
        """Return a list of elems that failed to connect to name.
        Also clears the list, assumes that object will be created 
        and it is not needed"""
        lst = [self._getname(elemname) for elemname in self._attempted[name]]
        del(self._attempted[name])
        return lst

    def _decommission(self, name):
        """Decommission the element given by name."""
        # remove the mapping of elems that failed to connect to this element.
        try:
            del(self._attempted[name])
        except KeyError:
            # no attempts to connect were made.
            pass

        element = self._getname(name)
        element.decommission()

        del(self._elems[name])

    def _rename(self, from_name, to_name):
        """Rename the element, and remap all it's references to old name.
        Do not execute if to_name exists."""

        if self._getname(to_name) is not None:
            # exit early if the new name already exists.
            return

        # get the original named object.
        old_elem = self._getname(from_name)

        # exit early if no such old element exists.
        if old_elem is None:
            return

        # set the new name on the object itself.
        old_elem.name = to_name

        # remove the current mapping.
        del(self._elems[from_name])

        # add the new mapping.
        self._addelem(to_name, old_elem)

    def run(self):
        """The main power system loop. 
        Checks the queue for posted commands and runs them."""

        solver = SolverBridge(loadflow)
        # set the swing bus, this will be automatically updated when
        # a real swingbus is set.
        solver.swingbus = SwingHolder()

        self._running = True
        while self._running:

            try:
                cmd = self._queue.get(timeout=0.1)
            except Queue.Empty:
                # no items in the queue after 0.1 seconds.
                pass
            else:
                # implement the command giving power system as the context.
                cmd.operate(context=self)

            # now get the netlist and solve the network.
            try:
                netlist = solver.solve()
            except (ElemError, NoSolution), msg:
                self.solution = False
            else:
                self.solution = True

                # notify callback 
                self._solution_callback(self._make_solution_callback(netlist))

    def _make_solution_callback(self, netlist):
        """Transform netlist and lineflow to a series of payload records 
        of the form:
            (recordtype, name, (*payload))
        """
        return tuple(element.torecord() for element in netlist)

    def stop(self):
        self._running = False
        while self.isAlive():
            pass

