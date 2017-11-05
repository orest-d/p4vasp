from p4vasp.paint3d.Paint3DInterface import *
from p4vasp.paint3d.MeshTools import *
from math import *

class ColladaGeometriesPaint3D(Paint3DInterface):
    def __init__(self,f):
        self.f=f
    def ambientLight(self, name=None):
        pass
    def pointLight(self, position, color=Vector(1,1,1), name=None):
        pass
    def orthographicCamera(self, position, look_at, name=None):
        pass
    def perspectiveCamera(self, position, look_at, name=None):
        pass
    def sphere(self, position, radius=1.0, color=Vector(0,0,0), name=None):
        pass
    def cylinder(self, position1, position2, radius=1.0, color=Vector(0,0,0), name=None):
        pass
    def line(self, position1, position2, width=1.0, color=Vector(0,0,0), name=None):
        pass
    def cone(self, base_position, tip_position, radius=1.0, color=Vector(0,0,0), name=None):
        pass
    def arrow(self, from_position, to_position, radius=0.5, tip_radius=1.0, tip_length=2.0, color=Vector(0,0,0), name=None):
        pass
    def mesh(self, coordinates, normals, triangles, color=Vector(0,0,0), name=None):
        self.f.write("""    <geometry id="Mesh-%s-mesh" name="Mesh-%s">
          <mesh>
    """%(str(name),str(name)))
        self.f.write("""        <source id="Mesh-%s-mesh-positions">\n"""%(str(name)))
        self.f.write("""          <float_array id="Mesh-%s-mesh-positions-array" count="%d">"""%(str(name),len(coordinates)*3))
        for v in coordinates:
            self.f.write("%f %f %f "%(v[0],v[1],v[2]))
        self.f.write("""</float_array>\n""")
        self.f.write("""          <technique_common>
                <accessor source="#Mesh-%s-mesh-positions-array" count="%d" stride="3">
                  <param name="X" type="float"/>
                  <param name="Y" type="float"/>
                  <param name="Z" type="float"/>
                </accessor>
              </technique_common>
            </source>
    """%(str(name),len(coordinates)))
        self.f.write("""        <source id="Mesh-%s-mesh-normals">\n"""%(str(name)))
        self.f.write("""          <float_array id="Mesh-%s-mesh-normals-array" count="%d">"""%(str(name),len(normals)*3))
        for v in normals:
            self.f.write("%f %f %f "%(v[0],v[1],v[2]))
        self.f.write("""</float_array>\n""")

        self.f.write("""          <technique_common>
                <accessor source="#Mesh-%s-mesh-normals-array" count="6" stride="3">
                  <param name="X" type="float"/>
                  <param name="Y" type="float"/>
                  <param name="Z" type="float"/>
                </accessor>
              </technique_common>
            </source>
    """%(str(name)))
        self.f.write("""        <vertices id="Mesh-%s-mesh-vertices">
              <input semantic="POSITION" source="#Mesh-%s-mesh-positions"/>
            </vertices>
    """%(str(name),str(name)))
        self.f.write("""        <polylist material="Material1" count="6">
              <input semantic="VERTEX" source="#Mesh-%s-mesh-vertices" offset="0"/>
              <input semantic="NORMAL" source="#Mesh-%s-mesh-normals" offset="1"/>
    """%(str(name),str(name)))

        self.f.write("""          <vcount>%s</vcount>\n"""%(" ".join(map(lambda x:str(len(x)),triangles))))
        self.f.write("""          <p>""")
        for v in triangles:
            for w in v:
                self.f.write("%d "%w)
                self.f.write("%d "%w)
        self.f.write("""</p>\n""")
        self.f.write("""        </polylist>\n""")
        self.f.write("""      </mesh>
          <extra><technique profile="MAYA"><double_sided>1</double_sided></technique></extra>
        </geometry>
    """)

