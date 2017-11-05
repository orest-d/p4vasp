from p4vasp.matrix import Vector
from p4vasp.paint3d.Paint3DInterface import *
from p4vasp.paint3d.data import Frame
from p4vasp.paint3d.MeshTools import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import *
import sys

class BasicOpenGLPaint3D(Paint3DInterface):
    lights=[GL_LIGHT0,GL_LIGHT1,GL_LIGHT2,GL_LIGHT3,GL_LIGHT4,GL_LIGHT5,GL_LIGHT6,GL_LIGHT7]
    n=16
    def __init__(self):
        Paint3DInterface.__init__(self)
        self.enable_light=0
        self.ambient_light=(0,0,0)
        self.materials={}
        self.quadratic = gluNewQuadric()

    def orthographicCamera(self, position, look_at, right, up, name=None):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-right.length(),right.length(),-up.length(),up.length(),-100,100)
        z=Vector(0.0,0.0,1.0)
        d=(look_at-position).normal()
        axis=z.cross(d)
        if axis.length()>0.0000001:
            axis=axis.normal()
            glRotatef(z*d,axis[0],axis[1],axis[2])
        glTranslatef(-position[0],-position[1],-position[2])
        glMatrixMode(GL_MODELVIEW)

    def perspectiveCamera(self, position, look_at, right, up, name=None):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        center=(look_at*0.1+position*0.9)
        gluLookAt(position[0],position[1],position[2],center[0],center[1],center[2],up[0],up[1],up[2])
        glMatrixMode(GL_MODELVIEW)

    def ambientLight(self, color, name=None):
        self.ambient_light=color

    def background(self, color, name=None):
        glClearColor(color[0],color[1],color[2],0.0)
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def pointLight(self, position, color, name=None):
        light=self.lights[self.enable_light]
        self.enable_light+=1
        glLightfv (light, GL_POSITION, (position[0],position[1],position[2]))
        glLightfv (light, GL_DIFFUSE, (color[0],color[1],color[2]))
        glEnable (light)
        glEnable (GL_LIGHTING)
        
    def colorMaterial(self, color=None, name=None):
        glColorMaterial (GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable (GL_COLOR_MATERIAL)
        glColor3f(color[0],color[1],color[2])
        self.materials[name]=color
    def sphere(self,position,radius=1.0,material=None, name=None):
        if material is not None:
            color=self.materials[material]
            glColor3f(color[0],color[1],color[2])
        glPushMatrix()
        glTranslatef(position[0],position[1],position[2])
        gluSphere(self.quadratic,radius,self.n,self.n)
        glPopMatrix()

    def cylinder(self,position1, position2, radius=1.0, material=None, name=None):
        if material is not None:
            color=self.materials[material]
            glColor3f(color[0],color[1],color[2])
        z=Vector(0.0,0.0,1.0)
        d=position2-position1
        if d.length()<1e-10:
            return
        d=d.normal()
        axis=z.cross(d)
        glPushMatrix()
        glTranslatef(position1[0],position1[1],position1[2])
        if axis.length()>0.0000001:
            axis=axis.normal()
            glRotatef(acos(z*d)*180/pi,axis[0],axis[1],axis[2])
        else:
            if d[2]<0:
                glRotatef(180,1,0,0)
        gluCylinder(self.quadratic,radius,radius,(position2-position1).length(),self.n,2)
        glPopMatrix()

    def line(self,position1,position2,width=1, material=None, name=None):
        self.cylinder(position1,position2,width*0.05,material)
    def cone(self,position1,position2,radius=1, material=None, name=None):
        if material is not None:
            color=self.materials[material]
            glColor3f(color[0],color[1],color[2])
        z=Vector(0.0,0.0,1.0)
        d=position2-position1
        if d.length()<1e-10:
            return
        d=d.normal()
        axis=z.cross(d)
        glPushMatrix()
        glTranslatef(position1[0],position1[1],position1[2])
        if axis.length()>0.0000001:
            axis=axis.normal()
            glRotatef(acos(z*d)*180/pi,axis[0],axis[1],axis[2])
        else:
            if d[2]<0:
                glRotatef(180,1,0,0)
        gluCylinder(self.quadratic,radius,0.0,(position2-position1).length(),self.n,2)
        glPopMatrix()
    def arrow(self, from_position=None, to_position=None, radius=0.5, tip_radius=1.0, tip_length=2.0, material=None, name=None):
        d=to_position-from_position
        n=d.normal()
        dl=d.length()
        tip_position=from_position+n*(dl-tip_length)
        self.cylinder(from_position, tip_position,radius,material)
        self.cone(tip_position, to_position,tip_radius,material)
    def mesh(self, coordinates=None, normals=None, triangles=None, material=None, name=None):
        if material is not None:
            color=self.materials[material]
            glColor3f(color[0],color[1],color[2])
        glBegin(GL_TRIANGLES)
        for t in triangles:
            for i in t:
                glNormal3f(normals[i][0],normals[i][1],normals[i][2])
                glVertex3f(coordinates[i][0],coordinates[i][1],coordinates[i][2])
        glEnd()

    def write(self,f):
        pass
    def exportTo(self,path):
        pass

class OpenGLPaint3DFrame(Frame,Paint3DRecorder):
    def __init__(self,clock,name=None):
        Frame.__init__(self,name)
        Paint3DRecorder.__init__(self)
        self.clock=clock

class OpenGLPaint3DRecorder(Paint3DRecorder):
    def __init__(self):
        Paint3DRecorder.__init__(self)
        self.clock=0
        self.frames=[]
    def frame(self, name=None):
        clock=self.clock
        self.clock+=1
        f=self.add(OpenGLPaint3DFrame(clock),name)
        self.frames.append(f)
        return f

class GLUTPaint3D(OpenGLPaint3DRecorder):
    def __init__(self):
        OpenGLPaint3DRecorder.__init__(self)
        self.showframe=0
        self.n=16
        self.lastx=0
        self.lasty=0
        self.zoom=1.0
    def mouseFunc(self,button,state,x,y):
        if button==3 and state==1:
            self.zoom*=1.1
            glutPostRedisplay()
        if button==4 and state==1:
            self.zoom/=1.1
            glutPostRedisplay()
    def draw(self):
        glViewport(0, 0, self.width, self.height)
        glMatrixMode (GL_PROJECTION)
        # roughly, measured in centimeters */
        glLoadIdentity()
        glOrtho(-self.width*0.01,self.width*0.01,-self.height*0.01,self.height*0.01,-100,100)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glScale(self.zoom,self.zoom,self.zoom)
        painter=BasicOpenGLPaint3D()
        painter.n=self.n
        glRotatef(self.lastx, 0.0, 1.0, 0.0)
        glRotatef(self.lasty, 1.0, 0.0, 0.0)
#        glTranslatef(0.0,0.0,-80.0)

        for command in self.commands:
            if isinstance(command,Frame):
                continue
            if isinstance(command,PerspectiveCamera):
                continue
            if isinstance(command,OrthographicCamera):
                continue
            command.call(painter)
        if len(self.frames)>self.showframe:
            for command in self.frames[self.showframe].commands:
                if isinstance(command,PerspectiveCamera):
                    continue
                if isinstance(command,OrthographicCamera):
                    continue
                command.call(painter)
        glutSwapBuffers ()
    def keyPressed(self,*args):
        if args[0] == '\033':
            sys.exit()
        if args[0] == '+':
            self.showframe+=1
            if self.showframe>=len(self.frames):
                self.showframe=0
        if args[0] == '-':
            self.showframe-=1
            if self.showframe<0:
                self.showframe=len(self.frames)-1
        glutPostRedisplay()
    def mouseMotion(self, x, y):
        self.lastx = x
        self.lasty = y
        glutPostRedisplay()
    def resize(self,width, height):
        if height == 0:						# Prevent A Divide By Zero If The Window Is Too Small
	         height = 1
        self.width=width
        self.height=height
        glutPostRedisplay()

    def glutinit(self,name="Paint 3D",width=640,height=400):        
        glutInit(sys.argv)
        self.width=width
        self.height=height
        glutInitWindowSize(width, height)

        glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH | GLUT_MULTISAMPLE)
        glutCreateWindow(name)
        glClearDepth (1.0)
        glEnable (GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glClearColor (0.0, 0.0, 0.0, 0.0)
        glShadeModel (GL_SMOOTH)

        glutDisplayFunc(self.draw)
        glutMotionFunc(self.mouseMotion)
        glutMouseFunc(self.mouseFunc)
        glutKeyboardFunc(self.keyPressed)
        glutReshapeFunc(self.resize)

    def mainloop(self,name="Paint 3D",width=640,height=400):
        self.glutinit(name,width,height)
        glutMainLoop()
    def mainloopevent(self):
        glutMainLoopEvent()
