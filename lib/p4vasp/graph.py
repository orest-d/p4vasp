#
# HappyDoc:docStringFormat='ClassicStructuredText'
#
#  p4vasp is a GUI-program and a library for processing outputs of the
#  Vienna Ab-inition Simulation Package (VASP)
#  (see http://cms.mpi.univie.ac.at/vasp/Welcome.html)
#
#  Copyright (C) 2003  Orest Dubay <odubay@users.sourceforge.net>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA



from math import *
from gtk import *
from p4vasp import *
from p4vasp.piddle.piddle import *
from types import *
from UserList import *
import re
import sys
import traceback
from string import split,strip

import copy

class Cloneable:
    def clone(self):
        return copy.deepcopy(self)

class GraphLine:
    def __init__(self,x1,y1,x2,y2,color=1,width=1.0):
        self.x1=x1
        self.y1=y1
        self.x2=x2
        self.y2=y2
        self.color=color
        self.width=width
    def render(self,canvas,graph):
        x1=graph.world2screenX(self.x1)
        y1=graph.world2screenY(self.y1)
        x2=graph.world2screenX(self.x2)
        y2=graph.world2screenY(self.y2)
        canvas.drawLine(x1,y1,x2,y2,graph.resolveColor(self.color),graph.resolveWidth(self.width))
    def exportGrace(self,f,i):
        f.write("""@with line
    @    line on
    @    line loctype world
    @    line g%d
    @    line %16.12f, %16.12f, %16.12f, %16.12f
    @    line linewidth %f
    @    line linestyle 1
    @    line color %d
    @    line arrow 0
    @    line arrow type 0
    @    line arrow length 1.000000
    @    line arrow layout 1.000000, 1.000000
    @line def
    """%(i,self.x1,self.y1,self.x2,self.y2,self.width,self.color))

class Set(UserList,Cloneable):
    hidden_false_p       = re.compile("hidden\\s+false\\s*$")
    hidden_true_p        = re.compile("hidden\\s+false\\s*$")
    type_p               = re.compile("type\\s+(.*)\\s*$")
    symbol_p             = re.compile("symbol\\s+(\\d+)")
    symbol_size_p        = re.compile("symbol\\s+size\\s+([0-9eE.+-]+)")
    symbol_color_p       = re.compile("symbol\\s+color\\s+(\\d+)")
    symbol_fill_color_p  = re.compile("symbol\\s+fill\\s+color\\s+(\\d+)")
    symbol_linewidth_p   = re.compile("symbol\\s+linewidth\\s+([0-9eE.+-]+)")
    line_p               = re.compile("line\\s+type\\s+(\\d+)")
    line_color_p         = re.compile("line\\s+color\\s+(\\d+)")
    line_linewidth_p     = re.compile("line\\s+linewidth\\s+([0-9eE.+-]+)")
    legend_p             = re.compile("legend\\s+\"(.*)\"")

    def __init__(self,data=[],graph=None):
        UserList.__init__(self,data)
        self.setGraph(graph)

        self.hidden=0
        self.type="xy"
        self.symbol=0
        self.symbol_size=1.0
        self.symbol_color=1
        self.symbol_fill_color=0
        self.symbol_linewidth=1.0
        self.line=1
        self.line_width=1.0
        self.line_color=1
        self.legend=0

    def clone(self):
        s=Set()

        for x in self.__dict__.keys():
            if x not in ["graph","world","resolveColor","encodeColor","resolveWidth","data"]:
                setattr(s,x,copy.deepcopy(getattr(self,x)))
        s.setGraph(self.graph)
        for d in self.data:
            s.append(tuple(d[:]))
        return s

    def setupFonts(self,canvas,world=None):
        pass

    def registerColors(self):
        self.graph.world.encodeColor(self.symbol_color)
        self.graph.world.encodeColor(self.symbol_fill_color)
        self.graph.world.encodeColor(self.line_color)

    def render(self,canvas,data=None):
        if not self.hidden:
            if data is None:
                data=self.data
            if self.line:
                lines=self.world.clipPolyline(
                        self.graph.world_xmin,self.graph.world_ymin,
                        self.graph.world_xmax,self.graph.world_ymax,
                        data)
                lines =map(lambda a,g=self.graph:
                            (g.world2screenX(a[0]),g.world2screenY(a[1]),
                             g.world2screenX(a[2]),g.world2screenY(a[3])),
                           lines)
                canvas.drawLines(lines)
                canvas.drawLines(lines,self.resolveColor(self.line_color),self.resolveWidth(self.line_width))
            if self.symbol:
                points=self.world.clipPoints(
                        self.graph.world_xmin,self.graph.world_ymin,
                        self.graph.world_xmax,self.graph.world_ymax,
                        data)
                drawsym=self.world.drawSymbol
                par=[canvas,None,None,self.symbol,self.symbol_size,
                     self.resolveColor(self.symbol_color),
                     self.resolveWidth(self.symbol_linewidth),
                     self.resolveColor(self.symbol_fill_color)]
                if self.type=="xy":
                    points=map(lambda a,g=self.graph:(g.world2screenX(a[0]),g.world2screenY(a[1])),
                               points)
                    for par[1],par[2] in points:
                        apply(drawsym,par)
                elif self.type=="xysize":
                    points=map(lambda a,g=self.graph,size=self.symbol_size:(g.world2screenX(a[0]),g.world2screenY(a[1]),size*a[2]),
                               points)
                    for par[1],par[2],par[4] in points:
#         for par[1],par[2],s in points:
                        apply(drawsym,par)


    def renderLegendLine(self,canvas,x0,y0,x1,y1):
        if self.line:
            canvas.drawLine(x0,y0,x1,y1,
              self.resolveColor(self.line_color),self.resolveWidth(self.line_width))
        if self.symbol:
            par=[canvas,None,None,self.symbol,self.symbol_size,
                 self.resolveColor(self.symbol_color),
                 self.resolveWidth(self.symbol_linewidth),
                 self.resolveColor(self.symbol_fill_color)]
            self.world.drawSymbol(canvas,x0,y0,self.symbol,self.symbol_size,
                 self.resolveColor(self.symbol_color),
                 self.resolveWidth(self.symbol_linewidth),
                 self.resolveColor(self.symbol_fill_color))
            self.world.drawSymbol(canvas,x1,y1,self.symbol,self.symbol_size,
                 self.resolveColor(self.symbol_color),
                 self.resolveWidth(self.symbol_linewidth),
                 self.resolveColor(self.symbol_fill_color))

    def setGraph(self,graph):
        self.graph=graph
        if isinstance(graph,Graph):
            self.world=graph.world
            if graph.world is not None:
                self.resolveColor=graph.world.resolveColor
                self.encodeColor =graph.world.encodeColor
                self.resolveWidth=graph.world.resolveWidth
            else:
                self.resolveColor=None
                self.resolveWidth=None
                self.encodeColor =None
        else:
            self.world=None
            self.resolveColor=None
            self.resolveWidth=None
            self.encodeColor =None

    def exportGrace(self,f,i):
        if self.hidden:
            f.write('@    s%d hidden true\n'%(i))
        else:
            f.write('@    s%d hidden false\n'%(i))
        f.write('@    s%d type %s\n'%(i,self.type))
        f.write('@    s%d symbol %d\n'%(i,self.symbol))
        f.write('@    s%d symbol size %f\n'%(i,self.symbol_size))
        f.write('@    s%d symbol color %d\n'%(i,self.encodeColor(self.symbol_color)))
        f.write('@    s%d symbol pattern 1\n'%(i))
        f.write('@    s%d symbol fill color %d\n'%(i,self.encodeColor(self.symbol_fill_color)))
        f.write('@    s%d symbol fill pattern 1\n'%(i))
        f.write('@    s%d symbol linewidth %f\n'%(i,self.symbol_linewidth))
        f.write('@    s%d symbol linestyle 1\n'%(i))
        f.write('@    s%d symbol char 65\n'%(i))
        f.write('@    s%d symbol char font 0\n'%(i))
        f.write('@    s%d symbol skip 0\n'%(i))
        f.write('@    s%d line type 1\n'%(i))
        f.write('@    s%d line linestyle %d\n'%(i,self.line))
        f.write('@    s%d line linewidth %f\n'%(i,self.line_width))
        f.write('@    s%d line color %d\n'%(i,self.encodeColor(self.line_color)))
        f.write('@    s%d line pattern 1\n'%(i))
        f.write('@    s%d baseline type 0\n'%(i))
        f.write('@    s%d baseline off\n'%(i))
        f.write('@    s%d dropline off\n'%(i))
        f.write('@    s%d fill type 0\n'%(i))
        f.write('@    s%d fill rule 0\n'%(i))
        f.write('@    s%d fill color 1\n'%(i))
        f.write('@    s%d fill pattern 1\n'%(i))
        f.write('@    s%d avalue off\n'%(i))
        f.write('@    s%d avalue type 2\n'%(i))
        f.write('@    s%d avalue char size 1.000000\n'%(i))
        f.write('@    s%d avalue font 0\n'%(i))
        f.write('@    s%d avalue color 1\n'%(i))
        f.write('@    s%d avalue rot 0\n'%(i))
        f.write('@    s%d avalue format general\n'%(i))
        f.write('@    s%d avalue prec 3\n'%(i))
        f.write('@    s%d avalue prepend ""\n'%(i))
        f.write('@    s%d avalue append ""\n'%(i))
        f.write('@    s%d avalue offset 0.000000 , 0.000000\n'%(i))
        f.write('@    s%d errorbar on\n'%(i))
        f.write('@    s%d errorbar place both\n'%(i))
        f.write('@    s%d errorbar color 1\n'%(i))
        f.write('@    s%d errorbar pattern 1\n'%(i))
        f.write('@    s%d errorbar size 1.000000\n'%(i))
        f.write('@    s%d errorbar linewidth 1.0\n'%(i))
        f.write('@    s%d errorbar linestyle 1\n'%(i))
        f.write('@    s%d errorbar riser linewidth 1.0\n'%(i))
        f.write('@    s%d errorbar riser linestyle 1\n'%(i))
        f.write('@    s%d errorbar riser clip off\n'%(i))
        f.write('@    s%d errorbar riser clip length 0.100000\n'%(i))
        f.write('@    s%d comment "dataset %d"\n'%(i,i))
        if self.legend:
            f.write('@    s%d legend  "%s"\n'%(i,self.legend))
        else:
            f.write('@    s%d legend  ""\n'%(i))

    def parseGraceStatement(self,s):
        #print "parse g%d.s%d: <%s>"%(self.graph.world.index(self.graph),
        #                            self.graph.index(self),s)

        m=self.hidden_false_p.match(s)
        if m:
            self.hidden=0
            return 1
        m=self.hidden_true_p.match(s)
        if m:
            self.hidden=1
            return 1
        m=self.type_p.match(s)
        if m:
            self.type=m.group(1)
            return 1
        m=self.symbol_p.match(s)
        if m:
            self.symbol=int(m.group(1))
            return 1
        m=self.symbol_size_p.match(s)
        if m:
            self.symbol_size=float(m.group(1))
            return 1
        m=self.symbol_color_p.match(s)
        if m:
            self.symbol_color=int(m.group(1))
            return 1
        m=self.symbol_fill_color_p.match(s)
        if m:
            self.symbol_fill_color=int(m.group(1))
            return 1
        m=self.symbol_linewidth_p.match(s)
        if m:
            self.symbol_width=float(m.group(1))
            return 1
        m=self.line_p.match(s)
        if m:
            self.line=int(m.group(1))
            return 1
        m=self.line_color_p.match(s)
        if m:
            self.line_color=int(m.group(1))
            return 1
        m=self.line_linewidth_p.match(s)
        if m:
            self.line_width=float(m.group(1))
            return 1
        m=self.legend_p.match(s)
        if m:
            self.legend=m.group(1)
            return 1
        return 0

    def exportGraceData(self,f,data=None):
        if data is None:
            data=self.data
        f.write('@type %s\n'%self.type)
        if self.type=="xy":
            for d in data:
                f.write('      %16.8g  %16.8g\n'%(d[0],d[1]))
        elif self.type=="xysize":
            for d in data:
                f.write('      %16.8g  %16.8g  %16.8g\n'%(d[0],d[1],d[2]))
        f.write('&\n')

    def cleanData(self):
        self.data=[]