class ColladaEffectsPaint3D(Paint3DInterface):
    def __init__(self,f):
        self.f=f
    def defineColor(self,color,name):
        self.f.write("""    <effect id="Material_%s-effect">
          <profile_COMMON>
            <technique sid="common">
              <phong>
                <emission>
                  <color>0 0 0 1</color>
                </emission>
                <ambient>
                  <color>0 0 0 1</color>
                </ambient>
                <diffuse>
                  <color>0.8 %f %f %f</color>
                </diffuse>
                <specular>
                  <color>0.5 0.5 0.5 1</color>
                </specular>
                <shininess>
                  <float>50</float>
                </shininess>
                <index_of_refraction>
                  <float>1</float>
                </index_of_refraction>
              </phong>
            </technique>
            <extra>
              <technique profile="GOOGLEEARTH">
                <double_sided>1</double_sided>
              </technique>
            </extra>
          </profile_COMMON>
          <extra><technique profile="MAX3D"><double_sided>1</double_sided></technique></extra>
        </effect>
    """%(str(name),color[0],color[1],color[2]))
    def sphere(self, position, radius=1.0, color=Vector(0,0,0), name=None):
        self.defineColor(color,name)
    def cylinder(self, position1, position2, radius=1.0, color=Vector(0,0,0), name=None):
        self.defineColor(color,name)
    def line(self, position1, position2, width=1.0, color=Vector(0,0,0), name=None):
        self.defineColor(color,name)
    def cone(self, base_position, tip_position, radius=1.0, color=Vector(0,0,0), name=None):
        self.defineColor(color,name)
    def arrow(self, from_position, to_position, radius=0.5, tip_radius=1.0, tip_length=2.0, color=Vector(0,0,0), name=None):
        self.defineColor(color,name)
    def mesh(self, coordinates, normals, triangles, color=Vector(0,0,0), name=None):
        self.defineColor(color,name)

class ColladaMaterialsPaint3D(ColladaEffectsPaint3D):
    def defineColor(self,color,name):
        self.f.write("""<material id="Material_%s-material" name="Material-%s">
          <instance_effect url="#Material_%s-effect"/>
        </material>
    """%(str(name),str(name),str(name)))

