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

SQLITE_DIR=/var/lib/sqlite
SQLITEDB="surfdrive.db"

CHECK_NAME="SURFDRIVE"

LOGFILE=/var/log/surfdrivemonitor.log
PERFORMANCELOGFILE=/var/log/surfdriveperformance.log

USER=user
PASSWD='password'

REMOTE_SERVER=surfdrive.surf.nl
STORAGE_PATH=/files/remote.php/nonshib-webdav
PROTOCOL=https
SITE=${PROTOCOL}://${REMOTE_SERVER}/${STORAGE_PATH}
OPTIONS="-s -S -k"
CURL=curl

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
insert_sqlite "$timestamp" "$1"
}

insert_sqlite () {

cd $SQLITE_DIR
echo "insert into availability (timestamp,result) values( '"$1"','"$2"' );" > $TMPFILE3
sqlite3 $SQLITEDB <$TMPFILE3
cd - >/dev/null 2>&1

}

log_performance () {
timestamp=`date --rfc-3339=seconds`
echo $timestamp $1": "$2" secs" >>${PERFORMANCELOGFILE}
}

cleanup () {
rm -f $TMPFILE1 >/dev/null 2>&1
rm -f $TMPFILE2 >/dev/null 2>&1
rm -f $TMPFILE3 >/dev/null 2>&1
${CURL} ${OPTIONS} --user ${USER}:${PASSWD} -X DELETE -L ${SITE}/testdir/ >/dev/null 2>&1
}

create_testfile () {
# This function creates a testfile to write to SURFdrive
dd if=/dev/random of=$TMPFILE1 bs=$TESTFILE_SIZE count=1 >/dev/null 2>&1
if [ "x$?" != "x0" ]; then
cleanup
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
exit $STATE_OK
