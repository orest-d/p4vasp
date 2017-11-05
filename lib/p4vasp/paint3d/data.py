from p4vasp.matrix import Vector

class ColorMaterial:
    def __init__(self,color=None, name=None):
        self.color = color
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.colorMaterial(self.color, name=self.name)
    def clone(self):
        return ColorMaterial(self.color)
    def __str__(self):
        return "ColorMaterial(%s)"%(str(self.color))

class Frame:
    def __init__(self,name=None):
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.frame(name=self.name)
    def clone(self):
        return Frame()
    def __str__(self):
        return "Frame()"

class AmbientLight:
    def __init__(self,color=None, name=None):
        self.color = color
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.ambientLight(self.color, name=self.name)
    def clone(self):
        return AmbientLight(self.color)
    def __str__(self):
        return "AmbientLight(%s)"%(str(self.color))

class Background:
    def __init__(self,color=None, name=None):
        self.color = color
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.background(self.color, name=self.name)
    def clone(self):
        return Background(self.color)
    def __str__(self):
        return "Background(%s)"%(str(self.color))

class PointLight:
    def __init__(self,position=None, color=None, name=None):
        self.position = position
        self.color = color
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.pointLight(self.position, self.color, name=self.name)
    def clone(self):
        return PointLight(self.position, self.color)
    def __str__(self):
        return "PointLight(%s, %s)"%(str(self.position), str(self.color))

class OrthographicCamera:
    def __init__(self,position=None, look_at=None, right=None, up=None, name=None):
        self.position = position
        self.look_at = look_at
        self.right = right
        self.up = up
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.orthographicCamera(self.position, self.look_at, self.right, self.up, name=self.name)
    def clone(self):
        return OrthographicCamera(self.position, self.look_at, self.right, self.up)
    def __str__(self):
        return "OrthographicCamera(%s, %s, %s, %s)"%(str(self.position), str(self.look_at), str(self.right), str(self.up))

class PerspectiveCamera:
    def __init__(self,position=None, look_at=None, right=None, up=None, name=None):
        self.position = position
        self.look_at = look_at
        self.right = right
        self.up = up
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.perspectiveCamera(self.position, self.look_at, self.right, self.up, name=self.name)
    def clone(self):
        return PerspectiveCamera(self.position, self.look_at, self.right, self.up)
    def __str__(self):
        return "PerspectiveCamera(%s, %s, %s, %s)"%(str(self.position), str(self.look_at), str(self.right), str(self.up))

class Sphere:
    def __init__(self,position=None, radius=1.0, material=None, name=None):
        self.position = position
        self.radius = radius
        self.material = material
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.sphere(self.position, self.radius, self.material, name=self.name)
    def clone(self):
        return Sphere(self.position, self.radius, self.material)
    def __str__(self):
        return "Sphere(%s, %s, %s)"%(str(self.position), str(self.radius), str(self.material))

class Cylinder:
    def __init__(self,position1=None, position2=None, radius=1.0, material=None, name=None):
        self.position1 = position1
        self.position2 = position2
        self.radius = radius
        self.material = material
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.cylinder(self.position1, self.position2, self.radius, self.material, name=self.name)
    def clone(self):
        return Cylinder(self.position1, self.position2, self.radius, self.material)
    def __str__(self):
        return "Cylinder(%s, %s, %s, %s)"%(str(self.position1), str(self.position2), str(self.radius), str(self.material))

class Line:
    def __init__(self,position1=None, position2=None, width=1.0, material=None, name=None):
        self.position1 = position1
        self.position2 = position2
        self.width = width
        self.material = material
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.line(self.position1, self.position2, self.width, self.material, name=self.name)
    def clone(self):
        return Line(self.position1, self.position2, self.width, self.material)
    def __str__(self):
        return "Line(%s, %s, %s, %s)"%(str(self.position1), str(self.position2), str(self.width), str(self.material))

class Cone:
    def __init__(self,base_position=None, tip_position=None, radius=1.0, material=None, name=None):
        self.base_position = base_position
        self.tip_position = tip_position
        self.radius = radius
        self.material = material
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.cone(self.base_position, self.tip_position, self.radius, self.material, name=self.name)
    def clone(self):
        return Cone(self.base_position, self.tip_position, self.radius, self.material)
    def __str__(self):
        return "Cone(%s, %s, %s, %s)"%(str(self.base_position), str(self.tip_position), str(self.radius), str(self.material))

class Arrow:
    def __init__(self,from_position=None, to_position=None, radius=0.5, tip_radius=1.0, tip_length=2.0, material=None, name=None):
        self.from_position = from_position
        self.to_position = to_position
        self.radius = radius
        self.tip_radius = tip_radius
        self.tip_length = tip_length
        self.material = material
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.arrow(self.from_position, self.to_position, self.radius, self.tip_radius, self.tip_length, self.material, name=self.name)
    def clone(self):
        return Arrow(self.from_position, self.to_position, self.radius, self.tip_radius, self.tip_length, self.material)
    def __str__(self):
        return "Arrow(%s, %s, %s, %s, %s, %s)"%(str(self.from_position), str(self.to_position), str(self.radius), str(self.tip_radius), str(self.tip_length), str(self.material))

class Mesh:
    def __init__(self,coordinates=None, normals=None, triangles=None, material=None, name=None):
        self.coordinates = coordinates
        self.normals = normals
        self.triangles = triangles
        self.material = material
        if name is None:
            self.name=str(id(self))
        else:
            self.name=name
    def call(self,painter):
        painter.mesh(self.coordinates, self.normals, self.triangles, self.material, name=self.name)
    def clone(self):
        return Mesh(self.coordinates, self.normals, self.triangles, self.material)
    def __str__(self):
        return "Mesh(%s, %s, %s, %s)"%(str(self.coordinates), str(self.normals), str(self.triangles), str(self.material))

