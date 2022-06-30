import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)
from Driver.controller_esp301 import *
from Driver.Program_LockIn import *
import time
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import re
from tqdm import tqdm

#%% Open Devices
SR830= SR830()
Stage = ESP301()
#%% Initialize

Stage.initialize()
Stage.wait_till_done()
#Stage.write('1VA10')
# Velocity of the stage: 1VAX with X mm/sec
time_con=8
SR830.setIT(i=time_con)
#Integration times are as follows:
#"10us:"0","30us":"1","100us":"2",
#"300us:"3","1ms":"4","3ms":"5",
#10ms:"6","30ms":"7","100ms":"8",
#"300ms:"9","1s":"10","3s":"11",
#10s:"12","30s":"13","100s":"14",
#300s:"15","1ks":"16","3ks":"17",
#10ks:"18","30ks":"19"}
sens=21
SR830.setSens(i=sens)
#Sensitivities are as follows:
#"2nV":"0","5nV":"1","10nV":"2","20nV":"3","50nV":"4","100nV":"5","200nV":"6","500nV":"7","1uV":"8",
#"2uV":"9","5uV":"10","10uV":"11","20uV":"12","50uV":"13","100uV":"14","200uV":"15","500uV":"16","1mV":"17",
#"2mV":"18","5mV":"19","10mV":"20","20mV":"21","50mV":"22","100mV":"23","200mV":"24","500mV":"25","1V":"26"}
dB=2
SR830.setdB(i=dB)
#low pass filter slope. The
#parameter i selects 6 dB/oct (i=0), 12 dB/oct (i=1), 18 dB/oct (i=2) or
#24 dB/oct (i=3)

#%% Live plotting function

plt.style.use('ggplot')

def live_plotter(x_vec,y1_data,line1,start,stop,identifier='',pause_time=0.001,Y_label='X (V)',X_label='stage position (mm)'):
    if line1==[]:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13,6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec,y1_data,'-',alpha=0.8)        
        #update plot label/title
        plt.xlabel(X_label)
        plt.ylabel(Y_label)
        #plt.title('Title: {}'.format(identifier))
        plt.show()
    
    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    # adjust limits if new data goes beyond bounds
    #if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
    #    plt.ylim([np.min(y1_data)-np.std(y1_data),np.max(y1_data)+np.std(y1_data)])
    plt.xlim(start-0.5*np.std(x_vec),stop+0.5*np.std(x_vec))

    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    
    # return line so we can update it again in the next iteration
    return line1

#%% File name management

#Daytime for File name management. The Program will automatically create a folder for the current day if not present. The file will get a name according to
# the time it was taken
now = datetime.now()
current_day=now.strftime("%Y:%m:%d")
current_time = now.strftime("%H:%M:%S")
#time=[int(s) for s in current_time.split() if s.isdigit()]
Current_time=re.findall(r'\d+', current_time)
#day=[int(s) for s in current_day.split() if s.isdigit()]
day=re.findall(r'\d+', current_day)
#initial_dir='Desktop\test'

path = '/Users/Lab II/Desktop/Data_THz_Spectroscopy/'+str(day[0])+str(day[1])+str(day[2])
initial_dir=path+'/'+str(Current_time[0])+'_'+str(Current_time[1])+'_'+str(Current_time[2])
isExist = os.path.exists(path)
if not isExist:
    os.makedirs(path)
    
#Data Acquisition
plt.close('all')
start=7.85 # 6.0
stop=11.85 # 15.0
step=0.004 #step in millimeter
time_constant=[10e-6,30e-6,100e-6,300e-6,1e-3,3e-3,10e-3,30e-3,100e-3,300e-3,1,3,10,30,100,300,1000,3000,10000,30000]
dB_values = [6, 12, 18, 24]
dB_waiting_time = [5,7,9,10] #multiplier of the waiting time for diffrent dB values
waiting_time = float(dB_waiting_time[dB]*time_constant[time_con]) #automatically change the waiting time accordlingly to the dB value that is used for the measurment
sensitivity=["2nV","5nV","10nV","20nV","50nV","100nV","200nV","500nV","1uV","2uV","5uV","10uV","20uV","50uV","100uV","200uV","500uV","1mV",
             "2mV","5mV","10mV","20mV","50mV","100mV","200mV","500mV","1V"]