class World(UserList,Cloneable):
#  tiny_font   = Font(size= 5.5,face="times")
#  small_font  = Font(size= 7.0,face="times")
#  medium_font = Font(size= 9.5,face="times")
#  large_font  = Font(size=16.5,face="times")
    tiny_font   = Font(size= 7,face="times")
    small_font  = Font(size=10,face="times")
    medium_font = Font(size=12,face="times")
    large_font  = Font(size=18,face="times")

    page_size_p=re.compile("@page\\s+size\\s+(\\d+)\\s*,\\s*(\\d+)")
    map_color_p=re.compile("@map\\s+color\\s+(\\d+)\\s+to\\s*"+
                           "\\("+
                           "\\s*(?P<red>\\d+)\\s*,"+
                           "\\s*(?P<green>\\d+)\\s*,"+
                           "\\s*(?P<blue>\\d+)\\s*\\)"+
                           "\\s*,\\s*\"(?P<name>.*)\"")
    background_color_p=re.compile(
                           "@background\\s+color\\s+(\\d+)")
    graph_head_p=re.compile("@g(\\d+)\\s+.*")
    with_g_p    =re.compile("@with\\s+g(\\d+)")
    with_block_p=re.compile("@\\s+.*")
    target_p    =re.compile("@target\\s+G(\\d+)\\.S(\\d+)")
    type_p      =re.compile("@type\\s+(.*)")

    def __init__(self,data=[]):
        UserList.__init__(self,data)
        self.background_color=0
        self.page_size_x=600
        self.page_size_y=400
        self.symbol_table=[
          self.drawNone,
          self.drawCircle,
          self.drawSquare,
          self.drawDiamond,
          self.drawTriangleUp,
          self.drawTriangleLeft,
          self.drawTriangleDown,
          self.drawTriangleRight,
          self.drawPlus,
          self.drawX,
          self.drawStar
        ]

        self.symbol_names=[
          "None",
          "Circle",
          "Square",
          "Diamond",
          "Triangle up",
          "Triangle left",
          "Triangle down",
          "Triangle right",
          "Plus",
          "X",
          "Star"
        ]

        self.color_table=[
          white,
          black,
          red,
          green,
          blue,
          yellow,
          brown,
          grey,
          violet,
          cyan,
          magenta,
          orange,
          indigo,
          maroon,
          turquoise,
          Color(0,139.0/255.0,0.0)
        ]

        self.color_names=[
          "white",
          "black",
          "red",
          "green",
          "blue",
          "yellow",
          "brown",
          "grey",
          "violet",
          "cyan",
          "magenta",
          "orange",
          "indigo",
          "maroon",
          "turquoise",
          "green4"
        ]
        for g in data:
            data.setWorld(self)

    def autotick(self):
        for g in self:
            g.autotick()

    def clone(self):
        w=World()
        for x in self.__dict__.keys():
            if x not in ["symbol_table","data"]:
#        print "clone World.%s"%x
                setattr(w,x,copy.deepcopy(getattr(self,x)))
        for g in self.data:
#      print "clone graph"
            w.append(g.clone())
        return w

    def identifyGraph(self,x,y):
        x=self.screen2viewX(x)
        y=self.screen2viewY(y)
        for g in self:
            if x>=g.view_xmin and x<=g.view_xmax:
                if y>=g.view_ymin and y<=g.view_ymax:
                    return g

    def identifyGraphIndex(self,x,y):
        x=self.screen2viewX(x)
        y=self.screen2viewY(y)
#    print "  view",x,y
        for i in range(len(self)):
            g=self[i]
#      print "  graph %2d: (%10.6f .. %10.6f), (%10.6f .. %10.6f)"%(i,g.view_xmin,g.view_xmax,g.view_ymin,g.view_ymax)
            if x>=g.view_xmin and x<=g.view_xmax:
                if y>=g.view_ymin and y<=g.view_ymax:
                    return i
        return None

    def setupFonts(self,canvas,face="times"):
        pass
    def setupFonts_old(self,canvas,face="times"):
        flag=0
        for ii in range(0,100):
            i0=60
            for i in [i0+ii,i0-ii]:
                font=Font(size=0.1*i,face=face)
                try:
                    canvas.drawString("test",30,30,font)
                    World.tiny_font=font
                    self.tiny_font=font
                    flag=1
                    break
                except:
                    pass
            if flag:
                break

        flag=0
        for ii in range(0,100):
            i0=70
            for i in [i0+ii,i0-ii]:
                font=Font(size=0.1*i,face=face)
                try:
                    canvas.drawString("test",30,30,font)
                    World.small_font=font
                    self.small_font=font
                    flag=1
                    break
                except:
                    pass
            if flag:
                break

        flag=0
        for ii in range(0,100):
            i0=110
            for i in [i0+ii,i0-ii]:
                font=Font(size=0.1*i,face=face)
                try:
                    canvas.drawString("test",30,30,font)
                    World.medium_font=font
                    self.medium_font=font
                    flag=1
                    break
                except:
                    pass
            if flag:
                break

        flag=0
        for ii in range(0,300):
            i0=170
            for i in [i0+ii,i0-ii]:
                font=Font(size=0.1*i,face=face)
                try:
                    canvas.drawString("test",30,30,font)
                    World.large_font=font
                    self.large_font=font
                    flag=1
                    break
                except:
                    pass
            if flag:
                break

        canvas.clear()
        for g in self:
            g.setupFonts(canvas,world=self)


    def viewAll(self,data=None):
        if data is None:
            for g in self:
                g.viewAll()
        else:
            for i in range(min(len(self),len(data))):
                self[i].viewAll(data[i])
    def viewAllX(self,data=None):
        if data is None:
            for g in self:
                g.viewAllX()
        else:
            for i in range(min(len(self),len(data))):
                self[i].viewAllX(data[i])
    def viewAllY(self,data=None):
        if data is None:
            for g in self:
                g.viewAllY()
        else:
            for i in range(min(len(self),len(data))):
                self[i].viewAllY(data[i])

    def cleanData(self):
        for x in self:
            x.cleanData()

    def parseGrace(self,f,closeflag=0):
        if type(f) is StringType:
            f=open(f,"r")
            closeflag=1

        self.color_table=[]
        self.color_names=[]
        errors=[]
        s=f.readline()
        while s!="":
