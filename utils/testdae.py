from p4vasp.paint3d.ColladaPaint3D import *

if __name__ == '__main__':
    from math import *
    p=ColladaPaint3D()

    p.ambientLight((0.1,0.1,1))
    p.perspectiveCamera((0.2,0.2,0),(5,0,0))
    p.pointLight((3,1,1),(10.0,0.8,0.8))
    p.sphere((5,0,0),0.2,color=(0,0,1))
    p.sphere((5,1,0),0.15,color=(1,0,1))
    #p.cylinder((5,0,0),(5,1,0),0.1,color=(1,1,1))
    p.cone((5,0,0),(5,1,0),0.2,color=(0,1,0))
    p.cone((5,1,0),(6,2,1),0.15,color=(0,1,0))

    l=[(0,0,0),(1,0,0),(1,1,0),(0,1,0)]
    w=Vector(0.5,0.5,1)*2
    v0=Vector(10,5,5)
    for i in range(len(l)):
        v1=Vector(l[i])*2
        v2=Vector(l[(i+1)%len(l)])*2
        p.cone(v0+v1,v0+v2,0.1,color=(0,1,0))
        p.arrow(v0+v1,v0+w,radius=0.1, tip_radius=0.2, tip_length=0.5,color=(0,1,0))


    p.write(open("test.dae","wb"))
