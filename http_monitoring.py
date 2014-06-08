#!/usr/bin/env python

import os
import sys
import re
import time,datetime
from socket import gethostname
from string import strip
import mysql.connector
from os import listdir
from os.path import isfile, join

db='db'
dbuser='dbuser'
dbhost='dbhost'
dbpasswd='dbpasswd'
 
logdir='/etc/httpd/logs'
parsed_files_file='/var/tmp/http_monitoring_parsed_files.txt'
logfile='/var/log/http_monitoring.log'

match=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+\-\s+\"(.+)\"\s+\"(.+)\"')
match2=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+([\-0-9]+)\s+\"(.+)\"\s+\"(.+)\"')
almatch=re.compile('^access\_log\-[0-9]{8}$')
opmatch=re.compile('([A-Za-z]+)\s+.+')
tmmatch=re.compile('([0-9]{2}\/[a-zA-Z]+\/[0-9]{4}\:[0-9]{2}\:[0-9]{2}\:[0-9]{2})\s+([\+\-][0-9]{4})')

sqlcmd="insert into http_monitoring (host,client,user,request,op,code,size,referer,user_agent,time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

def parse_timestamp(ts):
    tinfo=tmmatch.match(ts)
    if tinfo!=None:
        
        tuple=time.strptime(tinfo.groups()[0],"%d/%b/%Y:%H:%M:%S")
        ts_utc=time.gmtime(time.mktime(tuple))

        tstring=str(ts_utc[0])+'-'+str(ts_utc[1])+'-'+str(ts_utc[2])+' '+str(ts_utc[3])+':'+str(ts_utc[4])+':'+str(ts_utc[5])
    else:
        log("Unable to parse "+ts)
        sys.exit(1)

    return tstring
        
def log(text):

    f=open(logfile,'a')
    f.write(text+'\n')
    f.close()

def get_access_logs(dir):
    files = [ f for f in listdir(dir) if isfile(join(dir,f)) ]
  
    alfiles=[]
    for file in files:
        if almatch.match(file)!=None:
            alfiles.append(file)

    return alfiles

def get_op(r):

    o=opmatch.match(r)
    if o!=None:
        op=o.groups()[0]
    else:
        op=''

    return op

def parse_file (file):

    conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    c=conn.cursor()

    with open(logdir+'/'+file,'r') as f:
        while True:
            lines = f.readlines(65536)
            if not lines:
                break
            data=[]
            for line in lines:
                host=gethostname()
                m2=match2.match(strip(line))
                if m2 != None:
                    list=m2.groups()
                    client=list[0]
                    user=list[1]
                    timestamp=list[2]
                    request=list[3]
                    op=get_op(request)
                    code=list[4]
                    size=list[5]
                    referer=list[6]
                    user_agent=list[7]
                    time_string=parse_timestamp(timestamp)

                    data.append((host,client,user,request,op,code,size,referer,user_agent,time_string))
                else:
                    m=match.match(strip(line))
                    if m != None:
                        list=m.groups()
                        client=list[0]
                        user=list[1]
                        timestamp=list[2]
                        request=list[3]
                        op=get_op(request)
                        code=list[4]
                        size=0
                        referer=list[5]
                        user_agent=list[6]
                        time_string=parse_timestamp(timestamp)

                        data.append((host,client,user,request,op,code,size,referer,user_agent,time_string))
                    else:
                        log("Not able to parse "+line)
                        sys.exit(1)

            c.executemany(sqlcmd,data)
            
    conn.commit()
    conn.close()

def get_parsed_files_from_file():
    if os.path.isfile(parsed_files_file):
        f=open(parsed_files_file,'r')
        pf=strip(f.readline()).split(';')
        f.close()
    else:
        pf=[]

    return pf

def finalize_parsing(alfiles):
    
    for file in alfiles:
        if alfiles.index(file) == 0:
            txt=file
        else:
            txt=txt+';'+file
    
    f=open(parsed_files_file,'w')
    f.write(txt)
    f.close()

    

def get_files_to_parse(alfiles):

    parsed_files=get_parsed_files_from_file()

    files_to_parse=[]
    for file in alfiles:
        if file not in parsed_files: files_to_parse.append(file)

    return files_to_parse

def get_now():

    t=time.localtime()
    tstring=str(t[0])+'-'+str(t[1])+'-'+str(t[2])+' '+str(t[3])+':'+str(t[4])+':'+str(t[5])
   
    return tstring

def main():

    alfiles=get_access_logs(logdir)
    files=get_files_to_parse(alfiles)
    log("Processing access_logs at: "+get_now())
    for file in files:
        log("Processing "+file)
        parse_file(file)
        log("Processed "+file)
    finalize_parsing(alfiles)


if __name__ == '__main__':

    main()
