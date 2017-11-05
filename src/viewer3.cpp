#include <stdio.h>
#include <p4vasp/VisMain.h>
#include <p4vasp/VisNavDrawer.h>
#include <p4vasp/VisStructureDrawer.h>
#include <p4vasp/Structure.h>
#include <p4vasp/AtomInfo.h>


int main(int argc, char **argv){
/*  if (argc!=2){
    printf("Usage: viewer1 POSCAR\n");
    return 0;
  }*/
  Structure          *structure = new Structure();
//  structure->read(argv[1]);
  structure->read("../POSCAR");
  AtomInfo *atominfo  = new AtomInfo(10);
  AtomtypesRecord r;
  r.setElement("00");
  r.radius=1.0;
  r.red   =1.0;
  r.green =1.0;
  r.blue  =1.0;
  atominfo->append(&r);
  structure->info->fillAttributesWithTable(atominfo);
  VisInit();
  VisNavDrawer        *navigator        = new VisNavDrawer();
  VisStructureDrawer  *structure_drawer = new VisStructureDrawer();
  navigator->append(structure_drawer);
  structure_drawer->setStructure(structure);
  for (int i=0; i<100; i++){
    VisWindow           *win              = new VisWindow(0,0,400,400,"viewer");
    win->setDrawer(navigator);
    VisCheck();
    win->hide();
    VisCheck();
    win->hide();
    delete win;
    VisCheck();
  }
  return 1;
  
}
