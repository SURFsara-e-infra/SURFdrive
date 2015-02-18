#!/usr/bin/env python

import os,re,datetime,time
import sys
import mysql.connector
access_logs=re.compile('access_log.*')
eppn=re.compile('.+\@((?!\/).+)')
user=re.compile('.*\-\s(.+\@.+)\s\[.*')
monitoring=re.compile('.*nagios-plugin.*|.*onno\.zijlstra\@surfsara\.nl.*')

yy=datetime.date.today()-datetime.timedelta(days=1)
year=str(yy.strftime('%Y'))
month=str(yy.strftime('%b'))
day=str(yy.strftime('%d'))
yr=str(yy.year)
mn=str(yy.month)
dy=str(yy.day)

date=re.compile('.*\['+day+'\/'+month+'\/'+year+'\:.*')

logdir='/etc/httpd/logs'

def get_user(line):
    u=''
    uo=user.match(line)
    if uo!=None:
        u=uo.groups()[0]
    return u
    
def get_last_two_access_logs(path):

    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    ls=list(reversed(sorted(os.listdir(path), key=mtime)))
    
    access_log=[]
    i=0
    for l in ls:
        if access_logs.match(l):
            access_log.append(l)
            i=i+1
            if i==2: break
    
    return access_log


access_logs=get_last_two_access_logs(logdir)

users=[]

for access_log in access_logs:
    data=[]
    f=open(logdir+'/'+access_log,'r')
    data=f.readlines()
    f.close()

    for line in data:
        if date.match(line)==None: continue
        if monitoring.match(line)!=None: continue

        if eppn.match(line)!=None:
            u=get_user(line)
            if u!='' and u not in users:
                users.append(u)

    del data

yesterday=yr+'-'+mn+'-'+dy
conn=mysql.connector.Connect(host='127.0.0.1',user='user',password='passwd',database='database')
c=conn.cursor()
for user in users:
    s="insert into last_login (eppn,date) values ('"+user+"','"+yesterday+"') on duplicate key update date='"+yesterday+"';"
    c.execute(s)
    
conn.commit()
c.close()


