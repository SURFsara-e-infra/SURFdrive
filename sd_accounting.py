#!/usr/bin/env python

import time
import os
import sys
import re

import mysql.connector


storage_path='/glusterfs/volumes/gv0/owncloud-data/'

logfile='/var/log/accounting.log'
m=re.compile('@')
m2=re.compile('.+@(.+)')

def log(text):
    timestamp=get_timestamp()
    f=open(logfile,'a')
    f.write(timestamp+':'+text)
    f.close()

def get_eppns():
    eppns=[]
    if os.path.isdir(storage_path):
        entries=os.listdir(storage_path)
        for entry in entries:
            if os.path.isdir(storage_path+'/'+entry):
                if m.search(entry) != None:
                    eppns.append(entry)
    else:
        log(storage_path+' is a nonexisting directory\n')
        sys.exit(1)
    return eppns

def get_bytes_and_nfiles(dir):
    bytes=0
    nfiles=0
    for root, dirs, files in os.walk(dir):
        bytes=bytes+sum(os.path.getsize(os.path.join(root, name)) for name in files)
        nfiles=nfiles+len(files)

    return bytes,nfiles

def get_date():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d',tm)

    return timestamp

def get_timestamp():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp

def main():

    conn=mysql.connector.Connect(host='<hostip>',user='<user>',password='<password>',database='<database>')
    c=conn.cursor()

    date=get_date()
    eppns=get_eppns()
    for eppn in eppns:
        m3=m2.match(eppn)
        if m3==None:
            log('Corrupted input: '+eppn+'\n')
            sys.exit(1)
        organisation=m3.group(1)
        bytes,nfiles=get_bytes_and_nfiles(storage_path+'/'+eppn)
#        print date+';'+eppn+';'+organisation+';'+str(bytes)+';'+str(nfiles)
        s="insert into surfdrive_usage (date,eppn,organisation,bytes,nfiles) values ('"+date+"','"+eppn+"','"+organisation+"',"+ str(bytes)+","+str(nfiles)+");"
#        print s
        c.execute(s)

    conn.commit()
    c.close()
    

if __name__ == '__main__':

    main()


