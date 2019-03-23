#!/usr/bin/python
from time import sleep
from subprocess import Popen, PIPE, call
import syslog

syslog.syslog('Starting /home/pi/watchdog.py')
count=0
while True:
	ps = Popen(['ps', '-C', 'omxplayer.bin', '-o', '%cpu'], stdout=PIPE).communicate()[0]
	a=ps.split('\n')[1]
	if (a == '') or (float(a) < 10) or (float(a) > 50):
		#print ('Out of range')
		count=count+1
	else:
		#print ('Fine')
		count=0
	if count > 5:
		syslog.syslog('Restarting service videoloop')
		count=0
		call(['service', 'videoloop', 'restart'])
	sleep(2)



