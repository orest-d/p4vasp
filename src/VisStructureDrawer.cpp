/*
 *  p4vasp is a GUI-program and library for processing outputs of the
 *  Vienna Ab-inition Simulation Package (VASP)
 *  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
 *  
 *  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <p4vasp/VisWindow.h>
#include <p4vasp/VisStructureDrawer.h>
#include <math.h>
#include <FL/gl.h>
#include <GL/glu.h>
#include <stdio.h>
#include <p4vasp/vecutils.h>
#include <p4vasp/VisBackEvent.h>

AtomId::AtomId(){
  atom=0;
  nx=0;
  ny=0;
  nz=0;
}

const char *VisStructureDrawer::getClassName(){return "VisStructureDrawer";}

VisStructureDrawer::VisStructureDrawer():VisPrimitiveDrawer(){
  MUTEX_INIT(select_mutex);
  MUTEX_INIT(structure_mutex);
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  so_list_init_flag=0;
#endif  
  info=new AtomInfo();
#if CHECK>0
  if (info==NULL){
    THROW_NP_EXC("Failed to create AtomInfo() "
                 "in VisStructureDrawer constructor.");
  }
#endif
  structure=NULL;
  bondvec  =NULL;
  bondindex=NULL;
  bondcount=0;
  
  select_object_stacks = 8;
  select_object_slices = select_object_stacks*primitives_resolution;
  bond_factor=1.0;
  bond_radius =0.1;
  radius_factor=1.0;
  cell_line_width=2;
  cell_red       =1.0;
  cell_green     =1.0;
  cell_blue      =1.0;
  bond_red       =0.5;
  bond_green     =0.5;
  bond_blue      =0.7;
  nx=1;
  ny=1;
  nz=1;
  showcellflag=1;
  select_buffer  = NULL;
  select_count   = 0;
  select_size    = 0;
}

VisStructureDrawer::~VisStructureDrawer(){
#if VERBOSE>0
  printf("VisStructureDrawer::~VisStructureDrawer()\n");
#endif

#if VERBOSE>0
  printf("structure lock in VisStructureDrawer::~VisStructureDrawer()\n");
#endif
  
  structureLock();
  selectLock();
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  if (list_init_flag){
    if (glIsList(select_object_list)){
      glDeleteLists(select_object_list,1);
    }
    if (glIsList(structure_spheres_list)){
      glDeleteLists(structure_spheres_list,1);
    }
    if (glIsList(structure_bonds_list)){
      glDeleteLists(structure_bonds_list,1);
    }
    if (glIsList(structure_cell_list)){
      glDeleteLists(structure_cell_list,1);
    }
  }
  
#endif
#if CHECK>1
  if (info!=NULL){
    info=NULL;
    delete info;
  }
  else{
    fprintf(stderr,"Warning: info was NULL in VisStructureDrawer destructor.");
  }
#else
  delete info;
#endif
  if (structure!=NULL){
    delete structure;
    structure=NULL;
  }
  bondcount=0;
  if (bondindex!=NULL){
    delete bondindex;
    bondindex=NULL;
  }
  if (bondvec!=NULL){
    delete bondvec;
    bondvec=NULL;
  }
  selectUnlock();
#if VERBOSE>0
  printf("structure unlock in VisStructureDrawer::~VisStructureDrawer()\n");
#endif
  structureUnlock();
  rescaleSelectBuffer(0,1);
  MUTEX_DESTROY(select_mutex);
  MUTEX_DESTROY(structure_mutex);
}

void VisStructureDrawer::setPrimitivesResolution(int r){
#if VERBOSE>0
  printf("VisStructureDrawer::setPrimitivesResolution(%d)\n",r);
#endif  
  VisPrimitiveDrawer::setPrimitivesResolution(r);
  select_object_stacks = 8;
  select_object_slices = select_object_stacks*r;
  initSelectObject();
}

void VisStructureDrawer::initSelectObject(){
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  if (!so_list_init_flag){
    int l = glGenLists(4);
    select_object_list     =  l;
    structure_spheres_list =  l+1;
    structure_bonds_list   =  l+2;
    structure_cell_list    =  l+3;

    so_list_init_flag      = 1;    
  }
  glNewList(select_object_list,GL_COMPILE);
  glBegin(GL_LINE_STRIP);
  for (int i=0; i<=select_object_stacks*select_object_slices; i++){
    double a=M_PI*i/double(select_object_stacks*select_object_slices);
    double b=2*M_PI*i/double(select_object_slices);
    glVertex3d(cos(b)*sin(a),sin(b)*sin(a),cos(a));
  }
  glEnd();
  glEndList();
#endif
}

void VisStructureDrawer::init(){
#if VERBOSE>1
  printf("VisStructureDrawer::init()\n");
#endif
  if (quadObj==NULL){  
    quadObj = gluNewQuadric();
  }
/*
  if (quadObj1==NULL){  
    quadObj1 = gluNewQuadric();
  }*/
  setPrimitivesResolution(16);  
  is_init=true;
}

