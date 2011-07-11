import unittest

import powersystem

import time

class TestPS(unittest.TestCase):
    """Test the Power System Object."""
    def setUp(self):
        self.ps = powersystem.PowerSystem()

    def tearDown(self):
        self.ps.stop()

    def testAddBus(self):
        """Test the ability to add new buses to Power System."""
        ps = self.ps
        ps.start()

        ps.add_bus('john', pgen=10)
        time.sleep(0.1)

        self.assert_(len(ps._elems) == 1)

    def testAddLine(self):
        ps = self.ps
        ps.start()

        ps.add_line('john')
        time.sleep(0.1)

        self.assert_(len(ps._elems)== 1)

    def testBuildNetwork(self):
        """Test the ability to add two connecting buses and line."""
        ps = self.ps
        ps.start()

        ps.add_bus('john', connections=['phil']) 
        ps.add_bus('mary', connections=['phil'])

        ps.add_line('phil', connections=['john', 'mary'])
        time.sleep(0.1)

        self.assert_(len(ps._elems)== 3)
        self.assert_(ps._getname('john').elems[0].name == 'phil')

    def testUnordedNetwork(self):
        """Test the ability of network to connect buses and lines."""
        ps = self.ps
        ps.start()

        ps.add_line('phil', connections=['john', 'mary'])
        ps.add_bus('mary')
        ps.add_bus('john', connections=['phil'])

        time.sleep(0.1)

        self.assert_(len(ps._elems) == 3)
        self.assert_(len(ps._getname('mary').elems) == 1)

    def testStartStop(self):
        ps = self.ps
        ps.start()
        time.sleep(0.01)
        self.assert_(ps._running is True)
        ps.stop()
        self.assert_(ps._running is False)

    def testNetworkSolve(self):
        """Test a network of swing bus, load bus and generator bus."""
        ps = self.ps
        ps.start()
        
        # build the network.
        ps.add_line("phil", connections=['swing', 'gen'])
        ps.add_bus("swing", bustype=1)
        ps.add_bus('gen', pgen=1, qgen=0.2, connections=['intercon'])
        ps.add_line('intercon', connections=['gen', 'load'])
        ps.add_bus('load', pload=1)

        time.sleep(0.5)

        # assert that all elements have loaded.
        self.assert_(len(ps._elems) == 5)

        # assert that solution has been found.
        self.assert_(ps.solution is True)

    def testRename(self):
        """Test the renaming of an object."""
        ps = self.ps
        ps.start()

        # add an element.
        ps.add_bus('john', bustype=1)

        time.sleep(0.1)

        # check the object was added.
        self.assert_(ps._getname('john') is not None)

        ps.rename_element('john', 'susan')

        time.sleep(0.1)

        # check the change occured.
        self.assert_(ps._getname('john') is None)
        self.assert_(ps._getname('susan') is not None)

        # check that an invalid name change raises no error.
        ps.rename_element('jimbob', 'tuffnuts')

        time.sleep(0.1)

        # check that the old change hasn't reverted.
        self.assert_(ps._getname('susan') is not None)

    def testEdit(self):
        """Test the ability to change values of an object."""
        ps = self.ps
        ps.start()

        ps.add_bus('john', bustype=2)

        time.sleep(0.1)

        # check that the object was added.

        self.assert_(ps._getname('john') is not None)

        # now change the value of pgen.
        ps.edit_elem('john', dict(pgen=10))

        time.sleep(0.1)

        elem = ps._getname('john')

        self.assertAlmostEqual(elem.pgen, 10)
    def testDecommission(self):
        """Test the removal of line element from a 3 bus network."""
        ps = self.ps
        ps.start()

        # set up a small network.
        ps.add_bus('swing', bustype=1)
        ps.add_bus('load', pload=1)
        ps.add_bus('gen', pgen=0.8)
        ps.add_line('strong', connections=['swing', 'gen'])
        ps.add_line('shakey', connections=['gen', 'load'])

        time.sleep(0.5)

        # check that the objects were added.
        self.assert_(len(ps._elems) == 5)

        # now remove the shakey element.
        ps.decommission_element('shakey')

        time.sleep(0.5)

        # check the element is now gone.
        self.assert_(ps._getname('shakey') is None)
        # assert that 'load' is not connected to anything.
        self.assert_(len(ps._getname('load').elems) == 0)

    def testSolutionCallback(self):
        """Test that the solution callback correctly returns 
        records following a valid solution."""

        called = [False]

        def _checkrecord(record, itemtype, name, 
                    gen=None, voltage=None, angle=None,
                    pflow=None, frm=None, to=None):
            """check that the record returned is correct."""
            self.assert_(record[0] == itemtype)
            self.assert_(record[1] == name)
            payload = record[2]
            # check to this many significant places.
            PLACES = 2
            # check that if a bus, it generated the given amount.
            if gen:
                self.assertAlmostEqual(payload[2], gen, PLACES) 
            # check that if a bus, voltage and angle remain at voltage, angle.
            if voltage:
                self.assertAlmostEqual(payload[0], voltage, PLACES)
            if angle:
                self.assertAlmostEqual(payload[1], angle, PLACES)
            # check that if a line, the power flow is accurate.
            if pflow:
                self.assertAlmostEqual(payload[0], pflow, PLACES)
            # check that if a line, the from and to bus are correct.
            if frm:
                self.assert_(payload[-2] == frm)
            if to:
                self.assert_(payload[-1] == to)

        def _swing(record):
            try:
                _checkrecord(record, 'bus', 'swing', gen=0.0, 
                    voltage=1.0, angle=0.0)
            except AssertionError:
                print record
                raise
        def _phil(record):
            _checkrecord(record, 'line', 'phil', pflow=0.0,
                    frm='swing', to='gen')
        def _gen(record):
            _checkrecord(record, 'bus', 'gen', gen=1.0,
                    voltage=1.0, angle=0.0)
        def _intercon(record):
            _checkrecord(record, 'line', 'intercon', pflow=1.0,
                    frm='gen', to='load')
        def _load(record):
            _checkrecord(record, 'bus', 'load', gen=0.0)

        record_lookup = dict(
                            swing=_swing, 
                            phil=_phil,
                            gen=_gen,
                            intercon=_intercon,
                            load=_load
                        )

        def mycallback(records):
            called[0] = True
            self.assert_(len(records) == 5)

            # now assert that the actual records themselves are correct.
            for record in records:
                fn = record_lookup[record[1]]
                fn(record)

        ps = self.ps
        ps.start()
        
        # build the network.
        ps.add_bus("swing", bustype=1)
        ps.add_line("phil", connections=['swing', 'gen'])
        ps.add_bus('gen', pgen=1, qgen=0.2, connections=['intercon'])
        ps.add_line('intercon', connections=['gen', 'load'])
        ps.add_bus('load', pload=1)

        ps.set_solution_callback(mycallback)
        time.sleep(0.5)

        # assert that all elements have loaded.
        self.assert_(len(ps._elems) == 5)

        # assert that solution has been found.
        self.assert_(ps.solution is True)

        time.sleep(0.5)
        # assert that callback was called.
        self.assert_(called[0] is True)

if __name__ == "__main__":
    unittest.main()
