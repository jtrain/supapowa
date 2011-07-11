import unittest

import elem

import solverbridge as sbridge
from solver import loadflow

class TestBridge(unittest.TestCase):
    """Test bridge behaviour in isolation to
    powersystem object."""

    def setUp(self):
        # set up a swing bus.
        self.swing = elem.BusElem(bustype=1, 
                                    name='swing')
        # set up a mini network.
        self.b2 = elem.BusElem(bustype=2, 
                                pgen=10, name='gen')
        self.b3 = elem.BusElem(bustype=3, 
                                pload=10, name='load')
        self.l1 = elem.LineElem(name='connect')
        self.l2 = elem.LineElem(name='loadconnect')

        # connect the network up.
        self.l1.connect([self.swing, self.b2])
        self.l2.connect([self.b3, self.b2])

        # save a swing holder.
        self.swingholder = elem.SwingHolder()

    def testAddSwingBus(self):
        """Test the ability to add a SwingBusHolder 
        object."""

        # pass a dummy solver object.
        s = sbridge.SolverBridge(None)

        def assign_holder(bridge, swing):
            bridge.swingbus = swing

        # set the swing bus holder object.
        self.failureException(
                assign_holder(s, self.swingholder))
                
    def testNewSwing(self):
        """Test the addition of a new swing bus."""
        sw2 = elem.BusElem(bustype=1, name='swing2')
        l2 = elem.LineElem(name='swingline')
        l2.connect([self.swing, sw2])

        self.assert_(self.swingholder._swing.name == 'swing2')
        self.assert_(self.swing._bustype == 2, self.swing._bustype)
        self.assert_(sw2._bustype == 1)

    def testTastelessSwap(self):
        """Test the direct change of swing bus attribute."""
        self.swing.bustype = 2
        self.assert_(self.swingholder._swing is None)
        self.b2.bustype = 1
        self.assert_(self.swingholder._swing.name == 'gen')

    def testSmallSystem(self):
        """Test that the solver will solve for a small system."""
        s = sbridge.SolverBridge(loadflow)
        s.swingbus = self.swingholder

        self.failureException(s.solve())

class TestSolver(unittest.TestCase):
    """Test that the solver is returning a satisfactory 
    result, under a range of conditions."""
    def setUp(self):
        self.bridge = sbridge.SolverBridge(loadflow)
        # the swing bus.
        b1 = elem.BusElem(name='swing', bustype=1)
        b2 = elem.BusElem(name='two', bustype=2, pgen=1.63)
        b3 = elem.BusElem(name='three', bustype=2, pgen=0.85)
        b4 = elem.BusElem(name='four', bustype=3)
        b5 = elem.BusElem(name='five', bustype=3, pload=0.9, qload=0.3)
        b6 = elem.BusElem(name='six', bustype=3)
        b7 = elem.BusElem(name='seven', bustype=3, pload=1.0, qload=0.35)
        b8 = elem.BusElem(name='eight', bustype=3)
        b9 = elem.BusElem(name='nine', bustype=3, pload=1.25, qload=0.5)

        l1 = elem.LineElem(name='l1') 
        l2 = elem.LineElem(name='l2') 
        l3 = elem.LineElem(name='l3') 
        l4 = elem.LineElem(name='l4') 
        l5 = elem.LineElem(name='l5') 
        l6 = elem.LineElem(name='l6') 
        l7 = elem.LineElem(name='l7') 
        l8 = elem.LineElem(name='l8') 
        l9 = elem.LineElem(name='l9') 

        # connect the buses.
        l1.connect([b1, b4])
        l2.connect([b4, b5])
        l3.connect([b5, b6])
        l4.connect([b3, b6])
        l5.connect([b6, b7])
        l6.connect([b7, b8])
        l7.connect([b8, b2])
        l8.connect([b8, b9])
        l9.connect([b9, b4])

        # set up the swing bus.
        swing = elem.SwingHolder()
        self.bridge.swingbus = swing

    def testNetwork(self):
        """Test that the set-up network solves."""
        self.failureException(self.bridge.solve())


if __name__ == '__main__':
    unittest.main()


