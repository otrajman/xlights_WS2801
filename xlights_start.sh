#!/bin/sh
DIR=/home/dietpi/xlights_WS2801
SERVER=$DIR/xlights_server.sh
PATH=$PATH:$DIR
LOGFILE=/var/log/xlights/`date +"%F"`.log

cd $DIR
sudo -u dietpi $SERVER &
