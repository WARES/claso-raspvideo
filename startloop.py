#!/usr/bin/python

# Program name : startloop.py
# Creation date : february 2015
#
# By Enrique Nares
# Function : Plays a large video in loop
#                  Pressing a button pauses the large video and plays small video instead
# Uses : /etc/init.d/videoloop
#	     /home/pi/startfullscreen.sh
#        /home/pi/startloop.py
#	     /boot/clasovideoconfig.txt

# Importation section
from time import sleep
import RPi.GPIO as GPIO
from subprocess import call, Popen, PIPE
import time
import thread
import glob
import sys

# Global settings
GPIO.setmode (GPIO.BCM) #Broadcom SOC channel
GPIO.setwarnings (False)

# GPIO setup
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Global Variables
button_busy = False	# if True, pressing a button will do nothing
video_ending = False	# if True, pressing a button will do nothing
countdown = 0		# seconds that remains until reaching en of main video

# Reads config
with open('/boot/clasovideoconfig.txt', 'r') as f:
    f.readline()
    for line in f:
	if 'video_source' in line:	# Checks if files are on usb stick or in local directory
		usb_value = line.split("=")[1].strip()
f.close()

# gets source directory by default 0 on config.txt
if usb_value is '0':
	src_dir = '/home/pi/'
else:
	src_dir = '/media/USB/'

# gets the files to play from source directory
button_list = glob.glob(src_dir + 'Videos/button/*.h264')
video_list = glob.glob((src_dir + 'Videos/*[.mp4,.avi,.mkv,.mp3,.mov,.mpg,.flv,.m4v]'))

# deletes the log file
call(['rm -f ' + src_dir + 'Videos/LOG'], shell=True)

# Init variables
button_count = -1	# Number of video in folder Videos/button
video_count=-1		# Number of video in folder Videos

# Procedure that is called when a button is pressed
def button_pressed(button):
	global button_count	# Current video in folder button
	global playProcess	# Process that plays the main video
	if button == 1:
		# Loops through all videos in button directory
		button_count += 1
		if (button_count > len(button_list)-1):
			button_count = 0
		# Selects the video file and the sound file
		video = button_list[button_count].split('.')[0] + ".h264"

	# Plays the short video while interrupting the main
        print "playing " + video

	time.sleep(.5)
	# Sends a pause signal to the main video
	playProcess.stdin.write('p')
	# Plays the selected video
	ps_video=call(['/opt/vc/src/hello_pi/hello_video/hello_video.bin', video])
	# Sends a resume signal to the main video
	playProcess.stdin.write('p')
	# Cleans memory
	ps_video=None

# Plays the main video in a loop
def welcome_loop():
	global playProcess	# Process that plays the main video
	global video_count	# Current video in videos directory
	global countdown	# Seconds that remains until reaching en of main video
	global video_ending	# When True nothing happens when a button is pressed
	# Loops for ever playing the main video
	while True:
		print "Starting welcome_loop"
		time.sleep(.5)
		# Loops through all videos in videos directory
		video_count = video_count + 1
		if (video_count > len(video_list)-1):
			video_count = 0
		countdown = duration(video_list[video_count])	# Initialize the counter to the main video duration
		# Starts the main video
		playProcess=Popen(['/usr/bin/omxplayer', '-r', '--no-osd', '-o', 'local', video_list[video_count]], stdin=PIPE)
		# Enable buttons
		video_ending = False
		# Waits until the main video is finished
		playProcess.wait()
		playProcess = None							# Cleans memory
		call(['killall dbus-daemon'], shell=True)	# Kills orphan process (dont know why)

# Called when button is pressed
def button(channel):
	global button_busy	# if True, pressing a button will do nothing
	global video_ending	# if True, pressing a button will do nothing
        print "interupt 9"
	if (button_busy == False) and (video_ending == False):
		button_busy = True	# Disable buttons
		button_pressed(1)	# Plays current video from button folder
		button_busy = False	# Enable buttons


# Calculates the duration of main video file
def duration(video):
	# Launch omxplayer with --info
	ps  = Popen(['omxplayer', '--info', video], stdin=None, stdout=None, stderr=PIPE)
	# Receives the output in stderr
	ret_info = ps.communicate()[1].split('\n')
	ps = None
	# Extracts the time from the output of omxplayer
	for line in ret_info:
		if ('Duration' in line):
			if ('N/A' in line):
				return 0		# Returns 0 if file is not seekable
			else:
				tot = line.split(',')[0].split(':')
				hour = tot[1].strip()
				min = tot[2].strip()
				sec = tot[3].strip()
				return int((float(hour) * 3600) + (float(min) * 60) + float(sec)) # Returns duration in sec



# Adds the intrrupts
GPIO.add_event_detect(9, GPIO.FALLING, callback=button, bouncetime=300)

#Starts the loopback video in new thread
thread.start_new_thread( welcome_loop, () )

# Main loop
time_before_end = 10			# Seconds before end of main video
while True:

	try:
		# Decrements countdown if no button is pressed
		if (countdown > time_before_end) and (button_busy == False):
			countdown -= 1
		# If time before end is reached
		elif countdown == time_before_end:
			print 'Video is nearly at the end'
			video_ending = True		# Disable buttons
			countdown = 0			# Disables countdown
		# Waits one sec
		time.sleep(1)

	except KeyboardInterrupt:
		GPIO.cleanup()
		sys.exit()
