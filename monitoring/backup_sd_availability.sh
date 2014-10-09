#!/bin/sh

USER=user
PASSWD='password'

REMOTE_SERVER=surfdrive.surf.nl
STORAGE_PATH=/files/remote.php/nonshib-webdav
PROTOCOL=https
SITE=${PROTOCOL}://${REMOTE_SERVER}/${STORAGE_PATH}
OPTIONS="-s -S -k"
CURL=curl

cd /var/lib/sqlite
echo '.dump' | sqlite3 surfdrive.db | gzip -c >surfdrive.dump.gz
cd - >/dev/null 2>&1

${CURL} ${OPTIONS} --user $USER:$PASSWD -T /var/lib/sqlite/surfdrive.dump.gz -L ${SITE}/surfdrive.dump.gz >/dev/null 2>&1

