import unittest

import elem

class TestSwing(unittest.TestCase):
    """Test Unit to confirm that swing bus search 
    behaviour works effectively."""
    def setUp(self):
        # note this should auto register a swing bus.
        self.b3 = elem.BusElem(bustype=1, name='default')

    def testAutoSwingHolder(self):
        """Test that the swing holder was notified of swing bus creation."""
        self.failureException(elem.SwingHolder())
        self.assert_(elem.SwingHolder()._swing._bustype == 1)

    def testNetCreation(self):
        """Test that a radial network is built correctly."""
        b1 = elem.BusElem(bustype=1, name='bus1')
        b2 = elem.BusElem(bustype=2, name='bus2')

        # create line elements.
        l1 = elem.LineElem(name='line1')
        l2 = elem.LineElem(name='line2')

        l1.connect([b1, self.b3])
        l2.connect([b1, b2])

        swing = elem.SwingHolder()
        # assert that there are 5 elements in the network.
        self.assert_(len(swing.active_nodes()) == 5)

    def testNetFailure(self):
        """Test that on a line decommission that network 
        topology remains correct."""

        b1 = elem.BusElem(bustype=1, name='bus1')
        b2 = elem.BusElem(bustype=2, name='bus1')

        # create line elements.
        l1 = elem.LineElem(name='line1')
        l2 = elem.LineElem(name='line2')

        l1.connect([b1, self.b3])
        l2.connect([b1, b2])

        swing = elem.SwingHolder()
        # remove line between bus 1 and bus 2.
        l2.decommission()

        # assert that there are 3 elements in the network.
        self.assert_(len(swing.active_nodes()) == 3)

    def testRubbishSwingBus(self):
        """Assert that a rubbish swing bus cannot be created."""
        self.failUnlessRaises(elem.ElemError, elem.SwingHolder, "Rubbish")
        self.failUnlessRaises(elem.ElemError, elem.SwingHolder, 
                elem.BusElem(bustype=2, name='bus1'))
        self.failUnlessRaises(elem.ElemError, elem.SwingHolder, 
                elem.LineElem(name='line1'))

    def testBadBusType(self):
        """Assert that a BusElem cannot be created with incorrect bus type."""
        self.failUnlessRaises(elem.ElemError, elem.BusElem, 
                bustype=4, name='bus2')
        self.failUnlessRaises(elem.ElemError, elem.BusElem, 
                bustype="name", name='name')
        self.failUnlessRaises(elem.ElemError, elem.BusElem, 
                bustype=None, name='name')


class TestElem(unittest.TestCase):
    def setUp(self):
        self.b1 = elem.BusElem(name='b1')
        self.b2 = elem.BusElem(name='b2')
        self.b3 = elem.BusElem(name='b3')
        self.l1 = elem.LineElem(name='l1')

    def testTypeAdd(self):
        """Tests that BusElem cannot connect to BusElem."""
        try:
            self.b1.connect([self.b2, self.b3])
        except elem.ElemError:
            pass
        finally:
            self.assert_(len(self.b1.elems) == 0)
    def testLenLine(self):
        """Test that a LineElem cannot add more than two BusElems."""
        try:
            self.l1.connect([self.b1, self.b2, self.b3])
        except elem.ElemError:
            pass
        finally:
            self.assert_(len(self.l1.elems) == 0)
    def testSelfAdd(self):
        """Test that a BusElem cannot add itself."""
        try:
            self.b1.connect([self.b1])
        except elem.ElemError:
            pass
        finally:
            self.assert_(len(self.b1.elems) == 0)
    def testRepeatAdd(self):
        """Test that an Element doesn't add more 
        than one of the same element instance."""
        self.b1.connect([self.l1, self.l1])
        self.assert_(len(self.b1.elems) == 1)
    def testDecommission(self):
        """Test that decommissioning an element 
        removes it from connected elems."""
        self.l1.connect([self.b1, self.b2])
        self.l1.decommission()
        self.assert_(len(self.l1.elems) == 0 
                        and len(self.b1.elems) == 0 
                        and len(self.b2.elems) == 0
                    )
    def testParallelDecommission(self):
        """Test that a parallel decommissioned line
        doesn't affect the connected status of other line."""
        l2 = elem.LineElem(name='l2')
        l2.connect([self.b1, self.b2])
        self.l1.connect([self.b1, self.b2])
        l2.decommission()
        self.assert_(len(self.l1.elems) == 2
                        and len(self.b1.elems) == 1 
                        and len(self.b2.elems) == 1
                )
    def testConnectBadType(self):
        """Test that an Elem doesn't allow connection of a 
        Non Valid type."""
        def make_exception():
            self.l1.connect('12')
        self.failUnlessRaises(elem.ElemError, make_exception)

if __name__ == '__main__':
    unittest.main()



