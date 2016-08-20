#! /usr/bin/env python
from __future__ import print_function
import shapely.geometry
import rospy
import rosbag
import sys
from nav_msgs.msg import Odometry
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.interpolate import interp1d
import sys


plots = True
sys.setrecursionlimit(20000) # needed for deep recursions through ground_truth data
s = str(sys.argv[1])
n = str(sys.argv[2])
filepath = "/home/brandon/wanderbot_ws/src/wanderbot/bags/{}".format(s)
bagpath = "/home/brandon/wanderbot_ws/src/wanderbot/bags/{}/{}_{}.bag".format(s,s,n)
textpath = "/home/brandon/wanderbot_ws/src/wanderbot/bags/{}/{}_pre60.txt".format(s,s)
bag = rosbag.Bag(bagpath)
ground_truth_x =[]
ground_truth_y =[]
ground_truth_ROStime = []
amcl_pose_x=[]
amcl_pose_y=[]
amcl_pose_ROStime =[]

#################################################################################
### Reading From the Bag and getting {t,(x,y)} from both amcl and truth poses ###
#################################################################################
for topic, msg,t in bag.read_messages(topics=['ground_truth']):
    ground_truth_x.append(msg.pose.pose.position.x)
    ground_truth_y.append(msg.pose.pose.position.y)
    ground_truth_ROStime.append(t)

for topic, msg,t in bag.read_messages(topics=['amcl_pose']):
    amcl_pose_x.append(msg.pose.pose.position.x)
    amcl_pose_y.append(msg.pose.pose.position.y)
    amcl_pose_ROStime.append(t)
#############################################################################
#############################################################################


#############################################################################
######## Getting the time and pose arrays into useful (numpy) format ########
#############################################################################
ground_truth_time = []
amcl_pose_time = []
for i in range(len(ground_truth_ROStime)):
    ground_truth_time.append(ground_truth_ROStime[i].to_sec())
for i in range(len(amcl_pose_ROStime)):
    amcl_pose_time.append(amcl_pose_ROStime[i].to_sec())
bag.close() #close the bag files
##############################################################################
##############################################################################



###################################################
### Convert everything into useful numpy arrays ###
###################################################
gttime_presnip = np.array(ground_truth_time)
amcltime = np.array(amcl_pose_time)
gttime = gttime_presnip
#gttime = [s for s in gttime_presnip if (s<amcltime[-1]) and s>amcltime[0]] #Makes gttime start and end where amcltime starts and ends
#gttime -= gttime[0]# Zeroing the initial time so that t0 = 0
#amcltime -= amcltime[0]#zeroing time here too

gtx = np.array(ground_truth_x)
gty = np.array(ground_truth_y)
amclx = np.array(amcl_pose_x)
amcly = np.array(amcl_pose_y)
#####################################################
#####################################################


################################################
###      Out put raw data to text files      ###
################################################
# file_gt='/home/brandon/ground_truth.txt'
# file_guess='/home/brandon/position_guess.txt'
# with open(file_gt,'a+') as f1:
#     print('x y t',file=f1)
#     for i in range(len(gttime)):
#         print('{} {} {}'.format(gtx[i],gty[i],gttime[i]),file=f1)
# with open(file_guess,'a+') as f2:
#     print('x y t',file=f2)
#     for i in range(len(amcltime)):
#         print('{} {} {}'.format(amclx[i],amcly[i],amcltime[i]),file=f2)
###################################################
###################################################

