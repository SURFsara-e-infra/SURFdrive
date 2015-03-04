#!/usr/bin/env python

from datetime import date

file=open('kkk','r')
lines=file.readlines()
file.close()

x=[]
y=[]
ttt=lines[0].split(';')[0].split('-')
date0=date(int(ttt[0]),int(ttt[1]),int(ttt[2]))

for l in lines:
    q=l.split(';')
    ds=q[0]
    val=q[1].replace(',','.')
    y.append(val)
    dsp=ds.split('-')
    year=int(dsp[0])
    month=int(dsp[1])
    day=int(dsp[2])
    date1=date(year,month,day)
    delta=date1-date0
    x.append(delta.days)





sX=0
sY=0
sX2=0
sXY=0
for l,k in zip(y,x):
    sY=sY+float(l)
    sX=sX+k
    sXY=sXY+k*float(l)
    sX2=sX2+k**2
n=len(y)

s=(n*sXY-sX*sY)/(n*sX2-sX*sX)
c=(sY-s*sX)/n

print "slope: "+str(s)
print "intercept: "+str(c)
