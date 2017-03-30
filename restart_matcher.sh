#!/bin/bash
timestamp=`date +"%H:%M:%S %D"`

CMD=/etc/init.d/vm_matcher 
$CMD status
if [ $? -ne 0 ]
then
rm -fr  /tmp/vm_match.pid*
$CMD start
printf "Stopped\t%s" "$timestamp" > /wuwj/ihepcc-wuwj/Code/ATLAS/Monitor/All/VM_Matcher
else
printf "Running\t%s" "$timestamp" > /wuwj/ihepcc-wuwj/Code/ATLAS/Monitor/All/VM_Matcher
fi

