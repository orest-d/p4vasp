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
#include <p4vasp/VisIsosurfaceDrawer.h>
#include <math.h>
#include <FL/gl.h>
#include <GL/glu.h>
#include <stdio.h>
#include <string.h>
#include <p4vasp/vecutils.h>


const char *
VisIsosurfaceDrawer::getClassName ()
{
  return "VisIsosurfaceDrawer";
}

VisIsosurfaceDrawer::VisIsosurfaceDrawer ():VisDrawer ()
{
#if VERBOSE>0
  printf("VisIsosurfaceDrawer () constructor\n");
#endif

  this->chgcar = NULL;

  red   =0.8f;
  green =0.8f;
  blue  =0.8f;
  level =0.0;
  mx=1;
  my=1;
  mz=1;
  draw_as_points=false;
#ifndef NO_GL_LISTS
  list_update_required=true;
#endif

#if VERBOSE>0
  printf("VisIsosurfaceDrawer () constructor -\n");
#endif
}


VisIsosurfaceDrawer::~VisIsosurfaceDrawer ()
{
#if VERBOSE>0
  printf("~VisIsosurfaceDrawer ()\n");
#endif
  chgcar = NULL;
#ifndef NO_GL_LISTS
  if (glIsList(list)){
    glDeleteLists(list,1);
  }
#endif
#if VERBOSE>0
  printf("~VisIsosurfaceDrawer () -\n");
#endif
}


void VisIsosurfaceDrawer::setDrawAsPoints (bool b){
    draw_as_points=b;
    if (is_init)draw();
}

void
VisIsosurfaceDrawer::init ()
{
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::init ()\n");
#endif
  if (is_init==false){
#ifndef NO_GL_LISTS
    list=glGenLists(1);
#endif  
    is_init=true;    
  }
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::init () -\n");
#endif
}

void
VisIsosurfaceDrawer::draw ()
{
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::draw ()\n");
#endif
#ifndef NO_GL_LISTS
  if (list_update_required){
    updateList();
  }
#endif

  if (chgcar != NULL){
#if CHECK>1
    if (chgcar->structure==NULL){
      THROW_NP_EXC("chgcar->structure==NULL in VisIsosurfaceDrawer::draw ()\n");
    }
#endif      
    for (int i1=0;i1<mx;i1++){
      for (int i2=0;i2<my;i2++){
	for (int i3=0;i3<mz;i3++){
          double v[3]={0.0,0.0,0.0};
          add3(v,i1-mx/2,chgcar->structure->basis1);
          add3(v,i2-my/2,chgcar->structure->basis2);
          add3(v,i3-mz/2,chgcar->structure->basis3);

          glPushMatrix();
          glTranslatef(v[0],v[1],v[2]);
          glColor3f(red,green,blue);

#ifndef NO_GL_LISTS
	  glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
//	  glLineWidth(0.5);
//	  glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
	  glShadeModel(GL_SMOOTH);
	  glEnable(GL_MAP2_VERTEX_3);
	  glEnable(GL_AUTO_NORMAL);
	  glEnable(GL_NORMALIZE);
	  if (draw_as_points){
            glPointSize(2.0);
  	    glBegin(GL_POINTS);
	  }
	  else{
  	    glBegin(GL_TRIANGLES);
	  }
          glCallList(list);
          glEnd();

#else
	  glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
	  glShadeModel(GL_SMOOTH);
	  glEnable(GL_MAP2_VERTEX_3);
	  glEnable(GL_AUTO_NORMAL);
	  glEnable(GL_NORMALIZE);
	  glColor3f(red,green,blue);
	  if (draw_as_points){
            glPointSize(2.0);
  	    glBegin(GL_POINTS);
	  }
	  else{
  	    glBegin(GL_TRIANGLES);
	  }
	  paint_isosurface(chgcar,level);
	  glEnd();
#endif    

          glPopMatrix();
	}
      }
    }
  }
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::draw () -\n");
#endif
}

