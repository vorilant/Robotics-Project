#! /usr/bin/env python

import rospy
import time
from geometry_msgs.msg import Twist

cmd_vel_pub = rospy.Publisher('cmd_vel',Twist,queue_size=1)
rospy.init_node('red_light_green_light')

red_light_twist = Twist()
green_light_twist = Twist()
green_light_twist.linear.x = 0.5

driving_forward = False
light_change_time  = rospy.Time.now()
rate = rospy.Rate(1)
time_mark = time.time()

while not rospy.is_shutdown():
    while driving_forward==True:
        cmd_vel_pub.publish(green_light_twist)
        #rate.sleep()
        #print('forward')
        if (time.time() - time_mark)>=3.0:
            time_mark=time.time()
            driving_forward=False
    while driving_forward == False :
        cmd_vel_pub.publish(red_light_twist)
        #rate.sleep()
        #print('stopped')
        if (time.time() - time_mark)>=3.0:
            time_mark = time.time()
            driving_forward=True
