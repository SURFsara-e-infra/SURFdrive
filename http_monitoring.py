#!/usr/bin/env python

#PROPFIND
#GET
#POST
#PUT
#HEAD
#PROPPATCH
#MOVE
#MKCOL

import sys
import re
from string import strip
import mysql.connector

db='db'
dbuser='dbuser'
dbhost='dbhost'
dbpasswd='dbpasswd'

match=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+\-\s+\"(.+)\"\s+\"(.+)\"')
match2=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+([\-0-9]+)\s+\"(.+)\"\s+\"(.+)\"')

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

def main():
    file='/etc/httpd/logs/access_log'
    parse_file(file)

if __name__ == '__main__':

    main()
