from p4vasp.matrix import Vector
from p4vasp.paint3d.Paint3DInterface import *
from p4vasp.paint3d.data import Frame
from StringIO import StringIO
import os.path

class PovrayPaint3D(Paint3DInterface):
    def __init__(self):
        Paint3DInterface.__init__(self)
        self.f=StringIO()
    def orthographicCamera(self, position, look_at, right, up, name=None):
        if right[0]>0:
            right=right*-1
        self.f.write("""camera{
  orthographic
  location %s
  look_at  %s
  right    %s
  up       %s
  sky      %s
}

"""%(self.vec(position),self.vec(look_at),self.vec(right),self.vec(up),self.vec(up)))

    def perspectiveCamera(self, position, look_at, right, up, name=None):
        if right[0]>0:
            right=right*-1
        self.f.write("""camera{
  perspective
  location %s
  look_at  %s
  right    %s
  up       %s
  sky      %s
}

"""%(self.vec(position),self.vec(look_at),self.vec(right),self.vec(up),self.vec(up)))

    def ambientLight(self, color, name=None):
        self.f.write("""global_settings{
  ambient_light %s
}

"""%(self.colorvec(color)))


    def background(self, color, name=None):
        self.f.write("""background{%s}

"""%(self.colorvec(color)))

    def pointLight(self, position, color, name=None):
        self.f.write("""light_source{
  %s, rgb %s shadowless
}

"""%(self.vec(position),self.vec(color)))
    def vec(self,v):
        return "< %f, %f, %f >"%(v[0],v[1],v[2])
    def colorvec(self,v):
        return "color rgb < %f, %f, %f >"%(v[0],v[1],v[2])
    def colorMaterial(self, color=None, name=None):
        self.f.write("""#declare %s = texture{
  pigment{ %s }
  finish{ ambient 1 phong 0.9 }
}

"""%(str(name),self.colorvec(color)))
    
    def materialRef(self,material):
        if material is None:
            return ""
        else:
            return "texture{ %s }"%str(material)

    def sphere(self,position,radius=1.0,material=None, name=None):
        if material is None:
            m=""
        else:
            m="texture{ %s }"%str(material)

        self.f.write("""sphere{
  %s, %f
  %s
}

"""%(self.vec(position),radius,self.materialRef(material)))
    def cylinder(self,position1, position2, radius=1.0, material=None, name=None):
        self.f.write("""cylinder{
  %s, %s, %f
  %s
}

"""%(self.vec(position1),self.vec(position2),radius,self.materialRef(material)))
    def line(self,position1,position2,width=1, material=None, name=None):
        self.cylinder(position1,position2,width*0.05,material)
    def cone(self,position1,position2,radius=1, material=None, name=None):
        self.f.write("""cone{
  %s, %f, %s, %f
  %s
}

"""%(self.vec(position1),radius, self.vec(position2),0.0,self.materialRef(material)))
    def arrow(self, from_position=None, to_position=None, radius=0.5, tip_radius=1.0, tip_length=2.0, material=None, name=None):
        d=to_position-from_position
        n=d.normal()
        dl=d.length()
        tip_position=from_position+n*(dl-tip_length)
        self.cylinder(from_position, tip_position,radius,material)
        self.cone(tip_position, to_position,tip_radius,material)
    def mesh(self, coordinates=None, normals=None, triangles=None, material=None, name=None):
        self.f.write("mesh{\n")
        for i1,i2,i3 in triangles:
            self.f.write("  smooth_triangle{\n")
            self.f.write("    %s, %s,\n"%(self.vec(coordinates[i1]),self.vec(normals[i1])))
            self.f.write("    %s, %s,\n"%(self.vec(coordinates[i2]),self.vec(normals[i2])))
            self.f.write("    %s, %s\n"%(self.vec(coordinates[i3]),self.vec(normals[i3])))
            self.f.write("  }\n")
        self.f.write("  %s\n}\n"%self.materialRef(material))

    def write(self,f):
        f.write(self.f.getvalue())
    def exportTo(self,path):
        f=open(path,"w")
        self.write(f)
        f.close()

class PovrayPaint3DFrame(Frame,Paint3DRecorder):
    def __init__(self,clock,name=None):
        Frame.__init__(self,name)
        Paint3DRecorder.__init__(self)
        self.clock=clock
    def write(self,f):
        f.write("#if ((clock>=%d)&(clock<%d))\n"%(self.clock,self.clock+1))
        paint=PovrayPaint3D()
        self.play(paint)
        paint.write(f)
        f.write("\n#end\n\n")

class ExtendedPovrayPaint3D(Paint3DRecorder):
    def __init__(self):
        Paint3DRecorder.__init__(self)
        self.clock=0
    def frame(self, name=None):
        clock=self.clock
        self.clock+=1
        return self.add(PovrayPaint3DFrame(clock),name)
    def exportTo(self,path):
        f=open(path,"w")
        self.write(f)
        f.close()
        folder,filename=os.path.split(path)
        v=filename.split(".")
        if len(v)<=1:
           ext=""
        else:
           filename=".".join(v[:-1])
           ext="."+v[-1]
        inifilename=filename+".ini"
        f=open(os.path.join(folder,inifilename),"w")
        f.write("""
Input_File_Name  = %s%s
Output_File_Name = %s.png
Antialias        = true
Jitter           = false
+W%d +H%d
"""%(filename,ext,filename,self.width,self.height))
        if self.clock>0:
           f.write("""Initial_Clock    = 0
Final_Clock      = %d
Initial_Frame    = 0
Final_Frame      = %d
"""%(int(self.clock),int(self.clock)))
 
    def write(self,f):
        paint=PovrayPaint3D()
        self.play(paint)
        paint.write(f)
        for command in self.commands:
            if isinstance(command,Frame):
                command.write(f)
