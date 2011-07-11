import testcase 
import smallcase
from loadflow import loadflow
from ybus import ybus

import unittest

class TestLoadflow(unittest.TestCase):
    def test9Bus(self):
        """Test a 3 Machine 9 Bus system."""
        self.failureException(
                run_loadflow(testcase.bus, testcase.line))
    def testSmallNetwork(self):
        """Test a small 2 Bus network."""
        self.failureException(
                run_loadflow(smallcase.bus, smallcase.line))

def run_loadflow(bus, line):
    import pdb
    pdb.set_trace()
    return loadflow(bus, line, 0.02, 2, 0.95, 1.05, 1, 'n', 1)

def run_ybus():
    return ybus(bus, line, 2)

if __name__ == '__main__':
    unittest.main()
