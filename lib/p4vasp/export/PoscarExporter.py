from p4vasp.export.Exporter import *
from p4vasp import *
from p4vasp.util import xmlrepr

class PoscarExporter(Exporter):
    def name(self):
        return "POSCAR"
    def export(self,data,attributes,path):
        f=open(path,"w")
        schedule(self.exportSequence(f,data,attributes))
    def exportSequence(self,f,data,attributes):
        structures=data.structures
        process_sequence=data.process_sequence

        sequencelength=max(0,len(structures)-data.index)
        if process_sequence:
            for i in range(0,sequencelength,attributes.speed):
                structureindex=i+data.index
                structure=structures[structureindex]
                if i==0:
                    structure.write(f,newformat=False,closeflag=False)
                else:
                    if (structure.isSelective()): 
                        for i in range(0,len(structure)): 
                            f.write(str(structure[i])+" "+xmlrepr(structure.selective[i],LOGICAL_TYPE)+"\n") 
                    else: 
                        for i in range(0,len(structure)): 
                            f.write(str(structure[i])+"\n") 
                    f.write("\n") 

                msg().step(structureindex,sequencelength)
                yield 1
        else:
            structure=structures[0]
            structure.write(f,newformat=False,closeflag=False)

        msg().step(0,1)
        msg().status("OK")
        f.close()
        yield 1

