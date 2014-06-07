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
almatch=re.compile('^access\_log\-([0-9]{8})$')

def get_access_logs(dir):
    files = [ f for f in listdir(dir) if isfile(join(dir,f)) ]
  
    alfiles=[]
    for file in files:
        if almatch.match(file)!=None:
            alfiles.append(file)

    return alfiles

def parse_file (file):

    with open(file,'r') as f:
        while True:
            lines = f.readlines(8192)
            if not lines:
                break
            for line in lines:
                m2=match2.match(strip(line))
                if m2 != None:
                    list=m2.groups()
                    ip=list[0]
                    user=list[1]
                    timestamp=list[2]
                    request=list[3]
                    code=list[4]
                    size=list[5]
                    referer=list[6]
                    user_agent=list[7]
                else:
                    m=match.match(strip(line))
                    if m != None:
                        list=m.groups()
                        ip=list[0]
                        user=list[1]
                        timestamp=list[2]
                        request=list[3]
                        code=list[4]
                        size=0
                        referer=list[5]
                        user_agent=list[6]
                    else:
                        print "Not able to parse "+line
                        sys.exit(1)

def get_dates_from_alfile_names(alfiles):

    dates=[]
    for alf in alfiles:
        dates.append(long(almatch.match(alf).groups()[0]))

    return sorted(dates)

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
#        parse_file(file)
         print file
    finalize_parsing(alfiles)


if __name__ == '__main__':

    main()