#######################################################################################
#Returns index that points to the element in 'array' that most closely matches 'value'#
#######################################################################################
def find_indice(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx
#######################################################################################
timestop = find_indice(amcltime,60)

index_array=np.zeros(len(amcltime)).astype(int)
for i in range(len(amcltime)):
    index_array[i] = find_indice(gttime,amcltime[i])

gttime = gttime[index_array]
gtx = gtx[index_array]
gty = gty[index_array]


#TODO GET RID OF t_at_55 it's only for one use GET RID OF IT
t = 5 #ignore the first t seconds of the recording due to inescapable large errors from relaunching AMCL and rosbag play with -i option
ignored = find_indice(amcltime,amcltime[0]+t)
gtx = gtx[:timestop]
gty = gty[:timestop]
amclx = amclx[:timestop]
amcly = amcly[:timestop]
amcltime = amcltime[:timestop]
gttime = gttime[:timestop]

################################################
###    Trying to interpolate with griddata   ###
###                Doesn't Work              ###
################################################
# gtx = griddata(ground_truth_time,ground_truth_x,time,method=method)
# gty = griddata(ground_truth_time,ground_truth_y,time,method=method)
# amclx = griddata(amcl_pose_time,amcl_pose_x,time,method=method)
# amcly = griddata(amcl_pose_time,amcl_pose_y,time,method=method)
# n = abs(np.size(gttime)-np.size(gttime_presnip))
# gtx = gtx_preinterp[:-n]
# gty = gty_preinterp[:-n]
################################################


###################################################################
### Interpolating AMCL poses against the time from Ground Truth ###
###      With Interp1d  :   Doesn't Work                        ###
###################################################################
# method = 'linear'
# amclx_fn = interp1d(amcltime,amclx_preinterp,kind=method)
# amcly_fn = interp1d(amcltime,amcly_preinterp,kind=method)
# amclx = amclx_fn(gttime)
# amcly = amcly_fn(gttime)
# gtx_fn = interp1d(ground_truth_time,gtx,kind=method)
# gty_fn = interp1d(ground_truth_time,gty,kind=method)
# gtx = gtx_fn(amcltime)
# gty = gtx_fn(amcltime)
##################################################################



######################################
###    Calculating L2 Metrics      ###
######################################
error_x=gtx-amclx
error_y=gty-amcly
error_mag = np.sqrt((gtx-amclx)**2+(gty-amcly)**2)
error_mag-=error_mag[0] #zero the error at the beginning
L2_vector = abs(error_mag)
L2_squared_vector = error_mag**2
L2_avg = np.trapz(L2_vector,amcltime)/(amcltime[-1]-amcltime[0])
L2_squared_avg = np.trapz(L2_squared_vector,amcltime)/(amcltime[-1]-amcltime[0])

print('The average of L2 norms : ',L2_avg)
print('The average of L2 squared norms : ',L2_squared_avg)
#########################################
#########################################



################################################
### Finding the Area between the two curves  ###
################################################
polygon_vertices = []
ground_truth_y_reversed = ground_truth_y[::-1]
ground_truth_x_reversed = ground_truth_x[::-1]
for i in range(len(amcl_pose_x)):
    polygon_vertices.append((amcl_pose_x[i],amcl_pose_y[i]))
for i in range(len(ground_truth_y_reversed)):
    polygon_vertices.append((ground_truth_x_reversed[i],ground_truth_y_reversed[i]))
polygon = shapely.geometry.Polygon(polygon_vertices)
area=polygon.area
print('The area between the curves is : ',area)

################################################
################################################


##############################
#### Frechet Distance Code ###
####   Credit MaxBarelss   ###
##############################

# Euclidean distance.
def euc_dist(pt1,pt2):
    return np.sqrt((pt2[0]-pt1[0])*(pt2[0]-pt1[0])+(pt2[1]-pt1[1])*(pt2[1]-pt1[1]))
#Frechet Distance
def _c(ca,i,j,P,Q):
    if ca[i,j] > -1:
        return ca[i,j]
    elif i == 0 and j == 0:
        ca[i,j] = euc_dist(P[0],Q[0])
    elif i > 0 and j == 0:
        ca[i,j] = max(_c(ca,i-1,0,P,Q),euc_dist(P[i],Q[0]))
    elif i == 0 and j > 0:
        ca[i,j] = max(_c(ca,0,j-1,P,Q),euc_dist(P[0],Q[j]))
    elif i > 0 and j > 0:
        ca[i,j] = max(min(_c(ca,i-1,j,P,Q),_c(ca,i-1,j-1,P,Q),_c(ca,i,j-1,P,Q)),euc_dist(P[i],Q[j]))
    else:
        ca[i,j] = float("inf")
    return ca[i,j]
#Algorithm: http://www.kr.tuwien.ac.at/staff/eiter/et-archive/cdtr9464.pdf
###########################
###########################

n=4 #skip every n points to make the Frechet Dist calculation faster
amclx_skipping = amclx[::4]
amcly_skipping = amcly[::4]
gtx_skipping = gtx[::4]
gty_skipping = gty[::4]

def frechetDist(P,Q):
    ca = np.ones((len(P),len(Q)))
    ca = np.multiply(ca,-1)
    return _c(ca,len(P)-1,len(Q)-1,P,Q)

#Setting up 2-tuple arrays P and Q to be in the expected form
#For the function _c()
P = []
for i in range(len(amclx_skipping)):
    P.append((amclx_skipping[i],amcly_skipping[i]))
Q = []
for i in range(len(gtx_skipping)):
    Q.append((gtx_skipping[i],gty_skipping[i]))
P = np.array(P)
Q = np.array(Q)

FD = 'not calculated'
FD = frechetDist(P,Q)
print('Frechet Distance is : ', FD)




######################
# Writing Data File ##
######################
with open(textpath,'a') as text_file:
    text_file.write('{}_{}\n'.format(s,n))
    text_file.write('L2,{0}\nL2S,{1}\nAR,{2}\nFD,{3}\n'.format(L2_avg,L2_squared_avg,area,FD))
######################
######################



#############################
### Commence the Plotting ###
#############################

if plots:
    # fig_time_plots = plt.figure(1)
    # plt.subplot(221)
    # plt.plot(amcl_pose_time,amcl_pose_x)
    # plt.xlabel('Time(s)')
    # plt.ylabel('Position(m)')
    # plt.title('AMCL x-position')
    # plt.subplot(222)
    # plt.plot(amcl_pose_time,amcl_pose_y)
    # plt.xlabel('Time(s)')
    # plt.ylabel('Position(m)')
    # plt.title('AMCL y-position')
    # plt.subplot(223)
    # plt.plot(ground_truth_time,ground_truth_x)
    # plt.xlabel('Time(s)')
    # plt.ylabel('Position(m)')
    # plt.title('Ground Truth x-position')
    # plt.subplot(224)
    # plt.plot(ground_truth_time,ground_truth_y)
    # plt.xlabel('Time(s)')
    # plt.ylabel('Position(m)')
    # plt.title('Ground Truth y-position')

    fig_paths = plt.figure(2)
    plt.subplot(131)
    plt.plot(amclx,amcly, label = 'AMCL Path')
    plt.title('AMCL Path')
    plt.xlabel('x-position(m)')
    plt.ylabel('y-position(m)')
    plt.subplot(132)
    plt.plot(gtx,gty, label = 'True Path')
    plt.title('Ground Truth Path')
    plt.xlabel('x-position(m)')
    plt.ylabel('y-position(m)')
    plt.subplot(133)
    plt.plot(gtx[ignored:],gty[ignored:],'b', label = 'True Path')
    plt.plot(amclx[ignored:],amcly[ignored:],'r', label = 'AMCL Path')
    plt.title('Both on same graph')
    plt.xlabel('x-position(m)')
    plt.ylabel('y-position(m)')
    plt.legend()


    # fig_ground_truth = plt.figure(7)
    # plt.plot(ground_truth_x,ground_truth_y, label = 'True Path')
    # plt.title('Ground Truth Path')
    # plt.xlabel('x-position(m)')
    # plt.ylabel('y-position(m)')

    value = str(L2_avg)
    fig_l2 = plt.figure(3)
    plt.subplot(111)
    plt.fill_between(amcltime,L2_vector)
    plt.xlabel('Time(s)')
    plt.ylabel(r'$\Delta$ poses since bag record start time')
    plt.title('L2 norm integral: '+value)

    value = str(L2_squared_avg)
    fig_l2_squared = plt.figure(6)
    plt.subplot(111)
    plt.fill_between(amcltime,L2_squared_vector)
    plt.xlabel('Time(s)')
    plt.ylabel(r'$\Delta$ poses squared since bag record start time')
    plt.title('L2 squared norm integral: '+value)


    # fig_vector_error = plt.figure(4)
    # plt.subplot(121)
    # plt.plot(time,dx)
    # plt.title('discrepancy_x')
    # plt.xlabel('Time(s)')
    # plt.ylabel('Discrepancy Between X direction AMCL and Truth (m)')
    # plt.subplot(122)
    # plt.plot(time,dy)
    # plt.title('discrepancy_y')
    # plt.xlabel('Time(s)')
    # plt.ylabel('Discrepancy Between Y direction AMCL and Truth (m)')

    plt.show()
##################
##################



#fig_ground_truth.savefig('{}_{}.png'.format(s,n)) # if you just want to show ground truth plots (For UT Austin Stuff)