void VisStructureDrawer::draw(){
#if VERBOSE>0
  printf("structure lock in VisStructureDrawer::draw()\n");
#endif

  structureLock();
#if VERBOSE>0
  printf("VisStructureDrawer::draw()\n");
#endif
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  if (update_structure_flag){
    updateCellList();
    updateSpheresList();
    updateBondsList();
    update_structure_flag=0;
  }
#else  
  if (update_structure_flag){
    createHalfBondsList();
    update_structure_flag=0;
  }
#endif


  if (structure!=NULL){
    for (int i1=0;i1<nx;i1++){
      for (int i2=0;i2<ny;i2++){
        for (int i3=0;i3<nz;i3++){
          double v[3]={0.0,0.0,0.0};
          add3(v,i1-nx/2,structure->basis1);
          add3(v,i2-ny/2,structure->basis2);
          add3(v,i3-nz/2,structure->basis3);

          glPushMatrix();
          glTranslatef(v[0],v[1],v[2]);
          if (showcellflag){
  	    drawCell();
	  }
	  drawSpheres();
	  glColor3f(bond_red,bond_green,bond_blue);
	  drawBonds(); 
	  glColor3f(0.1,0.1,0.2);
          glPopMatrix();
	}
      }
    }
  }        
  drawSelection(); 
#if VERBOSE>0
  printf("VisStructureDrawer::draw() -\n");
#endif
#if VERBOSE>0
  printf("structure unlock in VisStructureDrawer::draw()\n");
#endif
  structureUnlock();
}

int VisStructureDrawer::handle(int event){
#if VERBOSE>1
  printf("VisStructureDrawer::handle(%d)\n",event);
#endif
  if (getKey()==' '){
    switchSelectionByPick(getMouseX(),getMouseY());
    return 1;
  }
  return 0;
}

int VisStructureDrawer::switchSelectionByPick(int x, int y){
#if VERBOSE>0
  printf("structure lock in VisStructureDrawer::switchSelectionByPick()\n");
#endif

  structureLock();
#if VERBOSE>0
  printf("VisStructureDrawer::switchSelectionByPick(%d,%d)\n",x,y);
#endif
  y=getHeight()-y;
  if (structure==NULL){
    return -1;
  }

  GLdouble projMatrix[16];
  GLdouble modelMatrix[16];
  GLint viewport[4];
  
  glGetDoublev(GL_PROJECTION_MATRIX,projMatrix);
  glGetDoublev(GL_MODELVIEW_MATRIX,modelMatrix);
  glGetIntegerv(GL_VIEWPORT,viewport);

  GLdouble X0,Y0,Z0,X1,Y1,Z1,dX,dY,dZ,dN;
  gluUnProject(x,y,0,modelMatrix,projMatrix,viewport,&X0,&Y0,&Z0);
  gluUnProject(x,y,1,modelMatrix,projMatrix,viewport,&X1,&Y1,&Z1);
  dX=X1-X0;
  dY=Y1-Y0;
  dZ=Z1-Z0;
  dN=sqrt(dX*dX+dY*dY+dZ*dZ);
/*
  printf("  V0      %+10.8f %+10.8f %+10.8f\n",X0,Y0,Z0);
  printf("  V1      %+10.8f %+10.8f %+10.8f\n",X1,Y1,Z1);
  printf("  dV      %+10.8f %+10.8f %+10.8f\n",dX,dY,dZ);
*/  
#if CHECK>1
  if (dN==0.0){
    THROW_EXC("dN=0 in switchSelectionByPick()");
  }
#endif  
  dX/=dN;
  dY/=dN;
  dZ/=dN;
//  printf("  dV/|dV| %+10.8f %+10.8f %+10.8f\n",dX,dY,dZ);

  double T=0.0;
  int index=-1;
  int NX=0,NY=0,NZ=0;
  
  for (int i1=0; i1<nx; i1++){
    for (int i2=0; i2<ny; i2++){
      for (int i3=0; i3<nz; i3++){
	for (int i=0; i<structure->len(); i++){
	  if (info->getRecord(i)->hidden){
	    continue;
	  }
	  double S[3];
	  copy3(S,structure->get(i));
          add3(S,i1-nx/2,structure->basis1);
          add3(S,i2-ny/2,structure->basis2);
          add3(S,i3-nz/2,structure->basis3);
	  double t=dX*(X0-S[0])+dY*(Y0-S[1])+dZ*(Z0-S[2]);
	  double Px=X0-t*dX;
	  double Py=Y0-t*dY;
	  double Pz=Z0-t*dZ;
	  double dPx=S[0]-Px;
	  double dPy=S[1]-Py;
	  double dPz=S[2]-Pz;
	  double dist = sqrt(dPx*dPx+dPy*dPy+dPz*dPz);
//	  printf("  %3d t=%f ",i,t);
	  if (dist<(info->getRecord(i)->radius*radius_factor)){
	    if ((t>=T) || (index==-1)){
//              printf("*");
              T=t;
	      index=i;
	      NX=i1;
	      NY=i2;
	      NZ=i3;
	    }
	  }    
//	  printf("\n");
	}
      }
    }
  }
  if (index!=-1){
//    printf("switchAtomSelection\n");

    int i = findSelectedAtom_nolock(index,NX,NY,NZ);
    if (i<0){
      appendSelected_nolock(index,NX,NY,NZ);
      notifySelected(index,NX,NY,NZ);
    }
    else{
      deselectAtom_nolock(index,NX,NY,NZ);      
      notifyDeselected(index,NX,NY,NZ);
    }
//    switchAtomSelection(index,NX,NY,NZ);
  }
#if VERBOSE>0
  printf("structure unlock in VisStructureDrawer::switchSelectionByPick()\n");
#endif
  structureUnlock();
  return index;
}

