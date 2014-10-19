#!/usr/bin/env python

import time
import datetime
import locale
import os
import sys
import getopt

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

import mysql.connector

mail_text="""

Hallo SURFdrivers,

Hier is de accounting data van %s.

Mvg,

De accounting database
"""

sender='sender@example.com'
to=['receiver@example.com']

db='db'
dbuser='dbuser'
dbhost='dbhost'
dbpasswd='dbpasswd'

GB=1024*1024*1024
TB=GB*1024

logfile='/var/log/reporting.log'

def log(text):
    timestamp=get_timestamp()
    f=open(logfile,'a')
    f.write(timestamp+':'+text)
    f.close()

def get_vorigemaand():
    locale.setlocale(locale.LC_ALL, 'nl_NL')
    today=datetime.date.today()
    first=datetime.date(day=1,month=today.month,year=today.year)
    lastdayoflastmonth=first-datetime.timedelta(days=1)
    vorige_maand=lastdayoflastmonth.strftime('%B %Y')

    return vorige_maand

def get_gisteren ():
    locale.setlocale(locale.LC_ALL, 'nl_NL')
    today=datetime.date.today()
    yesterday=today-datetime.timedelta(days=1)
    gisteren=yesterday.strftime('%d %B %Y')

    return gisteren

def get_yesterday():
    today=datetime.date.today()
    yesterday=today-datetime.timedelta(days=1)
    timestamp=yesterday.strftime('%Y-%m-%d')

    return timestamp

def get_lastdayoflastmonth():
    today=datetime.date.today()
    first=datetime.date(day=1,month=today.month,year=today.year)
    lastdayoflastmonth=first-datetime.timedelta(days=1)
    timestamp=lastdayoflastmonth.strftime('%Y-%m-%d')

    return timestamp

def get_timestamp():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp

def main(argv):

    if len(argv)==0:
        print 'sd_reporting.py [-m |-w]'
        sys.exit(0)

    month=False
    day=False

    try:
        opts, args = getopt.getopt(argv,"hmd")
    except getopt.GetoptError:
        print 'sd_reporting.py [-m |-d]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'sd_reporting.py [-m |-w]'
            sys.exit(0)
        elif opt in ("-m"):
            month=True
        elif opt in ("-d"):
            day=True

    conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    c=conn.cursor()

    if month: 
        pit=get_lastdayoflastmonth()
        pitd=get_vorigemaand()

    if day: 
        pit=get_yesterday()
        pitd=get_gisteren()

    csv_file='/var/tmp/surfdrive_accounting.'+pitd+'.csv'

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
            print >> sys.stderr,'Unable to find mapping for '+organisation+'.\n'
            sys.exit(1)
        map=str(m[0])
        odict.update({organisation:map})

    file=open(csv_file,'w')
    file.write('SURFdrive accounting '+pitd+';\n')
    file.write(';;;;;;\n')
    file.write('1 GB = '+str(GB)+' bytes;\n')
    file.write('1 TB = '+str(TB)+' bytes;\n')
    file.write(';;;;;;\n')

# write the amount of storage per organisation to file
    s="select organisation,sum(bytes) from surfdrive_usage where date='"+pit+"' group by organisation;"
    c.execute(s)
    file.write('Storage per organisation;\n')
    file.write('eppn;organisation;storage (TB);\n')
    for (organisation,bytes) in c:
        terabytes=round(float(bytes)/TB,3)
        file.write(str(organisation)+';'+odict[organisation]+';'+str(terabytes)+';\n')
    s="select sum(bytes) from surfdrive_usage where date='"+pit+"';"
    c.execute(s)
    terabytes=round(float(c.fetchone()[0])/TB,3)
    file.write('Total storage in TB;'+str(terabytes)+';\n')
    file.write(';;;;;;\n')

# write the number of users per organisation to file
    s="select organisation,count(eppn) from surfdrive_usage where date='"+pit+"' group by organisation;"
    c.execute(s)
    file.write('Number of users per organisation;\n')
    file.write('eppn;organisation;# users;\n')
    for (organisation,users) in c:
        file.write(str(organisation)+';'+odict[organisation]+';'+str(users)+';\n')
    s="select count(eppn) from surfdrive_usage where date='"+pit+"';"
    c.execute(s)
    file.write('Total number of users;'+str(c.fetchone()[0])+';\n')
    file.write(';;;;;;\n')

# write the number of files per organisation to file
    s="select organisation,sum(nfiles) from surfdrive_usage where date='"+pit+"' group by organisation;"
    c.execute(s)
    file.write('Number of files per organisation;\n')
    file.write('eppn;organisation;# files;\n')
    for (organisation,files) in c:
        file.write(str(organisation)+';'+odict[organisation]+';'+str(files)+';\n')
    s="select sum(nfiles) from surfdrive_usage where date='"+pit+"';"
    c.execute(s)
    file.write('Total number of files;'+str(c.fetchone()[0])+';\n')
    file.write(';;;;;;\n')

# write the average amount of data per user per organisation to file
    s="select organisation,sum(bytes)/count(eppn) from surfdrive_usage where date='"+pit+"' group by organisation;"
    c.execute(s)
    file.write('Average amount of data per user per organisation;\n')
    file.write('eppn;organisation;average storage per user (GB);\n')
    for (organisation,bytes) in c:
        gigabytes=round(float(bytes)/GB,3)
        file.write(str(organisation)+';'+odict[organisation]+';'+str(gigabytes)+';\n')
    s="select sum(bytes)/count(eppn) from surfdrive_usage where date='"+pit+"';"
    c.execute(s)
    gigabytes=round(float(c.fetchone()[0])/GB,3)
    file.write('Total average storage per user in GB;'+str(gigabytes)+';\n')
    file.write(';;;;;;\n')


    file.close()

    conn.commit()
    c.close()

    send_mail(sender,to,'SURFdrive accounting '+pitd,mail_text%(pitd),[ csv_file ])


def send_mail(send_from, send_to, subject, text, files=[], server="localhost"):
    assert isinstance(send_to, list)
    assert isinstance(files, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
    

if __name__ == '__main__':

    
    main(sys.argv[1:])


