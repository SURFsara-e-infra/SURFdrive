#!/usr/bin/env python

import time
import datetime
import locale
import os
import sys

import mysql.connector

db='db'
dbuser='dbuser'
dbhost='127.0.0.1'
dbpasswd='dbpasswd'

logfile='/var/log/institutes.log'

def log(text):
    timestamp=get_timestamp()
    f=open(logfile,'a')
    f.write(timestamp+':'+text)
    f.close()

def get_timestamp():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp

def get_yesterday():
    today=datetime.date.today()
    oneday=datetime.timedelta(days=1)
    yesterday=str(today-oneday)

    return yesterday

def main():

    conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    c=conn.cursor()


    yesterday=get_yesterday()

    s="select distinct(organisation) from surfdrive_usage where date='"+yesterday+"';"
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
            print >> sys.stderr,'Unable to find mapping for '+organisation+'.\n'
    conn.commit()
    c.close()

if __name__ == '__main__':

    main()
