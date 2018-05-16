#!/usr/bin/python2
import unittest
from p4vasp.paint3d.ColladaPaint3D import *
from p4vasp.matrix import Vector
from StringIO import StringIO

class TestColladaPaint3D(unittest.TestCase):
    def testCylinder(self):
        p=ColladaPaint3D()
        f=StringIO()
        position1=Vector(0,0,0)
        position2=Vector(0,0,1)
        color=Vector(1,0,0)

        p.cylinder(position1,position2,7,color)
        p.write(f)
if __name__ == '__main__':
    unittest.main()