class ColladaScenePaint3D(Paint3DInterface):
    def __init__(self,f):
        self.f=f
    def ambientLight(self, name=None):
        pass
    def pointLight(self, position, color=Vector(1,1,1), name=None):
        self.f.write("""      <node id="Lamp" type="NODE">
            <translate sid="location">4.076245 1.005454 5.903862</translate>
            <rotate sid="rotationZ">0 0 1 106.9363</rotate>
            <rotate sid="rotationY">0 1 0 3.163708</rotate>
            <rotate sid="rotationX">1 0 0 37.26105</rotate>
            <scale sid="scale">1 1 1</scale>
            <instance_light url="#Lamp-light"/>
          </node>
    """)
    def orthographicCamera(self, position, look_at, name=None):
        self.f.write("""      <node id="Camera" type="NODE">
            <translate sid="location">7.481132 -6.50764 5.343665</translate>
            <rotate sid="rotationZ">0 0 1 46.69195</rotate>
            <rotate sid="rotationY">0 1 0 0.619768</rotate>
            <rotate sid="rotationX">1 0 0 63.5593</rotate>
            <scale sid="scale">1 1 1</scale>
            <instance_camera url="#Camera-camera"/>
          </node>
    """)
    def perspectiveCamera(self, position, look_at, name=None):
        self.f.write("""      <node id="Camera" type="NODE">
            <translate sid="location">7.481132 -6.50764 5.343665</translate>
            <rotate sid="rotationZ">0 0 1 46.69195</rotate>
            <rotate sid="rotationY">0 1 0 0.619768</rotate>
            <rotate sid="rotationX">1 0 0 63.5593</rotate>
            <scale sid="scale">1 1 1</scale>
            <instance_camera url="#Camera-camera"/>
          </node>
    """)
    def sphere(self, position, radius=1.0, color=Vector(0,0,0), name=None):
        self.f.write("""      <node id="Sphere_%s" type="NODE">
            <translate sid="location">%f %f %f</translate>
            <rotate sid="rotationZ">0 0 1 0</rotate>
            <rotate sid="rotationY">0 1 0 0</rotate>
            <rotate sid="rotationX">1 0 0 0</rotate>
            <scale sid="scale">%f %f %f</scale>
            <instance_geometry url="#Mesh-Sphere-mesh">
              <bind_material>
                <technique_common>
                  <instance_material symbol="Material%s" target="#Material_%s-material"/>
                </technique_common>
              </bind_material>
            </instance_geometry>
          </node>
    """%(str(name),position[0],position[1],position[2],radius,radius,radius,str(name),str(name)))
    def cylinder(self, position1, position2, radius=1.0, color=Vector(0,0,0), name=None):
        v=Vector(position2)-Vector(position1)
        up=Vector(0,0,1)
        a=up.angle(v)
        tollerance=1e-8
        if a<tollerance or a>(pi-tollerance):
            axis=up
            angle=0
        else:
            axis=v.cross(up).normal()
            angle=180*up.angle(v)/pi
        self.f.write("""      <node id="Cylinder_%s" type="NODE">\n"""%str(name))
        self.f.write("""        <translate sid="location">%f %f %f</translate>\n"""%(
          position1[0],position1[1],position1[2]))
        self.f.write("""        <rotate>%f %f %f %f</rotate>\n"""%(axis[0],axis[1],axis[2],-angle))
        self.f.write("""        <scale sid="scale">%f %f %f</scale>\n"""%(radius,radius,v.length()))
        self.f.write("""        <instance_geometry url="#Mesh-Cylinder-mesh">
              <bind_material>
                <technique_common>
                  <instance_material symbol="Material%s" target="#Material_%s-material"/>
                </technique_common>
              </bind_material>
            </instance_geometry>
          </node>
    """%(str(name),str(name)))
    def line(self, position1, position2, width=1.0, color=Vector(0,0,0), name=None):
        self.cylinder(position1,position2,0.05*width,color,name)
    def cone(self, base_position, tip_position, radius=1.0, color=Vector(0,0,0), name=None):
        v=Vector(tip_position)-Vector(base_position)
        up=Vector(0,0,1)
        axis=v.cross(up).normal()
        angle=180*up.angle(v)/pi
        self.f.write("""      <node id="Cone_%s" type="NODE">\n"""%str(name))
        self.f.write("""        <translate sid="location">%f %f %f</translate>\n"""%(
          base_position[0],base_position[1],base_position[2]))
        self.f.write("""        <rotate>%f %f %f %f</rotate>\n"""%(axis[0],axis[1],axis[2],-angle))
        self.f.write("""        <scale sid="scale">%f %f %f</scale>\n"""%(radius,radius,v.length()))
        self.f.write("""        <instance_geometry url="#Mesh-Cone-mesh">
              <bind_material>
                <technique_common>
                  <instance_material symbol="Material%s" target="#Material_%s-material"/>
                </technique_common>
              </bind_material>
            </instance_geometry>
          </node>
    """%(str(name),str(name)))
    def arrow(self, from_position, to_position, radius=0.5, tip_radius=1.0, tip_length=2.0, color=Vector(0,0,0), name=None):
        d=Vector(to_position)-Vector(from_position)
        n=d.normal()
        l=radius*tip_length/tip_radius
        self.cone(to_position-tip_length*n,to_position,tip_radius,color,name)
        self.cylinder(from_position,from_position+n*(d.length()-l),radius,color,name)

    def mesh(self, coordinates, normals, triangles, color=Vector(0,0,0), name=None):
        self.f.write("""      <node id="Mesh_%s" type="NODE">
            <translate sid="location">0 0 0</translate>
            <rotate sid="rotationZ">0 0 1 0</rotate>
            <rotate sid="rotationY">0 1 0 0</rotate>
            <rotate sid="rotationX">1 0 0 0</rotate>
            <scale sid="scale">1 1 1</scale>
            <instance_geometry url="#Mesh-%s-mesh">
              <bind_material>
                <technique_common>
                  <instance_material symbol="Material1" target="#Material_%s-material"/>
                </technique_common>
              </bind_material>
            </instance_geometry>
          </node>
    """%(str(name),str(name),str(name)))

