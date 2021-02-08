#!/bin/bash
pid=`ps wwaux | grep "java" | grep -v "grep" | awk '{print $2}'`
ps -p $pid -o etimes | sed '1d'
