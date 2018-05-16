#!/usr/bin/python2
import unittest
from p4vasp.paint3d.PovrayPaint3D import *
from p4vasp.matrix import Vector
from StringIO import StringIO
from p4vasp.paint3d.MeshTools import sphereMesh

class TestPovrayPaint3D(unittest.TestCase):
    def testColorMaterial(self):
        p=PovrayPaint3D()
        position=Vector(2,3,4)
        p.colorMaterial(color=Vector(1,0,0),name="colmat")

        f=StringIO()
        p.write(f)
        self.assert_("< 1.0" in f.getvalue())
        self.assert_("colmat" in f.getvalue())
        f.close()

    def testSphere(self):
        p=PovrayPaint3D()
        position=Vector(2,3,4)
        p.colorMaterial(Vector(1,0,0),name="colmat")

        p.sphere(position,4,material="colmat")

        f=StringIO()
        p.write(f)
        self.assert_("sphere" in f.getvalue())
        self.assert_("< 2.0" in f.getvalue())
        self.assert_("colmat" in f.getvalue())
        self.assert_("color rgb < 1.0" in f.getvalue())
        f.close()

    def testCylinder(self):
        f=StringIO()
        p=PovrayPaint3D()
        position1=Vector(2,3,4)
        position2=Vector(4,5,6)
        p.colorMaterial(Vector(1,0,0),name="colmat")

        p.cylinder(position1,position2,7,material="colmat")

        p.write(f)
        self.assert_("cylinder" in f.getvalue())
        self.assert_("< 2.0" in f.getvalue())
        self.assert_("< 4.0" in f.getvalue())
        self.assert_("colmat" in f.getvalue())
        self.assert_("color rgb < 1.0" in f.getvalue())
        f.close()

    def testCone(self):
        f=StringIO()
        p=PovrayPaint3D()
        position1=Vector(2,3,4)
        position2=Vector(4,5,6)
        p.colorMaterial(Vector(1,0,0),name="colmat")

        p.cone(position1,position2,7,material="colmat")

        p.write(f)
        self.assert_("cone" in f.getvalue())
        self.assert_("< 2.0" in f.getvalue())
        self.assert_("< 4.0" in f.getvalue())
        self.assert_("colmat" in f.getvalue())
        self.assert_("color rgb < 1.0" in f.getvalue())
        f.close()

    def testLine(self):
        f=StringIO()
        p=PovrayPaint3D()
        position1=Vector(2,3,4)
        position2=Vector(4,5,6)
        p.colorMaterial(Vector(1,0,0),name="colmat")

        p.line(position1,position2,7,material="colmat")

        p.write(f)
        self.assert_("cylinder" in f.getvalue())
        self.assert_("< 2.0" in f.getvalue())
        self.assert_("< 4.0" in f.getvalue())
        self.assert_("colmat" in f.getvalue())
        self.assert_("color rgb < 1.0" in f.getvalue())
        f.close()

    def testPerspectiveCamera(self):
        p=PovrayPaint3D()
        camera_position=Vector(2,3,4)
        look_at=Vector(4,5,6)
        right=Vector(-1,0,0)
        up=Vector(0,1,0)

        p.perspectiveCamera(camera_position,look_at,right,up)

        f=StringIO()
        p.write(f)
        self.assert_("camera" in f.getvalue())
        self.assert_("< 2.0" in f.getvalue())
        self.assert_("< 4.0" in f.getvalue())
        self.assert_("perspective" in f.getvalue())
        f.close()

    def testOrthographicCamera(self):
        p=PovrayPaint3D()
        camera_position=Vector(2,3,4)
        look_at=Vector(4,5,6)
        right=Vector(-1,0,0)
        up=Vector(0,1,0)

        p.orthographicCamera(camera_position,look_at,right,up)

        f=StringIO()
        p.write(f)
        self.assert_("camera" in f.getvalue())
        self.assert_("< 2.0" in f.getvalue())
        self.assert_("< 4.0" in f.getvalue())
        self.assert_("orthographic" in f.getvalue())
        f.close()

    def testAmbientLight(self):
        p=PovrayPaint3D()

        p.ambientLight(Vector(1,0.5,0))

        f=StringIO()
        p.write(f)
        self.assert_("ambient_light" in f.getvalue())
        self.assert_("color rgb < 1.0" in f.getvalue())
        f.close()

    def testBackground(self):
        p=PovrayPaint3D()

        p.background(Vector(1,0.5,0))

        f=StringIO()
        p.write(f)
        self.assert_("background" in f.getvalue())
        self.assert_("color rgb < 1.0" in f.getvalue())
        f.close()

    def testPointLight(self):
        p=PovrayPaint3D()

        p.pointLight(Vector(2,3,4), Vector(1,1,1))

        f=StringIO()
        p.write(f)
        self.assert_("light_source" in f.getvalue())
        self.assert_("< 2.0" in f.getvalue())
        self.assert_("rgb < 1.0" in f.getvalue())
        f.close()

    def testFrame(self):
        p=PovrayPaint3D()
        frame=p.frame()

    def testMesh(self):
        p=PovrayPaint3D()
        coordinates,normals,triangles=sphereMesh(6)
        f=StringIO()
        p.mesh(coordinates,normals,triangles)
        p.write(f)
        self.assert_("mesh" in f.getvalue())
        self.assert_("smooth_triangle" in f.getvalue())
        f.close()
       
if __name__ == '__main__':
    unittest.main()
