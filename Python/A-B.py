import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
import numpy as np
from uncertainties import ufloat

path = '/Users/Lab II/Desktop/Data_THz_Spectroscopy/20220603/'
filenames = ['13_41_03positionvalue.txt', '13_43_13positionvalue.txt', '13_49_25positionvalue.txt']

lamb=800e-9
n_0=2.85
r=4.04e-12
L=1e-3/np.sin(np.pi/180 * 40) # detector thickness 

for i in range(len(filenames)):
    A = np.genfromtxt(path + filenames[0], delimiter='\t',skip_header=1)
    B = np.genfromtxt(path + filenames[1], delimiter='\t',skip_header=1)
    A_B = np.genfromtxt(path + filenames[2], delimiter='\t',skip_header=1)
    
    A = A[:,0]
    B = B[:,0]
    A_B = A_B[:,0]
    
    A_mean = ufloat(np.mean(A), np.std(A))
    B_mean = ufloat(np.mean(B), np.std(B))
    A_B_mean  = ufloat(np.mean(A_B), np.std(A_B))
    
    E=(A_B_mean)/(A_mean+B_mean)*lamb/(2*np.pi*L*n_0**3*r) #Used A and B out ouf signal and A-B inside signal
    print('A_mean: ',A_mean,'B_mean: ',B_mean, 'A_mean-B_mean', A_mean-B_mean,'measured A-B mean: ', A_B_mean)
    print('A-B/A+B in percent: ',(A_mean-B_mean)/(A_mean+B_mean))
    print('A-B/A+B in percent, with measured A-B: ', (A_B_mean)/(A_mean+B_mean))
    print('Electric Field in kV: ', abs(E/100/1000), '\n')



E=(A_mean-B_mean)/(A_mean+B_mean)*lamb/(2*np.pi*L*n_0**3*r)