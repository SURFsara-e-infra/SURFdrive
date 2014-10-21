#!/usr/bin/env python

import time
import datetime
import locale
import os
import sys
import getopt
import tempfile
import commands
import re

import mysql.connector

php_script="""
<?php
function SOAPdebug ($client) {
    print "\n";
    print "Request :\n".htmlspecialchars($client->__getLastRequest()) ."\n";

    print "Response:\n".htmlspecialchars($client->__getLastResponse())."\n"; print "\n";
}


$client = new SoapClient("https://HOST:PORT/interface.php?wsdl", array ('trace' => 1, 'exceptions' => 0));

$user = "user";
$pass = "pass";
$params = array (
%s
);

$result = $client->%s ( $user, $pass, $params );
print_r ($result);

SOAPdebug($client);

?>
"""

db='db'
dbuser='dbuser'
dbhost='dbhost'
dbpasswd='dbpasswd'

GB=1024*1024*1024
TB=GB*1024

def usage():
    print >> sys.stderr,'sd_reporting_dashboard.py [insert|delete|approve]\n'
    

def log(text):
    timestamp=get_timestamp()
    print >> sys.stderr,timestamp+':'+text+'\n'

def get_lastdayoflastmonth():
    today=datetime.date.today()
    first=datetime.date(day=1,month=today.month,year=today.year)
    lastdayoflastmonth=first-datetime.timedelta(days=1)
    timestamp=lastdayoflastmonth.strftime('%Y-%m-%d')

    return timestamp

def get_lastmonth():
    today=datetime.date.today()
    first=datetime.date(day=1,month=today.month,year=today.year)
    lastdayoflastmonth=first-datetime.timedelta(days=1)
    timestamp=lastdayoflastmonth.strftime('%Y-%m')

    return timestamp

def get_timestamp():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp

def main(operation):

    conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    c=conn.cursor()

    pit=get_lastdayoflastmonth()

    last_month=get_lastmonth()

    s="select distinct(organisation) from surfdrive_usage where date='"+pit+"';"
    c.execute(s)
    olist=[]
    for o in c:
         olist.append(str(o[0]))

    odict={}
    for organisation in olist:
        s="select map from orgmap where organisation='"+organisation+"';"
        c.execute(s)
        m=c.fetchone()
        if m==None:
            log('Unable to find mapping for '+organisation+'.')
            sys.exit(1)
        map=str(m[0])
        odict.update({organisation:map})

