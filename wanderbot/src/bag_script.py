#! /usr/bin/env python
import subprocess
import time
import os
import signal
import sys


masterbagname="master_laserodom.bag"
name = sys.argv[1] #name of folder to place bags (also prefix of bag names)
max_n = int(sys.argv[2]) #number of bag files (trial runs) to create
min_range = int(sys.argv[3]) #minimum range of the laser to test
max_range = int(sys.argv[4]) #maximum range of the laser to test
odom_script_dir = '/home/brandon/wanderbot_ws/src/wanderbot/src'
bag_dir = '/home/brandon/wanderbot_ws/src/wanderbot/bags/'
trial_dir = '/home/brandon/wanderbot_ws/src/wanderbot/bags/{}'.format(name)
masterpath_dir = '/home/brandon/wanderbot_ws/src/wanderbot/bags/master'
laser_filter_dir = '/home/brandon/wanderbot_ws/src/wanderbot/src'



def terminate_process_and_children(p):
    ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % p.pid, shell=True, stdout=subprocess.PIPE)
    ps_output = ps_command.stdout.read()
    retcode = ps_command.wait()
    assert retcode == 0, "ps command returned %d" % retcode

    for pid_str in ps_output.split("\n")[:-1]:
        os.kill(int(pid_str), signal.SIGINT)
    p.terminate()


def record_bag(name,n,masterpath_dir,bag_dir,trial_dir,laser_range):
    makefolder = subprocess.Popen(['mkdir','-p','{}_{}'.format(name,laser_range)],cwd=bag_dir)
    amcl = subprocess.Popen(['roslaunch','wanderbot','amcl.launch'])
    time.sleep(3)
    record = subprocess.Popen(['rosbag','record','-O','{}_{}_{}.bag'.format(name,laser_range,n),'amcl_pose','ground_truth'],cwd = trial_dir)
    time.sleep(1)
    playmaster = subprocess.Popen(['rosbag','play','-d','3','{}'.format(masterbagname)],cwd=masterpath_dir)
    playmaster.wait()
    os.kill(amcl.pid, signal.SIGINT)
    os.kill(laser_odom.pid,signal.SIGINT)
    terminate_process_and_children(record)


i=0
for laser_range in range(min_range,max_range+1)[::-1]:
    directory = '/home/brandon/wanderbot_ws/src/wanderbot/bags/{}_{}'.format(name,laser_range)
    laser_filter = subprocess.Popen(['python','laser_filter.py','-max','{}'.format(laser_range)],cwd=laser_filter_dir)
    time.sleep(1)
    laser_odom = subprocess.Popen(['roslaunch','wanderbot','tortoisebot_odom.launch'])#comment out if you don't want laser odometry
    time.sleep(1)
    for i in range(max_n):
        record_bag(name,i,masterpath_dir,bag_dir,directory,laser_range)
        time.sleep(.2)
        odom_script = subprocess.Popen(['rosrun','wanderbot','odom_compare.py','{}_{}'.format(name,laser_range),'{}'.format(i)],cwd = odom_script_dir)
    laser_filter.kill()
    laser_odom.kill()