class ColladaPaint3D(Paint3DRecorder):
    def __init__(self,n=20):
        Paint3DRecorder.__init__(self)
        self.n=n
    def write(self,f):
        f.write("""<?xml version="1.0" encoding="utf-8"?>
    <COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">
      <asset>
        <contributor>
          <author>p4vasp user</author>
          <authoring_tool>p4vasp</authoring_tool>
        </contributor>
        <created>2012-04-01T20:33:51</created>
        <modified>2012-04-01T20:33:51</modified>
        <unit name="meter" meter="1"/>
        <up_axis>Z_UP</up_axis>
      </asset>
      <library_cameras>
        <camera id="Camera-camera" name="Camera">
          <optics>
            <technique_common>
              <perspective>
                <xfov sid="xfov">49.13434</xfov>
                <aspect_ratio>1.777778</aspect_ratio>
                <znear sid="znear">0.1</znear>
                <zfar sid="zfar">100</zfar>
              </perspective>
            </technique_common>
          </optics>
        </camera>
      </library_cameras>
      <library_lights>
        <light id="Lamp-light" name="Lamp">
          <technique_common>
            <point>
              <color sid="color">1 1 1</color>
              <constant_attenuation>1</constant_attenuation>
              <linear_attenuation>0</linear_attenuation>
              <quadratic_attenuation>0.00111109</quadratic_attenuation>
            </point>
          </technique_common>
          <extra>
            <technique profile="blender">
              <adapt_thresh>0.000999987</adapt_thresh>
              <area_shape>0</area_shape>
              <area_size>1</area_size>
              <area_sizey>1</area_sizey>
              <area_sizez>1</area_sizez>
              <atm_distance_factor>1</atm_distance_factor>
              <atm_extinction_factor>1</atm_extinction_factor>
              <atm_turbidity>2</atm_turbidity>
              <att1>0</att1>
              <att2>1</att2>
              <backscattered_light>1</backscattered_light>
              <bias>1</bias>
              <blue>1</blue>
              <buffers>1</buffers>
              <bufflag>0</bufflag>
              <bufsize>2880</bufsize>
              <buftype>2</buftype>
              <clipend>30.002</clipend>
              <clipsta>1.000799</clipsta>
              <compressthresh>0.04999995</compressthresh>
              <dist sid="blender_dist">29.99998</dist>
              <energy sid="blender_energy">1</energy>
              <falloff_type>2</falloff_type>
              <filtertype>0</filtertype>
              <flag>0</flag>
              <gamma sid="blender_gamma">1</gamma>
              <green>1</green>
              <halo_intensity sid="blnder_halo_intensity">1</halo_intensity>
              <horizon_brightness>1</horizon_brightness>
              <mode>8192</mode>
              <ray_samp>1</ray_samp>
              <ray_samp_method>1</ray_samp_method>
              <ray_samp_type>0</ray_samp_type>
              <ray_sampy>1</ray_sampy>
              <ray_sampz>1</ray_sampz>
              <red>1</red>
              <samp>3</samp>
              <shadhalostep>0</shadhalostep>
              <shadow_b sid="blender_shadow_b">0</shadow_b>
              <shadow_g sid="blender_shadow_g">0</shadow_g>
              <shadow_r sid="blender_shadow_r">0</shadow_r>
              <shadspotsize>45</shadspotsize>
              <sky_colorspace>0</sky_colorspace>
              <sky_exposure>1</sky_exposure>
              <skyblendfac>1</skyblendfac>
              <skyblendtype>1</skyblendtype>
              <soft>3</soft>
              <spotblend>0.15</spotblend>
              <spotsize>75</spotsize>
              <spread>1</spread>
              <sun_brightness>1</sun_brightness>
              <sun_effect_type>0</sun_effect_type>
              <sun_intensity>1</sun_intensity>
              <sun_size>1</sun_size>
              <type>0</type>
            </technique>
          </extra>
        </light>
      </library_lights>
    """)
        f.write("""  <library_effects>\n""")
        self.play(ColladaEffectsPaint3D(f))
        f.write("""  </library_effects>\n""")
        f.write("""  <library_materials>\n""")
        self.play(ColladaMaterialsPaint3D(f))
        f.write("""  </library_materials>\n""")

        f.write("  <library_geometries>\n")
        p=ColladaGeometriesPaint3D(f)
        coordinates,normals,triangles=coneMesh(self.n)
        p.mesh(coordinates,normals,triangles,name="Cone")
        coordinates,normals,triangles=sphereMesh(self.n)
        p.mesh(coordinates,normals,triangles,name="Sphere")
        coordinates,normals,triangles=cylinderMesh(self.n)
        p.mesh(coordinates,normals,triangles,name="Cylinder")
        self.play(p)
        f.write("  </library_geometries>\n")
        f.write("""  <library_visual_scenes>
        <visual_scene id="Scene" name="Scene">
    """)
        self.play(ColladaScenePaint3D(f))
        f.write("""    </visual_scene>
      </library_visual_scenes>
    """)
        f.write("""  <scene>
        <instance_visual_scene url="#Scene"/>
      </scene>
    </COLLADA>""")

