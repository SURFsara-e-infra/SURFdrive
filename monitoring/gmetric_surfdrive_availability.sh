#!/bin/sh


av=`/usr/local/sbin/sd_availability.sh`
gmetric --name=SURFdrive --value=${av} --units=percent --type=float --dmax=3600