void VisStructureDrawer::selectObject(double x,double y,double z,double radius,double phase){
  glPushMatrix();
  glTranslatef(x,y,z);
  glScalef(radius,radius,radius);
  glRotated(phase,0,0,1);
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  glCallList(select_object_list);
#else
  glBegin(GL_LINE_STRIP);
  for (int i=0; i<=select_object_stacks*select_object_slices; i++){
    double a=M_PI*i/double(select_object_stacks*select_object_slices);
    double b=2*M_PI*i/double(select_object_slices);
    glVertex3d(cos(b)*sin(a),sin(b)*sin(a),cos(a));
  }
  glEnd();
#endif  
  glPopMatrix();
}

void VisStructureDrawer::fillInfo(){
#if VERBOSE>0
  printf("structure lock in VisStructureDrawer::fillInfo()\n");
#endif

  structureLock();
#if VERBOSE>0
  printf("VisStructureDrawer::fillInfo()\n");
#endif
#if CHECK>1
  if (info==NULL){
    THROW_NP_EXC("info=NULL in VisStructureDrawer::fillInfo()");
  }
#endif
  if (structure==NULL){
    info->allocate(0);
  }
  else{

    AtomInfo *si = structure->info;
#if CHECK>0
    if (si==NULL){
      THROW_NP_EXC("structure.info=NULL in VisStructureDrawer::fillInfo()");
    }
#endif

    if (structure->len()!=si->getNatoms()){
    /*
      THROW_EXC("Inconsistent structure: "
        	"len(structure) != structure.getNatoms()\n"
		"found in VisStructureDrawer::fillInfo()");
		*/
      printf("Inconsistent (corrupted) structure: "
             "len(structure)=%d  differs from structure.getNatoms()=%d\n"
	     "found in VisStructureDrawer::fillInfo()",structure->len(),si->getNatoms());
      
      info->allocate(0);
      delete structure;
      structure=NULL;
    }
    else{
      info->allocate(structure->len());

      int l=si->len();
      int index=0;
      for (int i=0; i<l;i++){
	int ll=si->getRecord(i)->atomspertype;
	for (int j=0; j<ll;j++){
          info->setRecord(index,si->getRecord(i));
	  index++;
	}
      }
    }
  }
#if VERBOSE>0
  printf("structure unlock in VisStructureDrawer::fillInfo()\n");
#endif
  structureUnlock();
}

void VisStructureDrawer::updateStructure(){
  update_structure_flag=1;
  redraw();
}

