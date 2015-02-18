#!/usr/bin/env python

import re,time

lmatch=re.compile('([A-Za-z]{3}\s+[0-9]+\s+[0-9]{2}\:[0-9]{2}\:[0-9]{2})\s+(.+)\s+ownCloud\[[0-9]+\]\:\s+\{.+\}\s+User\s+(.+)\s+logged\s+into\s+ownCloud\s.+')
tmmatch=re.compile('([A-Za-z]{3})\s+([0-9]+)\s+([0-9]{2})\:([0-9]{2})\:([0-9]{2})')

a='Jun 29 13:58:53 s35-06 ownCloud[37997]: {admin_audit} User 702412@uvt.nl logged into ownCloud from IP address: 145.100.27.80'

m=lmatch.match(a)
if m != None:
    list=m.groups()
    tm=list[0]
    host=list[1]
    user=list[2]

    ts=tmmatch.match(tm).groups()
    month=str(ts[0])
    day=str(ts[1])

    ct=time.localtime()
    if ct[1]!=12 and re.search('Dec',month): 
        year=str(ct[0]-1)
    else:
        year=str(ct[0])

    hour=str(ts[2])
    minute=str(ts[3])
    second=str(ts[4])
    
    tmstr=year+' '+month+' '+day+' '+hour+':'+minute+':'+second
    tuple=time.strptime(tmstr,"%Y %b %d %H:%M:%S")
    ts_utc=time.gmtime(time.mktime(tuple))

    print ts_utc

    