#ifndef NO_GL_LISTS
void
VisIsosurfaceDrawer::updateList ()
{
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::updateList ()\n");
#endif
  if (!is_init){
    init();
  }
  if (chgcar==NULL){
#if VERBOSE>0
    printf("  no CHGCAR\n");
#endif
    glNewList(list,GL_COMPILE);
    glEndList();
  }
  else{
    glNewList(list,GL_COMPILE);
    paint_isosurface(chgcar,level);

    glEndList();    
    list_update_required=false;
  }  
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::updateList () -\n");
#endif
}
#endif  

void
VisIsosurfaceDrawer::updateIsosurface ()
{
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::updateIsosurface ()\n");
#endif
#ifndef NO_GL_LISTS
  list_update_required=true;
#endif
  redraw();
#if VERBOSE>0
  printf("VisIsosurfaceDrawer::updateIsosurface () -\n");
#endif
}

void
VisIsosurfaceDrawer::paint_isosurface (Chgcar * c, double level)
{
  long nx = c->nx - 1;
  long ny = c->ny - 1;
  long nz = c->nz - 1;
  /*
     double dx[3];
     double dy[3];
     double dz[3];
     double zero[3]={0.0,0.0,0.0};
   */
  /*
     copy3(dx,c->structure->basis1);
     mul3(dx,1.0/nx);
     copy3(dy,c->structure->basis2);
     mul3(dy,1.0/ny);
     copy3(dz,c->structure->basis3);
     mul3(dz,1.0/nz);
   */
  for (int i = 0; i <= nx; i++)
    {
      for (int j = 0; j <= ny; j++)
	{
	  for (int k = 0; k <= nz; k++)
	    {
//        printf("\n*** (%d,%d.%d) ***\n",i,j,k);
//        printf("000 %+8.4f %+8.4f
//        printf("RED:\n");
//        glColor3d(1.0,0.0,0.0);
	      handle_tetrahedron (c, i + 0, j + 0, k + 0,
				  i + 1, j + 0, k + 0,
				  i + 0, j + 1, k + 0,
				  i + 1, j + 0, k + 1, level);
//        printf("YELLOW:\n");
//        glColor3d(1.0,1.0,0.0);
	      handle_tetrahedron (c, i + 0, j + 0, k + 0,
				  i + 0, j + 0, k + 1,
				  i + 0, j + 1, k + 0,
				  i + 1, j + 0, k + 1, level);
//        printf("GREEN:\n");
//        glColor3d(0.0,1.0,0.0);
	      handle_tetrahedron (c, i + 0, j + 0, k + 1,
				  i + 0, j + 1, k + 1,
				  i + 0, j + 1, k + 0,
				  i + 1, j + 0, k + 1, level);
//        printf("CYAN:\n");
//        glColor3d(0.0,1.0,1.0);
	      handle_tetrahedron (c, i + 1, j + 0, k + 0,
				  i + 1, j + 1, k + 0,
				  i + 0, j + 1, k + 0,
				  i + 1, j + 0, k + 1, level);
//        printf("BLUE:\n");
//        glColor3d(0.0,0.0,1.0);
	      handle_tetrahedron (c, i + 1, j + 1, k + 0,
				  i + 1, j + 1, k + 1,
				  i + 0, j + 1, k + 0,
				  i + 1, j + 0, k + 1, level);
//        printf("MAGENTA:\n");
//        glColor3d(1.0,0.0,1.0);
	      handle_tetrahedron (c, i + 0, j + 1, k + 1,
				  i + 1, j + 1, k + 1,
				  i + 0, j + 1, k + 0,
				  i + 1, j + 0, k + 1, level);

	    }
	}
    }
}

