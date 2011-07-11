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

    def testEditElem(self):
        """Test the ability to edit the element."""
        self.gs.edit_tile('gen', dict(pgen=0.5))
        time.sleep(0.4)
        elem = self.gs.ps._getname('gen')
        self.assertAlmostEqual(elem.pgen, 0.5, 1)

if __name__ == '__main__':
    unittest.main()



