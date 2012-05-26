#!/bin/bash

LOGDIR=$HOME/.simple-monitoring/logs

[[ ! -d $LOGDIR ]] && mkdir -p $LOGDIR

uptime >> $LOGDIR/uptimelog
