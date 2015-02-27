#!/usr/bin/env python

import mysql.connector
import datetime
import re
import sys

'''
+-----------+------------+------+-----+-------------------+----------------+
| Field     | Type       | Null | Key | Default           | Extra          |
+-----------+------------+------+-----+-------------------+----------------+
| scheduled | tinyint(1) | NO   |     | 1                 |                |
| start     | datetime   | NO   | MUL | NULL              |                |
| end       | datetime   | NO   | MUL | NULL              |                |
| id        | bigint(20) | NO   | PRI | NULL              | auto_increment |
| created   | timestamp  | NO   |     | CURRENT_TIMESTAMP |                |
+-----------+------------+------+-----+-------------------+----------------+
'''

dt=re.compile('[0-9]{4}\-[0-9]{2}\-[0-9]{2}')
tm=re.compile('[0-9]{2}\:[0-9]{2}')
sc=re.compile('[yYnN]')
iy=re.compile('[0-9]+')

db='db'
dbuser='dbuser'
dbhost='dbhost'
dbpasswd='dbpasswd'

def get_datetime(s):

    try:
        dt=datetime.datetime.strptime(s,'%Y-%m-%d %H:%M')
    except:
        sys.stderr.write('Invalid input\n')
        sys.exit(1)

    return dt

def get_input(s,r):

    d=raw_input(s)

    if r.match(d)==None:
        sys.stderr.write('Invalid input\n')
        sys.exit(1)

    return d

def get_maintenance_type(s):
    scheduled=None
    if re.match('y',s)!=None or re.match('Y',s)!=None:
        scheduled=1
    if re.match('n',s)!=None or re.match('N',s)!=None:
        scheduled=0
    if scheduled==None:
        sys.stderr.write('Invalid input\n')
        sys.exit(1)

    return scheduled

def usage():
        sys.stderr.write('Usage: downtime.py <list|delete|insert>\n')

def get_start_end():
    start_date=get_input('start date (YYYY-MM-DD): ',dt)
    start_time=get_input('start time (HH:MM): ',tm)
    start=get_datetime(start_date+' '+start_time)

    end_date=get_input('end date (YYYY-MM-DD): ',dt)
    end_time=get_input('end time (HH:MM): ',tm)
    end=get_datetime(end_date+' '+end_time)

    if end<=start:
        sys.stderr.write('The start time is later than the end time.\n')
        sys.exit(1)

    return start,end
   
def main():

    if len(sys.argv)!=2:
        usage()
        sys.exit(1)

    if sys.argv[1]=='list':

        start,end=get_start_end()

        conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
        c=conn.cursor()

        s="select id,start,end,scheduled from maintenances where end>='"+str(start)+"' and start<='"+str(end)+"';"
        c.execute(s)
        m=c.fetchall()

        print '%10s'%'id','%24s'%'start','%24s'%'end','%12s'%'scheduled'
        for i in m:
            id=str(i[0])
            st=str(i[1])
            en=str(i[2])
            sch=str(i[3])
            print '%10s'%id,'%24s'%st,'%24s'%en,'%12s'%sch

    elif sys.argv[1]=='delete':      
        id=get_input('Id number: ',iy)
        conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
        c=conn.cursor()
        s="delete from maintenances where id="+id+";"
        c.execute(s)
        conn.commit()
        c.close()
    elif sys.argv[1]=='insert':      
  
        start,end=get_start_end()

        sm=get_input('Scheduled (y/n): ',sc)
        scheduled=get_maintenance_type(sm)

        conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
        c=conn.cursor()
        s="select count(*) from maintenances where ( start<='"+str(start)+"' and end>'"+str(start)+"' ) or ( end>='"+str(end)+"' and start<'"+str(end)+"' );"
        c.execute(s)
        m=c.fetchone()

        if m[0]!=0:
            sys.stderr.write('Your downtime is overlapping with an already existing downtime. Overlapping downtimes are not allowed.\n')
            sys.exit(1)

        s="insert into maintenances (start,end,scheduled) values ('"+str(start)+"','"+str(end)+"',"+str(scheduled)+");"
        c.execute(s)

        conn.commit()
        c.close()

    else:
        sys.stderr.write('Command unknown.\n')
        sys.exit(1)



if __name__ == '__main__':
    main()