#      print "parse",s
            try:
                m=self.page_size_p.match(s)
                if m:
                    self.page_size_x=int(m.group(1))
                    self.page_size_y=int(m.group(2))
                    s=f.readline()
                    continue

                m=self.map_color_p.match(s)
                if m:
                    c=Color(float(m.group("red"))/255.0,
                            float(m.group("green"))/255.0,
                            float(m.group("blue"))/255.0)
                    self.color_table.append(c)
                    self.color_names.append(m.group("name"))
                    s=f.readline()
                    continue

                m=self.background_color_p.match(s)
                if m:
                    self.background_color=int(m.group(1))
                    s=f.readline()
                    continue

                m=self.graph_head_p.match(s)
                g=None
                if m:
                    g=int(m.group(1))
                    if len(self)<=g:
                        for i in range(len(self),g+1):
                            self.append(Graph())
                    self[g].parseGraceStatement(s)

                m=self.with_g_p.match(s)
                if m:
                    g=int(m.group(1))
                    if len(self)<=g:
                        for i in range(len(self),g+1):
                            self.append(Graph())
                    s=f.readline()
                    while s!="":
                        if not self.with_block_p.match(s):
                            break
                        try:
                            self[g].parseGraceStatement(s)
                        except:
                            errors.append((s,sys.exc_info()))
                        s=f.readline()
                    continue

                m=self.target_p.match(s)
                if m:
                    g     =int(m.group(1))
                    setnum=int(m.group(2))
                    if len(self)<=g:
                        for i in range(len(self),g+1):
                            self.append(Graph())
                    if len(self[g])<=setnum:
                        for i in range(len(self[g]),setnum+1):
                            self[g].append(Set())
                    set=self[g][setnum]
                    s=f.readline()
                    while s!="":
                        if strip(s)=="&":
                            break
                        m=self.type_p.match(s)
                        if m:
                            set.parseGraceStatement(s)
                            s=f.readline()
                            continue

                        try:
                            if set.type=="xy":
                                set.append(map(float,split(s)[:2]))
                            elif set.type=="xysize":
                                set.append(map(float,split(s)[:3]))

                        except:
                            errors.append((s,sys.exc_info()))
                        s=f.readline()
                    s=f.readline()
                    continue

            except:
                errors.append((s,sys.exc_info()))
            s=f.readline()

        for s,e in errors:
            msg().error("Graph parsing error:%s"%s)
            #apply(traceback.print_exception,e)
        if closeflag:
            f.close()
        return errors

    def render(self,canvas,data=None):
        c=self.resolveColor(self.background_color)
        canvas.drawRect(0,0,max(canvas.size[0],self.page_size_x),
                            max(canvas.size[1],self.page_size_y),c,1,c)
        if data is None:
            for g in self:
                g.render(canvas)
        else:
