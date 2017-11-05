from p4vasp.export.Exporter import *
from p4vasp.util import getAtomtypes
from p4vasp.matrix import Matrix,Vector
from p4vasp import *
from p4vasp.isosurface import partialIsosurface,convertMeshFormat
import p4vasp.cStructure

class PaintExporter(Exporter):
    CELLMATERIAL       = "CellMaterial"
    BONDMATERIAL       = "BondMaterial"
    ARROWMATERIAL      = "ArrowMaterial"
    ELEMENTMATERIAL    = "ElementMaterial"
    ISOSURFACEMATERIAL = "IsosurfaceMaterial"

    def __init__(self,name,file_extension,paintCreator):
        self._name=name
        self._file_extension=file_extension
        self.paint=[paintCreator]
        self.atomtypes=getAtomtypes()
    def fileExtension(self):
        return self._file_extension
    def name(self):
        return self._name

    def transform(self,position,attributes):
        m=Matrix(attributes.rotmat)
        offset=Vector([m[0][3],m[1][3],m[2][3]])
        m=m.trans()
        return self.transformVector(position-offset,attributes)

    def transformVector(self,position,attributes):
        m=attributes.rotmat
        zoom=attributes.zoom
        R=Matrix(3,3)
        for i in (0,1,2):
          for j in (0,1,2):
            R.set(i,j,m.get(i,j))
        R=R.trans()
        return R*position*(1.0/zoom)

    def exportCamera(self,paint,attributes):
        if attributes.perspective:
            look_at=self.transform(Vector(0,0,0),attributes)
            camera_position=self.transform(Vector(0,0,20),attributes)
            right=self.transformVector(Vector(-attributes.width*0.004,0,0),attributes)
            up=self.transformVector(Vector(0,attributes.height*0.004,0),attributes)
            paint.perspectiveCamera(camera_position,look_at,right,up)
        else:
            look_at=self.transform(Vector(0,0,0),attributes)
            camera_position=self.transform(Vector(0,0,30),attributes)
            right=self.transformVector(Vector(-attributes.width*0.04,0,0),attributes)
            up=self.transformVector(Vector(0,attributes.height*0.04,0),attributes)
            paint.orthographicCamera(camera_position,look_at,right,up)

    def exportFrame(self,paint,structure,arrows,elementmaterials,attributes):