void VisStructureDrawer::setStructure(Structure *s){
#if VERBOSE>0
  printf("VisStructureDrawer::setStructure()\n");
#endif
#if VERBOSE>0
  printf("structure lock in VisStructureDrawer::setStructure()\n");
#endif
  structureLock();
  if (s!=NULL){  
    structure=new Structure(s);
    structure->setCarthesian();
    structure->createMindistMatrix();        
  }
  else{
    structure=NULL;
  }
#if VERBOSE>0
  printf("structure unlock in VisStructureDrawer::setStructure()\n");
#endif
  structureUnlock();
  fillInfo();
  updateStructure();
}

Structure *VisStructureDrawer::getStructure(){
  return structure;
}


long VisStructureDrawer::createHalfBondsList(int storeflag){
#if VERBOSE>0
  printf("VisStructureDrawer::createHalfBondsList(%d)\n",storeflag);
#endif
#if CHECK>1
    if (info==NULL){
      THROW_NP_EXC("info=NULL"
                   " in VisStructureDrawer::createHalfBondsList()");
    }
#endif  

  if (storeflag){
    if (bondindex!=NULL){
      delete bondindex;
      bondindex=NULL;
    }
    if (bondvec!=NULL){
      delete bondvec;
      bondvec=NULL;
    }
  }
  
  if (structure==NULL){
    bondcount=0;
    return 0;
  }


  if (storeflag){
    bondcount=countHalfBonds();
    if (bondcount==0){
      return 0;
    }
    bondvec   = new double[3*bondcount];
#if CHECK>0
    if (bondvec==NULL){
      THROW_MA_EXC("bondvec allocation failed"
                   " in VisStructureDrawer::createHalfBondsList()");
    }
#endif  
    bondindex = new int[bondcount];  
#if CHECK>0
    if (bondindex==NULL){
      THROW_MA_EXC("bondindex allocation failed"
                   " in VisStructureDrawer::createHalfBondsList()");
    }
#endif  
  }  

  long N=0;
  double buff[3];
  int len = structure->len();
  
  for (int i=0; i<len; i++){
    if (info->getRecord(i)->hidden){
      continue;
    }
    for (int j=0; j<len; j++){
      if (info->getRecord(j)->hidden){
	continue;
      }
      double bond = bond_factor*(info->getRecord(i)->covalent+info->getRecord(j)->covalent);
      double mindist = structure->getMindist(i,j);
      //printf("%3d %3d bond=%14.8f mindist=%14.8f\n",i,j,bond,mindist);
      if (mindist<=bond){
        for (int i1=-1; i1<=1; i1++){
          for (int i2=-1; i2<=1; i2++){
            for (int i3=-1; i3<=1; i3++){
              if ((i==j) && (i1==0) && (i2==0) && (i3==0)) continue;
              copy3(buff,&structure->positions[3*j]);
              sub(buff,&structure->positions[3*i]);

              add3(buff,i1,structure->basis1);
              add3(buff,i2,structure->basis2);
              add3(buff,i3,structure->basis3);

              if (veclength3(buff)<=bond){
                mul3(buff,0.5);
		if (storeflag){
                  copy3(&bondvec[3*N],buff);
                  bondindex[N]=i;
		}
                N++;
              }
            }
          }
        }
      }
    }
  }
  return N;
}

long VisStructureDrawer::countHalfBonds(){
#if VERBOSE>0
  printf("VisStructureDrawer::countHalfBonds()\n");
#endif
  long l=createHalfBondsList(0);
#if VERBOSE>0
  printf("VisStructureDrawer::countHalfBonds() = %ld\n",l);
#endif
  return l;
}


