#!/bin/bash
# Ron Trompert, september 2014
#
# Description:
#
# This plugin checks if the SURFdrive service is running properly.
# Nagios return codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3
STATE_DEPENDENT=4

LOCK=/var/lock/subsys/check_surfdrive

DBUSER='dbuser'
DBPASSWD='dbpasswd'
DB='db'
DBHOST='dbhost'

CHECK_NAME="NAME"

LOGFILE=/var/log/monitor.log
PERFORMANCELOGFILE=/var/log/performance.log

USER=user
PASSWD='ppasswd'

REMOTE_SERVER=remote.server.org
STORAGE_PATH=/files/remote.php/nonshib-webdav
PROTOCOL=https
SITE=${PROTOCOL}://${REMOTE_SERVER}/${STORAGE_PATH}
TIMEOUT=300
OPTIONS="-s -S -k --max-time ${TIMEOUT}"
CURL=curl

if [ -f ${LOCK} ]; then
# previous monitoring job is still running
    exit STATE_OK
fi

touch ${LOCK}

#Create a 1 MB file.
TESTFILE_SIZE=1048576
TMPFILE1=`mktemp -q`
TMPFILE2="/tmp/testfile"`date +%s`
TMPFILE3=`mktemp -q`
${CURL} ${OPTIONS} --user ${USER}:${PASSWD} -X DELETE -L ${SITE}/testdir/ >/dev/null 2>&1

elapsed_time () {
   python -c "print $2 - $1"
}

timestamp () {
    date +%s.%N
}

log () {
timestamp=`date --rfc-3339=seconds`
echo $timestamp $1 >>${LOGFILE}
insert_av_sql "$timestamp" "$1"
}

insert_av_sql () {

echo "insert into availability (timestamp,result) values( '"$1"','"$2"' );" > $TMPFILE3
mysql -u ${DBUSER} --password=${DBPASSWD} -h ${DBHOST} ${DB} <$TMPFILE3 2>/dev/null

}

insert_pf_sql () {

echo "insert into performance (timestamp,test,time) values( '"$1"','"$2"',"$3" );" > $TMPFILE3
mysql -u ${DBUSER} --password=${DBPASSWD} -h ${DBHOST} ${DB} <$TMPFILE3 2>/dev/null

}

log_performance () {
timestamp=`date --rfc-3339=seconds`
echo $timestamp $1": "$2" secs" >>${PERFORMANCELOGFILE}
insert_pf_sql "$timestamp" "$1" "$2"
}

cleanup () {
rm -f $TMPFILE1 >/dev/null 2>&1
rm -f $TMPFILE2 >/dev/null 2>&1
rm -f $TMPFILE3 >/dev/null 2>&1
${CURL} ${OPTIONS} --user ${USER}:${PASSWD} -X DELETE -L ${SITE}/testdir/ >/dev/null 2>&1
}

create_testfile () {
# This function creates a testfile to write to SURFdrive
dd if=/dev/urandom of=$TMPFILE1 bs=$TESTFILE_SIZE count=1 >/dev/null 2>&1
if [ "x$?" != "x0" ]; then
cleanup
rm -f ${LOCK}
exit $STATE_WARNING
fi
}

test_create_directory () {

t0=`timestamp`
${CURL} ${OPTIONS} --user ${USER}:${PASSWD} -X MKCOL -L ${SITE}/testdir/ >/dev/null 2>&1
ret=$?
t1=`timestamp`
if [ "x$ret" != "x0" ]; then
cleanup
log "test_create_directory failed"
rm -f ${LOCK}
exit $STATE_CRITICAL
fi
elaps=`elapsed_time $t0 $t1`
log_performance "test_create_directory" $elaps
}

test_delete_directory () {

t0=`timestamp`
${CURL} ${OPTIONS} --user ${USER}:${PASSWD} -X DELETE -L ${SITE}/testdir/ >/dev/null 2>&1
ret=$?
t1=`timestamp`
if [ "x$ret" != "x0" ]; then
cleanup
log "test_delete_directory failed"
rm -f ${LOCK}
exit $STATE_CRITICAL
fi
elaps=`elapsed_time $t0 $t1`
log_performance "test_delete_directory" $elaps
}

test_list_directory () {

t0=`timestamp`
listing=`${CURL} ${OPTIONS} --user ${USER}:${PASSWD} -L ${SITE}/testdir/ | grep sabreAction | grep -v favicon | sed 's/.*href\=\"//' | sed 's/\".*//' | grep testfile 2>&1`
t1=`timestamp`
if [ "x$listing" == "x" ]; then
cleanup
log "test_list_directory failed"
rm -f ${LOCK}
exit $STATE_CRITICAL
fi
elaps=`elapsed_time $t0 $t1`
log_performance "test_list_directory" $elaps
}

test_read () {
# Client read test

t0=`timestamp`
${CURL} ${OPTIONS} --user $USER:$PASSWD -L ${SITE}/testdir/testfile -o $TMPFILE2 >/dev/null 2>&1
ret=$?
t1=`timestamp`
if [ "x$ret" != "x0" ]; then
cleanup
log "test_read failed"
rm -f ${LOCK}
exit $STATE_CRITICAL
fi
elaps=`elapsed_time $t0 $t1`
log_performance "test_read" $elaps
}

test_write () {
# Client write test

t0=`timestamp`
${CURL} ${OPTIONS} --user $USER:$PASSWD -T ${TMPFILE1} -L ${SITE}/testdir/testfile >/dev/null 2>&1
ret=$?
t1=`timestamp`
if [ "x$ret" != "x0" ]; then
cleanup
log "test_write failed"
rm -f ${LOCK}
exit $STATE_CRITICAL
fi
elaps=`elapsed_time $t0 $t1`
log_performance "test_write" $elaps
}

test_checksum () {
MD5_1=`md5sum ${TMPFILE1}| awk '{print $1}'`
MD5_2=`md5sum ${TMPFILE2}| awk '{print $1}'`
if [ "x${MD5_1}" != "x${MD5_2}" ]; then
cleanup
log "test_checksum failed"
rm -f ${LOCK}
exit $STATE_CRITICAL
fi
}

create_testfile
test_create_directory
test_write
test_list_directory
test_read
test_delete_directory
test_checksum
cleanup

#All's well that ends well!
log "OK"
rm -f ${LOCK}
exit $STATE_OK
