import unittest
from p4vasp.Structure import AtomInfo

class TestAtominfo(unittest.TestCase):
    def testDownscale(self):
        a = AtomInfo(2)
        a[0].atomspertype=2
        a[1].atomspertype=4
        self.assertEquals(a.atomspertype,[2,4],"Atoms per type should match")
        a.downscale(2)
        self.assertEquals(a.atomspertype,[1,2],"Atoms per type should be downscaled")

if __name__ == '__main__':
    unittest.main()
