#!/usr/bin/python

from string import *
from UserList import *
from ConfigParser import *
from os import mkdir
import os.path
from p4vasp import *
from p4vasp.Structure import Structure
import p4vasp.cStructure
from p4vasp.matrix import Vector


class DBI:
    def __init__(self,db=None,name=None,connect=1):
        self.db=db
        self.blocksize=10
        self.subst={}
        self.cfg={}
        self.name=name
        if connect:
            self.connect()

        if hasattr(self,"init"):
            self.init()


    def assure(self,key):
        if self.subst.has_key(key):
            return 1
        raise Exception("The %s is missing."%(key[1:]))

    def config(self,c,name=None):
        if name is not None:
            self.name=name

        self.cfg.update(c)
        for k,v in self.cfg.items():
            if lower(k) in ["user_uid","username"]:
                self.subst["#"+upper(k)]='"%s"'%v
                continue
            key=None
            if lower(k[:7])=="define_":
                key=upper(k[7:])
            elif lower(k[:6])=="table_":
                key=upper(k[6:])
            if key is not None:
                if "#" not in key:
                    self.subst["#"+key]=v


    def connect(self):
        self.onConnect()

    def onConnect(self):
        pass

    def disconnect(self):
        self.db=None
        self.user_id=None

    def isConnected(self):
        return self.db is not None

    def subs(self,s):
        keys=map(lambda x:(-len(x),x),self.subst.keys())
        keys.sort()
        keys=map(lambda x:x[1],keys)
        for k in keys:
            s=replace(s,k,self.subst[k])
#    print s
        return s

    def exe(self,s,ignore_errors=0):
        try:
            c=self.db.cursor()
            c.execute(self.subs(s))
        except:
            if not ignore_errors:
                raise


    def fetchall(self,s):
        c=self.db.cursor()
        c.execute(self.subs(s))
        return c.fetchall()

    def fetchone(self,s):
        c=self.db.cursor()
        c.execute(self.subs(s))
        return c.fetchone()

    def fetchiter(self,s):
        c=self.db.cursor()
        c.execute(self.subs(s))
        while 1:
            d=c.fetchone()
            if d is not None:
                yield d
            else:
                break

    def fetchvalue(self,s):
        return self.fetchone(s)[0]
    def fetchvalues(self,s):
        return map(lambda x:x[0],self.fetchall(s))

    def run(self,s,ignore_errors=0):
        for ss in split(s,";"):
            self.exe(ss,ignore_errors=ignore_errors)

    def runfile(self,f,ignore_errors=0):
        if type(f)==type(""):
            f=open(f,"r")
        s=f.read()
        f.close()
        self.run(s,ignore_errors)

    def insertRecord(self,table,indexname,keys,values):
        self.exe("INSERT INTO %s (%s) VALUES (%s)"%(table,keys,values))
        return self.fetchvalue("SELECT MAX(%s) FROM %s"%(indexname,table))

    def commit(self):
        self.db.commit()



class Query:
    def __init__(self,container,data,fromstatement,condition,cachesize=200):
        self.container     = container
        self.data          = data
        self.fromstatement = fromstatement
        self.condition     = condition
        self.cachesize     = cachesize
        self.refresh()

    def __len__(self):
        return int(self.cumulative[-1])

    def refresh(self):
        self.cache      = []
        self.hash       = {}
        self.count()

    def finddb(self,i):
        for j in xrange(len(self.cumulative)-1):
            if self.cumulative[j]<=i and self.cumulative[j+1]>i:
                return j

    def shrinkCache(self,n):
        "Remove (up to) n elements from the cache."
        n=min(n,len(self.cache))
        if n>0:
            del self.cache[:n]

            for k,v in self.hash.items():
                if v<n:
                    del self.hash[k]
                else:
                    self.hash[k]=v-n

    def addToCache(self,i,r):
        v=len(self.cache)
        self.cache.append(r)
        self.hash[i]=v

    def fetchblock(self,i):
        di=self.finddb(i)
        if di is not None:
            d=self.container[di]
            blocksize=d.blocksize
            offset=i-self.cumulative[di]
            self.shrinkCache(len(self.cache)+blocksize-self.cachesize)
            for x in d.fetchiter("SELECT %s %s %s LIMIT %d, %d"%(self.data,self.fromstatement,self.condition,offset,blocksize)):
                self.addToCache(i,(di,x))
                i+=1

    def get(self,i):
        if i>=0 and i<len(self):
            if self.hash.has_key(i):
