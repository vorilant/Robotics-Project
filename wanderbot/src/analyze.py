#! /usr/bin/env python
from __future__ import print_function
import numpy as np
import sys
import matplotlib.pyplot as plt


name = sys.argv[1] # which data set to perform analysis on
#n = sys.argv[2] # which range to analyze
bagpath='/home/brandon/wanderbot_ws/src/wanderbot/bags'
graph_path = '/home/brandon/wanderbot_ws/src/wanderbot/graphs/Range'





write=True
def write_stats(n,write=True):
    maximum=[];minimum=[];rms=[];stdv=[];mean=[]
    metrics = ['Sum of L2 norms','Sum of squared L2 norms','Area between Curves','Frechet Distance']
    #importing raw data as strings and turning it into useful numpy array syntax as floats
    datapath = bagpath+'/{0}_{1}/{0}_{1}.txt'.format(name,n)
    raw_data = np.loadtxt(datapath,dtype = 'string')
    L2_data = np.array(raw_data[1::5])
    L2_squared = np.array(raw_data[2::5])
    area = np.array(raw_data[3::5])
    FD = np.array(raw_data[4::5])

    L2_data = [s[3:] for s in L2_data]
    L2_squared = [s[4:] for s in L2_squared]
    area = [s[3:] for s in area]
    FD = [s[3:] for s in FD]

    L2_data = np.array(L2_data).astype(np.float)
    L2_squared = np.array(L2_squared).astype(np.float)
    area = np.array(area).astype(np.float)
    FD = np.array(FD).astype(np.float)
    vec_data = [L2_data,L2_squared,area,FD]

    with open(bagpath+'/{}_{}/'.format(name,n)+'max_range_statistics.txt','w') as statsfile:
        for i in range(len(vec_data)):

            maximum.append(vec_data[i].max())
            minimum.append(vec_data[i].min())
            rms.append(np.sqrt(np.mean(np.square(vec_data[i]))))
            stdv.append(vec_data[i].std())
            mean.append(vec_data[i].mean())
            if write:
                output_streams = [sys.stdout,statsfile]
                for stream in output_streams:
                    print('{} :'.format(metrics[i]),\
                        'max={}'.format(maximum[i]),\
                        'min={}'.format(minimum[i]),\
                        'rms={}'.format(rms[i]),\
                        'stdv={}'.format(stdv[i]),\
                        'mean={}\n'.format(mean[i]),\
                        sep='\n',end='\n',file=stream)
for i in range(1,11):
    write_stats(i)