void VisStructureDrawer::updateCellList(double *lattice){
/*
     8        7
     +--------+
    /|       /|
  5/ |     6/ |
  +--------+  |
  |  +-----|--+
  | /4     | /3
  |/       |/
  +--------+
  1        2

*/
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  if (lattice==NULL){
    glNewList(structure_cell_list,GL_COMPILE);
    glEndList();
  }
  else{
    double  v1[3]={0.0,0.0,0.0};
    double *v2   =&lattice[0];
    double  v3[3];
    double *v4   =&lattice[3];
    double *v5   =&lattice[6];
    double  v6[3];
    double  v7[3];
    double  v8[3];
    add3(&v3[0],v2,v4);
    add3(&v6[0],v2,v5);
    add3(&v8[0],v4,v5);
    add3(&v7[0],&v3[0],v5);


    glNewList(structure_cell_list,GL_COMPILE);
    glNormal3d(1,1,1);
    glBegin(GL_LINE_STRIP);
    glVertex3d(v1[0],v1[1],v1[2]);
    glVertex3d(v2[0],v2[1],v2[2]);
    glVertex3d(v3[0],v3[1],v3[2]);
    glVertex3d(v4[0],v4[1],v4[2]);
    glVertex3d(v1[0],v1[1],v1[2]);
    glVertex3d(v5[0],v5[1],v5[2]);
    glVertex3d(v6[0],v6[1],v6[2]);
    glVertex3d(v7[0],v7[1],v7[2]);
    glVertex3d(v8[0],v8[1],v8[2]);
    glVertex3d(v5[0],v5[1],v5[2]);
    glEnd();

    glBegin(GL_LINES);
    glVertex3d(v2[0],v2[1],v2[2]);
    glVertex3d(v6[0],v6[1],v6[2]);
    glVertex3d(v3[0],v3[1],v3[2]);
    glVertex3d(v7[0],v7[1],v7[2]);
    glVertex3d(v4[0],v4[1],v4[2]);
    glVertex3d(v8[0],v8[1],v8[2]);
    glEnd();

    glEndList();
  }
#endif
}

void VisStructureDrawer::updateCellList(){
  if (structure==NULL){
    updateCellList(NULL);
  }
  else{
    updateCellList(structure->basis);
  }
}

void VisStructureDrawer::updateSpheresList(){
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  if (structure==NULL){
    glNewList(structure_spheres_list,GL_COMPILE);
    glEndList();
  }
  else{
#  if CHECK>1
    if (info==NULL){
      THROW_NP_EXC("info=NULL in VisStructureDrawer::updateSpheresList()");
    }
#  endif
#  if CHECK>0
    if (info->len() != structure->len()){
      THROW_EXC("len(info) != len(structure) in VisStructureDrawer::updateSpheresList()");
    }
#  endif
  
    glNewList(structure_spheres_list,GL_COMPILE);
    for (int i=0; i<structure->len(); i++){
      AtomtypesRecord *a=info->getRecord(i);
      if (!a->hidden){      
	glColor3f(a->red,a->green,a->blue);
	sphere((*structure)[i][0],(*structure)[i][1],(*structure)[i][2],a->radius*radius_factor);
      }
    }    
    glEndList();
  }
#endif  
}

void VisStructureDrawer::updateBondsList(){
  createHalfBondsList();
#if VERBOSE>0
  printf("VisStructureDrawer::updateBondsList()\n");
#endif
#if (!defined(NO_GL_LISTS)) && (!defined(NO_GL_LISTS_S))
  if (bondvec==NULL){
#if VERBOSE>1
    printf("  bondvec=NULL\n");
#endif
    glNewList(structure_bonds_list,GL_COMPILE);
    glEndList();
  }
  else{
    glNewList(structure_bonds_list,GL_COMPILE);
#if VERBOSE>1
    printf("  bondcount=%ld\n",bondcount);
#endif
    for (long i=0; i<bondcount; i++){
      double *u,*v;
      u=(*structure)[bondindex[i]];
      v=&bondvec[3*i];
      cylinder(u[0],u[1],u[2],u[0]+v[0],u[1]+v[1],u[2]+v[2],bond_radius);
    }
    glEndList();
  } 
#endif  
}



void VisStructureDrawer::drawCell(){
#if VERBOSE>0
  printf("VisStructureDrawer::drawCell()\n");
#endif
  glColor3f(cell_red,cell_green,cell_blue);
  glLineWidth(cell_line_width); 

  GLboolean lightflag = glIsEnabled(GL_LIGHTING);
  glDisable(GL_LIGHTING);
#if (defined(NO_GL_LISTS)) || (defined(NO_GL_LISTS_S))
  if (structure!=NULL){
    double  v1[3]={0.0,0.0,0.0};
    double *v2   =structure->basis1;
    double  v3[3];
    double *v4   =structure->basis2;
    double *v5   =structure->basis3;
    double  v6[3];
    double  v7[3];
    double  v8[3];
    add3(&v3[0],v2,v4);
    add3(&v6[0],v2,v5);
    add3(&v8[0],v4,v5);
    add3(&v7[0],&v3[0],v5);


    glBegin(GL_LINE_STRIP);
    glVertex3d(v1[0],v1[1],v1[2]);
    glVertex3d(v2[0],v2[1],v2[2]);
    glVertex3d(v3[0],v3[1],v3[2]);
    glVertex3d(v4[0],v4[1],v4[2]);
    glVertex3d(v1[0],v1[1],v1[2]);
    glVertex3d(v5[0],v5[1],v5[2]);
    glVertex3d(v6[0],v6[1],v6[2]);
    glVertex3d(v7[0],v7[1],v7[2]);
    glVertex3d(v8[0],v8[1],v8[2]);
    glVertex3d(v5[0],v5[1],v5[2]);
    glEnd();

    glBegin(GL_LINES);
    glVertex3d(v2[0],v2[1],v2[2]);
    glVertex3d(v6[0],v6[1],v6[2]);
    glVertex3d(v3[0],v3[1],v3[2]);
    glVertex3d(v7[0],v7[1],v7[2]);
    glVertex3d(v4[0],v4[1],v4[2]);
    glVertex3d(v8[0],v8[1],v8[2]);
    glEnd();
  }
#else
  glCallList(structure_cell_list);    
#endif
  if (lightflag){
    glEnable(GL_LIGHTING);
  }
}