int
VisIsosurfaceDrawer::handle_tetrahedron (Chgcar * c, int a1, int a2, int a3,
					 int b1, int b2, int b3,
					 int c1, int c2, int c3,
					 int d1, int d2, int d3, double level)
{
  double posA[3];
  double posB[3];
  double posC[3];
  double posD[3];
  double nA[3];
  double nB[3];
  double nC[3];
  double nD[3];
  double A = c->get (a1, a2, a3) - level;
  double B = c->get (b1, b2, b3) - level;
  double C = c->get (c1, c2, c3) - level;
  double D = c->get (d1, d2, d3) - level;
//  printf("A  %3d %3d %3d %f\n",a1,a2,a3,A);
//  printf("B  %3d %3d %3d %f\n",b1,b2,b3,B);
//  printf("C  %3d %3d %3d %f\n",c1,c2,c3,C);
//  printf("D  %3d %3d %3d %f\n",d1,d2,d3,D);
  int type = 0;
  if (A > 0)
    type++;
  if (B > 0)
    type++;
  if (C > 0)
    type++;
  if (D > 0)
    type++;
//  printf("type=%d\n",type);
  if (type == 0 || type == 4)
    {
//    printf("return\n\n");
      return type;
    }

  copy3 (posA, c->structure->basis1);
  mul3 (posA, double (a1) / (c->nx));
  add3 (posA, double (a2) / (c->ny), c->structure->basis2);
  add3 (posA, double (a3) / (c->nz), c->structure->basis3);

  copy3 (posB, c->structure->basis1);
  mul3 (posB, double (b1) / (c->nx));
  add3 (posB, double (b2) / (c->ny), c->structure->basis2);
  add3 (posB, double (b3) / (c->nz), c->structure->basis3);

  copy3 (posC, c->structure->basis1);
  mul3 (posC, double (c1) / (c->nx));
  add3 (posC, double (c2) / (c->ny), c->structure->basis2);
  add3 (posC, double (c3) / (c->nz), c->structure->basis3);

  copy3 (posD, c->structure->basis1);
  mul3 (posD, double (d1) / (c->nx));
  add3 (posD, double (d2) / (c->ny), c->structure->basis2);
  add3 (posD, double (d3) / (c->nz), c->structure->basis3);

  c->getGrad (nA, a1, a2, a3);
  c->getGrad (nB, b1, b2, b3);
  c->getGrad (nC, c1, c2, c3);
  c->getGrad (nD, d1, d2, d3);

//  glColor3d(0.5,0.5,0.5);
  if (type == 3)
    {
      A *= -1;
      B *= -1;
      C *= -1;
      D *= -1;
      type = 1;
//    printf("inv\n");
    }

  if (type == 1)
    {
      if (A > 0)
	{
//      printf("1 ABCD\n\n");
	  handle_type1 (posA, posB, posC, posD, nA, nB, nC, nD, A, B, C, D);
	}
      else if (B > 0)
	{
//      printf("1 BCDA\n\n");
	  handle_type1 (posB, posC, posD, posA, nB, nC, nD, nA, B, C, D, A);
	}
      else if (C > 0)
	{
//      printf("1 CDAB\n\n");
	  handle_type1 (posC, posD, posA, posB, nC, nD, nA, nB, C, D, A, B);
	}
      else if (D > 0)
	{
//      printf("1 DABC\n\n");
	  handle_type1 (posD, posA, posB, posC, nD, nA, nB, nC, D, A, B, C);
	}
    }
  else
    {
      if ((A > 0) && (B > 0))
	{
//      printf("2 ABCD\n\n");
	  handle_type2 (posA, posB, posC, posD, nA, nB, nC, nD, A, B, C, D);
	}
      else if ((B > 0) && (C > 0))
	{
//      printf("2 BCDA\n\n");
	  handle_type2 (posB, posC, posD, posA, nB, nC, nD, nA, B, C, D, A);
	}
      else if ((C > 0) && (D > 0))
	{
//      printf("2 CDAB\n\n");
	  handle_type2 (posC, posD, posA, posB, nC, nD, nA, nB, C, D, A, B);
	}
      else if ((D > 0) && (A > 0))
	{
//      printf("2 DABC\n\n");
	  handle_type2 (posD, posA, posB, posC, nD, nA, nB, nC, D, A, B, C);
	}
      else if ((A > 0) && (C > 0))
	{
//      printf("2 ACBD\n\n");
	  handle_type2 (posA, posC, posB, posD, nA, nC, nB, nD, A, C, B, D);
	}
      else if ((B > 0) && (D > 0))
	{
//      printf("2 BDAC\n\n");
	  handle_type2 (posB, posD, posA, posC, nB, nD, nA, nC, B, D, A, C);
	}
    }
    return type;
}

