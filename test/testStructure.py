import unittest
from p4vasp.Structure import *
from StringIO import *

class TestStructure(unittest.TestCase):
    def testParsingCell(self):
        f=StringIO("""test chgcar
1
1 2 3
4 5 6
7 8 9
1
cart
0 0 0
""")
       
        s=Structure()
        s.read(f)
        self.assertEquals(s.basis[0][0],1)
        self.assertEquals(s.basis[0][1],2)
        self.assertEquals(s.basis[0][2],3)
        self.assertEquals(s.basis[1][0],4)
        self.assertEquals(s.basis[1][1],5)
        self.assertEquals(s.basis[1][2],6)
        self.assertEquals(s.basis[2][0],7)
        self.assertEquals(s.basis[2][1],8)
        self.assertEquals(s.basis[2][2],9)
    def testReciprocalLattice(self):
        f=StringIO("""test chgcar
1
0 10 10
10 0 10
10 10 0
1
cart
0 0 0
""")
       
        s=Structure()
        s.read(f)
        s.updateRecipBasis()
        self.assertEquals(s.rbasis[0][0],-0.05)
        self.assertEquals(s.rbasis[0][1],0.05)
        self.assertEquals(s.rbasis[0][2],0.05)

        self.assertEquals(s.rbasis[1][0],0.05)
        self.assertEquals(s.rbasis[1][1],-0.05)
        self.assertEquals(s.rbasis[1][2],0.05)

        self.assertEquals(s.rbasis[2][0],0.05)
        self.assertEquals(s.rbasis[2][1],0.05)
        self.assertEquals(s.rbasis[2][2],-0.05)
    def testAppendAtom(self):
        s=Structure()
        self.assertEquals(len(s.info),0)
        self.assertEquals(len(s.positions),0)
        s.appendAtom(0,(1,2,3))
        self.assertEquals(len(s.info),1)
        self.assertEquals(len(s.positions),1)
        self.assertEquals(s[0][0],1)
        self.assertEquals(s[0][1],2)
        self.assertEquals(s[0][2],3)
        s.appendAtom(1,(4,5,6))
        self.assertEquals(len(s.info),2)
        self.assertEquals(len(s.positions),2)
        self.assertEquals(s[1][0],4)
        self.assertEquals(s[1][1],5)
        self.assertEquals(s[1][2],6)
        s.appendAtom(0,(7,8,9))
        self.assertEquals(len(s.info),2)
        self.assertEquals(len(s.positions),3)
        self.assertEquals(s[0][0],1)
        self.assertEquals(s[0][1],2)
        self.assertEquals(s[0][2],3)
        self.assertEquals(s[1][0],7)
        self.assertEquals(s[1][1],8)
        self.assertEquals(s[1][2],9)
        self.assertEquals(s[2][0],4)
        self.assertEquals(s[2][1],5)
        self.assertEquals(s[2][2],6)
    def testNewSpecie(self):
        s=Structure()
        self.assertEquals(len(s.info),0)
        self.assertEquals(len(s.positions),0)
        s.appendAtomOfNewSpecie((1,2,3))
        self.assertEquals(len(s.info),1)
        self.assertEquals(len(s.positions),1)
        self.assertEquals(s[0][0],1)
        self.assertEquals(s[0][1],2)
        self.assertEquals(s[0][2],3)
        s.appendAtomOfNewSpecie((4,5,6))
        self.assertEquals(len(s.info),2)
        self.assertEquals(len(s.positions),2)
        self.assertEquals(s[0][0],1)
        self.assertEquals(s[0][1],2)
        self.assertEquals(s[0][2],3)
        self.assertEquals(s[1][0],4)
        self.assertEquals(s[1][1],5)
        self.assertEquals(s[1][2],6)
        

    

if __name__ == '__main__':
    unittest.main()