#        print "cache hit",i,self.hash[i],self.cache[self.hash[i]]
                return self.cache[self.hash[i]]
            else:
#        print "not in cache -> fetch",i
                self.fetchblock(i)
                if self.hash.has_key(i):
#          print "      got",i,self.hash[i],self.cache[self.hash[i]]
                    return self.cache[self.hash[i]]
                else:
#          print "error -> refresh"
                    self.refresh()
                    self.fetchblock(i)
                    if self.hash.has_key(i):
#            print "      got",i,self.hash[i],self.cache[self.hash[i]]
                        return self.cache[self.hash[i]]
                    else:
#            print "FAILED"
                        return None

    def getiter(self):
        return self.container.fetchiter("SELECT %s %s"%(self.data,self.fromstatement,self.condition))

    def __getitem__(self,i):
#    print "getitem",i,"/",len(self),":",self.get(i)
        g=self.get(i)
        if g is not None:
            return g[1]

    def __iter__(self,i):
        for x in self.getiter():
            yield x[1]

    def count(self):
        self.counts     = []
        self.cumulative = [0]
        s=0

        for d in self.container:
            if d.isConnected():
                l=d.fetchvalue("SELECT count(*) %s %s"%(self.fromstatement, self.condition))
                s+=l
                self.counts.append(l)
                self.cumulative.append(s)
            else:
                self.counts.append(0)
                self.cumulative.append(s)



class DBIContainer(UserList):
    def exe(self,s):
        for x in self:
            x.exe(s)

    def fetchone(self,s):
        for x in self:
            if x.isConnected():
                v=x.fetchone(s)
                if v is not None:
                    return v
        return None

    def fetchiter(self,s):
        for d in self:
            if d.isConnected():
                for r in d.fetchiter(s):
                    yield r

    def query(self, data, fromstatement,condition="",cachesize=200):
        return Query(self,data,fromstatement,condition,cachesize)

    def fetchvalue(self,s):
        return self.fetchone(s)[0]

    def run(self,s,ignore_errors=0):
        for x in self:
            if x.isConnected():
                x.run(s,ignore_errors=ignore_errors)

    def commit(self):
        for x in self:
            if x.isConnected():
                x.commit()

    def connect(self):
        for x in self:
            try:
                x.connect()
            except:
                msg().exception()

    def disconnect(self):
        for x in self:
            x.disconnect()

    def isConnected(self):
        for x in self:
            if x.isConnected():
                return 1
        return 0



def von(x):
    "str(x) or NULL"
    if x is None:
        return "NULL"
    else:
        return str(x)

def son(x):
    '"str(x)" or NULL'
    if x is None:
        return "NULL"
    else:
        return '"%s"'%str(x)

class UserManagementMixin(DBI):
    def init(self):
        self.user_id=None

    def getUserName(self):
        return self.cfg["username"]

    def getUserUID(self):
        return self.cfg["user_uid"]

    def login(self):
        self.assure("#USER_UID")
        try:
            self.user_id=self.fetchvalue('SELECT id FROM #USERINFO WHERE user_uid=#USER_UID')
        except:
            self.user_id=None
        return self.user_id


    def addUser(self):
        self.assure("#USER_UID")
        self.assure("#USERNAME")
        if self.getUserID() is None:
            self.exe("INSERT INTO #USERINFO (user_uid,username) VALUES (#USER_UID, #USERNAME)")
            self.commit()
            self.login()

    def getUserID(self):
        if self.user_id is None:
            self.login()
        return self.user_id

    def onConnect(self):
        try:
            scriptname=self.cfg["creation_script"]
        except:
            return
        self.runfile(scriptname,ignore_errors=1)