int
VisIsosurfaceDrawer::handle_type1 (double *va, double *vb, double *vc,
				   double *vd, double *nA, double *nB,
				   double *nC, double *nD, double A, double B,
				   double C, double D)
{
  double pos1[3];
  double pos2[3];
  double pos3[3];
  double n1[3];
  double n2[3];
  double n3[3];
  double f;
  if ((A == B) || (A == C) || (A == D))
    {
      return -1;
    }
  f = B / (B - A);
  copy3 (pos1, va);
  mul3 (pos1, f);
  add3 (pos1, 1.0 - f, vb);
  copy3 (n1, nA);
  mul3 (n1, f);
  add3 (n1, 1.0 - f, nB);

  f = C / (C - A);
  copy3 (pos2, va);
  mul3 (pos2, f);
  add3 (pos2, 1.0 - f, vc);
  copy3 (n2, nA);
  mul3 (n2, f);
  add3 (n2, 1.0 - f, nC);

  f = D / (D - A);
  copy3 (pos3, va);
  mul3 (pos3, f);
  add3 (pos3, 1.0 - f, vd);
  copy3 (n3, nA);
  mul3 (n3, f);
  add3 (n3, 1.0 - f, nD);

/*
  printf("{\n");
  printf("va %+8.4f %+8.4f %+8.4f\n",va[0],va[1],va[2]);
  printf("vb %+8.4f %+8.4f %+8.4f\n",vb[0],vb[1],vb[2]);
  printf("vc %+8.4f %+8.4f %+8.4f\n",vc[0],vc[1],vc[2]);
  printf("}\n\n");

  printf("triangle{\n");
  printf(" %+8.4f %+8.4f %+8.4f\n",pos1[0],pos1[1],pos1[2]);
  printf(" %+8.4f %+8.4f %+8.4f\n",pos2[0],pos2[1],pos2[2]);
  printf(" %+8.4f %+8.4f %+8.4f\n",pos3[0],pos3[1],pos3[2]);
  printf("}\n\n");
  */
//  glColor3d(1.0,0.0,0.0);
  if (level>=0){
    glNormal3d (n1[0], n1[1], n1[2]);
    glVertex3d (pos1[0], pos1[1], pos1[2]);
    glNormal3d (n2[0], n2[1], n2[2]);
    glVertex3d (pos2[0], pos2[1], pos2[2]);
    glNormal3d (n3[0], n3[1], n3[2]);
    glVertex3d (pos3[0], pos3[1], pos3[2]);
  }
  else{
    glNormal3d (-n1[0], -n1[1], -n1[2]);
    glVertex3d (pos1[0], pos1[1], pos1[2]);
    glNormal3d (-n2[0], -n2[1], -n2[2]);
    glVertex3d (pos2[0], pos2[1], pos2[2]);
    glNormal3d (-n3[0], -n3[1], -n3[2]);
    glVertex3d (pos3[0], pos3[1], pos3[2]);
  }
  return 0;
}