void VisStructureDrawer::drawSpheres(){
#if VERBOSE>0
  printf("VisStructureDrawer::drawSpheres()\n");
#endif
#if (defined(NO_GL_LISTS)) || (defined(NO_GL_LISTS_S))
  if (structure!=NULL){
#  if CHECK>1
    if (info==NULL){
      THROW_NP_EXC("info=NULL in VisStructureDrawer::drawSpheres()");
    }
#  endif
#  if CHECK>0
    if (info->len() != structure->len()){
      THROW_EXC("len(info) != len(structure) in VisStructureDrawer::drawSpheres()");
    }
#  endif
  
    for (int i=0; i<structure->len(); i++){
      AtomtypesRecord *a=info->getRecord(i);      
//      printf("info(%3d).hidden=%d\n",i,a->hidden);
      if (!a->hidden){
        glColor3f(a->red,a->green,a->blue);
/*	
	printf("sphere %+12.8f %+12.8f %+12.8f %+12.8f\n",	
	(*structure)[i][0],(*structure)[i][1],(*structure)[i][2],a->radius*radius_factor
	);
*/	
        double *v=structure->get(i);
        sphere(v[0],v[1],v[2],a->radius*radius_factor);
      }	
    }    
  }
#else  
  glCallList(structure_spheres_list);  
#endif  
#if VERBOSE>0
  printf("VisStructureDrawer::drawSpheres() -\n");
#endif
}

void VisStructureDrawer::drawSelection(){
#if VERBOSE>0
  printf("VisStructureDrawer::drawSelection()\n");
#endif
  selectLock();
  if (structure!=NULL){
    for (int i=0; i<select_count; i++){
#if CHECK>1
      if (select_buffer==NULL){
        THROW_NP_EXC("select_buffer=NULL "
	             "in VisStructureDrawer::drawSelection()");
      }
#endif    
      AtomId *a = &select_buffer[i];
      double v[3];
      if ((a->atom<structure->len())&&(a->atom>=0)){
	copy3(v,structure->get(a->atom));

	add3(v,a->nx-nx/2,structure->basis1);
	add3(v,a->ny-ny/2,structure->basis2);
	add3(v,a->nz-nz/2,structure->basis3);

	selectObject(v[0],v[1],v[2],info->getRecord(a->atom)->radius*radius_factor*1.05);
      }
    }
  }
  selectUnlock();
}


void VisStructureDrawer::drawBonds(){
#if VERBOSE>0
  printf("VisStructureDrawer::drawBonds()\n");
#endif
  glColor3f(bond_red,bond_green,bond_blue);
#if (defined(NO_GL_LISTS)) || (defined(NO_GL_LISTS_S))
  if (bondvec!=NULL){
    for (long i=0; i<bondcount; i++){
#if CHECK>1
      if (bondindex==NULL){
        THROW_NP_EXC("bondindex is NULL in VisStructureDrawer::drawBonds()");
      }    
      if (structure==NULL){
        THROW_NP_EXC("structure is NULL in VisStructureDrawer::drawBonds()");
      }    
      if (bondvec==NULL){
        THROW_NP_EXC("bondvec is NULL in VisStructureDrawer::drawBonds()");
      }    
#endif
      double *u,*v;
      u=(*structure)[bondindex[i]];
      v=&bondvec[3*i];
      cylinder(u[0],u[1],u[2],u[0]+v[0],u[1]+v[1],u[2]+v[2],bond_radius);
    }
  } 
#else
  glCallList(structure_bonds_list);  
#endif  
#if VERBOSE>0
  printf("VisStructureDrawer::drawBonds() -\n");
#endif
}

