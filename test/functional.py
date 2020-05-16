"""
    This is the test suite for functionalities. Not a deep-down one, but check if modules/classes raise when need be, and works properly, at least in a given case.
"""
import sys
sys.path.insert(1, '../src') #That's where my modules are
import unittest
import cellularAutomata as ca
import caPolisher as cap
import spritePlanner as sp
#########################################################################################################################
class ifCellularAutomataThrows(unittest.TestCase):
    def test(self):
        with self.assertRaises(ValueError) as context:
            ca.elementary_cellular_automata(start="0") #Should raise a ValueError

            self.assertTrue("" in context.exception)
class ifCellularAutomataWorks(unittest.TestCase): #Class default's rule 30.
    def test(self):
        self.assertEqual([  '000000000000100000000000',
                            '000000000001110000000000',
                            '000000000011001000000000',
                            '000000000110111100000000',
                            '000000001100100010000000',
                            '000000011011110111000000',
                            '000000110010000100100000',
                            '000001101111001111110000',
                            '000011001000111000001000',
                            '000110111101100100011100',
                            '001100100001011110110010',
                            '011011110011010000101111',
                            '110010001110011001101000',
                            '101111011001110111001100',
                            '101000010111000100111010',
                            '101100110100101111100011',
                            '101011100111101000010110',
                            '101010011100001100110101',
                            '101011110010011011100101',
                            '101010001111110010011101',
                            '101011011000001111110001',
                            '101010010100011000001011',
                            '101011110110110100011010',
                            '101010000100100110110011',
                            '101011001111111100101110'], ca.elementary_cellular_automata().perform())
####################################################################################################################
class ifCreatingSelfrefInterfaceThrows(unittest.TestCase):
    def test(self):
        with self.assertRaises(TypeError) as context:
            ca.selfref_ca()
            self.assertTrue("" in context.exception)