int
VisIsosurfaceDrawer::handle_type2 (double *va, double *vb, double *vc,
				   double *vd, double *nA, double *nB,
				   double *nC, double *nD, double A, double B,
				   double C, double D)
{
  double posAC[3];
  double posAD[3];
  double posBC[3];
  double posBD[3];
  double nAC[3];
  double nAD[3];
  double nBC[3];
  double nBD[3];
  double f;
  if ((A == C) || (A == D) || (B == C) || (B == D))
    {
      return -1;
    }
  f = C / (C - A);
  copy3 (posAC, va);
  mul3 (posAC, f);
  add3 (posAC, 1 - f, vc);
  copy3 (nAC, nA);
  mul3 (nAC, f);
  add3 (nAC, 1 - f, nC);

  f = D / (D - A);
  copy3 (posAD, va);
  mul3 (posAD, f);
  add3 (posAD, 1 - f, vd);
  copy3 (nAD, nA);
  mul3 (nAD, f);
  add3 (nAD, 1 - f, nD);

  f = C / (C - B);
  copy3 (posBC, vb);
  mul3 (posBC, f);
  add3 (posBC, 1 - f, vc);
  copy3 (nBC, nB);
  mul3 (nBC, f);
  add3 (nBC, 1 - f, nC);

  f = D / (D - B);
  copy3 (posBD, vb);
  mul3 (posBD, f);
  add3 (posBD, 1 - f, vd);
  copy3 (nBD, nB);
  mul3 (nBD, f);
  add3 (nBD, 1 - f, nD);

  if (level>=0){
    //glColor3d(0.0,1.0,0.0);
    glNormal3d (nAC[0], nAC[1], nAC[2]);
    glVertex3d (posAC[0], posAC[1], posAC[2]);
    glNormal3d (nAD[0], nAD[1], nAD[2]);
    glVertex3d (posAD[0], posAD[1], posAD[2]);
    glNormal3d (nBC[0], nBC[1], nBC[2]);
    glVertex3d (posBC[0], posBC[1], posBC[2]);
    //glColor3d(0.0,0.0,1.0);
    glNormal3d (nAD[0], nAD[1], nAD[2]);
    glVertex3d (posAD[0], posAD[1], posAD[2]);
    glNormal3d (nBD[0], nBD[1], nBD[2]);
    glVertex3d (posBD[0], posBD[1], posBD[2]);
    glNormal3d (nBC[0], nBC[1], nBC[2]);
    glVertex3d (posBC[0], posBC[1], posBC[2]);
  }
  else{
    glNormal3d (-nAC[0], -nAC[1], -nAC[2]);
    glVertex3d (posAC[0], posAC[1], posAC[2]);
    glNormal3d (-nAD[0], -nAD[1], -nAD[2]);
    glVertex3d (posAD[0], posAD[1], posAD[2]);
    glNormal3d (-nBC[0], -nBC[1], -nBC[2]);
    glVertex3d (posBC[0], posBC[1], posBC[2]);
    //glColor3d(0.0,0.0,1.0);
    glNormal3d (-nAD[0], -nAD[1], -nAD[2]);
    glVertex3d (posAD[0], posAD[1], posAD[2]);
    glNormal3d (-nBD[0], -nBD[1], -nBD[2]);
    glVertex3d (posBD[0], posBD[1], posBD[2]);
    glNormal3d (-nBC[0], -nBC[1], -nBC[2]);
    glVertex3d (posBC[0], posBC[1], posBC[2]);
  }
  /*
     printf("rectangle{\n");
     printf(" %+8.4f %+8.4f %+8.4f\n",posAC[0],posAC[1],posAC[2]);
     printf(" %+8.4f %+8.4f %+8.4f\n",posAD[0],posAD[1],posAD[2]);
     printf(" %+8.4f %+8.4f %+8.4f\n",posBC[0],posBC[1],posBC[2]);
     printf(" %+8.4f %+8.4f %+8.4f\n",posBD[0],posBD[1],posBD[2]);
     printf("}\n\n");
   */
  return 0;
}

void VisIsosurfaceDrawer::setMultiple(int a,int b,int c){
  mx=a;
  my=b;
  mz=c;
  redraw();
}

void VisIsosurfaceDrawer::setMultiple1(int a){
  mx=a;
  redraw();
}

void VisIsosurfaceDrawer::setMultiple2(int a){
  my=a;
  redraw();
}

void VisIsosurfaceDrawer::setMultiple3(int a){
  mz=a;
  redraw();
}

int VisIsosurfaceDrawer::getMultiple1(){
  return mx;
}

int VisIsosurfaceDrawer::getMultiple2(){
  return my;
}

int VisIsosurfaceDrawer::getMultiple3(){
  return mz;
}