#      for i in range(min(len(self),len(data))):
#        self[i].render(canvas,data[i])
            for i in range(len(self)):
                if len(data)>i:
                    self[i].render(canvas,data[i])
                else:
                    self[i].render(canvas,[])

    def clipLines(self,x1,y1,x2,y2,lines):
        tiny=1e-10
        if x1>x2:
            s=x1
            x1=x2
            x2=s
        if y1>y2:
            s=y1
            y1=y2
            y2=s

        l=[]

        for xx1,yy1,xx2,yy2 in lines:
            dx=float(xx2-xx1)
            dy=float(yy2-yy1)

            if abs(dx)<tiny:
                if yy1>yy2:
                    s   = yy1
                    yy1 = yy2
                    yy2 = s
                    s   = xx1
                    xx1 = xx2
                    xx2 = s

                if (xx1<x1) or (xx1>x2): continue
                yy1=max(yy1,y1)
                if yy1>y2: continue
                yy2=min(yy2,y2)
                if yy2<y1: continue
                l.append((xx1,yy1,xx2,yy2))
                continue

            if abs(dy)<tiny:
                if xx1>xx2:
                    s   = yy1
                    yy1 = yy2
                    yy2 = s
                    s   = xx1
                    xx1 = xx2
                    xx2 = s

                if (yy1<y1) or (yy1>y2): continue
                xx1=max(xx1,x1)
                if xx1>x2: continue
                xx2=min(xx2,x2)
                if xx2<x1: continue
                l.append((xx1,yy1,xx2,yy2))
                continue

            a=dy/dx
            b=yy1-a*xx1

            if xx1<x1:
                if xx2<=x1:
                    continue
                else:
                    xx1=x1
                    yy1=a*x1+b
            else:
                if xx2<x1:
                    xx2=x1
                    yy2=a*x1+b

            if xx1>x2:
                if xx2>=x2:
                    continue
                else:
                    xx1=x2
                    yy1=a*x2+b
            else:
                if xx2>x2:
                    xx2=x2
                    yy2=a*x2+b

            if yy1<y1:
                if yy2<=y1:
                    continue
                else:
                    xx1=(y1-b)/a
                    yy1=y1
            else:
                if yy2<y1:
                    xx2=(y1-b)/a
                    yy2=y1

            if yy1>y2:
                if yy2>=y2:
                    continue
                else:
                    xx1=(y2-b)/a
                    yy1=y2
            else:
                if yy2>y2:
                    xx2=(y2-b)/a
                    yy2=y2

            l.append((xx1,yy1,xx2,yy2))
        return l

    def clipPolyline(self,x1,y1,x2,y2,points):
        tiny=1e-10
        if x1>x2:
            s=x1
            x1=x2
            x2=s
        if y1>y2:
            s=y1
            y1=y2
            y2=s

        l=[]

        for i in range(1,len(points)):
            xx1,yy1=points[i-1][0],points[i-1][1]
            xx2,yy2=points[i][0],points[i][1]

            dx=float(xx2-xx1)
            dy=float(yy2-yy1)

            if abs(dx)<tiny:
                if yy1>yy2:
                    s   = yy1
                    yy1 = yy2
                    yy2 = s
                    s   = xx1
                    xx1 = xx2
                    xx2 = s

                if (xx1<x1) or (xx1>x2): continue
                yy1=max(yy1,y1)
                if yy1>y2: continue
                yy2=min(yy2,y2)
                if yy2<y1: continue
                l.append((xx1,yy1,xx2,yy2))
                continue

            if abs(dy)<tiny:
                if xx1>xx2:
                    s   = yy1
                    yy1 = yy2
                    yy2 = s
                    s   = xx1
                    xx1 = xx2
                    xx2 = s

                if (yy1<y1) or (yy1>y2): continue
                xx1=max(xx1,x1)
                if xx1>x2: continue
                xx2=min(xx2,x2)
                if xx2<x1: continue
                l.append((xx1,yy1,xx2,yy2))
                continue

            a=dy/dx
            b=yy1-a*xx1

            if xx1<x1:
                if xx2<=x1:
                    continue
                else:
                    xx1=x1
                    yy1=a*x1+b
            else:
                if xx2<x1:
                    xx2=x1
                    yy2=a*x1+b

            if xx1>x2:
                if xx2>=x2:
                    continue
                else:
                    xx1=x2
                    yy1=a*x2+b
            else:
                if xx2>x2:
                    xx2=x2
                    yy2=a*x2+b

            if yy1<y1:
                if yy2<=y1:
                    continue
                else:
                    xx1=(y1-b)/a
                    yy1=y1
            else:
                if yy2<y1:
                    xx2=(y1-b)/a
                    yy2=y1

            if yy1>y2:
                if yy2>=y2:
                    continue
                else:
                    xx1=(y2-b)/a
                    yy1=y2
            else:
                if yy2>y2:
                    xx2=(y2-b)/a
                    yy2=y2

            l.append((xx1,yy1,xx2,yy2))
        return l

    def clipPoints(self,x1,y1,x2,y2,points):
        p=[]
        if x1>x2:
            s=x1
            x1=x2
            x2=s
        if y1>y2:
            s=y1
            y1=y2
            y2=s
        for pp in points:
            if pp[0]<x1:continue
            if pp[0]>x2:continue
            if pp[1]<y1:continue
            if pp[1]>y2:continue
            p.append(pp)
        return p

    def drawSymbol(self,canvas,x,y,symbol=0,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        if type(symbol) is StringType:
            symbol=self.symbol_names.index(symbol)
        if type(symbol) is IntType:
            symbol=self.symbol_table[symbol]
        symbol(canvas,x,y,size,edgeColor,edgeWidth,fillColor)

    def drawNone(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        pass

    def drawSquare(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size*0.9
    #  canvas.drawRect(x-ds,y-ds,x+ds,y+ds,edgeColor,edgeWidth,fillColor)
        canvas.drawPolygon([(x-ds,y-ds),(x-ds,y+ds),(x+ds,y+ds),(x+ds,y-ds)],edgeColor,edgeWidth,fillColor,1)

    def drawTriangleDown(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size
        v=sqrt(3)*ds/3.0
        canvas.drawPolygon([(x-ds,y-v),(x,y+2*v),(x+ds,y-v)],edgeColor,edgeWidth,fillColor,1)

    def drawTriangleUp(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size
        v=sqrt(3)*ds/3.0
        canvas.drawPolygon([(x-ds,y+v),(x,y-2*v),(x+ds,y+v)],edgeColor,edgeWidth,fillColor,1)

    def drawTriangleLeft(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size
        v=sqrt(3)*ds/3.0
        canvas.drawPolygon([(x+v,y-ds),(x-2*v,y),(x+v,y+ds)],edgeColor,edgeWidth,fillColor,1)

    def drawTriangleRight(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size
        v=sqrt(3)*ds/3.0
        canvas.drawPolygon([(x-v,y-ds),(x+2*v,y),(x-v,y+ds)],edgeColor,edgeWidth,fillColor,1)

    def drawDiamond(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size*1.1
        v=sqrt(3)*ds/3.0
        canvas.drawPolygon([(x-ds,y),(x,y+ds),(x+ds,y),(x,y-ds)],edgeColor,edgeWidth,fillColor,1)

    def drawPlus(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size*0.9
        v=sqrt(3)*ds/3.0
        canvas.drawLines([(x-ds,y,x+ds+1,y),(x,y+ds+1,x,y-ds)],edgeColor,edgeWidth)

    def drawX(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size*1.1
        #v=sqrt(3)*ds/3.0
        canvas.drawLines([(x-ds,y-ds,x+ds,y+ds),(x-ds,y+ds,x+ds,y-ds)],edgeColor,edgeWidth)

    def drawStar(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size*1.1
        sq=ds/sqrt(2.0)
        canvas.drawLines([(x-ds,y   ,x+ds,y   ),
                          (x   ,y+ds,x   ,y-ds),
                          (x+sq,y+sq,x-sq,y-sq),
                          (x+sq,y-sq,x-sq,y+sq)],edgeColor,edgeWidth)

    def drawCircle(self,canvas,x,y,size=1,edgeColor=black,edgeWidth=1,fillColor=white):
        size*=4
        ds=size
        v=sqrt(3)*ds/3.0
        canvas.drawEllipse(x-ds,y-ds,x+ds,y+ds,edgeColor,edgeWidth,fillColor)

    def resolveColor(self,c):
        if type(c) is IntType:
            return self.color_table[c]
        if type(c) is StringType:
            return self.color_table[self.color_names.index(c)]
        if isinstance(c,Color):
            return c
        return Color(0.5,0.5,0.5)

    def encodeColor(self,c,name=None):
        if type(c) is IntType:
            return c
        if type(c) is StringType:
            return self.color_names.index(c)
        if c in self.color_table:
            return self.color_table.index(c)
        if not name:
            name="(%3d,%3d,%3d)"%(int(255*c.red),int(255*c.green),int(255*c.blue))
        i=len(self.color_table)
        self.color_table.append(c)
        self.color_names.append(name)
        return i

    def resolveWidth(self,x):
        return int(x)

    def view2screenX(self,x):
        return x*self.page_size_x*0.7
    def view2screenY(self,y):
        return (1.0-y)*self.page_size_y

    def screen2viewX(self,x):
        return float(x)/float(self.page_size_x)/0.7
    def screen2viewY(self,y):
        return 1.0-float(y)/float(self.page_size_y)

    def append(self,g):
        self.data.append(g)
        g.setWorld(self)
    def extend(self,l):
        self.data.extend(l)
        for g in l:
            g.setWorld(self)

    def registerColors(self):
        Color(self.background_color)
        for x in self:
            x.registerColors()

    def exportGrace(self,f,closeflag=0,data=1):
        if type(f) is StringType:
            f=open(f,"w")
            closeflag=1
        self.registerColors()
        f.write("""# Grace project file
    #
    # generated by p4vasp.graph,
    # author: Orest Dubay; dubay@ap.univie.ac.at
    #
    @version 50104
    """)
        f.write("@page size %d, %d\n"%(self.page_size_x,self.page_size_y))
        f.write("""@page scroll 5%
    @page inout 5%
    @link page off
    @map font 0 to "Times-Roman", "Times-Roman"
    @map font 1 to "Times-Italic", "Times-Italic"
    @map font 2 to "Times-Bold", "Times-Bold"
    @map font 3 to "Times-BoldItalic", "Times-BoldItalic"
    @map font 4 to "Helvetica", "Helvetica"
    @map font 5 to "Helvetica-Oblique", "Helvetica-Oblique"
    @map font 6 to "Helvetica-Bold", "Helvetica-Bold"
    @map font 7 to "Helvetica-BoldOblique", "Helvetica-BoldOblique"
    @map font 8 to "Courier", "Courier"
    @map font 9 to "Courier-Oblique", "Courier-Oblique"
    @map font 10 to "Courier-Bold", "Courier-Bold"
    @map font 11 to "Courier-BoldOblique", "Courier-BoldOblique"
    @map font 12 to "Symbol", "Symbol"
    @map font 13 to "ZapfDingbats", "ZapfDingbats"
    """)
        for i in range(0,len(self.color_table)):
            c=self.color_table[i]
            r=int(255*c.red)
            g=int(255*c.green)
            b=int(255*c.blue)
            f.write('@map color %d to (%d, %d, %d), "%s"\n'%(i,r,g,b,self.color_names[i]))
        f.write("""@reference date 0
    @date wrap off
    @date wrap year 1950
    @default linewidth 1.0
    @default linestyle 1
    @default color 1
    @default pattern 1
    @default font 0
    @default char size 1.000000
    @default symbol size 1.000000
    @default sformat "%16.8g"
    """)

        f.write("""@background color %d
    @page background fill on
    """%self.encodeColor(self.background_color))

        for i in range(0,len(self)):
            for l in self[i].graph_lines:
                l.exportGrace(f,i)

        for i in range(0,len(self)):
            self[i].exportGrace(f,i)
        if data!=0:
            if type(data) is IntType:
                for i in range(0,len(self)):
                    self[i].exportGraceData(f,i)
            else:
                for i in range(len(data)):
                    self[i].exportGraceData(f,i,data[i])


        if closeflag:
            f.close()



class Axis(Cloneable):
    bar_on_p          = re.compile("bar\\s+on\\s*$")
    bar_off_p         = re.compile("bar\\s+off\\s*$")
    bar_color_p       = re.compile("bar\\s+color\\s+(\\d+)")
    bar_linewidth_p   = re.compile("bar\\s+linewidth\\s+([0-9eE.+-]+)")
    label_p           = re.compile("label\\s+\"(.*)\"")
    label_color_p     = re.compile("label\\s+color\\s+(\\d+)")
    tick_on_p         = re.compile("tick\\s+on\\s*$")
    tick_off_p        = re.compile("tick\\s+off\\s*$")
    major_p           = re.compile("tick\\s+major\\s+([0-9eE.+-]+)")
    minor_p           = re.compile("tick\\s+minor\\s+ticks\\s+(\\d+)")
    major_size_p      = re.compile("tick\\s+major\\s+size\\s+([0-9eE.+-]+)")
    major_linewidth_p = re.compile("tick\\s+major\\s+linewidth\\s+([0-9eE.+-]+)")
    major_color_p     = re.compile("tick\\s+major\\s+color\\s+(\\d+)")
    minor_size_p      = re.compile("tick\\s+minor\\s+size\\s+([0-9eE.+-]+)")
    minor_linewidth_p = re.compile("tick\\s+minor\\s+linewidth\\s+([0-9eE.+-]+)")
    minor_color_p     = re.compile("tick\\s+minor\\s+color\\s+(\\d+)")
    orientation_in_p  = re.compile("tick\\s+in\\s*$")
    orientation_out_p = re.compile("tick\\s+out\\s*$")
    orientation_both_p= re.compile("tick\\s+both\\s*$")
    ticklabel_on_p    = re.compile("ticklabel\\s+on\\s*$")
    ticklabel_off_p   = re.compile("ticklabel\\s+off\\s*$")
    ticklabel_color_p = re.compile("ticklabel\\s+color\\s+(\\d+)")

    def __init__(self,graph):
        self.bar=1
        self.bar_color=1
        self.bar_width=1
        self.label="Axis"
        self.label_font=World.medium_font
        self.label_color=1

        self.tick=1
        self.major=0.5
        self.major_size = 1.0
        self.major_color= 1
        self.major_width= 1

        self.minor=1
        self.orientation="in"
        self.minor_size = 0.5
        self.minor_color= 1
        self.minor_width= 1

        self.ticklabel=1
        self.ticklabel_font=World.medium_font
        self.ticklabel_color=1

        self.setGraph(graph)

    def clone(self):
        a=apply(self.__class__,(self.graph))
        a.setAxis(self)
        return a

    def autotick(self):
        if self.major or self.minor:
            w=self.getWorldSize()
            if w==0:
                return None
            ticks=self.estimateTicksCount()
            d=w/ticks
            order=(10.0**int(log10(d)))
            d/=order
            if d<1:
                order/=10.0
                d*=10.0
            if d<4:
                major=2*order
                minor=1
            else:
                major=5*order
                minor=4
            if self.major:
                self.major=major
            if self.minor:
                self.minor=minor

    def parseGraceStatement(self,s):
        m=self.bar_on_p.match(s)
        if m:
            self.bar=1
            return 1
        m=self.bar_off_p.match(s)
        if m:
            self.bar=0
            return 1
        m=self.bar_color_p.match(s)
        if m:
            self.bar_color=int(m.group(1))
            return 1
        m=self.bar_linewidth_p.match(s)
        if m:
            self.bar_width=float(m.group(1))
            return 1
        m=self.label_p.match(s)
        if m:
            self.label=m.group(1)
            return 1
        m=self.label_color_p.match(s)
        if m:
            self.label_color=int(m.group(1))
            return 1
        m=self.tick_off_p.match(s)
        if m:
            self.tick=0
            return 1
        m=self.tick_on_p.match(s)
        if m:
            self.tick=1
            return 1
        m=self.major_p.match(s)
        if m:
            self.major=float(m.group(1))
            return 1
        m=self.minor_p.match(s)
        if m:
            self.minor=int(m.group(1))
            return 1
        m=self.major_size_p.match(s)
        if m:
            self.major_size=float(m.group(1))
            return 1
        m=self.major_linewidth_p.match(s)
        if m:
            self.major_width=float(m.group(1))
            return 1
        m=self.major_color_p.match(s)
        if m:
            self.major_color=int(m.group(1))
            return 1
        m=self.minor_size_p.match(s)
        if m:
            self.minor_size=float(m.group(1))
            return 1
        m=self.minor_linewidth_p.match(s)
        if m:
            self.minor_width=float(m.group(1))
            return 1
        m=self.minor_color_p.match(s)
        if m:
            self.minor_color=int(m.group(1))
            return 1
        m=self.orientation_in_p.match(s)
        if m:
            self.orientation="in"
            return 1
        m=self.orientation_out_p.match(s)
        if m:
            self.orientation="out"
            return 1
        m=self.orientation_both_p.match(s)
        if m:
            self.orientation="both"
            return 1
        m=self.ticklabel_on_p.match(s)
        if m:
            self.ticklabel=1
            return 1
        m=self.ticklabel_off_p.match(s)
        if m:
            self.ticklabel=0
            return 1
        m=self.ticklabel_color_p.match(s)
        if m:
            self.ticklabel_color=int(m.group(1))
            return 1

        return 0

    def setAxis(self,a):
        self.bar             = a.bar
        self.bar_color       = a.bar_color
        self.bar_width       = a.bar_width
        self.label           = a.label
        self.label_font      = a.label_font
        self.label_color     = a.label_color

        self.major           = a.major
        self.major_size      = a.major_size
        self.major_color     = a.major_color
        self.major_width     = a.major_width

        self.minor           = a.minor
        self.orientation     = a.orientation
        self.minor_size      = a.minor_size
        self.minor_color     = a.minor_color
        self.minor_width     = a.minor_width

        self.tick            = a.tick
        self.ticklabel       = a.ticklabel
        self.ticklabel_font  = a.ticklabel_font
        self.ticklabel_color = a.ticklabel_color

        self.setGraph(a.graph)

    def setupFonts(self,canvas,world=None):
        if world is None:
            if self.graph is not None:
                world=self.graph.world
        self.label_font      =world.medium_font
        self.ticklabel_font  =world.medium_font

    def setGraph(self,graph):
        self.graph=graph
        if graph:
            self.world           =graph.world
            self.resolveColor    =graph.world.resolveColor
            self.resolveWidth    =graph.world.resolveWidth
        else:
            self.world=None
            self.resolveColor=None
            self.resolveWidth=None

    def registerColors(self):
        self.graph.encodeColor(self.bar_color)
        self.graph.encodeColor(self.label_color)
        self.graph.encodeColor(self.major_color)
        self.graph.encodeColor(self.minor_color)
        self.graph.encodeColor(self.ticklabel_color)

    def exportGrace(self,f):
        f.write("""@    %s  on
    @    %s  type zero false
    @    %s  offset 0.000000 , 0.000000
    """%(self.axis,self.axis,self.axis))
        if self.bar:
            f.write("@    %s  bar on\n"%self.axis)
        else:
            f.write("@    %s  bar off\n"%self.axis)
        f.write("@    %s  bar color %d\n"%(self.axis,self.graph.encodeColor(self.bar_color)))
        f.write("@    %s  bar linestyle 1\n"%(self.axis))
        f.write("@    %s  bar linewidth %f\n"%(self.axis,self.bar_width))
        f.write('@    %s  label "%s"\n'%(self.axis,self.label))
        f.write('@    %s  label layout para\n'%(self.axis))
        f.write('@    %s  label place auto\n'%(self.axis))
        f.write('@    %s  label char size 1.0\n'%(self.axis))
        f.write('@    %s  label font 0\n'%(self.axis))
        f.write('@    %s  label color %d\n'%(self.axis,self.graph.encodeColor(self.label_color)))
        f.write('@    %s  label place normal\n'%(self.axis))

        if self.tick:
            f.write('@    %s  tick on\n'%(self.axis))
        else:
            f.write('@    %s  tick off\n'%(self.axis))
        f.write('@    %s  tick major %f\n'%(self.axis,self.major))
        f.write('@    %s  tick minor ticks %d\n'%(self.axis,self.minor))
        f.write('@    %s  tick default 6\n'%(self.axis))
        f.write('@    %s  tick place rounded true\n'%(self.axis))
        f.write('@    %s  tick %s\n'%(self.axis,self.orientation))

        f.write('@    %s  tick major size %f\n'%(self.axis,self.major_size))
        f.write('@    %s  tick major color %d\n'%(self.axis,self.graph.encodeColor(self.major_color)))
        f.write('@    %s  tick major linewidth %d\n'%(self.axis,self.major_width))
        f.write('@    %s  tick major linestyle 1\n'%(self.axis))
        f.write('@    %s  tick major grid off\n'%(self.axis))

        f.write('@    %s  tick minor color %d\n'%(self.axis,self.graph.encodeColor(self.minor_color)))
        f.write('@    %s  tick minor linewidth %d\n'%(self.axis,self.minor_width))
        f.write('@    %s  tick minor linestyle 1\n'%(self.axis))
        f.write('@    %s  tick minor grid off\n'%(self.axis))
        f.write('@    %s  tick minor size %f\n'%(self.axis,self.minor_size))

        if self.ticklabel:
            f.write('@    %s  ticklabel on\n'%(self.axis))
        else:
            f.write('@    %s  ticklabel off\n'%(self.axis))
        f.write('@    %s  ticklabel format general\n'%(self.axis))
        f.write('@    %s  ticklabel prec 5\n'%(self.axis))
        f.write('@    %s  ticklabel formula ""\n'%(self.axis))
        f.write('@    %s  ticklabel append ""\n'%(self.axis))
        f.write('@    %s  ticklabel prepend ""\n'%(self.axis))
        f.write('@    %s  ticklabel angle 0\n'%(self.axis))
        f.write('@    %s  ticklabel skip 0\n'%(self.axis))
        f.write('@    %s  ticklabel stagger 0\n'%(self.axis))
        f.write('@    %s  ticklabel place normal\n'%(self.axis))
        f.write('@    %s  ticklabel offset auto\n'%(self.axis))
        f.write('@    %s  ticklabel offset 0.00, 0.00\n'%(self.axis))
        f.write('@    %s  ticklabel start type auto\n'%(self.axis))
        f.write('@    %s  ticklabel start 0.000000\n'%(self.axis))
        f.write('@    %s  ticklabel stop type auto\n'%(self.axis))
        f.write('@    %s  ticklabel stop 0.000000\n'%(self.axis))
        f.write('@    %s  ticklabel char size 1.0\n'%(self.axis))
        f.write('@    %s  ticklabel font 0\n'%(self.axis))
        f.write('@    %s  ticklabel color %d\n'%(self.axis,self.graph.encodeColor(self.ticklabel_color)))
        f.write('@    %s  tick place both\n'%(self.axis))
        f.write('@    %s  tick spec type none\n'%(self.axis))

class XAxis(Axis):
    def __init__(self,graph):
        Axis.__init__(self,graph)
        self.axis="xaxis"
        self.label="X Axis"
        self.position="down"

    def getWorldSize(self):
        return abs(self.graph.world_xmin-self.graph.world_xmax)
    def estimateTicksCount(self):
        return abs(self.graph.getScreenXmin()-self.graph.getScreenXmax())/85

    def render(self,canvas):
        self.setupFonts(canvas)
        if self.label:
            if self.position=="down":
                label=self.label
                w=canvas.stringWidth(label,self.label_font)
                h=canvas.fontHeight(self.label_font)
                hh=canvas.fontHeight(self.ticklabel_font)
                x=(self.graph.getScreenXmin()+self.graph.getScreenXmax()-w)/2
                y=self.graph.getScreenYmin()+(h)*1.1+hh*1.3

                canvas.drawString(label,x,y,self.label_font,
                  self.graph.resolveColor(self.label_color))
        if self.position=="down":
            pos=self.graph.getScreenYmin()
        elif self.position=="up":
            pos=self.graph.getScreenYmax()
        else:
            pos=self.graph.world2screenY(self.position)

        if self.bar:
            canvas.drawLine(self.graph.getScreenXmin(),pos,
                            self.graph.getScreenXmax(),pos,
                            self.graph.resolveColor(self.bar_color),
                            self.graph.resolveWidth(self.bar_width))

        ts=10

        if self.tick:
            dp =ts*self.major_size
            dpm=ts*self.minor_size
            if self.orientation=="both":
                tpos=pos-dp
                tposm=pos-dpm
                dp*=2
                dpm*=2
            else:
                tpos=pos
                tposm=pos
                if self.position=="down":
                    if self.orientation=="in":
                        dp*=-1
                        dpm*=-1
                elif self.position=="up":
                    if self.orientation=="out":
                        dp*=-1
                        dpm*=-1

            m=self.major
            mm=m/(self.minor+1)

            c  = self.graph.resolveColor(self.major_color)
            cm = self.graph.resolveColor(self.minor_color)
            cl = self.graph.resolveColor(self.ticklabel_color)
            hl = canvas.fontHeight(self.ticklabel_font)
            w  = self.graph.resolveWidth(self.major_width)
            wm = self.graph.resolveWidth(self.minor_width)
            for i in range(int(self.graph.world_xmin/m)-1,
                           int(self.graph.world_xmax/m)+2):
                a=i*m
                if (a>=self.graph.world_xmin) and (a<=self.graph.world_xmax):
                    aa=self.graph.world2screenX(a)
                    canvas.drawLine(aa,tpos,aa,tpos+dp,c,w)
                    if self.ticklabel:
                        s=str(a)
                        wl=canvas.stringWidth(s,self.ticklabel_font)
                        canvas.drawString(s,aa-wl/2,tpos+hl*1.2,self.ticklabel_font,cl)
                if self.minor:
                    for j in range(1,self.minor+1):
                        am=a+j*mm
                        if (am>=self.graph.world_xmin) and (am<=self.graph.world_xmax):
                            aam=self.graph.world2screenX(am)
                            canvas.drawLine(aam,tposm,aam,tposm+dpm,cm,wm)


class YAxis(Axis):
    def __init__(self,graph):
        Axis.__init__(self,graph)
        self.axis="yaxis"
        self.label="Y Axis"
        self.position="left"

    def getWorldSize(self):
        return abs(self.graph.world_ymin-self.graph.world_ymax)
    def estimateTicksCount(self):
        return abs(self.graph.getScreenYmin()-self.graph.getScreenYmax())/30

    def render(self,canvas):
        self.setupFonts(canvas)
        z=1.0
        if self.label:
            if self.position=="left":
                label=self.label
                w=canvas.stringWidth(label,self.label_font)
                h=canvas.fontHeight(self.label_font)
#       x=self.graph.getScreenXmin()-w*1.1
#       y=(self.graph.getScreenYmin()+self.graph.getScreenYmax()+h)/2
                x=self.graph.getScreenXmin()-canvas.stringWidth("0.00",self.label_font)
                y=self.graph.getScreenYmax()-h*1.0

                canvas.drawString(label,x,y,self.label_font,
                  self.graph.resolveColor(self.label_color))
        if self.position=="left":
            pos=self.graph.getScreenXmin()
        elif self.position=="right":
            pos=self.graph.getScreenXmax()
        else:
            pos=self.graph.world2screenX(self.position)

        if self.bar:
            canvas.drawLine(pos,self.graph.getScreenYmin(),
                            pos,self.graph.getScreenYmax(),
                            self.graph.resolveColor(self.bar_color),
                            self.graph.resolveWidth(self.bar_width))

        ts=10

        if self.tick:
            dp =ts*self.major_size*z
            dpm=ts*self.minor_size*z
            if self.orientation=="both":
                tpos=pos-dp
                tposm=pos-dpm
                dp*=2
                dpm*=2
            else:
                tpos=pos
                tposm=pos
                if self.position=="left":
                    if self.orientation=="out":
                        dp*=-1
                        dpm*=-1
                elif self.position=="right":
                    if self.orientation=="in":
                        dp*=-1
                        dpm*=-1

            m=self.major
            mm=m/(self.minor+1)

            c  = self.graph.resolveColor(self.major_color)
            cm = self.graph.resolveColor(self.minor_color)
            cl = self.graph.resolveColor(self.ticklabel_color)
            hl = canvas.fontHeight(self.ticklabel_font)
            w  = self.graph.resolveWidth(self.major_width)
            wm = self.graph.resolveWidth(self.minor_width)
            for i in range(int(self.graph.world_ymin/m)-1,
                           int(self.graph.world_ymax/m)+2):
                a=i*m
                if (a>=self.graph.world_ymin) and (a<=self.graph.world_ymax):
                    aa=self.graph.world2screenY(a)
                    canvas.drawLine(tpos,aa,tpos+dp,aa,c,w)
                    if self.ticklabel:
                        s=str(a)
                        wl=canvas.stringWidth(s,self.ticklabel_font)
                        canvas.drawString(s,tpos-wl-5*z,aa+hl/2,self.ticklabel_font,cl)
                if self.minor:
                    for j in range(1,self.minor+1):
                        am=a+j*mm
                        if (am>=self.graph.world_ymin) and (am<=self.graph.world_ymax):
                            aam=self.graph.world2screenY(am)
                            canvas.drawLine(tposm,aam,tposm+dpm,aam,cm,wm)




class Graph(UserList,Cloneable):
    world_p          = re.compile("@\\s+world\\s+([0-9eE.+-]+)\\s+([0-9eE.+-]+)\\s+([0-9eE.+-]+)\\s+([0-9eE.+-]+)")
    world_xmin_p     = re.compile("@\\s+world\\s+xmin\\s+([0-9eE.+-]+)")
    world_xmax_p     = re.compile("@\\s+world\\s+xmax\\s+([0-9eE.+-]+)")
    world_ymin_p     = re.compile("@\\s+world\\s+ymin\\s+([0-9eE.+-]+)")
    world_ymax_p     = re.compile("@\\s+world\\s+ymax\\s+([0-9eE.+-]+)")
    view_p           = re.compile("@\\s+view\\s+([0-9eE.+-]+)\\s+([0-9eE.+-]+)\\s+([0-9eE.+-]+)\\s+([0-9eE.+-]+)")
    view_xmin_p      = re.compile("@\\s+view\\s+xmin\\s+([0-9eE.+-]+)")
    view_xmax_p      = re.compile("@\\s+view\\s+xmax\\s+([0-9eE.+-]+)")
    view_ymin_p      = re.compile("@\\s+view\\s+ymin\\s+([0-9eE.+-]+)")
    view_ymax_p      = re.compile("@\\s+view\\s+ymax\\s+([0-9eE.+-]+)")
    title_p          = re.compile("@\\s+title\\s+\"(.*)\"")
    title_color_p    = re.compile("@\\s+title\\s+color\\s+(\\d+)")
    subtitle_p       = re.compile("@\\s+subtitle\\s+\"(.*)\"")
    subtitle_color_p = re.compile("@\\s+subtitle\\s+color\\s+(\\d+)")
    xaxis_p          = re.compile("@\\s+xaxis\\s*(.*)")
    yaxis_p          = re.compile("@\\s+yaxis\\s*(.*)")
    legend_on_p      = re.compile("@\\s+legend\\s+on")
    legend_off_p     = re.compile("@\\s+legend\\s+off")
    legend_p         = re.compile("@\\s+legend\\s+([0-9eE.+-]+)\\s*,\\s*([0-9eE.+-]+)")
    legend_box_color_p = re.compile("@\\s+legend\\s+box\\s+color\\s+(\\d+)")
    legend_box_linewidth_p = re.compile("@\\s+legend\\s+box\\s+linewidth\\s+([0-9eE.+-]+)")
    legend_box_fill_color_p = re.compile("@\\s+legend\\s+box\\s+fill\\s+color\\s+(\\d+)")
    legend_color_p   = re.compile("@\\s+legend\\s+color\\s+(\\d+)")
    frame_color_p    = re.compile("@\\s+frame\\s+\\s+color\\s+(\\d+)")
    frame_linewidth_p= re.compile("@\\s+frame\\s+linewidth\\s+([0-9eE.+-]+)")
    frame_background_color_p = re.compile("@\\s+frame\\s+background\\s+color\\s+(\\d+)")
    set_p            = re.compile("@\\s+s(\\d+)\\s+(.*)")


    def __init__(self,sets=[],world=None):
        UserList.__init__(self,sets)
        for s in sets:
            s.setGraph(self)
        self.default_set=Set()

        self.setWorld(world)
        self.graph_lines=[]
        self.world_xmin=0.0
        self.world_xmax=1.0
        self.world_ymin=0.0
        self.world_ymax=1.0

        self.view_xmin=0.15
        self.view_xmax=1.15
        self.view_ymin=0.15
        self.view_ymax=0.85

        self.title="Graph"
        self.title_font=World.large_font
        self.title_color=1

        self.xaxis=XAxis(self)
        self.xaxis_up=XAxis(self)
        self.xaxis_up.position     = "up"
        self.xaxis_up.label        = None
        self.xaxis_up.ticklabel    = None

        self.yaxis=YAxis(self)
        self.yaxis_right=YAxis(self)
        self.yaxis_right.position     = "right"
        self.yaxis_right.label        = None
        self.yaxis_right.ticklabel    = None

        self.subtitle="subtitle"
        self.subtitle_font=World.medium_font
        self.subtitle_color=1

        self.legend=1
        self.legend_x=self.view_xmax+0.05
        self.legend_y=self.view_ymax

        self.legend_box_color=1
        self.legend_box_width=1
        self.legend_box_fillcolor=0
        self.legend_font=World.medium_font
        self.legend_color=1

        self.frame=1
        self.frame_width=1
        self.frame_color=1
        self.frame_background_color=0

    def autotick(self):
        self.xaxis.autotick()
        self.yaxis.autotick()

    def clone(self):
        g=Graph()

        for x in self.__dict__.keys():
            if x not in ["world","data","view2screenX",
                         "view2screenY",
                         "screen2viewX",
                         "screen2viewY",
                         "resolveColor",
                         "resolveWidth",
                         "encodeColor",
                         "xaxis",
                         "xaxis_up",
                         "yaxis",
                         "yaxis_right"
                         ]:
#        print "clone Graph.%s"%x
                setattr(g,x,copy.copy(getattr(self,x)))
        g.xaxis.setAxis(self.xaxis)
        g.yaxis.setAxis(self.yaxis)
        g.xaxis_up.setAxis(self.xaxis_up)
        g.yaxis_right.setAxis(self.yaxis_right)

        g.setWorld(self.world)
        for s in self.data:
#      print "clone set"
            g.append(s.clone())
        return g

    def cleanData(self):
        for x in self:
            x.cleanData()

    def viewAll(self,data=None):
#    print "viewAll"
        if data is None:
            data=self.data
        xmax=[]
        xmin=[]
        ymax=[]
        ymin=[]
        for s in data:
            mx=map(lambda x:x[0],s)
            my=map(lambda x:x[1],s)
            try:
                xmax.append(max(mx))
                xmin.append(min(mx))
            except:
                pass
            try:
                ymax.append(max(my))
                ymin.append(min(my))
            except:
                pass
        try:
            self.world_xmax=max(xmax)
            self.world_xmin=min(xmin)
        except:
            pass
        try:
            self.world_ymax=max(ymax)
            self.world_ymin=min(ymin)
        except:
            pass
        if self.world_xmax==self.world_xmin:
            self.world_xmax+=1
            self.world_xmin-=1
        if self.world_ymax==self.world_ymin:
            self.world_ymax+=1
            self.world_ymin-=1

    def viewAllX(self,data=None):
#    print "viewAll"
        if data is None:
            data=self.data
        xmax=[]
        xmin=[]
        for s in data:
            Min=min(self.world_ymin,self.world_ymax)
            Max=max(self.world_ymin,self.world_ymax)
            s=filter(lambda x,Min=Min,Max=Max:(x[1]>=Min)and(x[1]<=Max),s)
            mx=map(lambda x:x[0],s)
            try:
                xmax.append(max(mx))
                xmin.append(min(mx))
            except:
                pass
        try:
            self.world_xmax=max(xmax)
            self.world_xmin=min(xmin)
        except:
            pass
        if self.world_xmax==self.world_xmin:
            self.world_xmax+=1
            self.world_xmin-=1

    def viewAllY(self,data=None):
#    print "viewAll"
        if data is None:
            data=self.data
        ymax=[]
        ymin=[]
        for s in data:
            Min=min(self.world_xmin,self.world_xmax)
            Max=max(self.world_xmin,self.world_xmax)
            s=filter(lambda x,Min=Min,Max=Max:(x[0]>=Min)and(x[0]<=Max),s)
            my=map(lambda x:x[1],s)
            try:
                ymax.append(max(my))
                ymin.append(min(my))
            except:
                pass
        try:
            self.world_ymax=max(ymax)
            self.world_ymin=min(ymin)
        except:
            pass
        if self.world_ymax==self.world_ymin:
            self.world_ymax+=1
            self.world_ymin-=1

    def identifySetPoint(self,x,y,data=None):
        ml,mi,mj=None,None,None
        if data is None:
            data = self.data
        for i in range(len(data)):
            set=data[i]
            for j in range(len(set)):
                p=set[j]
                dx=self.world2screenX(p[0])-x
                dy=self.world2screenY(p[1])-y
                l=dx*dx+dy*dy
                if ml is None:
                    ml,mi,mj=l,i,j
                elif l<ml:
                    ml,mi,mj=l,i,j

        return mi,mj

    def identifySetPointVisible(self,x,y,data=None):
        ml,mi,mj=None,None,None
        if data is None:
            data = self.data
        for i in range(len(data)):
            set=data[i]
            for j in range(len(set)):
                xx,yy=set[j][0],set[j][1]
                if xx<min(self.world_xmin,self.world_xmax):
                    continue
                if xx>max(self.world_xmin,self.world_xmax):
                    continue
                if yy<min(self.world_ymin,self.world_ymax):
                    continue
                if yy>max(self.world_ymin,self.world_ymax):
                    continue

                dx=self.world2screenX(xx)-x
                dy=self.world2screenY(yy)-y
                l=dx*dx+dy*dy
                if ml is None:
                    ml,mi,mj=l,i,j
                elif l<ml:
                    ml,mi,mj=l,i,j

        return mi,mj



    def parseGraceStatement(self,s):
        #print "parseGraceStatement",s
        m=self.world_p.match(s)
        if m:
            self.world_xmin=float(m.group(1))
            self.world_ymin=float(m.group(2))
            self.world_xmax=float(m.group(3))
            self.world_ymax=float(m.group(4))
            return 1
        m=self.world_xmin_p.match(s)
        if m:
            self.world_xmin=float(m.group(1))
            return 1
        m=self.world_xmax_p.match(s)
        if m:
            self.world_xmax=float(m.group(1))
            return 1
        m=self.world_ymin_p.match(s)
        if m:
            self.world_ymin=float(m.group(1))
            return 1
        m=self.world_ymax_p.match(s)
        if m:
            self.world_ymax=float(m.group(1))
            return 1
        m=self.view_p.match(s)
        if m:
            self.view_xmin=float(m.group(1))
            self.view_xmax=float(m.group(2))
            self.view_ymin=float(m.group(3))
            self.view_ymax=float(m.group(4))
            return 1
        m=self.view_xmin_p.match(s)
        if m:
            self.view_xmin=float(m.group(1))
            return 1
        m=self.view_xmax_p.match(s)
        if m:
            self.view_xmax=float(m.group(1))
            return 1
        m=self.view_ymin_p.match(s)
        if m:
            self.view_ymin=float(m.group(1))
            return 1
        m=self.view_ymax_p.match(s)
        if m:
            self.view_ymax=float(m.group(1))
            return 1
        m=self.title_p.match(s)
        if m:
            self.title=m.group(1)
            return 1
        m=self.title_color_p.match(s)
        if m:
            self.title_color=int(m.group(1))
            return 1
        m=self.subtitle_p.match(s)
        if m:
            self.subtitle=m.group(1)
            return 1
        m=self.subtitle_color_p.match(s)
        if m:
            self.subtitle_color=int(m.group(1))
            return 1
        m=self.xaxis_p.match(s)
        if m:
            return self.xaxis.parseGraceStatement(m.group(1))
        m=self.yaxis_p.match(s)
        if m:
            return self.yaxis.parseGraceStatement(m.group(1))
        m=self.legend_on_p.match(s)
        if m:
            self.legend=1
            return 1
        m=self.legend_off_p.match(s)
        if m:
            self.legend=0
            return 1
        m=self.legend_p.match(s)
        if m:
            self.legend_x=float(m.group(1))
            self.legend_y=float(m.group(2))
            return 1
        m=self.legend_box_color_p.match(s)
        if m:
            self.legend_box_color=int(m.group(1))
            return 1
        m=self.legend_box_linewidth_p.match(s)
        if m:
            self.legend_box_width=float(m.group(1))
            return 1
        m=self.legend_box_fill_color_p.match(s)
        if m:
            self.legend_box_fill_color=int(m.group(1))
            return 1
        m=self.legend_color_p.match(s)
        if m:
            self.legend_color=int(m.group(1))
            return 1
        m=self.frame_color_p.match(s)
        if m:
            self.frame_color=int(m.group(1))
            return 1
        m=self.frame_linewidth_p.match(s)
        if m:
            self.frame_width=float(m.group(1))
            return 1
        m=self.frame_background_color_p.match(s)
        if m:
            self.frame_background_color=int(m.group(1))
            return 1
        m=self.set_p.match(s)
        if m:
            set=int(m.group(1))
            if len(self)<=set:
                for i in range(len(self),set+1):
                    self.append(Set())
            self[set].setGraph(self)
            return self[set].parseGraceStatement(m.group(2),)

        return 0

    def exportGrace(self,f,i):
        f.write("""@g%d on
    @g%d hidden false
    @g%d type XY
    @g%d stacked false
    @g%d bar hgap 0.000000
    @g%d fixedpoint off
    @g%d fixedpoint type 0
    @g%d fixedpoint xy 0.000000, 0.000000
    @g%d fixedpoint format general general
    @g%d fixedpoint prec 6, 6
    @with g%d
    """%(i,i,i,i,i,i,i,i,i,i,i))
        f.write("@    world xmin %f\n"%self.world_xmin)
        f.write("@    world xmax %f\n"%self.world_xmax)
        f.write("@    world ymin %f\n"%self.world_ymin)
        f.write("@    world ymax %f\n"%self.world_ymax)
        f.write("""@    stack world 0, 0, 0, 0
    @    znorm 1
    """)
        f.write("@    view xmin %f\n"%self.view_xmin)
        f.write("@    view xmax %f\n"%self.view_xmax)
        f.write("@    view ymin %f\n"%self.view_ymin)
        f.write("@    view ymax %f\n"%self.view_ymax)

        f.write('@    title "%s"\n'%self.title)
        f.write('@    title font 0\n')
        f.write('@    title size 1.5\n')
        f.write('@    title color %d\n'%self.encodeColor(self.title_color))

        f.write('@    subtitle "%s"\n'%self.subtitle)
        f.write('@    subtitle font 0\n')
        f.write('@    subtitle size 1.0\n')
        f.write('@    subtitle color %d\n'%self.encodeColor(self.subtitle_color))

        f.write("""@    xaxes scale Normal
    @    yaxes scale Normal
    @    xaxes invert off
    @    yaxes invert off
    """)
        self.xaxis.exportGrace(f)
        self.yaxis.exportGrace(f)
        f.write("""@    altxaxis  off
    @    altyaxis  off
    """)
        if self.legend:
            f.write('@    legend on\n')
        else:
            f.write('@    legend off\n')
        f.write('@    legend loctype view\n')
        f.write('@    legend %f, %f\n'%(self.legend_x,self.legend_y))
        f.write('@    legend box color %d\n'%self.encodeColor(self.legend_box_color))
        f.write('@    legend box pattern 1\n')
        f.write('@    legend box linewidth %f\n'%self.legend_box_width)
        f.write('@    legend box linestyle 1\n')
        f.write('@    legend box fill color %d\n'%self.encodeColor(self.legend_box_fillcolor))
        f.write('@    legend box fill pattern 1\n')
        f.write('@    legend font 0\n')
        f.write('@    legend char size 1.00000\n')
        f.write('@    legend color %d\n'%self.encodeColor(self.legend_color))
        f.write('@    legend length 4\n')
        f.write('@    legend vgap 1\n')
        f.write('@    legend hgap 1\n')
        f.write('@    legend invert false\n')

        f.write('@    frame type 0\n')
        f.write('@    frame linestyle 1\n')
        f.write('@    frame linewidth %f\n'%self.frame_width)
        f.write('@    frame color %d\n'%self.encodeColor(self.frame_color))
        f.write('@    frame pattern 1\n')
        f.write('@    frame background color %d\n'%self.encodeColor(self.frame_background_color))
        f.write('@    frame background pattern 1\n')
        for j in range(0,len(self)):
            self[j].exportGrace(f,j)

    def exportGraceData(self,f,i,data=None):
        if data is None:
            for j in range(len(self)):
                f.write('@target G%d.S%d\n'%(i,j))
                self[j].exportGraceData(f)
        else:
            self.default_set.setGraph(self)
            expdata=self.default_set.exportGraceData
            for j in range(len(data)):
                f.write('@target G%d.S%d\n'%(i,j))
                expdata(f,data[j])

    def registerColors(self):
        self.xaxis.registerColors()
        self.yaxis.registerColors()
        self.xaxis_up.registerColors()
        self.yaxis_right.registerColors()
        self.encodeColor(self.title_color)
        self.encodeColor(self.subtitle_color)
        self.encodeColor(self.legend_box_color)
        self.encodeColor(self.legend_box_fillcolor)
        self.encodeColor(self.legend_color)
        self.encodeColor(self.frame_color)
        self.encodeColor(self.frame_background_color)
        for x in self:
            x.registerColors()

    def setupFonts(self,canvas,world=None):
        if world is None:
            world=self.world
        self.title_font     =world.large_font
        self.subtitle_font  =world.medium_font
        self.legend_font    =world.medium_font
        self.xaxis.setupFonts(canvas,world=world)
        self.yaxis.setupFonts(canvas,world=world)
        for s in self:
            s.setupFonts(canvas,world=world)

    def setWorld(self,world):
        self.world=world
        if isinstance(world,World):
            self.xaxis.setGraph(self)
            self.yaxis.setGraph(self)
            self.xaxis_up.setGraph(self)
            self.yaxis_right.setGraph(self)
            self.view2screenX   =world.view2screenX
            self.view2screenY   =world.view2screenY
            self.screen2viewX   =world.screen2viewX
            self.screen2viewY   =world.screen2viewY
            self.resolveColor   =world.resolveColor
            self.resolveWidth   =world.resolveWidth
            self.encodeColor    =world.encodeColor
        else:
            self.view2screenX   =None
            self.view2screenY   =None
            self.screen2viewX   =None
            self.screen2viewY   =None
            self.resolveColor   =None
            self.resolveWidth   =None
            self.encodeColor    =None

    def view2worldX(self,x):
        w0=self.world_xmin
        w1=self.world_xmax
        v0=self.view_xmin
        v1=self.view_xmax
        return w0+(x-v0)*(w1-w0)/(v1-v0)

    def view2worldY(self,y):
        w0=self.world_ymin
        w1=self.world_ymax
        v0=self.view_ymin
        v1=self.view_ymax
        return w0+(y-v0)*(w1-w0)/(v1-v0)

    def world2viewX(self,x):
        w0=self.world_xmin
        w1=self.world_xmax
        v0=self.view_xmin
        v1=self.view_xmax
        return v0+(x-w0)*(v1-v0)/(w1-w0)

    def world2viewY(self,y):
        w0=self.world_ymin
        w1=self.world_ymax
        v0=self.view_ymin
        v1=self.view_ymax
        return v0+(y-w0)*(v1-v0)/(w1-w0)

    def world2screenX(self,x):
        return self.view2screenX(self.world2viewX(x))
    def world2screenY(self,y):
        return self.view2screenY(self.world2viewY(y))

    def screen2worldX(self,x):
        return self.view2worldX(self.screen2viewX(x))
    def screen2worldY(self,y):
        return self.view2worldY(self.screen2viewY(y))

    def getScreenXmin(self):
        return self.view2screenX(self.view_xmin)
    def getScreenXmax(self):
        return self.view2screenX(self.view_xmax)
    def getScreenYmin(self):
        return self.view2screenY(self.view_ymin)
    def getScreenYmax(self):
        return self.view2screenY(self.view_ymax)

    def renderFrame(self,canvas):
        x0=self.getScreenXmin()
        y0=self.getScreenYmin()
        x1=self.getScreenXmax()
        y1=self.getScreenYmax()

        canvas.drawPolygon([(x0,y0),(x0,y1),(x1,y1),(x1,y0)],
                        self.resolveColor(self.frame_color),
                        self.resolveWidth(self.frame_width),
                        self.resolveColor(self.frame_background_color),1)

    def renderTitle(self,canvas,title=None):
        if title is None:
            title=self.title

        w=canvas.stringWidth(title,self.title_font)
        h=canvas.fontHeight(self.title_font)
        hh=canvas.fontHeight(self.subtitle_font)
        x=(self.getScreenXmin()+self.getScreenXmax()-w)/2
        y=self.getScreenYmax()-(h+hh)*1.1

        canvas.drawString(title,x,y,self.title_font,
          self.resolveColor(self.title_color))

    def renderSubtitle(self,canvas,title=None):
        if title is None:
            title=self.subtitle

        w=canvas.stringWidth(title,self.subtitle_font)
        h=canvas.fontHeight(self.subtitle_font)
        x=(self.getScreenXmin()+self.getScreenXmax()-w)/2
        y=self.getScreenYmax()-h*1.1

        canvas.drawString(title,x,y,self.subtitle_font,
          self.resolveColor(self.subtitle_color))

    def renderLegend(self,canvas,set=None):
        if not set:
            set=self.data

        set   =filter(lambda x:x.legend,set)
        if not len(set):
            return None
        widths =map(lambda x,sw=canvas.stringWidth,f=self.legend_font:
                    sw(x.legend,f), set)
        h=canvas.fontHeight(self.legend_font)*1.5
        lmarg=0.03
        rmarg=0.03
        dl=0.05
        ds=0.03
        H=len(set)*h
        x0=self.view2screenX(self.legend_x)
        y0=self.view2screenY(self.legend_y)
        x1=self.view2screenX(self.legend_x+lmarg+dl+ds+rmarg)+max(widths)
        y1=self.view2screenY(self.legend_y)+H
        if x0>x1:
            s=x0
            x0=x1
            x1=s
        if y0>y1:
            s=y0
            y0=y1
            y1=s

        canvas.drawRect(x0,y0,x1,y1,self.resolveColor(self.legend_box_color),
                                    self.resolveWidth(self.legend_box_width),
                                    self.resolveColor(self.legend_box_fillcolor))
#    canvas.drawPolygon([(x0,y0),(x0,y1),(x1,y1),(x1,y0)],self.resolveColor(self.legend_box_color),
#                                self.resolveWidth(self.legend_box_width),
#                               self.resolveColor(self.legend_box_fillcolor),1)
        lx0=self.view2screenX(self.legend_x+lmarg)
        lx1=self.view2screenX(self.legend_x+lmarg+dl)
        tx =self.view2screenX(self.legend_x+lmarg+dl+ds)
        c=self.resolveColor(self.legend_color)

        for i in range(len(set)):
            s=set[i]
            y=self.view2screenY(self.legend_y)  +h*(i+0.9)
            ly0=self.view2screenY(self.legend_y)+h*(i+0.5)
            ly1=ly0
            s.renderLegendLine(canvas,lx0,ly0,lx1,ly1)
            canvas.drawString(s.legend,tx,y,self.legend_font,c)


    def render(self,canvas,data=None):
        self.setupFonts(canvas)
        if self.frame:
            self.renderFrame(canvas)
        if self.title:
            self.renderTitle(canvas)
        if self.subtitle:
            self.renderSubtitle(canvas)
        self.xaxis.render(canvas)

        xaxis_up=XAxis(self)
        xaxis_up.setAxis(self.xaxis)
        xaxis_up.position     = "up"
        xaxis_up.label        = None
        xaxis_up.ticklabel    = None
        xaxis_up.render(canvas)

        self.yaxis.render(canvas)
        yaxis_right=YAxis(self)
        yaxis_right.setAxis(self.yaxis)
        yaxis_right.position  = "right"
        yaxis_right.label     = None
        yaxis_right.ticklabel = None
        yaxis_right.render(canvas)

        if self.legend:
            self.renderLegend(canvas)
        if data is None:
            for s in self:
                s.render(canvas)
        else:
            for i in range(min(len(self),len(data))):
                self[i].render(canvas,data[i])
            self.default_set.setGraph(self)
            for i in range(len(self),len(data)):
                self.default_set.render(canvas,data[i])
        for l in self.graph_lines:
            l.render(canvas,self)

    def append(self,set=None):
        if set is None:
            s=Set(graph=self)
            UserList.append(self,s)
            return s
        elif isinstance(set,Set):
            UserList.append(self,set)
            set.setGraph(self)
            return set
        else:
            set=Set(graph=self,data=set)
            UserList.append(self,set)
            return set

    def extend(self,l):
        for s in l:
            self.append(s)