if __name__ == '__main__':
    from math import *
    from MeshTools import *
    p=ColladaPaint3D()

    p.ambientLight((0.1,0.1,1))
    p.perspectiveCamera((0.2,0.2,0),(5,0,0))
#  p.pointLight((3,1,1),(10.0,0.8,0.8))
#  p.sphere((5,0,0),0.2,color=(0,0,1))
#  p.sphere((5,1,0),0.15,color=(1,0,1))
#  p.cylinder((5,0,0),(5,1,0),0.1,color=(1,1,1))
#  p.cone((5,0,0),(5,1,0),0.2,color=(0,1,0))

    def fnc(u,v):
        return sin(u)*sin(v)

    def cn(f,u,v,d=0.0001):
        c=Vector(u,v,f(u,v))
        v1=Vector(u+d,v,f(u+d,v))-c
        v2=Vector(u,v+d,f(u,v+d))-c
        n=-v1.cross(v2).normal()
        return c,n

    coordinates=[]
    normals=[]
    l=[]
    ii=0
    du=0.07
    dv=0.07
    for i in range(10):
        for j in range(10):
            u=3+i*du
            v=-1+j*dv
            c,n=cn(fnc,u,v)
            coordinates.append(c)
            normals.append(n)
            c,n=cn(fnc,u+du*0.9,v)
            coordinates.append(c)
            normals.append(n)
            c,n=cn(fnc,u,v+dv*0.9)
            coordinates.append(c)
            normals.append(n)
            c,n=cn(fnc,u+du*0.9,v+dv*0.9)
            coordinates.append(c)
            normals.append(n)
            l.append([ii,ii+1,ii+2])
            l.append([ii+1,ii+3,ii+2])
            ii+=4

    p.mesh(coordinates,normals,l,(0,1,0.5))
    p.mesh([
      Vector(0,0,0),Vector(1,0,0),Vector(0,1,0),
      Vector(0,0,1),Vector(1,0,1),Vector(0,1,1)],
     [Vector(0,0,1),Vector(0,0,1),Vector(0,0,1),
      Vector(0,0,1),Vector(0,0,1),Vector(0,0,1),
      Vector(0,1,0),Vector(0,1,0),Vector(0,1,0)
     ],
    [[0,1,2],[3,4,5],[0,1,3]])
#  coordinates,normals,triangles=cylinderMesh(10)
#  p.mesh(coordinates,normals,triangles,"c")
#  coordinates,normals,triangles=coneMesh(10)
#  p.mesh(coordinates,normals,triangles,"s")
    p.sphere(Vector(1,0,0),0.5)
    p.sphere(Vector(1,1,0),0.5)
    p.sphere(Vector(0,0,1),1.0)
    p.write(open("test.dae","wb"))
