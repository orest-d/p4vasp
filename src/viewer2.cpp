#include <stdio.h>
#include <p4vasp/VisMain.h>
#include <p4vasp/VisNavDrawer.h>
#include <p4vasp/VisStructureDrawer.h>
#include <p4vasp/VisIsosurfaceDrawer.h>
#include <p4vasp/Structure.h>
#include <p4vasp/Chgcar.h>
#include <p4vasp/AtomInfo.h>

int main(int argc, char **argv){

  if (argc!=2){
    printf("Usage: viewer2 CHGCAR\n");
    return 0;
  }

  Chgcar          *chgcar = new Chgcar();
  chgcar->read(argv[1]);
  
//  chgcar->downSampleByFactors(4,4,2);
  AtomInfo *atominfo  = new AtomInfo(10);
  AtomtypesRecord r;
  r.setElement("00");
  r.radius=1.0;
  r.red   =1.0;
  r.green =1.0;
  r.blue  =1.0;
  atominfo->append(&r);
  chgcar->structure->info->fillAttributesWithTable(atominfo);
  VisInit();
  
  VisWindow           *win               = new VisWindow(0,0,400,400,"viewer1");
  VisNavDrawer        *navigator         = new VisNavDrawer();
  VisStructureDrawer  *structure_drawer  = new VisStructureDrawer();
  VisIsosurfaceDrawer *isosurface_drawer = new VisIsosurfaceDrawer();
  chgcar->structure->correctScaling();
  structure_drawer->setStructure(chgcar->structure);
  isosurface_drawer->setLevel(1000);
  
  navigator->append(structure_drawer);
  navigator->append(isosurface_drawer);
  win->setDrawer(navigator);
  isosurface_drawer->setChgcar(chgcar);
  VisMainLoop();
  return 1;
}
