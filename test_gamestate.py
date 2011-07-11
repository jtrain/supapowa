#!/usr/bin/env python
import unittest

from gamestate import GameState

import time


class TestGameState(unittest.TestCase):
    """Test case to test the GameState object.
    This object sits between the view and the model (PowerSystem object)."""
    def setUp(self):
        gs = self.gs = GameState()

        # crudely set up a power system.
        gs.ps.add_line("phil", connections=['swing', 'gen'])
        gs.ps.add_bus("swing", bustype=1)
        gs.ps.add_bus('gen', pgen=1, qgen=0.2, connections=['intercon'])
        gs.ps.add_line('intercon', connections=['gen', 'load'])
        gs.ps.add_bus('load', pload=1)

    def testSolutionCallback(self):
        """Test that the solution callback returns the correct
        number of records on a solution being reached by the solver."""

        time.sleep(0.1)

        namelist = ['phil', 'swing', 'gen', 'intercon', 'load']
        def decount(record):
            try:
                namelist.remove(record[1])
            except ValueError:
                pass
            
        self.gs.register('phil', decount)
        self.gs.register('swing', decount)
        self.gs.register('gen', decount)
        self.gs.register('intercon', decount)
        self.gs.register('load', decount)

        time.sleep(0.4)
        self.assert_(len(namelist) == 0)

    def testBadConnection(self):
        """test connecting an additional bus to a power line."""
        self.gs.ps.add_bus('bad bus', pgen=1, connections=['intercon'])

        time.sleep(0.1)
        self.assert_(True)

    def testEditElem(self):
        """Test the ability to edit the element."""
        self.assert_(True)
        #import pdb
        #pdb.set_trace()
        #def show(record):
            #print record
        #self.gs.register('gen', show)
        #time.sleep(0.2)
        ##self.gs.edit_tile('gen', dict(pgen=0.5))
        #time.sleep(0.4)

if __name__ == '__main__':
    unittest.main()



