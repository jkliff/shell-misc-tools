#!/bin/bash

LOGDIR=$HOME/.simple-monitoring/logs

[[ ! -d $LOGDIR ]] && mkdir -p $LOGDIR

UPTIME=$(uptime)
echo $UPTIME >> $LOGDIR/uptimelog

echo $UPTIME >> $LOGDIR/dflog
df >> $LOGDIR/dflog