class P4VMixin(UserManagementMixin):
    def init(self,calc_id=None,pm=None):
        UserManagementMixin.init(self)
        self.calc_id=calc_id
        self.pm=pm


    def getDefaultCommit(self):
        if self.cfg.has_key("default_commit"):
            if lower(self.cfg["default_commit"]) in ["t","true","yes","y","enable","enabled"]:
                return 1
        return 0

    def canCommit(self):
        if self.cfg.has_key("commit"):
            if lower(self.cfg["commit"]) in ["t","true","yes","y","enable","enabled"]:
                return 1
        return 0

    def addRecord(self,pm=None,keywords=None,name=None):
        if pm is None:
            pm=self.pm
        else:
            self.pm=pm
        self.login()
        if name is None:
            name     = pm.NAME
        if name is None:
            name=""
        if keywords is None:
            keywords = pm.KEYWORDS
        if keywords is None:
            keywords=""

        user_id = self.user_id
        if user_id is None:
            raise Exception("Can not login to %s"%self.name)
        self.calc_id=self.insertRecord("#CALC","id","name,user_id,keywords",'"%s",%d,"%s"'%(name,user_id,keywords))
        self.commit()
        return self.calc_id

    def storePMgen(self,pm,keywords=None,name=None, date=None, description=None):
        import p4vasp.util
        import p4vasp
        import time
        calc_id=self.addRecord(pm,keywords=keywords,name=name)
        msg().status("Store calculation %s to database %s."%(name,self.name))
        yield 1
        try:
            s=pm.PATH
            if s is not None and '"' not in s and "'" not in s:
                self.exe('UPDATE #CALC SET path="%s" WHERE id=%d'%(str(s),calc_id))
            else:
                self.exe('UPDATE #CALC SET path=NULL WHERE id=%d'%(calc_id))

            s=pm.KPOINTS_TEXT
            if s is not None:
                s=s.replace("'","")
                s=s.replace('"',"")
                self.exe('UPDATE #CALC SET kpoints_text="%s" WHERE id=%d'%(str(s),calc_id))
            else:
                self.exe('UPDATE #CALC SET kpoints_text=NULL WHERE id=%d'%(calc_id))

            s=date
            if s is None:
                s=pm.DATE
            if s is None:
                s=time.localtime()
            if type(s) != type(""):
                s=time.strftime("%Y-%m-%d %H:%M:%S",s)
            self.exe('UPDATE #CALC SET cdatetime="%s" WHERE id=%d'%(s,calc_id))

            s=pm.FREE_ENERGY
            if s is not None:
                s=float(s)
                self.exe('UPDATE #CALC SET free_energy=%f WHERE id=%d'%(s,calc_id))

            s=pm.E_FERMI
            if s is not None:
                s=float(s)
                self.exe('UPDATE #CALC SET fermi_energy=%f WHERE id=%d'%(s,calc_id))

            s=description
            if s is None:
                s=pm.DESCRIPTION
            if s is not None:
                s=str(s)
                s=s.replace('"'," ")
                s=s.replace("'"," ")
                s=s.replace("\\"," ")
                self.exe('UPDATE #CALC SET description="%s" WHERE id=%d'%(s,calc_id))

            s=pm.PROGRAM
            if s is not None:
                s=str(s)
                s=s.replace('"'," ")
                s=s.replace("'"," ")
                s=s.replace("\\"," ")
                self.exe('UPDATE #CALC SET program="%s" WHERE id=%d'%(s,calc_id))

            s=pm.VERSION
            if s is not None:
                s=str(s)
                s=s.replace('"'," ")
                s=s.replace("'"," ")
                s=s.replace("\\"," ")
                self.exe('UPDATE #CALC SET version="%s" WHERE id=%d'%(s,calc_id))

            s=pm.SUBVERSION
            if s is not None:
                s=str(s)
                s=s.replace('"'," ")
                s=s.replace("'"," ")
                s=s.replace("\\"," ")
                self.exe('UPDATE #CALC SET subversion="%s" WHERE id=%d'%(s,calc_id))

            s=pm.PLATFORM
            if s is not None:
                s=str(s)
                s=s.replace('"'," ")
                s=s.replace("'"," ")
                s=s.replace("\\"," ")
                self.exe('UPDATE #CALC SET platform="%s" WHERE id=%d'%(s,calc_id))

            incar = pm.INCAR
            parameters = pm.PARAMETERS
            if incar is not None:
                if parameters is None:
                    parameters=incar
                for key,value in parameters.items():
                    msg().status("Store parameters (%s)"%key)
                    yield 1
                    fieldtype   = parameters.getFieldType(key)
                    isarray     = p4vasp.util.isArray(value)
                    isspecified = int(incar.has_key(key))
                    if isarray:
                        if fieldtype == p4vasp.LOGICAL_TYPE:
                            value = map(int,value)
                        svalue = ' '.join(map(str,value))
                    else:
                        if fieldtype == p4vasp.LOGICAL_TYPE:
                            value = int(value)
                        svalue = str(value)
                    if len(svalue)>254:
                        textvalue='"'+svalue+'"'
                        svalue="NULL"
                    else:
                        svalue='"'+svalue+'"'
                        textvalue="NULL"
                    self.exe('INSERT INTO #PARAMETERS '
                             '(calc_id, name, fieldtype, isarray, isspecified, value, textvalue) '
                             'VALUES (%d, "%s", "%s", %d, %d, %s, %s)'%(calc_id, key, fieldtype, isarray, isspecified, svalue, textvalue))

            dos=pm.TOTAL_DOS
            if dos is not None:
                msg().status("Store total DOS")
                yield 1
                if len(dos)==1:
                    spins=[0]
                elif len(dos)==2:
                    spins=[1,2]
                else:
                    spins=[-1,-2,-3,-4]
                progress=0
                total=len(dos)*len(dos[0])
                for s in xrange(len(dos)):
                    sd=dos[s]
                    for i in xrange(len(sd)):
                        sdi=sd[i]
                        energy     =sdi[0]
                        density    =sdi[1]
                        integrated =sdi[2]
                        self.exe('INSERT INTO #DOS (calc_id,spin,energy,density,integrated) VALUES (%d, %d, %f, %f, %f)'%(calc_id,spins[s],energy,density,integrated))
                        progress+=1
                        if not progress%10:
                            msg().step(progress,total)
                            yield 1
                msg().step(0,1)
                yield 1

            dos=pm.PARTIAL_DOS_L
            if dos is not None:
                msg().status("Store local DOS")
                yield 1
                if len(dos[0])==1:
                    spins=[0]
                elif len(dos[0])==2:
                    spins=[1,2]
                else:
                    spins=[-1,-2,-3,-4]
                progress=0
                total=len(dos)*len(dos[0])*len(dos[0][0])
                for ion in xrange(len(dos)):
                    iond=dos[ion]
                    for spin in xrange(len(iond)):
                        sd=iond[spin]

                        for i in xrange(len(sd)):
                            sdi=sd[i]
                            energy     =sdi[0]
                            for j in xrange(1,len(dos.field)):
                                density    =sdi[j]
                                orbital    =dos.field[j]
                                self.exe('INSERT INTO #LDOS (calc_id,spin,energy,atomnumber,orbital,density)'
                                ' VALUES (%d, %d, %f, %d, "%s", %f)'%(calc_id,spins[spin],energy,ion,orbital,density))
                            progress+=1
                            if not progress%10:
                                msg().step(progress,total)
                                yield 1
                msg().step(0,1)
                yield 1

            s=pm.INITIAL_STRUCTURE
            if s is not None:
                msg().status("Store initial structure.")
                yield 1
                self.storeStructure(s,-1)

            s=pm.FINAL_STRUCTURE
            if s is not None:
                msg().status("Store final structure.")
                yield 1
                self.storeStructure(s,-2)

            seq  =pm.STRUCTURE_SEQUENCE_L
            fseq =pm.FORCES_SEQUENCE_L

            if seq is not None:
                msg().status("Store structure sequence.")
                yield 1
                for i in range(len(seq)):
                    msg().step(i,len(seq))
                    yield 1
                    sid=self.storeStructure(seq[i],i)
                    if fseq is not None:
                        f=fseq[i]
                        if f is not None:
                            self.storeForce(f,sid)
                msg().step(0,1)
                yield 1

            self.commit()

            msg().status("OK")
            msg().step(0,1)
            yield 1
        except:
            if calc_id is not None:
                self.removeCalculation(calc_id)
            raise

    def removeStructure(self,i):
        if i is not None:
            self.exe("DELETE FROM #STRUCT WHERE id=%d"%(i))
            self.exe("DELETE FROM #STRUCTPOS WHERE structure_id=%d"%(i))
            self.exe("DELETE FROM #STRUCTFORCE WHERE structure_id=%d"%(i))
            self.exe("DELETE FROM #STRUCTVELOCITY WHERE structure_id=%d"%(i))
            self.exe("DELETE FROM #STRUCTCONSTRAINTS WHERE structure_id=%d"%(i))
            self.commit()

    def removeCalculation(self,i):
        if i is not None:
            self.exe("DELETE FROM #CALC WHERE id=%d"%(i))
            self.exe("DELETE FROM #PARAMETERS WHERE calc_id=%d"%(i))
            self.exe("DELETE FROM #STRUCTPOS WHERE calc_id=%d"%(i))
            self.exe("DELETE FROM #STRUCTFORCE WHERE calc_id=%d"%(i))
            self.exe("DELETE FROM #STRUCTVELOCITY WHERE calc_id=%d"%(i))
            self.exe("DELETE FROM #STRUCTCONSTRAINTS WHERE calc_id=%d"%(i))
            self.commit()

    def storeStructure(self,s,step=None):
        calc_id=self.calc_id
        if calc_id is not None and step is not None:
            for l in self.fetchall("SELECT id FROM #STRUCT WHERE calc_id=%d AND step=%d"%(calc_id,step)):
                removeStructure(db,l[0])

        info=s.info

        if len(s.scaling)!=1:
            s.correctScaling()

        cmd ="%s, %s,"%(von(calc_id), von(step))
        cmd+="%14.12f,'%s',"%(    s.scaling[0],s.comment)
        cmd+="""%14.12f,%14.12f,%14.12f,
        %14.12f,%14.12f,%14.12f,
        %14.12f,%14.12f,%14.12f,%d"""%(
        s.basis[0][0],s.basis[0][1],s.basis[0][2],
        s.basis[1][0],s.basis[1][1],s.basis[1][2],
        s.basis[2][0],s.basis[2][1],s.basis[2][2],s.types)

        Id=self.insertRecord("#STRUCT","id","calc_id, step, scale,comment,a11,a12,a13,a21,a22,a23,a31,a32,a33,species",cmd)

        if s.isSelective():
            sel    = s.selective
            for i in range(len(sel)):
                self.exe("""INSERT INTO #STRUCTCONSTRAINTS (structure_id,calc_id,atomnumber,x,y,z)
                VALUES (%d,%s,%d,%d,%d,%d)"""%(Id,von(calc_id),i,sel[i][0],sel[i][1],sel[i][2]))


        sc=Structure()
        sc.setStructure(s)
        sc.setCartesian()


        for i in range(len(s)):
            si=s.speciesIndex(i)

            self.exe("""INSERT INTO #STRUCTPOS (structure_id,calc_id,atomnumber,specie,element,x,y,z)
            VALUES (%d,%s,%d,%d,'%s',%14.12f,%14.12f,%14.12f)"""%(Id,von(calc_id),i,si,info[si].element,
            sc[i][0],            sc[i][1],            sc[i][2]))
        self.commit()
        return Id


    def readStructure(self,Id,cstructure=False):
        s=Structure()
        l=self.fetchone("""SELECT calc_id,scale,comment,a11,a12,a13,a21,a22,a23,a31,a32,a33,
          species FROM #STRUCT WHERE id=%d"""%(Id))
        (calc_id,scale ,s.comment,
         s.basis[0][0],s.basis[0][1],s.basis[0][2],
         s.basis[1][0],s.basis[1][1],s.basis[1][2],
         s.basis[2][0],s.basis[2][1],s.basis[2][2],spec)=l

        s.scaling=[scale]
        s.setCartesian()

        l=self.fetchall("SELECT specie,element,x,y,z FROM #STRUCTPOS WHERE structure_id=%d ORDER BY atomnumber"%(Id))
        for spec,element,x,y,z in l:
            i=s.appendAtom(spec,Vector(x,y,z))
            s.info.getRecordForAtom(i).element=str(element)

        l=self.fetchall("SELECT x,y,z FROM #STRUCTCONSTRAINTS WHERE structure_id=%d ORDER BY atomnumber"%(Id))
        if len(l):
            s.setSelective()
            for i in range(len(l)):
                s.selective[i]=[int(l[i][0]),int(l[i][1]),int(l[i][2])]

        if cstructure:
            s=p4vasp.cStructure.Structure(s)

        return s

    def removeForce(self,structure_id):
        self.exe("DELETE FROM #STRUCTFORCE WHERE structure_id=%d"%(structure_id))
        self.commit()

    def readForce(self,structure_id):
        from matrix import Vector
        force=[]

        l=self.fetchall("SELECT x,y,z FROM #STRUCTFORCE WHERE structure_id=%d ORDER BY atomnumber"%(structure_id))
        for x,y,z in l:
            force.append(Vector(x,y,z))
        return force

    def storeForce(self,force,structure_id):
        if not self.fetchvalue("SELECT count(*) FROM #STRUCT WHERE id=%d"%(structure_id)):
            raise Exception("Can't store the force for a nonexistend Structure structure_id=%d"%structure_id)

        calc_id = self.fetchvalue("SELECT calc_id FROM #STRUCT WHERE id=%d"%(structure_id))

        for i in range(len(force)):
            self.exe("""INSERT INTO #STRUCTFORCE (structure_id,calc_id,atomnumber,x,y,z)
            VALUES (%d,%s,%d,%14.12f,%14.12f,%14.12f)"""%(structure_id,von(calc_id),i,
            force[i][0], force[i][1], force[i][2]))
        self.commit()
        return structure_id

