#!/bin/sh

tmpfile=`mktemp`
s="select date,sum(bytes)*1.0/(sum(nfiles)*1000000) from surfdrive_usage group by date asc;"
echo $s >$tmpfile

mysql -u user -p -r -h dbserver database < ${tmpfile} | awk '{print $1";"$2}' | sed 's/\./\,/'

rm -f ${tmpfile}