# write the number of users per organisation to file
    s="select organisation,count(eppn) from surfdrive_usage where date='"+pit+"' group by organisation;"
    c.execute(s)
   
    _,tmpfile=tempfile.mkstemp()
    for (organisation,users) in c:

        if odict[organisation]=='TEST': continue
        
        f=open(tmpfile,'w')
        
        if operation=='er_InsertReport':
            php_array= \
                      '\"Value\" => '+str(users)+',\n       \
                       \"Type\" => \"Aantal gebruikers\",\n \
                       \"DepartmentList\"=> \"MWS,AA\",\n   \
                       \"Period\" => \"'+last_month+'\",\n  \
                       \"Organisation\" => \"'+odict[organisation]+'\",\n  \
                       \"IsKPI\" => false,\n                \
                       \"IsHidden\" => false,\n'
            f.write(php_script%(php_array,'er_InsertReport'))
        elif operation=='er_DeleteReport':
            php_array= \
                      '\"Type\" => \"Aantal gebruikers\",\n \
                       \"Period\" => \"'+last_month+'\",\n  \
                       \"Organisation\" => \"'+odict[organisation]+'\",\n'
            f.write(php_script%(php_array,'er_DeleteReport'))
        elif operation=='er_ApproveReport':
            php_array= \
                      '\"Type\" => \"Aantal gebruikers\",\n \
                       \"Period\" => \"'+last_month+'\",\n  \
                       \"Organisation\" => \"'+odict[organisation]+'\",\n'
            f.write(php_script%(php_array,'er_ApproveReport'))
        else:
            log('You should not get here in the code.\n')
            sys.exit(1)

        f.close()

        command='php -f '+tmpfile
        retval,output=commands.getstatusoutput(command)

        if retval!=0:
            log('Unable to perform '+operation+' for '+odict[organisation]+'.')
            log(output)
            sys.exit(1)

        returncode=re.search('(?<=\[ReturnCode\]\s\=\>\s).+',output).group(0)
        returntext=re.search('(?<=\[ReturnText\]\s\=\>\s).+',output).group(0)

        if returncode!='1':
            log('Unable to perform  '+operation+' for '+odict[organisation]+' failed. returncode: '+returncode+', returntext: '+returntext+'.')
        else:
            log('Successfully performed '+operation+' for '+odict[organisation]+'. returncode: '+returncode+', returntext: '+returntext+'.')

    s="select count(eppn) from surfdrive_usage where date='"+pit+"';"
    c.execute(s)
    users=str(c.fetchone()[0])

    f=open(tmpfile,'w')

    if operation=='er_InsertReport':
        php_array= \
              '\"Value\" => '+users+',\n       \
               \"Type\" => \"Totaal aantal gebruikers\",\n \
               \"DepartmentList\"=> \"MWS,AA\",\n   \
               \"Period\" => \"'+last_month+'\",\n  \
               \"IsKPI\" => false,\n                \
               \"IsHidden\" => false,\n'
        f.write(php_script%(php_array,'er_InsertReport'))
    elif operation=='er_DeleteReport':
        php_array= \
              '\"Type\" => \"Totaal aantal gebruikers\",\n \
               \"Period\" => \"'+last_month+'\",\n'
        f.write(php_script%(php_array,'er_DeleteReport'))
    elif operation=='er_ApproveReport':
        php_array= \
              '\"Type\" => \"Totaal aantal gebruikers\",\n \
               \"Period\" => \"'+last_month+'\",\n'
        f.write(php_script%(php_array,'er_ApproveReport'))
    else:
        log('You should not get here in the code.\n')
        sys.exit(1)

    f.close()

    command='php -f '+tmpfile
    retval,output=commands.getstatusoutput(command)

    if retval!=0:
        log('Unable to perform '+operation+' for totaal aantal gebruikers.')
        log(output)
        sys.exit(1)

    returncode=re.search('(?<=\[ReturnCode\]\s\=\>\s).+',output).group(0)
    returntext=re.search('(?<=\[ReturnText\]\s\=\>\s).+',output).group(0)

    if returncode!='1':
        log('Unable to perform  '+operation+' for totaal aantal gebruikers failed. returncode: '+returncode+', returntext: '+returntext+'.')
    else:
        log('Successfully performed '+operation+' for totaal aantal gebruikers. returncode: '+returncode+', returntext: '+returntext+'.')

    s="select sum(bytes) from surfdrive_usage where date='"+pit+"';"
    c.execute(s)
    terabytes=str(round(float(c.fetchone()[0])/TB,3))

    f=open(tmpfile,'w')

    if operation=='er_InsertReport':
        php_array= \
              '\"Value\" => '+terabytes+',\n       \
               \"Type\" => \"Hoeveelheid storage\",\n \
               \"DepartmentList\"=> \"MWS,AA\",\n   \
               \"Period\" => \"'+last_month+'\",\n  \
               \"IsKPI\" => false,\n                \
               \"IsHidden\" => false,\n'
        f.write(php_script%(php_array,'er_InsertReport'))
    elif operation=='er_DeleteReport':
        php_array= \
              '\"Type\" => \"Hoeveelheid storage\",\n \
               \"Period\" => \"'+last_month+'\",\n'
        f.write(php_script%(php_array,'er_DeleteReport'))
    elif operation=='er_ApproveReport':
        php_array= \
              '\"Type\" => \"Hoeveelheid storage\",\n \
               \"Period\" => \"'+last_month+'\",\n'
        f.write(php_script%(php_array,'er_ApproveReport'))
    else:
        log('You should not get here in the code.\n')
        sys.exit(1)

    f.close()

    command='php -f '+tmpfile
    retval,output=commands.getstatusoutput(command)

    if retval!=0:
        log('Unable to perform '+operation+' for hoeveelheid storage.')
        log(output)
        sys.exit(1)

    returncode=re.search('(?<=\[ReturnCode\]\s\=\>\s).+',output).group(0)
    returntext=re.search('(?<=\[ReturnText\]\s\=\>\s).+',output).group(0)

    if returncode!='1':
        log('Unable to perform  '+operation+' for hoeveelheid storage failed. returncode: '+returncode+', returntext: '+returntext+'.')
    else:
        log('Successfully performed '+operation+' for hoeveelheid storage. returncode: '+returncode+', returntext: '+returntext+'.')

    os.remove(tmpfile)

    conn.commit()
    c.close()



if __name__ == '__main__':

    if len(sys.argv)==2:
        o=sys.argv[1]
        if o=='insert':
            operation='er_InsertReport'
        elif o=='delete':
            operation='er_DeleteReport'
        elif o=='approve':
            operation='er_ApproveReport'
        else:
            usage()
            sys.exit(1)
    else:
        usage()
        sys.exit(1)

    main(operation)