void VisStructureDrawer::setRadiusFactor(double r){
#if VERBOSE>0
  printf("structure lock in VisStructureDrawer::setRadiusFactor()\n");
#endif

  structureLock();
  radius_factor=r;
  updateSpheresList();
#if VERBOSE>0
  printf("structure unlock in VisStructureDrawer::setRadiusFactor()\n");
#endif
  structureUnlock();
  redraw();
}
double VisStructureDrawer::getRadiusFactor(){
  return radius_factor;
}

void VisStructureDrawer::setBondRadius(double r){
  structureLock();
  bond_radius=r;
  updateBondsList();
  structureUnlock();
  redraw();
}

double VisStructureDrawer::getBondRadius(){
  return bond_radius;
}

void VisStructureDrawer::setBondFactor(double r){
  structureLock();
  bond_factor=r;
  updateStructure();
  structureUnlock();
}

double VisStructureDrawer::getBondFactor(){
  return bond_factor;
}

void VisStructureDrawer::setMultiple(int a,int b,int c){
  nx=a;
  ny=b;
  nz=c;
  redraw();
}

void VisStructureDrawer::showCell(int f){
  showcellflag=f;
  redraw();
}

void VisStructureDrawer::setMultiple1(int a){
  nx=a;
  redraw();
}

void VisStructureDrawer::setMultiple2(int a){
  ny=a;
  redraw();
}

void VisStructureDrawer::setMultiple3(int a){
  nz=a;
  redraw();
}

int VisStructureDrawer::getMultiple1(){
  return nx;
}

int VisStructureDrawer::getMultiple2(){
  return ny;
}

int VisStructureDrawer::getMultiple3(){
  return nz;
}

int VisStructureDrawer::getCellLineWidth(){
  return cell_line_width;
}

void VisStructureDrawer::setCellLineWidth(int w){
  cell_line_width=w;
  redraw();
}

void VisStructureDrawer::setCellColor(float r,float g,float b){
  cell_red  =r;
  cell_green=g;
  cell_blue =b;
  redraw();
}


void VisStructureDrawer::setBondColor(float r,float g,float b){
  bond_red  =r;
  bond_green=g;
  bond_blue =b;
  redraw();
}


void VisStructureDrawer::rescaleSelectBuffer(int len,int force){
#if VERBOSE>0 
  printf("VisStructureDrawer::rescaleSelectBuffer(%3d,%3d)\n",len,force);
#endif  
  if ((structure==NULL)||len==0){
    if (select_buffer!=NULL){
      delete []select_buffer;
      select_buffer = NULL;
      select_count  = 0;
      select_size   = 0;
    }
  }
  else{
    if (len==-1){
      len=nx*ny*nz*structure->len();
      if (len>128){
        len=128;
      }
    }
    if ((len>select_size)||force){
      AtomId *newbuff=new AtomId[len];
#if CHECK>0      
      if (newbuff==NULL){
        THROW_MA_EXC(
	"select buffer allocation failed "
	"in VisStructureDrawer::rescaleSelectBuffer()");
      }
#endif          
      if ((select_count>0)&&(select_count<=len)){
#if CHECK>0
        if (select_buffer==NULL){
	  THROW_NP_EXC(
	  "select_buffer=NULL "
          "in VisStructureDrawer::rescaleSelectBuffer()");	  
	}
#endif
        memcpy(newbuff,select_buffer,select_count*sizeof(AtomId));
      }
      else{
        select_count=0;
      }
      if (select_buffer!=NULL){
        delete []select_buffer;
      }
      select_buffer=newbuff;
      select_size=len;
    }
  }
#if VERBOSE>0 
  printf("VisStructureDrawer::rescaleSelectBuffer -\n");
#endif  
}

AtomId *VisStructureDrawer::getSelected(int i){
#if CHECK>0
  if ((i<0)||(i>select_count)){
    THROW_R_EXC("VisStructureDrawer::getSelect() failed.",0,select_count,i);
  }
#endif
  return &select_buffer[i];
}

int VisStructureDrawer::getSelectedCount(){
  return select_count;
}

void VisStructureDrawer::appendSelected(int atom,int nx,int ny,int nz){
  selectLock();
  appendSelected_nolock(atom,nx,ny,nz);
  selectUnlock();
}

