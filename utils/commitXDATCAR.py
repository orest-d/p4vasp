from p4vasp.db import *
from p4vasp.Structure import Structure
from sys import stdout

db=getDatabase()[0]
db.connect()
db.addUser()

path="XDATCAR"
s=Structure(path)
s.write(stdout)
f=open(path)
for i in range(8):f.readline() #Skip header

db.addRecord(keywords="MD,XDATCAR",name=s.comment)

step=0
while 1:
    for i in range(len(s)):
        s[i]=map(float,f.readline().split())
    step+=1
    #s.write(stdout)
    db.storeStructure(s,step)
    if f.readline().strip()!="":
        break
