#! /usr/bin/env python

import rospy
import numpy as np
from sensor_msgs.msg import LaserScan
import argparse

rospy.init_node('laser_filter')


parser = argparse.ArgumentParser(description="Subscribes to the ROS topic /scan and modifies LaserScan message data to the desired parameters and publishes on /scan_filtered")
parser.add_argument("-max", "--maxrange",default = 10., help = "set the maximum detection range", type=float)
parser.add_argument("-min", "--minrange",default = .15, help = "set the minimum detection range", type=float)
parser.add_argument("-l", "--leftangle",default = 180. ,help = "set the left angle cut off; 0 is forward bearing; use positive number", type = float)
parser.add_argument("-r","--rightangle",default = 180., help = "set the right angle cut off; 0 is forward bearing; use positive number", type = float)
parser.add_argument("-res","--resolution",default = 720.,help = "points per full 360 degree revolution", choices = [360.,720.],type = float)
parser.add_argument("-n","--stdv",default = 0.02, help="sets the standard deviation of gaussian noise to apply, 0 means no noise",type = float)
args = parser.parse_args()

# setting some parameters based off the desired simulated laser
# max settings refer to the actual hardware,
# or GPU ray trace settings desribed in the URDF if using Gazebo simulator
#note: 0 degrees is forward bearing
new_max_range = args.maxrange
new_min_range = args.minrange
left_angle_cutoff = args.leftangle
right_angle_cutoff = args.rightangle
left_angle_max = 180.
right_angle_max = 180.
max_resolution = args.resolution
max_fov = left_angle_max + right_angle_max
max_increment = max_fov/max_resolution
stdv_noise = args.stdv
mean = 0

if args.stdv == 0:
    noise = False
else:
    noise = True

left_indice_cutoff = int(max_resolution/2 + left_angle_cutoff/max_increment)
right_indice_cutoff = int(max_resolution/2 - right_angle_cutoff/max_increment)

left_indice_mask = np.arange(left_indice_cutoff,int(max_resolution))
right_indice_mask = np.arange(0,right_indice_cutoff)



new = LaserScan()

#TODO queue_size is pretty arbitrarily picked from something I saw on the internet
scan_pub  =   rospy.Publisher('scan_filtered',LaserScan,queue_size=1)

def scan_callback(old):
    #setting new LaserScan message equal to the old /scan topic that comes
    #from gazebo GPU ray tracing (for simulation)
    new.angle_min = old.angle_min
    new.angle_max = old.angle_max
    new.angle_increment = old.angle_increment
    new.time_increment = old.time_increment
    new.scan_time = old.scan_time
    new.range_min = new_min_range
    new.range_max = new_max_range
    new.ranges = old.ranges
    new.intensities = old.intensities

    #convert new.ranges to a numpy array to support indice broadcasting
    numpy_ranges = np.array(new.ranges)

    #apply guassian noise if noise = True
    if noise:
        noise_array = np.random.normal(mean,stdv_noise,max_resolution)
        numpy_ranges+=noise_array


    #stripping out data based on new desired fov
    numpy_ranges[left_indice_mask] = float('nan')
    numpy_ranges[right_indice_mask] = float('nan')
    #numpy_ranges[numpy_ranges>new_max_range] = float('nan') # Unnecessary

    # testing (produces a backward cone with 180 degree fov)
    #spoilers: it runs into walls
    #numpy_ranges[np.arange(180,540)] = float('nan')

    #pushing value of stripped numpy_array back into new.ranges
    new.ranges = numpy_ranges

    #publishing on the new /scan_filtered topic after setting the header to the old /scan header
    new.header.seq = old.header.seq
    new.header.stamp = old.header.stamp
    new.header.frame_id = old.header.frame_id
    scan_pub.publish(new)

#subscribing to the /scan topic published by Gazebo
scan_sub  =   rospy.Subscriber('scan', LaserScan,scan_callback)

rospy.spin()
