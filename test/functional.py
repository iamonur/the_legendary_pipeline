import sys
sys.path.insert(1, '../src')
import unittest
import cellularAutomata as ca
#cellularAutomata.py tests

    #elementary_cellular_automata

        #1- Check if it throws with not valid start

class ifCellularAutomataThrows(unittest.TestCase):
    def test(self):
        with self.assertRaises(ValueError) as context:
            ca.elementary_cellular_automata(start="0") #Should raise a ValueError

            self.assertTrue("" in context.exception)
class ifCellularAutomataWorks(unittest.TestCase):
    def test(self):
        
if __name__ == '__main__':
    unittest.main()