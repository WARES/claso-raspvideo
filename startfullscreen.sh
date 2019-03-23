#!/bin/sh
# Lauch watchdog to restart service if hangs
'/home/pi/watchdog.py' &
if [ -z $DISPLAY ] ; then
	DISPLAY=:0
	'/home/pi/startloop.py'
else
	'xterm -fullscreen -fg black -bg black -e /home/pi/startloop.py'
fi
