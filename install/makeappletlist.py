from glob import *
from os.path import join,split

def applets(path):
    modules=[]
    for x in glob(join(path,"*Applet.py")):
        l=["p4vasp","applet"]
        s=split(x)[1].replace(".py","")
        if s not in ["Applet"]:
            l.append(s)
            l.append(s)
            modules.append(".".join(l))
    return modules

f=open(join("..","lib","p4vasp","applet","appletlist.py"),"w")
f.write("def appletlist():\n")
f.write("  return [\n")
app=applets(join("..","lib","p4vasp","applet"))
f.write(",\n".join(map(lambda x:"    '%s'"%x,app)))
f.write("\n  ]\n")
