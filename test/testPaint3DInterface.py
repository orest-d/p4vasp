import unittest
from p4vasp.paint3d.data import *
from p4vasp.paint3d.Paint3DInterface import *

class TestPaint3DInterface(unittest.TestCase):
    def testColorMaterial(self):
        p=Paint3DRecorder()
        p.colorMaterial(Vector(0.5,0.5,0.5))
        self.assertEquals(1,len(p.commands))
        self.assert_("ColorMaterial" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testFrame(self):
        p=Paint3DRecorder()
        p.frame()
        self.assertEquals(1,len(p.commands))
        self.assert_("Frame" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testAmbientLight(self):
        p=Paint3DRecorder()
        p.ambientLight(Vector(0.3,0.3,0.3))
        self.assertEquals(1,len(p.commands))
        self.assert_("AmbientLight" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testBackground(self):
        p=Paint3DRecorder()
        p.background(Vector(0,0,0))
        self.assertEquals(1,len(p.commands))
        self.assert_("Background" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testPointLight(self):
        p=Paint3DRecorder()
        p.pointLight(Vector(0,0,0), Vector(1,1,1))
        self.assertEquals(1,len(p.commands))
        self.assert_("PointLight" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testOrthographicCamera(self):
        p=Paint3DRecorder()
        p.orthographicCamera(Vector(0,0,0), Vector(0,0,1), Vector(1.33,0,0), Vector(0,1,0))
        self.assertEquals(1,len(p.commands))
        self.assert_("OrthographicCamera" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testPerspectiveCamera(self):
        p=Paint3DRecorder()
        p.perspectiveCamera(Vector(0,0,0), Vector(0,0,1), Vector(1.33,0,0), Vector(0,1,0))
        self.assertEquals(1,len(p.commands))
        self.assert_("PerspectiveCamera" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testSphere(self):
        p=Paint3DRecorder()
        p.sphere(Vector(0,0,0), 1.0, None)
        self.assertEquals(1,len(p.commands))
        self.assert_("Sphere" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testCylinder(self):
        p=Paint3DRecorder()
        p.cylinder(Vector(0,0,0), Vector(1,0,0), 1.0, None)
        self.assertEquals(1,len(p.commands))
        self.assert_("Cylinder" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testLine(self):
        p=Paint3DRecorder()
        p.line(Vector(0,0,0), Vector(1,0,0), 1.0, None)
        self.assertEquals(1,len(p.commands))
        self.assert_("Line" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testCone(self):
        p=Paint3DRecorder()
        p.cone(Vector(0,0,0), Vector(10,0,0), 1.0, None)
        self.assertEquals(1,len(p.commands))
        self.assert_("Cone" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testArrow(self):
        p=Paint3DRecorder()
        p.arrow(Vector(0,0,0), Vector(10,0,0), 0.5, 1.0, 2.0, None)
        self.assertEquals(1,len(p.commands))
        self.assert_("Arrow" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)
    def testMesh(self):
        p=Paint3DRecorder()
        p.mesh(None, None, None, None)
        self.assertEquals(1,len(p.commands))
        self.assert_("Mesh" in str(p.commands[0]))
        self.assertEquals("1",p.commands[0].name)


if __name__ == '__main__':
    unittest.main()
