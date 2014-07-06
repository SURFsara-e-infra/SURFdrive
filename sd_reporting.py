#!/usr/bin/env python

import time
import locale
import os
import sys

import smtplib, os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

import mysql.connector

locale.setlocale(locale.LC_ALL, 'nl_NL')
maand=time.strftime('%B %Y',time.gmtime(time.time()-1814400))
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

def get_date(secs=0):
    tm=time.localtime(time.time()-secs)
    timestamp=time.strftime('%Y-%m-%d',tm)

    return timestamp

def get_timestamp():
    tm=time.localtime(time.time())
    timestamp=time.strftime('%Y-%m-%d %H:%M:%S',tm)

    return timestamp

def main():

    conn=mysql.connector.Connect(host=dbhost,user=dbuser,password=dbpasswd,database=db)
    c=conn.cursor()

    date=get_date()
    yesterday=get_date(86400)

    csv_file='/var/tmp/surfdrive_accounting.'+date+'.csv'

    file=open(csv_file,'w')
    file.write('SURFdrive accounting '+maand+';\n')
    file.write(';;;;;;\n')
    file.write('1 GB = '+str(GB)+' bytes;\n')
    file.write('1 TB = '+str(TB)+' bytes;\n')
    file.write(';;;;;;\n')

# write the amount of storage per organisation to file
    s="select organisation,sum(bytes) from surfdrive_usage where date='"+yesterday+"' group by organisation;"
    c.execute(s)
    file.write('Storage per organisation;\n')
    file.write('organisation;storage (TB);\n')
    for (organisation,bytes) in c:
        terabytes=round(float(bytes)/TB,3)
        file.write(str(organisation)+';'+str(terabytes)+';\n')
    s="select sum(bytes) from surfdrive_usage where date='"+yesterday+"';"
    c.execute(s)
    terabytes=round(float(c.fetchone()[0])/TB,3)
    file.write('Total storage in TB;'+str(terabytes)+';\n')
    file.write(';;;;;;\n')

# write the number of users per organisation to file
    s="select organisation,count(eppn) from surfdrive_usage where date='"+yesterday+"' group by organisation;"
    c.execute(s)
    file.write('Number of users per organisation;\n')
    file.write('organisation;# users;\n')
    for (organisation,users) in c:
        file.write(str(organisation)+';'+str(users)+';\n')
    s="select count(eppn) from surfdrive_usage where date='"+yesterday+"';"
    c.execute(s)
    file.write('Total number of users;'+str(c.fetchone()[0])+';\n')
    file.write(';;;;;;\n')

# write the number of files per organisation to file
    s="select organisation,sum(nfiles) from surfdrive_usage where date='"+yesterday+"' group by organisation;"
    c.execute(s)
    file.write('Number of files per organisation;\n')
    file.write('organisation;# files;\n')
    for (organisation,files) in c:
        file.write(str(organisation)+';'+str(files)+';\n')
    s="select sum(nfiles) from surfdrive_usage where date='"+yesterday+"';"
    c.execute(s)
    file.write('Total number of files;'+str(c.fetchone()[0])+';\n')
    file.write(';;;;;;\n')

# write the average amount of data per user per organisation to file
    s="select organisation,sum(bytes)/count(eppn) from surfdrive_usage where date='"+yesterday+"' group by organisation;"
    c.execute(s)
    file.write('Average amount of data per user per organisation;\n')
    file.write('organisation;average storage per user (GB);\n')
    for (organisation,bytes) in c:
        gigabytes=round(float(bytes)/GB,3)
        file.write(str(organisation)+';'+str(gigabytes)+';\n')
    s="select sum(bytes)/count(eppn) from surfdrive_usage where date='"+yesterday+"';"
    c.execute(s)
    gigabytes=round(float(c.fetchone()[0])/GB,3)
    file.write('Total storage per user in GB;'+str(gigabytes)+';\n')
    file.write(';;;;;;\n')


    file.close()

    conn.commit()
    c.close()

    send_mail(sender,to,'SURFdrive accounting '+maand,mail_text%(maand),[ csv_file ])


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

    main()


