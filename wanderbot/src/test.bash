#!/bin/bash
source /opt/ros/indigo/setup.bash
source ~/wanderbot_ws/devel/setup.bash
i="1"
n="11"
while [ $i -lt $n ];do
	echo $1_$i
	i=$[$i+1]
	done

ls
roscd wanderbot/bags
echo test>>test.txt
ls