void VisStructureDrawer::appendSelected_nolock(int atom,int nx,int ny,int nz){
#if VERBOSE>0 
  printf("VisStructureDrawer::appendSelected_nolock(%3d,%3d,%3d,%3d)\n",atom,nx,ny,nz);
#endif  
  if (select_size<=select_count){
    rescaleSelectBuffer(select_count+16);
  }
  if (select_buffer!=NULL){
    AtomId *a = &select_buffer[select_count];
    a->atom = atom;
    a->nx   = nx;
    a->ny   = ny;
    a->nz   = nz;
    select_count++;
  }
  //redraw();
#if VERBOSE>1
  printf("VisStructureDrawer::appendSelected_nolock -\n");
#endif  
}

void VisStructureDrawer::removeSelectedAll(){
  select_count=0;
  redraw();
}

void VisStructureDrawer::removeSelectedItem(int i){
  selectLock();
  removeSelectedItem_nolock(i);
  selectUnlock();
}

void VisStructureDrawer::removeSelectedItem_nolock(int i){
#if CHECK>0
  if ((i<0)||(i>select_count)){
    THROW_R_EXC("VisStructureDrawer::removeSelectedItem() failed.",0,select_count,i);
  }
#endif
  if (i<(select_count-1)){
    memmove(&select_buffer[i], &select_buffer[i+1],
    (select_count-i-1)*sizeof(AtomId));
  }
  select_count--;  
  //redraw();
}

int VisStructureDrawer::findSelectedAtom(int atom,int nx,int ny,int nz){
  selectLock();
  int i=findSelectedAtom_nolock(atom,nx,ny,nz);
  selectUnlock();
  return i;
}

int VisStructureDrawer::findSelectedAtom_nolock(int atom,int nx,int ny,int nz){
#if VERBOSE>0 
  printf("VisStructureDrawer::findSelectedAtom_nolock(%3d,%3d,%3d,%3d)\n",atom,nx,ny,nz);
#endif  
  for (int i=0;i<select_count;i++){
    AtomId *a = &select_buffer[i];
#if VERBOSE>1    
    printf("  %3d/%3d: %3d %3d %3d %3d\n",
    i,select_count,a->atom,a->nx,a->ny,a->nz);
#endif    
    if ((a->atom==atom) && (a->nx==nx) && (a->ny==ny) && (a->nz==nz)){
#if VERBOSE>1 
      printf("VisStructureDrawer::findSelectedAtom_nolock - return %d\n",i);
#endif  
      return i;
    }
  }
#if VERBOSE>1 
      printf("VisStructureDrawer::findSelectedAtom_nolock - return -1 (not found)\n");
#endif  
  return -1;
}

void VisStructureDrawer::deselectAtom(int atom,int nx,int ny,int nz){
  selectLock();
  deselectAtom_nolock(atom,nx,ny,nz);
  selectUnlock();
}

void VisStructureDrawer::deselectAtom_nolock(int atom,int nx,int ny,int nz){
  for(;;){
    int i = findSelectedAtom_nolock(atom,nx,ny,nz);
    if (i<0) break;
    removeSelectedItem_nolock(i);    
  }
  //redraw();
}

void VisStructureDrawer::selectAtom(int atom,int nx,int ny,int nz){
  selectLock();
  selectAtom_nolock(atom,nx,ny,nz);
  selectUnlock();
}

void VisStructureDrawer::selectAtom_nolock(int atom,int nx,int ny,int nz){
  deselectAtom_nolock(atom,nx,ny,nz);  
  appendSelected_nolock(atom,nx,ny,nz);  
  //redraw();
}

void VisStructureDrawer::switchAtomSelection(int atom,int nx, int ny, int nz){
  selectLock();
#if VERBOSE>0
  printf("VisStructureDrawer::switchAtomSelection(%3d,%3d,%3d,%3d) "
         "count=%3d\n",
  atom,nx,ny,nz,select_count);
#endif  
  int i = findSelectedAtom_nolock(atom,nx,ny,nz);
  if (i<0){
    appendSelected_nolock(atom,nx,ny,nz);  
  }
  else{
    deselectAtom_nolock(atom,nx,ny,nz);      
  }
  selectUnlock();
  //redraw();
}	

void VisStructureDrawer::notifySelected(int atom,int nx, int ny, int nz){
 
VisBackEventQueue::get()->append(VisBackEvent::createSelected(atom,nx,ny,nz,this));
}

void VisStructureDrawer::notifyDeselected(int atom,int nx, int ny, int nz){
 
VisBackEventQueue::get()->append(VisBackEvent::createDeselected(atom,nx,ny,nz,this));
}
