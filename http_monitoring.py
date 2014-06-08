#!/usr/bin/env python

#PROPFIND
#GET
#POST
#PUT
#HEAD
#PROPPATCH
#MOVE
#MKCOL

import os
import sys
import re
import time,datetime
from socket import gethostname
from string import strip
#import mysql.connector
from os import listdir
from os.path import isfile, join

db='db'
dbuser='dbuser'
dbhost='dbhost'
dbpasswd='dbpasswd'
 
logdir='logs'
parsed_files_file='/var/tmp/http_monitoring_parsed_files.txt'

match=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+\-\s+\"(.+)\"\s+\"(.+)\"')
match2=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+([\-0-9]+)\s+\"(.+)\"\s+\"(.+)\"')
almatch=re.compile('^access\_log\-[0-9]{8}$')
tmmatch=re.compile('([0-9]{2}\/[a-zA-Z]+\/[0-9]{4}\:[0-9]{2}\:[0-9]{2}\:[0-9]{2})\s+([\+\-][0-9]{4})')

sqlcmd=("insert into http_monitoring (host,timestamp,client,user,request,code,size,referer,user_agent) values (%s,%s,%s,%s,%s,%s,%s,%s,%s);")

def parse_timestamp(ts):
    tinfo=tmmatch.match(ts)
    if tinfo!=None:
        
        tuple=time.strptime(tinfo.groups()[0],"%d/%B/%Y:%H:%M:%S")
        ts_utc=time.gmtime(time.mktime(tuple))

        tstring=str(ts_utc[0])+'-'+str(ts_utc[1])+'-'+str(ts_utc[2])+' '+str(ts_utc[3])+':'+str(ts_utc[4])+':'+str(ts_utc[5])
    else:
        print "Unable to parse "+ts
        sys.exit(1)

    return tstring
        

def get_access_logs(dir):
    files = [ f for f in listdir(dir) if isfile(join(dir,f)) ]
  
    alfiles=[]
    for file in files:
        if almatch.match(file)!=None:
            alfiles.append(file)

    return alfiles

def parse_file (file):

    with open(logdir+'/'+file,'r') as f:
        while True:
            lines = f.readlines(8192)
            if not lines:
                break
            for line in lines:
                host=gethostname()
                m2=match2.match(strip(line))
                if m2 != None:
                    list=m2.groups()
                    client=list[0]
                    user=list[1]
                    timestamp=list[2]
                    request=list[3]
                    code=list[4]
                    size=list[5]
                    referer=list[6]
                    user_agent=list[7]
                    time_string=parse_timestamp(timestamp)

                    data=(host,timestamp,client,user,request,code,size,referer,user_agent)
                else:
                    m=match.match(strip(line))
                    if m != None:
                        list=m.groups()
                        client=list[0]
                        user=list[1]
                        timestamp=list[2]
                        request=list[3]
                        code=list[4]
                        size=0
                        referer=list[5]
                        user_agent=list[6]
                        time_string=parse_timestamp(timestamp)

                        data=(host,timestamp,client,user,request,code,size,referer,user_agent)
                    else:
                        print "Not able to parse "+line
                        sys.exit(1)

                c.execute(sqlcmd,data)
            

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
    


def main():

    alfiles=get_access_logs(logdir)
    files=get_files_to_parse(alfiles)
    for file in files:
        parse_file(file)
        print file
    finalize_parsing(alfiles)


if __name__ == '__main__':

    main()
