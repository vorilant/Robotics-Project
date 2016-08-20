#!/usr/bin/env python

import subprocess
import sys
t=sys.argv[1]#time to wait after advertising topics must be equal to sleep_time in restamp_cmd_vel.py
bagname=sys.argv[2]
bag = 'twist_new.bag'
restamp_dir = '/home/brandon/wanderbot_ws/src/wanderbot/src'
playbag = subprocess.Popen(['rosbag','play','-d',t,'{}'.format(bagname)])
restamp = subprocess.Popen(['python','restamp_cmd_vel.py',t],cwd=restamp_dir)