class SQLiteDBI(P4VMixin):
    def __init__(self,db=None,connect=1):
        if type(db)==type(""):
            self.path=db
            DBI.__init__(self,connect=connect)
        else:
            DBI.__init__(self,db,connect=connect)

    def config(self,c,name=None):
        cc={}
        cc.update(c)
        c=cc
        DBI.config(self,c,name)
        if c.has_key("path"):
            if self.isConnected():
                self.disconnect()
                self.path=c["path"]
                self.connect()
            else:
                self.path=c["path"]

    def connect(self):
#    try:
#      import sqlite
#    except ImportError:
#      from pysqlite2 import dbapi2 as sqlite
        from pysqlite2 import dbapi2 as sqlite
        if self.isConnected():
            self.disconnect()
        self.db=sqlite.connect(self.path)
        self.onConnect()


    def disconnect(self):
        self.db=None


class MySQLDBI(P4VMixin):
    def __init__(self,user=None,password=None,host=None,database=None,connect=1):
        self.user     = user
        self.password = password
        self.host     = host
        self.database = database

        DBI.__init__(self,connect=connect)

    def config(self,c,name=None):
        cc={}
        cc.update(c)
        c=cc
        DBI.config(self,c,name)

        reconnect=0
        isconnected=self.isConnected()
        for key in ["user","password","host","database"]:
            if c.has_key("db_"+key):
                if self.isConnected():
                    self.disconnect()
                setattr(self,key,c["db_"+key])
                reconnect=1
        if reconnect and isconnected:
            self.connect()

    def connect(self):
        import MySQLdb as mysql
        if self.isConnected():
            self.disconnect()
        self.db=mysql.connect(host=self.host,user=self.user,db=self.database,passwd=self.password)
        self.onConnect()


    def commit(self):
        pass

    def disconnect(self):
        self.db=None

