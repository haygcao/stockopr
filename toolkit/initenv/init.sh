#!/bin/sh

root_dir=`dirname $0`/../..
root_dir=`realpath $root_dir`

crontab -l > /tmp/cron_bkp
echo "0 * * * 1-5 $root_dir/run_watch_dog.sh" >> /tmp/cron_bkp
crontab /tmp/cron_bkp
rm /tmp/cron_bkp

exit 0

grep -v "^exit 0" /etc/rc.local > /tmp/rc.local_bkp
echo "$root_dir/run_watch_dog.sh" >> /tmp/rc.local_bkp
echo "exit 0" >> /tmp/rc.local_bkp
sudo cp /tmp/rc.local_bkp /etc/rc.local