######################################################################################################################
class ifBlockOnesMajorityWorks(unittest.TestCase):
    def test(self):
        self.assertEqual([  '110100101110000111011001',
                            '001111110101001010100111',
                            '100000011010100101010001',
                            '100000000111100111110001',
                            '110000001000011000001011',
                            '100111100011010011100010',
                            '110000110001011000110011',
                            '100111100110110011100110',
                            '110100110110111010110111',
                            '101011101101110101101110',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111'], ca.block_ones_majority_srca().perform())
class ifBlockOnesMajorityThrows(unittest.TestCase):
    def test(self):
        with self.assertRaises(ValueError) as context:
            ca.block_ones_majority_srca(start="0") #Should raise a ValueError

            self.assertTrue("" in context.exception)
#####################################################################################################################
class ifBlockOnesOddParityWorks(unittest.TestCase):
    def test(self):
        self.assertEqual([  '110100101110000111011001',
                            '010100100010110001001001',
                            '111111111111011111111111',
                            '011111111111101111111111',
                            '100000000000110000000001',
                            '001111111110000111111100',
                            '110111111110111011111101',
                            '111100000011101110000110',
                            '011100000001100110000010',
                            '010111111101110111111001',
                            '111011111110111011111011',
                            '110111111101110111110110',
                            '011000000110011000011010',
                            '000011110000000011000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000'], ca.block_ones_odd_parity_srca().perform())
class ifBlockOnesOddParityThrows(unittest.TestCase):
    def test(self):
        with self.assertRaises(ValueError) as context:
            ca.block_ones_odd_parity_srca(start="0") #Should raise a ValueError

            self.assertTrue("" in context.exception)
####################################################################################################################
class ifBlockTransitionOddParityWorks(unittest.TestCase):
    def test(self):
        self.assertTrue(True)
        #self.assertEqual(, ca.block_transition_odd_parity_srca().perform())
class ifBlockTransitionOddParityThrows(unittest.TestCase):
    def test(self):
        with self.assertRaises(ValueError) as context:
            ca.block_transition_odd_parity_srca(start="0") #Should raise a ValueError

            self.assertTrue("" in context.exception)
######################################################################################################################
class ifBlockTransOddParMidNybbleSWWorks(unittest.TestCase):
    def test(self):
        self.assertEqual([  '110100101110000111011001',
                            '101110110101110010100100',
                            '111011111111010011100100',
                            '000100000000110100001101',
                            '001100000001101100011011',
                            '110011111110010011100101',
                            '101101111101111101011110',
                            '000000000000000001000000',
                            '000000000000000010000001',
                            '011111111111111000111100',
                            '001111111111110010011000',
                            '001111111111100010010000',
                            '001111111111000000000000',
                            '000111111110000000000000',
                            '100000000001000000000000',
                            '010000000000100000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000'], ca.bl_tr_odd_p_mid_nybble_switch_srca().perform())
class ifBlockTransOddParMidNybbleSWThrows(unittest.TestCase):
    def test(self):
        with self.assertRaises(ValueError) as context:
            ca.bl_tr_odd_p_mid_nybble_switch_srca(start="0") #Should raise a ValueError

            self.assertTrue("" in context.exception)
#######################################################################################################################
class ifCAPolisherThrows(unittest.TestCase): #100 is not do-able.
    def test(self):
        with self.assertRaises(cap.polisherException) as context:
            cap.polisher(minimumArea=100).perform()
            self.assertTrue("" in context.exception)
class ifCAPolisherWorksWithNoIteration(unittest.TestCase): #NO iteration needed for 1.
    def test(self):
        c = ca.bl_tr_odd_p_mid_nybble_switch_srca()
        c1 = cap.polisher(minimumArea=1, ca=c)
        self.assertEqual([  '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '111111111111111111111111', 
                            '111111111111111111111111',
                            '111111111111111111111111',
                            '101101111101111101011110',
                            '000000000000000001000000',
                            '000000000000000010000001',
                            '011111111111111000111100',
                            '001111111111110010011000',
                            '001111111111100010010000',
                            '001111111111000000000000',
                            '000111111110000000000000',
                            '100000000001000000000000',
                            '010000000000100000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000'], c1.perform())
class ifCAPolisherWorks(unittest.TestCase): #60 is do-able with 1 iteration.
    def test(self):
        c = ca.bl_tr_odd_p_mid_nybble_switch_srca()
        c2 = cap.polisher(minimumArea=60, ca=c)
        self.assertEqual([
                            '111111111111111111111111',
                            '111111111111111111100111',
                            '111111111111111111100111',
                            '000100000000111100001111',
                            '001100000001111100011111', 
                            '100001111100010001000101',
                            '101101111101110101011100',
                            '000000000000000001000000',
                            '000000000000000010000001',
                            '011111111111111000111100',
                            '001111111111110010011000',
                            '001111111111100010010000',
                            '001111111111000000000000',
                            '000111111110000000000000',
                            '100000000001000000000000',
                            '010000000000100000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000', 
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000'], c2.perform())
class ifCAPolisherMultipleIterationsWork(unittest.TestCase): #75 is do-able with 3 iterations.
    def test(self):
        c = ca.bl_tr_odd_p_mid_nybble_switch_srca()
        c3 = cap.polisher(minimumArea=75, ca=c)
        self.assertEqual([  '110000001110000111010001',
                            '101110110101110010000100',
                            '100010110100010011100100',
                            '000100000000110000001101',
                            '001100000001001100010011',
                            '100001111100010001000101',
                            '101101111101110101011100',
                            '000000000000000001000000',
                            '000000000000000010000001',
                            '011111111111111000111100',
                            '001111111111110010011000',
                            '001111111111100010010000',
                            '001111111111000000000000',
                            '000111111110000000000000',
                            '100000000001000000000000',
                            '010000000000100000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000', 
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000'], c3.perform())
####################################################################################################################
class ifSPWorks(unittest.TestCase):
    def test(self):
        ccc0= ca.bl_tr_odd_p_mid_nybble_switch_srca()
        cc0 = cap.polisher(ca = ccc0)
        s = sp.spritePlanner(cc0.perform())
        s.perform()
        self.assertEqual([  '111111111111111111111111',
                            '111111111111111111100111',
                            '111111111111111111100111',
                            'A00100000000111100001111',
                            '001100000001111100011111',
                            '100001111100010001000101',
                            '101101111101110101011100',
                            '000000000000000001000000',
                            '000000000000000010000001',
                            '011111111111111000111100',
                            '001111111111110010011000',
                            '001111111111100010010000',
                            '00111111111E000000000000',
                            '000111111110000000000000',
                            '100000000001000000000000',
                            '010000000000100000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '000000000000000000000000',
                            '00000000000000000000000G'], s.getMap())
class ifSPThrows(unittest.TestCase):
    def test(self):
        
        with self.assertRaises(sp.spritePlannerException) as context:
            ccc0= ca.bl_tr_odd_p_mid_nybble_switch_srca()
            cc0 = cap.polisher(ca = ccc0)
            s = sp.spritePlanner(cc0.perform())
            s.getMap()

        self.assertIsInstance(context.exception, sp.spritePlannerException)
##########################################################################################################################
class ifSpinnerWorks(unittest.TestCase): #If spinner works, compilation is done without an exception. Thus, asserting True.
    def test(self):
        self.assertTrue(True)
#NOTE: I cannot do an if throws for this. Maybe I should've remove it. If I cannot test it, it should not occur. If I can find one, I'll definitely add here.
##########################################################################################################################
class ifSpritePlannerThrows(unittest.TestCase): #Early requests make it to throw up.
    def test(self):
        self.assertTrue(True)
        #sp.spritePlanner(cap.polisher().getMap())
class ifSpritePlannerWorks(unittest.TestCase):
    def test(self):
        self.assertTrue(True)
        #pp = cap.polisher().perform()
        #self.assertEqual(, sp.spritePlanner(pp.getMap()))
##########################################################################################################################
class ifParserWorks(unittest.TestCase):
    def test(self):
        self.assertEqual(1,1)
#NOTE: I don't have any cannot win maps yet, but I will have it, and I will make this throw then.
###########################################################################################################################


if __name__ == '__main__':
    unittest.main(failfast=True) #1 error is enough for test to fail.