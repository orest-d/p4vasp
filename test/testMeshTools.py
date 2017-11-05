import unittest
from p4vasp.paint3d.MeshTools import *

class TestMeshTools(unittest.TestCase):
    def testCylinder(self):
        coordinates,normals,triangles=cylinderMesh(10)
        for v in coordinates:
            v[2]=0
            self.assert_(abs(v.length()-1)<0.0001)
        self.assertEquals(20,len(coordinates))
        self.assertEquals(20,len(normals))
        self.assertEquals(20,len(triangles))
    def testSphere(self):
        coordinates,normals,triangles=sphereMesh(10)
        for v in coordinates:
            self.assert_(abs(v.length()-1)<0.0001)
        for v in normals:
            self.assert_(abs(v.length()-1)<0.0001)
        self.assertEquals(100,len(coordinates))
        self.assertEquals(100,len(normals))
        self.assertEquals(200,len(triangles))
    def testCone(self):
        coordinates,normals,triangles=coneMesh(10)
        for v in coordinates:
            self.assert_(abs(v.length()-1)<0.0001)
        self.assertEquals(20,len(coordinates))
        self.assertEquals(20,len(normals))
        self.assertEquals(10,len(triangles))

if __name__ == '__main__':
    unittest.main()
