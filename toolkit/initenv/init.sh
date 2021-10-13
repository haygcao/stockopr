#!/bin/sh

root_dir=`dirname $0`/../..
root_dir=`realpath $root_dir`

crontab -l > /tmp/cron_bkp
echo "0 * * * 1-5 $root_dir/run_watch_dog.sh" >> /tmp/cron_bkp
crontab /tmp/cron_bkp
rm /tmp/cron_bkp