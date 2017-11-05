from p4vasp.paint3d.data import *
from p4vasp.matrix import Vector

class Paint3DInterface:
    def __init__(self):
        self.parent=None
    def colorMaterial(self, color=None, name=None):
        return name
    def frame(self, name=None):
        return name
    def ambientLight(self, color=None, name=None):
        return name
    def background(self, color=None, name=None):
        return name
    def pointLight(self, position=None, color=None, name=None):
        return name
    def orthographicCamera(self, position=None, look_at=None, right=None, up=None, name=None):
        return name
    def perspectiveCamera(self, position=None, look_at=None, right=None, up=None, name=None):
        return name
    def sphere(self, position=None, radius=1.0, material=None, name=None):
        return name
    def cylinder(self, position1=None, position2=None, radius=1.0, material=None, name=None):
        return name
    def line(self, position1=None, position2=None, width=1.0, material=None, name=None):
        return name
    def cone(self, base_position=None, tip_position=None, radius=1.0, material=None, name=None):
        return name
    def arrow(self, from_position=None, to_position=None, radius=0.5, tip_radius=1.0, tip_length=2.0, material=None, name=None):
        return name
    def mesh(self, coordinates=None, normals=None, triangles=None, material=None, name=None):
        return name

    def write(self,f):
        pass

from exceptions import Exception
 
class Paint3DRecorder(Paint3DInterface):
    def __init__(self):
        Paint3DInterface.__init__(self)
        self.reset()
    def get(self,name):
        if self.dictionary.has_key(name):
            return self.dictionary[name]
        if self.parent is None:
            return None
        return self.parent.get(name)
    def reset(self):
        self.commands=[]
        self.dictionary={}
    def add(self,o,name=None):
        self.commands.append(o)
        if name is None:
            o.name=str(len(self.commands))
        else:
            o.name=name
        if self.dictionary.has_key(o.name):
            raise Exception("Attempt to redefine Paint3D object %s"%o.name)
        self.dictionary[o.name]=o
        o.parent=self
        return o
    def play(self,painter):
        for command in self.commands:
            command.call(painter)
    def colorMaterial(self, color=None, name=None):
        return self.add(ColorMaterial(color),name)
    def frame(self, name=None):
        return self.add(Frame(),name)
    def ambientLight(self, color=None, name=None):
        return self.add(AmbientLight(color),name)
    def background(self, color=None, name=None):
        return self.add(Background(color),name)
    def pointLight(self, position=None, color=None, name=None):
        return self.add(PointLight(position, color),name)
    def orthographicCamera(self, position=None, look_at=None, right=None, up=None, name=None):
        return self.add(OrthographicCamera(position, look_at, right, up),name)
    def perspectiveCamera(self, position=None, look_at=None, right=None, up=None, name=None):
        return self.add(PerspectiveCamera(position, look_at, right, up),name)
    def sphere(self, position=None, radius=1.0, material=None, name=None):
        return self.add(Sphere(position, radius, material),name)
    def cylinder(self, position1=None, position2=None, radius=1.0, material=None, name=None):
        return self.add(Cylinder(position1, position2, radius, material),name)
    def line(self, position1=None, position2=None, width=1.0, material=None, name=None):
        return self.add(Line(position1, position2, width, material),name)
    def cone(self, base_position=None, tip_position=None, radius=1.0, material=None, name=None):
        return self.add(Cone(base_position, tip_position, radius, material),name)
    def arrow(self, from_position=None, to_position=None, radius=0.5, tip_radius=1.0, tip_length=2.0, material=None, name=None):
        return self.add(Arrow(from_position, to_position, radius, tip_radius, tip_length, material),name)
    def mesh(self, coordinates=None, normals=None, triangles=None, material=None, name=None):
        return self.add(Mesh(coordinates, normals, triangles, material),name)

