#!/usr/bin/env python

PROPFIND | grep -v GET | grep -v POST | grep -v PUT | grep -v HEAD | grep -v PROPPATCH | grep -v MOVE | grep -v MKCOL
import sys
import re
from string import strip

match=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+\-\s+\"(.+)\"\s+\"(.+)\"')
match2=re.compile('^(.+)\s+\-\s+(.+)\s+\[(.+)\]\s+\"(.+)\"\s+([0-9]+)\s+([\-0-9]+)\s+\"(.+)\"\s+\"(.+)\"')

def main ():

    with open('/etc/httpd/logs/access_log','r') as f:
        while True:
            lines = f.readlines(8192)
            if not lines:
                break
            for line in lines:
                m2=match2.match(strip(line))
                if m2 != None:
                    list=m2.groups()
                    ip=list[0]
                    eppn=list[1]
                    timestamp=list[2]
                    request=list[3]
                    code=list[4]
                    size=list[5]
                    file=list[6]
                    browser=list[7]
                else:
                    m=match.match(strip(line))
                    if m != None:
                        list=m.groups()
                        ip=list[0]
                        eppn=list[1]
                        timestamp=list[2]
                        request=list[3]
                        code=list[4]
                        size=0
                        file=list[5]
                        browser=list[6]
                    else:
                        print "Not able to parse "+line
                        sys.exit(1)

if __name__ == '__main__':

    main()
