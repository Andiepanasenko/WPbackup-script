#!/bin/bash
pid=`ps wwaux | grep "java" | grep -v "grep" | awk '{print $2}'`
current_memory=`/usr/lib/jvm/jdk1.8.0_121/bin/jstat -gc $pid | awk '{print ($1+$2+$5+$7)*1024}' | sed '1d'`
usage_memory=`/usr/lib/jvm/jdk1.8.0_121/bin/jstat -gc $pid | awk '{print ($8+$6+$3+$4)*1024}' | sed '1d'`

if [[ "$1" == "usage" ]]
        then
                echo $usage_memory
fi

if [[ "$1" == "current" ]]
        then
                echo $current_memory
