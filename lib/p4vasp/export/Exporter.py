from p4vasp.matrix import *

class Attributes:
    """Exporter attributes. This encapsulates typically 'non-essential' data for the exporter,
typically influencing style (e.g. colors and scales)."""
    CELL_CENTERING_NONE   = 0
    CELL_CENTERING_INSIDE = 1
    CELL_CENTERING_ZERO   = 2

    def __init__(self,
        
        radius_factor=0.5,
        bond_factor=1.0,
        bond_radius=0.1,
        bond_color=Vector(0.5,0.5,0.7),
        multiple=(1,1,1),
        background=Vector(0,0,0)
        ):
        self.radius_factor=radius_factor
        self.bond_factor=bond_factor
        self.bond_radius=bond_radius
        self.bond_color=bond_color
        self.multiple=multiple
        self.background=background
        self.cell_color=Vector(1.0,1.0,1.0)
        self.perspective=False
        self.zoom=1.0
        self.rotmat=Rz(0)
        self.width=800
        self.height=600
        self.showcell=True
        self.cell_line_width=1
        self.multiple=(1,1,1)
        self.radius_factor=1.0
        self.speed=1
        self.arrow_scale=1.0
        self.arrow_color=Vector(0.0,1.0,0.0)
        self.arrow_radius=0.1
        self.arrowhead_radius=0.2
        self.arrowhead_length=0.2

class Data:
    """This object collects all data that may be exported.
structures - list of structures to be exported. It can be a single structure (list with one element) or a sequence (e.g. an MD)
vectors - list of sets of vectors to be shown as arrows (e.g. forces). It either is None or it needs to have the same dimensions as structures (each atom in structures must have a vector).
index - index to a single structure to be exported (if relevant).
process_sequence - True if structures should be processed as a sequence - otherwise only a first (index) structure is exported.
isosurfaces - list of tuples (chgcar, level, color) defining isosurfaces. For now isosurfaces do not depend on time.
"""
    def __init__(self,structures=[],vectors=None,index=0,process_sequence=False,isosurfaces=[]):
        self.structures=structures
        self.vectors=vectors
        self.index=index
        self.process_sequence=process_sequence
        self.isosurfaces=isosurfaces

class Exporter:
    def name(self):
        return "None"
    def export(self,data,attributes,path):
        pass
    def fileExtension(self):
        return ""