#        bondlist=self.createHalfBondsList(structure,attributes.bond_factor)
        bond_factor=attributes.bond_factor
        info=structure.info
        structure.setCarthesian()
        bondlist=[]
        for i in range(len(structure)):
            element_i=self.atomtypes.getRecordForElementSafe(info.getRecordForAtom(i).element,info.speciesIndex(i))
            for j in range(len(structure)):
                element_j=self.atomtypes.getRecordForElementSafe(info.getRecordForAtom(i).element,info.speciesIndex(i))
                bond = bond_factor*(element_i.covalent+element_j.covalent)
                mindist = structure.mindistCartVectors(structure[i],structure[j])
                if (mindist<=bond):
                    for i1 in (-1,0,1):
                        for i2 in (-1,0,1):
                            for i3 in (-1,0,1):
                                if ((i==j) and (i1==0) and (i2==0) and (i3==0)):
                                    continue
                                buff=structure[j]-structure[i]+i1*structure.basis[0]+i2*structure.basis[1]+i3*structure.basis[2]
                                if buff.length()<=bond:
                                    buff=0.5*buff
                                    bondlist.append((structure[i],buff))
            msg().status("Creating bondlist %d/%d"%(i,len(structure)))
            yield 1

        yield 1
        for step,total,m1,m2,m3,offset in self.multiple(structure,attributes):
            for dummy in self.paintStructure(paint,structure,elementmaterials,attributes,offset):
                yield 1
            msg().step(step,total)
            msg().status("Creating arrows")
            yield 1
            self.paintArrows(paint,structure,arrows,attributes,offset)
            msg().status("Creating bonds")
            yield 1
            self.paintBonds(paint,bondlist,attributes,offset)
        if attributes.showcell:
            msg().status("Creating cell")
            yield 1
            for step,total,m1,m2,m3,offset in self.multiple(structure,attributes):
                paint.line(offset,offset+structure.basis[0],attributes.cell_line_width,material=self.CELLMATERIAL)
                paint.line(offset,offset+structure.basis[1],attributes.cell_line_width,material=self.CELLMATERIAL)
                paint.line(offset,offset+structure.basis[2],attributes.cell_line_width,material=self.CELLMATERIAL)
            multiple=map(int,attributes.multiple)
            for m1 in range(multiple[0]):
                for m2 in range(multiple[1]):
                    m3=multiple[2]
                    offset=(m1-multiple[0]/2)*structure.basis[0]
                    offset=offset+(m2-multiple[1]/2)*structure.basis[1]
                    offset=offset+(m3-multiple[2]/2)*structure.basis[2]
                    paint.line(offset,offset+structure.basis[0],attributes.cell_line_width,material=self.CELLMATERIAL)
                    paint.line(offset,offset+structure.basis[1],attributes.cell_line_width,material=self.CELLMATERIAL)
            for m2 in range(multiple[0]):
                for m3 in range(multiple[1]):
                    m1=multiple[0]
                    offset=(m1-multiple[0]/2)*structure.basis[0]
                    offset=offset+(m2-multiple[1]/2)*structure.basis[1]
                    offset=offset+(m3-multiple[2]/2)*structure.basis[2]
                    paint.line(offset,offset+structure.basis[1],attributes.cell_line_width,material=self.CELLMATERIAL)
                    paint.line(offset,offset+structure.basis[2],attributes.cell_line_width,material=self.CELLMATERIAL)
            for m3 in range(multiple[0]):
                for m1 in range(multiple[1]):
                    m2=multiple[1]
                    offset=(m1-multiple[0]/2)*structure.basis[0]
                    offset=offset+(m2-multiple[1]/2)*structure.basis[1]
                    offset=offset+(m3-multiple[2]/2)*structure.basis[2]
                    paint.line(offset,offset+structure.basis[2],attributes.cell_line_width,material=self.CELLMATERIAL)
                    paint.line(offset,offset+structure.basis[0],attributes.cell_line_width,material=self.CELLMATERIAL)
            for m1 in range(multiple[0]):
                m2=multiple[1]
                m3=multiple[2]
                offset=(m1-multiple[0]/2)*structure.basis[0]
                offset=offset+(m2-multiple[1]/2)*structure.basis[1]
                offset=offset+(m3-multiple[2]/2)*structure.basis[2]
                paint.line(offset,offset+structure.basis[0],attributes.cell_line_width,material=self.CELLMATERIAL)
            for m2 in range(multiple[1]):
                m3=multiple[2]
                m1=multiple[0]
                offset=(m1-multiple[0]/2)*structure.basis[0]
                offset=offset+(m2-multiple[1]/2)*structure.basis[1]
                offset=offset+(m3-multiple[2]/2)*structure.basis[2]
                paint.line(offset,offset+structure.basis[1],attributes.cell_line_width,material=self.CELLMATERIAL)
            for m3 in range(multiple[2]):
                m1=multiple[0]
                m2=multiple[1]
                offset=(m1-multiple[0]/2)*structure.basis[0]
                offset=offset+(m2-multiple[1]/2)*structure.basis[1]
                offset=offset+(m3-multiple[2]/2)*structure.basis[2]
                paint.line(offset,offset+structure.basis[2],attributes.cell_line_width,material=self.CELLMATERIAL)

    def multiple(self,structure,attributes):
        multiple=map(int,attributes.multiple)
        total=multiple[0]*multiple[1]*multiple[2]
        step=0
        for m1 in range(multiple[0]):
            for m2 in range(multiple[1]):
                for m3 in range(multiple[2]):
                    offset=(m1-multiple[0]/2)*structure.basis[0]
                    offset=offset+(m2-multiple[1]/2)*structure.basis[1]
                    offset=offset+(m3-multiple[2]/2)*structure.basis[2]
                    yield step,total,m1,m2,m3,offset
                    step+=1 
        
    def exportIsosurfaces(self,paint,isosurfaces,attributes):
        for i in range(len(isosurfaces)):
            msg().status("Processing isosurface %d/%d"%(i+1,len(isosurfaces)))
            chgcar,level,color=isosurfaces[i]
            structure=p4vasp.cStructure.Structure(pointer=chgcar.structure)
            material="%s%02d"%(self.ISOSURFACEMATERIAL,i)
            paint.colorMaterial(color,material)
            mesh=[]
            for step,total,meshpart in partialIsosurface(chgcar,level):
                msg().status("Processing isosurface %d/%d (creating mesh)"%(i+1,len(isosurfaces)))
                msg().step(step,total)
                mesh.extend(meshpart)
                yield 1
            for step,total,m1,m2,m3,offset in self.multiple(structure,attributes):
                msg().status("Processing isosurface %d/%d (exporting mesh)"%(i+1,len(isosurfaces)))
                msg().step(step,total)
                yield 1
                if len(mesh):
                    coordinates,normals,triangles=convertMeshFormat(mesh,offset)
                    paint.mesh(coordinates,normals,triangles,material=material)

    def prepareStructure(self,structure,attributes):
        structure.setCartesian()
        if attributes.cell_centering==attributes.CELL_CENTERING_INSIDE:
            structure.toUnitCell()
        elif attributes.cell_centering==attributes.CELL_CENTERING_ZERO:
            structure.toCenteredUnitCell()
        return structure

    def exportSequence(self,paint,data,attributes,path):
        structures=data.structures
        arrows=data.vectors
        process_sequence=data.process_sequence
        isosurfaces=data.isosurfaces
        msg().status("Create atom materials")
        yield 1
        elementmaterials=self.createElementMaterials(paint,structures[0])

        sequencelength=max(0,len(structures)-data.index)
        if process_sequence:
            for i in range(0,sequencelength,attributes.speed):
                structureindex=i+data.index
                frame=paint.frame()
                structure=self.prepareStructure(structures[structureindex],attributes)
             
                if arrows is None:
                    a=None
                else:
                    a=arrows[structureindex]
                msg().step(structureindex,sequencelength)
                for dummy in self.exportFrame(frame,structure,a,elementmaterials,attributes):
                    yield 1
        else:
            structure=self.prepareStructure(structures[0],attributes)
            if arrows is None:
                a=None
            else:
                a=arrows[0]
            for dummy in self.exportFrame(paint,structure,a,elementmaterials,attributes):
                yield 1

        for dummy in self.exportIsosurfaces(paint,isosurfaces,attributes):
            yield 1

        paint.exportTo(path)

        msg().step(0,1)
        msg().status("OK")
        yield 1
    def export(self,data,attributes,path):
        paint=self.paint[0]()
        paint.width=attributes.width
        paint.height=attributes.height

        self.exportCamera(paint,attributes)

        paint.ambientLight(Vector(0.2,0.2,0.2))
        paint.background(Vector(attributes.background))
        paint.pointLight(self.transform(Vector(30,30,30),attributes),Vector(1,1,1))
        
        paint.colorMaterial(attributes.cell_color,self.CELLMATERIAL)
        paint.colorMaterial(attributes.bond_color,self.BONDMATERIAL)
        paint.colorMaterial(attributes.arrow_color,self.ARROWMATERIAL)
        schedule(self.exportSequence(paint,data,attributes,path))

    def createElementMaterials(self,paint,structure):
        info=structure.info
        materials=[]
        for i in range(len(structure)):
            element=self.atomtypes.getRecordForElementSafe(info.getRecordForAtom(i).element,info.speciesIndex(i))
            name=self.ELEMENTMATERIAL+"_%03d"%i
            color=Vector(element.red,element.green,element.blue)
            paint.colorMaterial(color,name)
            materials.append(name)
        return materials

    def paintStructure(self,paint,structure,materials,attributes,offset):
        info=structure.info
        msg().status("Create atom spheres")
        yield 1
        for i in range(len(structure)):
            element=self.atomtypes.getRecordForElementSafe(info.getRecordForAtom(i).element,info.speciesIndex(i))
            radius=element.radius
            paint.sphere(structure[i]+offset,radius*attributes.radius_factor,material=materials[i]);
            
    def paintArrows(self,paint,structure,arrows,attributes,offset):
        info=structure.info
        materials=[]
        if arrows is not None:
            for i in range(min(len(structure),len(arrows))):
                paint.arrow(
                    structure[i]+offset,
                    structure[i]+offset+Vector(arrows[i])*attributes.arrow_scale,
                    attributes.arrow_radius,
                    attributes.arrowhead_radius,
                    attributes.arrowhead_length,
                    material=self.ARROWMATERIAL
                )

    def paintBonds(self,paint,bondlist,attributes,offset):
        for pos,bond in bondlist:
            paint.cylinder(pos+offset,pos+bond+offset,attributes.bond_radius,material=self.BONDMATERIAL)

