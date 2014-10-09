#!/bin/sh

DAYS="30"

CURRENTDATE="$(date --rfc-3339='seconds')"
OLDERDATE="$(date --rfc-3339='seconds' -d "$DAYS days ago")"

SQLITE_DIR=/var/lib/sqlite
SQLITEDB="surfdrive.db"
TMPFILE=`mktemp -q`

sqlite_query () {

cd /var/lib/sqlite
sqlite3 surfdrive.db <$TMPFILE
cd - >/dev/null 2>&1

}
 
echo "select count(*) from availability where timestamp>'"${OLDERDATE}"';">$TMPFILE

total=`sqlite_query`

echo "select count(*) from availability where timestamp>'"${OLDERDATE}"' and result !='OK';">$TMPFILE

failed=`sqlite_query`

python -c "print ($total - $failed)*100.0/$total"
