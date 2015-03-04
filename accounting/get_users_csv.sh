#!/bin/sh

tmpfile=`mktemp`
s="select date,count(eppn) from surfdrive_usage group by date asc;"
echo $s >$tmpfile

mysql -u user -p -r -h dbserver database <${tmpfile} | awk '{print $1";"$2}'

rm -f ${tmpfile}
