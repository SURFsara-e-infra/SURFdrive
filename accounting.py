#!/usr/bin/env python

import time
import os
import sys
import re


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

def get_size_and_nfiles(dir):
    size=0
    nfiles=0
    for root, dirs, files in os.walk(dir):
        size=size+sum(os.path.getsize(os.path.join(root, name)) for name in files)
        nfiles=nfiles+len(files)

    return size,nfiles

def get_date():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d',tm)

    return timestamp

def get_timestamp(tm):
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp


def main():
    date=get_date()
    eppns=get_eppns()
    for eppn in eppns:
        m3=m2.match(eppn)
        if m3==None:
            log('Corrupted input: '+eppn+'\n')
            sys.exit(1)
        institute=m3.group(1)
        size,nfiles=get_size_and_nfiles(storage_path+'/'+eppn)
        print date+';'+eppn+';'+institute+';'+str(size)+';'+str(nfiles)


if __name__ == '__main__':

    main()