set_sens=sensitivity[sens]
stepcount=int((stop-start)/step)
x=np.array(np.linspace(start,stop,stepcount+1))
X=[]
Y=[]
R=[]
theta=[]
out=[]
line1=[]
Comment='Without Preamplifier,Fluence with Filter (NE07A-B), ZnTe detector angle 40deg, Chopper 230Hz, time constant='+str(time_constant[time_con])+'s '+str(dB_values[dB])+'dB, waiting time= '+str(np.round(waiting_time, 4))+'s, sensitivity='+set_sens # Comment for meta data
pos=0
plot_y=np.empty(len(x))  # Plot_y is the array which will be live plotted. It is given by (out[pos])[i] and i determines the measured parameter
plot_y[:]=np.NaN
start_time = time.time()
for i in tqdm(x):
    if pos==0:
        f=open(initial_dir+'.txt','w')
        f.write('Time (s) \t Position (mm) \t Delay (s) \t X \t Y \t R \t theta \n')
        f.write('#'+str(Comment))
    #print(i)
    
    Stage.set_pos_abs(i)
    Stage.wait_till_done()
    x[pos]=float(Stage.read_after_write('1TP?'))
    delay=6.6713e-12*x[pos]
    time.sleep(waiting_time)
    Measurement=SR830.get_All_Outputs()
    out.append(Measurement)   #all the lock in outputs will be connected in an array [X,Y,R,theta]
    end_time = time.time()
    abs_time = end_time - start_time
    plot_y[pos]=(out[pos])[0]
    #line1=live_plotter(x,np.array(X),line1)
    line1=live_plotter(x,plot_y,line1,start=start,stop=stop)
    plt.ylim(np.min(plot_y[0:pos+1])-np.std(plot_y[0:pos+1]),np.max(plot_y[0:pos+1])+np.std(plot_y[0:pos+1]))
     
    f.write('\n'+str(np.round(abs_time, 4))+'\t'+str(x[pos])+'\t'+str(delay)+'\t'+str(Measurement[0])+'\t'+str(Measurement[1])+'\t'+str(Measurement[2])+'\t'+str(Measurement[3]))
    pos+=1
f.close() # Be careful: If f.close() not excecuted, the measurent data is not updated and the information from the last measurement will be saved in the txt file!!!
#%% Measure value at one stage position
now = datetime.now()
current_day=now.strftime("%Y:%m:%d")
current_time = now.strftime("%H:%M:%S")
#time=[int(s) for s in current_time.split() if s.isdigit()]
Current_time=re.findall(r'\d+', current_time)
#day=[int(s) for s in current_day.split() if s.isdigit()]
day=re.findall(r'\d+', current_day)
#initial_dir='Desktop\test'
path = '/Users/Lab II/Desktop/Data_THz_Spectroscopy/'+str(day[0])+str(day[1])+str(day[2])
initial_dir=path+'/'+str(Current_time[0])+'_'+str(Current_time[1])+'_'+str(Current_time[2])
plt.close('all')
position = 3  #set position of test measurment 
length = 1000
time_constant=[10e-6,30e-6,100e-6,300e-6,1e-3,3e-3,10e-3,30e-3,100e-3,300e-3,1,3,10,30,100,300,1000,3000,10000,30000]
dB_values = [6, 12, 18, 24]
dB_waiting_time = [5,7,9,10] #multiplier of the waiting time for diffrent dB values
sensitivity=["2nV","5nV","10nV","20nV","50nV","100nV","200nV","500nV","1uV","2uV","5uV","10uV","20uV","50uV","100uV","200uV","500uV","1mV",
             "2mV","5mV","10mV","20mV","50mV","100mV","200mV","500mV","1V"]
set_sens=sensitivity[sens]
out=[]
line1=[]
waiting_time = 1  #time between single measurments
x=np.ones(length)*position
x_axis = np.linspace(1, 1000, length)
plot_y=np.empty(len(x))  # Plot_y is the array which will be live plotted. It is given by (out[pos])[i] and i determines the measured parameter
plot_y[:]=np.NaN
pos = 0
Comment='With Preamplifier,Turning the emitter ZnTe, ZnTe detector angle dependance 40deg, Chopper inside probe 388Hz inside Pump 230Hz, time constant='+str(time_constant[time_con])+'s '+str(dB_values[dB])+'dB, waiting time= '+str(np.round(waiting_time, 4))+'s, sensitivity='+set_sens+', position '+str(position)+'mm' # Comment for meta data

Stage.set_pos_abs(position)
Stage.wait_till_done()
for i in tqdm(x):
    if pos==0:
        f=open(initial_dir+'positionvalue'+'.txt','w')
        f.write('X \t Y \t R \t theta \n')
        f.write('#'+str(Comment))
    time.sleep(waiting_time)
    Measurement=SR830.get_All_Outputs()
    out.append(Measurement)   #all the lock in outputs will be connected in an array [X,Y,R,theta]
    plot_y[pos]=(out[pos])[0]
    #line1=live_plotter(x,np.array(X),line1)
    line1=live_plotter(x_axis,plot_y,line1,start=x_axis[0],stop=x_axis[-1], X_label='Measurment')
    plt.ylim(np.min(plot_y[0:pos+1])-np.std(plot_y[0:pos+1]),np.max(plot_y[0:pos+1])+np.std(plot_y[0:pos+1]))
    f.write('\n'+str(Measurement[0])+'\t'+str(Measurement[1])+'\t'+str(Measurement[2])+'\t'+str(Measurement[3]))
    pos+=1
f.close()
#%% Close Devices
SR830.close()
Stage.close()

