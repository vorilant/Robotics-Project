#!/usr/bin/env python

import rospy
from tf2_msgs.msg import TFMessage
from geometry_msgs.msg import TwistStamped
from geometry_msgs.msg import Twist
#from jsk_recognition_msgs.msg import BoundingBoxArray
import message_filters
import subprocess
import sys


sleep_time = int(sys.argv[1])


def cb_2(msg):
    global first_stamp
    global now

    if now == None:
        tfmessage = rospy.wait_for_message("tf", TFMessage)
        now = tfmessage.transforms[0].header.stamp

    if first_stamp is None:
        first_stamp = msg.header.stamp
    msg.header.stamp -= first_stamp
    msg.header.stamp += now
    # for i, box in enumerate(msg.boxes):
    #     box.header.stamp -= first_stamp
    #     box.header.stamp += now
    pub_2.publish(msg)


rospy.init_node('restamp_cmd_vel')

first_stamp = None
now = None

rospy.sleep(sleep_time)

#now = rospy.Time.now()




pub_2 = rospy.Publisher('cmd_vel',TwistStamped, queue_size=5)

sub_2 = rospy.Subscriber('cmd_vel_new', TwistStamped, cb_2)



rospy.spin()
