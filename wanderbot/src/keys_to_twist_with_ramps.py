#! /usr/bin/env python

import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import math

key_mapping={'w':[ 0, 1] , 's':[ 0,-1],
             'a':[-1, 0] , 'd':[ 1, 0],
             'q':[ 0, 0] }
g_last_twist = None
g_target_twist = None
g_last_send_time = None
g_vel_scales = [.3,.3] #default is very slow
g_acc_ramps = [1,1] #units: meters per second^2

def ramped_vel(v_prev,v_target, t_prev, t_now, ramp_rate):
    # compute max velocity step
    step = ramp_rate * (t_now - t_prev).to_sec()
    sign = 1.0 if (v_target>v_prev) else -1.0
    error = math.fabs(v_target-v_prev)
    if error<step:
        return v_target # reaching target velocity this step
    else:
        return v_prev + sign*step # step forward toward target velocity

def ramped_twist(prev,target,t_prev,t_now,ramps):
    tw = Twist()
    tw.angular.z = ramped_vel(prev.angular.z,target.angular.z,t_prev,t_now,ramps[0])
    tw.linear.x = ramped_vel(prev.linear.x,target.linear.x,t_prev,t_now,ramps[1])
    return tw

def send_twist():
    global g_last_twist_send_time,g_target_twist,g_last_twist,g_vel_scales,g_acc_ramps,g_twist_pub
    t_now = rospy.Time.now()
    g_last_twist = ramped_twist(g_last_twist, g_target_twist,\
                                g_last_twist_send_time,t_now,g_acc_ramps)
    g_last_twist_send_time = t_now
    g_twist_pub.publish(g_last_twist)


def send_stop():
    stop = Twist() #stop is zero vector
    g_twist_pub.publish(stop)


def keys_cb(msg):
    global g_target_twist, g_last_twist, g_vel_scales
    if len(msg.data) == 0 or not key_mapping.has_key(msg.data[0]):
        return
    vels = key_mapping[msg.data[0]]
    g_target_twist.angular.z=vels[0]*g_vel_scales[0]
    g_target_twist.linear.x= vels[1]*g_vel_scales[1]

def fetch_param(name,default):
    if rospy.has_param(name):
        return rospy.get_param(name)
    else:
        print "parameter [%s] not defined. Daulting to %.3f"%(name,default)
        return default


if __name__ == '__main__':
    rospy.init_node('keys_to_twist')
    g_last_twist_send_time = rospy.Time.now()
    g_twist_pub = rospy.Publisher('cmd_vel',Twist,queue_size=1)
    rospy.Subscriber('keys',String,keys_cb)
    g_target_twist = Twist()#initilizes to zero
    g_last_twist = Twist()
    g_vel_scales[0] = fetch_param('~angular_scale',-10)
    g_vel_scales[1] = fetch_param('~linear_scale',10)
    g_acc_ramps[0] = fetch_param('~angular_acc',10)
    g_acc_ramps[1] = fetch_param('~linear_acc',10)



    rate = rospy.Rate(60)
    while not rospy.is_shutdown():
        send_twist()
        rate.sleep()
