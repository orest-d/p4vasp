#include <stdio.h>
#include <p4vasp/VisMain.h>
#include <p4vasp/VisNavDrawer.h>
#include <p4vasp/VisStructureDrawer.h>
#include <p4vasp/Structure.h>
#include <p4vasp/AtomInfo.h>


int main(int argc, char **argv){
  if (argc!=2){
    printf("Usage: viewer1 POSCAR\n");
    return 0;
  }
  Structure          *structure = new Structure();
  structure->read(argv[1]);
  AtomInfo *atominfo  = new AtomInfo(10);
  AtomtypesRecord r1,r2,r3;
  r1.setElement("00");
  r1.radius=0.7;
  r1.red   =1.0;
  r1.green =0.0;
  r1.blue  =0.0;
  r2.setElement("01");
  r2.radius=0.7;
  r2.red   =0.0;
  r2.green =1.0;
  r2.blue  =0.0;
  r3.setElement("02");
  r3.radius=0.7;
  r3.red   =0.0;
  r3.green =0.0;
  r3.blue  =1.0;
  atominfo->append(&r1);
  atominfo->append(&r2);
  atominfo->append(&r3);
  structure->info->fillAttributesWithTable(atominfo);
  structure->correctScaling();
  VisInit();
  VisWindow           *win              = new VisWindow(0,0,400,400,"viewer1");
  VisNavDrawer        *navigator        = new VisNavDrawer();
  VisStructureDrawer  *structure_drawer = new VisStructureDrawer();
  navigator->append(structure_drawer);
  win->setDrawer(navigator);
  structure_drawer->setStructure(structure);
  VisMainLoop();
  return 1;
}