def createFromConfig(l,prototypes={"sqlite":SQLiteDBI,"mysql":MySQLDBI}):
    import os.path
    import getpass
    defaults={}
    defaults["home"]=os.path.expanduser("~")
    defaults["user"]=getpass.getuser()
    c=ConfigParser(defaults)
    c.read(l)
#  c.write(open("out","w"))
    cont=DBIContainer()
    for s in c.sections():
#    try:
        t=lower(c.get(s,"type"))
        print "CREATE",s,t
#    except:
#      print "Section %s - type missing"%s
#      continue
#    try:
        DBI=prototypes[t]

        d=DBI(connect=0)

#    except:
#      print "Section %s - unsupported type %s"%(s,t)
#      continue
#    try:
#      print "config",c
        d.config(dict(c.items(s)),s)
#    except:
#      print "Section %s - configuration failed"%(s)
#      continue
        cont.append(d)
    return cont


_currentDBI=None

def getDatabase():
    from p4vasp.uuid import uuid_random as uuid
    from getpass import getuser
    global _currentDBI

    if _currentDBI is not None and type(_currentDBI) != type(""):
        for x in _currentDBI:
            print "DBI:::::::::::::",x.__class__.__name__,x.name
        return _currentDBI


    _currentDBI=os.path.join(getUserConfigurationDirectory(),"database.cfg")

    if os.path.isfile(_currentDBI):
        _currentDBI=createFromConfig([_currentDBI])
        return _currentDBI

    f=open(_currentDBI,"w")
    username = getuser()
    uid = username+"_"+uuid()[1:-1]
    sqlitepath=os.path.join(getUserConfigurationDirectory(),"database.sqlite")
    sqlitecreationscript= os.path.join(p4vasp_home,"data","database","tables_sqlite.sql")
    mysqlcreationscript= os.path.join(p4vasp_home,"data","database","tables_mysql.sql")
    f.write(
    """
  [DEFAULT]
  # The following is the unique user id. It should be a string uniquely
  # identifying the user. The user_uid should be special enough, so that it will be
  # highly unlikely, that any other user will choose exactly the same id.
  # A good value could be e.g. an e-mail address (string derived from the e-mail address),
  # or possibly a combination of the name of the user and the instititute/company name.
  # Think of the user_uid as a long unique login name to all the p4vasp databases where you have access.
  # The given value was generated as a combination of your login name and a random string:

  user_uid                : %s

  # This will be the easy short name (nickname) to access the databases.
  # It should be the same in each database, unless there is a reason
  # to use a different username (e.g. if the username is already used).

  username                : %s

  # Table names. No need to change them.

  table_userinfo          : userinfo
  table_calc              : calc
  table_parameters        : parameters
  table_struct            : struct
  table_energy            : energy
  table_structpos         : structpos
  table_structforce       : structforce
  table_structvelocity    : structvelocity
  table_structconstraints : structconstraints
  table_dos               : dos
  table_ldos              : ldos

  # Each section (starting by a name in the square brackets) is a configuration for one database.
  # Now there is just one - the "Local database":

  [Local database]

  # This is a database type (or database driver).

  type                    : sqlite

  # Path to a file, where the sqlite database should be stored.
  # Usually it does not work, if the file is on a file server.  <------------ IMPORTANT !!!
  # Point the path to a file on a local disk:

  path                    : %s

  # Don't change this unless you know, what are you doing.
  creation_script         : %s

  # If you want to use mysql, uncomment and edit the following lines:

  #[MySQL]
  #
  #commit                  : enabled
  #
  #type                    : mysql
  #default_commit          : disabled
  #db_user                 : p4vasp
  #db_password             : p4vasp
  #db_database             : p4vasp
  #db_host                 : localhost
  #
  #creation_script         : %s

  """%(uid,username,sqlitepath,sqlitecreationscript,mysqlcreationscript))
    f.close()

    msg().confirm(
  """
  The database configuration file was created in
  %s.
  Please, edit this file and restart p4vasp.
  """%_currentDBI)

    return None


#if __name__=="__main__":
#  import p4vasp.SystemPM as pm
#  d=createFromConfig(["tables.cfg"],mixin=P4VMixin)
#  d.connect()
#  cmd=open("tables1.sql").read()
#  d.run(cmd,ignore_errors=1)
#
#  d[0].addUser()
#  s=pm.XMLSystemPM("vasprun.xml")
#  d[0].storePM(s)
