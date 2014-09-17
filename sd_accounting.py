#!/usr/bin/env python

import time
import os
import sys
import re

import mysql.connector


#Where is the owncloud data stored
storage_path='/path/to/owncloud-data/'

#Database connection details
db='db'
dbhost='dbhost'
dbuser='dbuser'
dbpasswd='dbpasswd'


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
        sbytes=0
        for name in files:
            try:
                sbytes=sbytes+os.path.getsize(os.path.join(root, name))
                nfiles=nfiles+1
            except:
                e=str(sys.exc_info()[0])
                log('Error:'+e+'\n')
        bytes=bytes+sbytes

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


    date=get_date()
    sql_file='/var/tmp/surfdrive_accounting.'+date+'.sql'
    eppns=get_eppns()
    clist=[]
    file=open(sql_file,'w')

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
        file.write(s+'\n')
        clist.append(s)

    file.close()

    conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    c=conn.cursor()

    for s in clist:

        c.execute(s)

    conn.commit()
    c.close()
    

if __name__ == '__main__':

    main()


