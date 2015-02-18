#!/usr/bin/env python

import os,re,datetime,time
import sys
import mysql.connector

yy=datetime.date.today()-datetime.timedelta(days=1)
yr=str(yy.year)
mn=str(yy.month)
dy=str(yy.day)
yesterday=yr+'-'+mn+'-'+dy

conn=mysql.connector.Connect(host='127.0.0.1',user='user',password='passwd',database='database')
c=conn.cursor()
s="select count(*) from last_login where date='"+yesterday+"';"
c.execute(s)
row=c.fetchone()
unique_users=str(row[0])

if unique_users!="":
    s="insert into unique_users (number,date) values ("+unique_users+",'"+yesterday+"');"
    c.execute(s)
    
conn.commit()
c.close()


