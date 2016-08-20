#! /usr/bin/env python

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist

key_mapping={'w':[ 0, 1] , 's':[ 0,-1],
             'a':[-1, 0] , 'd':[ 1, 0],
             'q':[ 0, 0] }

def keys_cb(msg, twist_pub):
    if len(msg.data) == 0 or not key_mapping.has_key(msg.data[0]):
        return #unkown key
    vels = key_mapping[msg.data[0]]
    twist = Twist()
    twist.angular.z = vels[0]
    twist.linear.x = vels[1]
    twist_pub.publish(twist)

if __name__ == '__main__':
    rospy.init_node('keys_to_twist')
    twist_pub = rospy.Publisher('cmd_vel',Twist,queue_size=1)
    rospy.Subscriber('keys',String,keys_cb,twist_pub)
    rospy.spin()
