#!/usr/bin/env python

import time
import os
import sys
import re
import threading

import mysql.connector


#Where is the owncloud data stored
storage_path='/path/to/storage'

#Number of active threads
nthreads=4

#Database connection details
db='db'
dbhost='dbhost'
dbuser='dbuser'
dbpasswd='dbpasswd'


logfile='/var/log/accounting.log'
m=re.compile('@')
m2=re.compile('.+@(.+)')

data=[]

#We want to use thread local variables
threadlocal=threading.local()

#We want to lock threads as well
lock=threading.Lock()

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

def get_bytes_and_nfiles(dir,lock):
    bytes=0
    nfiles=0
    for root, dirs, files in os.walk(dir):
        sbytes=0
        for name in files:
            try:
                sbytes=sbytes+os.path.getsize(os.path.join(root, name))
                nfiles=nfiles+1
            except:
                e=str(sys.exc_info()[0])
                lock.acquire()
                log('Error:'+e+'\n')
                lock.release()
                continue
        bytes=bytes+sbytes

    return bytes,nfiles

def worker (date,ran,eppns,lock,threadid):
    start=ran[threadid][0]
    end=ran[threadid][1]
    for i in range(start,end):
        m3=m2.match(eppns[i])
        if m3!=None:
            threadlocal.organisation=m3.group(1)
            threadlocal.bytes,threadlocal.nfiles=get_bytes_and_nfiles(storage_path+'/'+eppns[i],lock)
            lock.acquire()
            data.append([date,eppns[i],threadlocal.organisation,threadlocal.bytes,threadlocal.nfiles])
            lock.release()

def get_date():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d',tm)

    return timestamp

def get_timestamp():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp

def main():

    global nthreads
    date=get_date()
    eppns=get_eppns()

    num_eppns=len(eppns)

    if num_eppns<nthreads: nthreads=1

    ran=[]
    e=nthreads
    istart=0
    iend=0
    for i in range(0,nthreads):
        iend=istart+(num_eppns-iend)/e
        ran.append([istart,iend])
        istart=iend
        e=e-1

    for i in range(0,nthreads):

        thread = threading.Thread(target=worker, args=(date,ran,eppns,lock,i,))
        thread.setDaemon(True)
        thread.start()

    main_thread = threading.currentThread()
    for t in threading.enumerate():
        if t is not main_thread:
            t.join()

#Where to put the sql file
    sql_file='/var/tmp/surfdrive_accounting.'+date+'.sql'
    file=open(sql_file,'w')
    for i in range(0,len(data)):


        date=data[i][0]
        eppn=data[i][1]
        organisation=data[i][2]
        bytes=data[i][3]
        nfiles=data[i][4]

        s="insert into surfdrive_usage (date,eppn,organisation,bytes,nfiles) values ('"+date+"','"+eppn+"','"+organisation+"',"+ str(bytes)+","+str(nfiles)+");"
        file.write(s+'\n')

    file.close()

    s="insert into surfdrive_usage (date,eppn,organisation,bytes,nfiles) values ( %s, %s, %s, %s, %s )"
    conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    c=conn.cursor()

    for s in clist:

        c.executemany(s,data)

    conn.commit()
    c.close()
    

if __name__ == '__main__':

    main()


