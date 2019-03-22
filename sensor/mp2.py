import socket
import types
import time
import datetime
import threading
import os
import decode_data
import copy
import numpy as np
import scipy.signal

import matplotlib.pyplot as plt
import Queue
import errno
import multiprocessing
import pywt

###info
# this file utilize multi thread to solve the delay of visualition.

#ServerIP and port config.
PORT = 5000    #udp protocol port
ServerIp = '192.168.1.193'

# file saved path.
FILEPATH = './'  #data saved path

#plot config.
PLOT_NUM =160  # x-axis totally number is 600*PLOT_NUM
PLOT_COUNT = 30 # figure is updated every 0.06*PLOT_COUNT s

# sensor config
sensor_ip_list =[]

sensor_ip_list.append('192.168.1.153')
sensor_ip_list.append('192.168.1.112')

data_time =30 #receiv data time limit, the unit is seconds, 0 means receive data all the time.

GAIN = 60

#*************config end*************
manager = multiprocessing.Manager()
queue = []
for ii in range(len(sensor_ip_list)):
    queue.append(manager.Queue(0))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ServerIp, PORT)

server_socket.bind(server_address)

def all_receive_data(sensor_ip_list, time_lim):
    
    time_tag = get_time_tag()
    old_min = time_tag[14:16]
    file_date = time_tag[0:14]
    start_second = int(time.time());

    all_data  = []
    plot_data = [[0*x for x in range(600*PLOT_NUM)] for j in range(len(sensor_ip_list))]
    plot_count = np.zeros(len(sensor_ip_list))
    plot_data_count=np.zeros(len(sensor_ip_list))
    filter_data = [[0*x for x in range(600*PLOT_COUNT)] for j in range(len(sensor_ip_list))]


    for ii in range(len(sensor_ip_list)):
        all_data.append([])  #initial data list
        all_data[ii] = ''

    # initial plot info
    data_location_num = 0
    
#thread = threading.Thread(target=myplot, args=(len(sensor_ip_list),))
#   thread.setDaemon(True)
#   thread.start()
    p = multiprocessing.Process(target = myplot, args=(len(sensor_ip_list),))
    p.start()   

    server_socket.setblocking(0)
    data_flag = False
    while True:
        time_tag = get_time_tag()
        new_min = time_tag[14:16]
 
        #time_limit
        now_second = int(time.time())
        if (time_lim >0) & (now_second - start_second > time_lim):
            sensor_stop(sensor_ip_list)    
            #save file
            filename = file_date + new_min + '.txt'
            writ_data = copy.deepcopy(all_data)
            threading.Thread(target=save_file, args=(sensor_ip_list,filename,writ_data,)).start()
            p.terminate()
            break
       
       
        # save file
        if new_min != old_min:
            filename = file_date + old_min + '.txt'
            old_min = new_min
            file_date = time_tag[0:14]
            writ_data = copy.deepcopy(all_data)
#threading.Thread(target=save_file, args=(sensor_ip_list,filename,writ_data,)).start()
   
            for ii in range(len(sensor_ip_list)):
                all_data[ii] = ''

# receive sensor package
        try:
            receive_data, client_address = server_socket.recvfrom(2048)
            data_flag = True
            time_tag = get_time_tag()
        except IOError as e:
            if e.errno == errno.EWOULDBLOCK:
                data_flag = False
            continue
        
        t1 = time.clock()
        data_ip = str(client_address[0])
        
        if len(receive_data) < 100:
            re_message = decode_data.decode_config_message(receive_data)        
            if re_message in 'Sp':
                print("%s is stoped!"%data_ip)
            continue 
        if data_ip in sensor_ip_list:
            data_location_num = sensor_ip_list.index(data_ip)
        else:
            print ('%s sensor still upload data!'%data_ip)
            continue
        
        de_code_data =  decode_data.decode_data(receive_data)
#        print time_tag 
#        print len(receive_data)
        
        all_data[data_location_num] =all_data[data_location_num] + time_tag + de_code_data +'\n'
        
        use_data = de_code_data.split('(')[2]
        use_data = use_data.replace(')', '')
        char_list = use_data.split(',')
        int_data = [int(x) for x in char_list]
        
        filter_data[data_location_num] = filter_data[data_location_num] +int_data 
        filter_data[data_location_num][0:600] = []
        plot_count[data_location_num] = plot_count[data_location_num] +1
        
        # put data into queue
        if plot_count[data_location_num] >= PLOT_COUNT:
            queue[data_location_num].put(filter_data[data_location_num])
            plot_count[data_location_num] =0
        
     
        t2 = time.clock()
#       print("data process time is %f"%(t2-t1))
        time.sleep(0.01)


def myplot(number):
   
    time_x = np.linspace(0, PLOT_NUM*0.06, 600*PLOT_NUM) 
    plot_data = [[0*x for x in range(600*PLOT_NUM)] for j in range(len(sensor_ip_list))]
    raw_data = [[0*x for x in range(600*PLOT_NUM)] for j in range(len(sensor_ip_list))]
    plt.rcParams['figure.figsize'] =(10,6)

    foot_step = [[0*x for x in range(66)] for j in range(len(sensor_ip_list))]
    print("############################ is %d width is %d"%(len(foot_step),len(foot_step[0]))) 
    name_list =[]
    f = plt.figure(0)
    
    ax =[]
    for ii in range(number +3):
        ax.append(f.add_subplot(3,2,ii+1))
        if ii < number:
            name_list.append('Sensor ' + str(ii +1))
    plt.subplots_adjust(left = None, right=None, top=None, wspace =0.2, hspace =0.6)
    wid = 0.1
    x1 = list(range(number))
    x2 = list(range(number))
    x3 = list(range(number))
    x4 = list(range(number))
    x5 = list(range(number))
    x6 = list(range(number))
    for i in range(number):
        x2[i] = x2[i] + wid
        x3[i] = x3[i] + 2*wid
        x4[i] = x4[i] + 3*wid
        x5[i] = x5[i] + 4*wid
        x6[i] = x6[i] + 5*wid

    print(name_list)

#wavelet
    scale = np.arange(256)+1
    
    vb = []
    vb_wt = []

    count_flg = 0
    while True:
        t1 = time.clock()
#       vb = []
#vb_wt = []
        for ii in range(number):
            if not queue[ii].empty():
                count_flg = count_flg +1
                data = queue[ii].get()
                raw_data[ii] = raw_data[ii] + data
                new_len = len( data )
                raw_data[ii][0:new_len] = []
#raw_data = raw_data - np.mean(raw_data)
                filter_data = raw_data[ii][300*PLOT_NUM :600*PLOT_NUM]
                filter_data = filter_data - np.mean(filter_data)
                filtered_sig = scipy.signal.wiener(filter_data, 501).tolist()
#               filtered_sig = filter_data
                used_data =filtered_sig[(300*(PLOT_NUM -1)- new_len):300*(PLOT_NUM-1)]
                
                plot_data[ii] = plot_data[ii] + used_data
                tmp_peak, _ = scipy.signal.find_peaks(used_data, height= 5000, distance=2000)
                tmp_step = len(tmp_peak)
                if count_flg < 4:
	            tmp_step =0

                foot_step[ii] = foot_step[ii] + [tmp_step]
                del(foot_step[ii][0])
#print(foot_step[ii])
                tmplen= len(used_data)
                plot_data[ii][0:tmplen] = []

                #extract one vibration signal
                if (ii ==1) and (len(tmp_peak) > 0):
                    position = tmp_peak[0]
                    print('/n/n')
                    print("position is %d"%(position))
                    print('/n/n')
                    if (position < 100) or (position + 300 > tmplen):
                        vb =[]
                    else:
                        vb = raw_data[ii][600*PLOT_NUM -new_len - 300 + position -200 :600*PLOT_NUM-new_len -300 + position +600]
                        vb = vb - np.mean(vb)
                        
                        vb_w, ff = pywt.cwt(vb,scale, 'mexh') 
                        select_sc = vb_w[20:30][:]
                        vb_wt = np.sqrt(np.sum((select_sc**2)/10, 0))
                    
                
                t1 = time.clock()
                ax[ii].cla()
                ax[ii].set_ylim([-30000, 30000])
                ax[ii].set_ylabel('Digital amplitude')
                ax[ii].set_xlabel('Time(s)')
                ax[ii].set_title('Sensor ' + str(ii+1))
                ax[ii].plot(time_x, plot_data[ii])
                plt.pause(0.001)
                t2 = time.clock()

#   print("all time is %f"%(t2-t1))
            if ii == (number -1):
                ax[ii +1].cla()
                ax[ii +1].set_ylim([-30000, 30000])
                ax[ii +1].set_title('Vibration Signal')
                ax[ii +1].set_ylabel('Footstep Number')
                ax[ii +1].plot(vb)
                print("vb length is %d"%(len(vb)))
                plt.legend()
                plt.pause(0.001)
            
            if ii == (number -1):
                
                ax[ii +3].cla()
                ax[ii +3].set_title('Wavelet transform')
#ax[ii +3].set_ylabel('Footstep Number')
                ax[ii +3].plot(vb_wt)
                plt.legend()
                plt.pause(0.001)
          
            if ii == (number -1):
                s1 = [row[0:11] for row in foot_step[:]]
                s2 = [row[11:22] for row in foot_step[:]]
                s3 = [row[22:33] for row in foot_step[:]]
                s4 = [row[33:44] for row in foot_step[:]]
                s5 = [row[44:55] for row in foot_step[:]]
                s6 = [row[55:66] for row in foot_step[:]]

                l1 = np.sum(s1, axis=1)
                l2 = np.sum(s2, axis=1)
                l3 = np.sum(s3, axis=1)
                l4 = np.sum(s4, axis=1)
                l5 = np.sum(s5, axis=1)
                l6 = np.sum(s6, axis=1)
                
                ax[ii +2].cla()
                y_lim = max(max(l1), max(l2), max(l3), max(l4), max(l5), max(l6))
                ax[ii +2].set_ylim([0, y_lim +3])
                ax[ii +2].set_title('Occupant Activity Level in Different regions')
                ax[ii +2].set_ylabel('Footstep Number')
                rec1 =ax[ii +2].bar( x1, l1, width=wid, label='past 120-100 s', fc='y')
                rec2 =ax[ii +2].bar( x2, l2, width=wid, label='past 100-80 s', fc='g')
                rec3 =ax[ii +2].bar( x3, l3, width=wid, label='past 80-60 s', fc='b')
                rec4 =ax[ii +2].bar( x4, l4, width=wid, label='past 60-40 s', tick_label= name_list, fc='gray')
                rec5 =ax[ii +2].bar( x5, l5, width=wid, label='past 40-20 s', fc='lightblue')
                rec6 =ax[ii +2].bar( x6, l6, width=wid, label='past 20-0 s', fc='purple')
#plt.legendi()
		autolabel(rec1, ax[ii +2])
		autolabel(rec2, ax[ii +2])
		autolabel(rec3, ax[ii +2])
		autolabel(rec4, ax[ii +2])
		autolabel(rec5, ax[ii +2])
		autolabel(rec6, ax[ii +2])
                box = ax[ii+2].get_position()
                
		ax[ii +2].legend(bbox_to_anchor=(0.9, -0.2))
                plt.pause(0.001)
          
        t2 = time.clock()
        print("all_time_is %f"%(t2-t1))
        time.sleep(0.06*PLOT_COUNT*0.3)

def autolabel(rects, ax):
    # Get y-axis height to calculate label position from.
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom

    for rect in rects:
        height = rect.get_height()
        label_position = height + (y_height * 0.01)

        ax.text(rect.get_x() + rect.get_width()/2., label_position,
                '%d' % int(height),
                ha='center', va='bottom')

def receive_data(sensor_ip, target_str):
    
    flag = False
    start_time = time.time()
    while True:

        receive_data, client_address = server_socket.recvfrom(1024)
        real_data = decode_data.decode_config_message(receive_data)        
#        print ('%s and message is %s'%(str(client_address[0]), real_data))
        
        if (cmp(str(client_address[0]), sensor_ip)== 0) and target_str in real_data:
#    print ('%s and message is %s'%(client_address, real_data))
            flag = True
            break
        now_time = time.time()
        if now_time - start_time > 1:
            break

    return flag

def send_data(sensor_ip, data_str):

    sensor_address = (sensor_ip, PORT)    
    server_socket.sendto(data_str.encode(),sensor_address)

def save_file(sensor_ip_list, filename, data_list):
    
    date = filename.split('_')[0]
    for count in range( len(sensor_ip_list)):
        if os.path.exists(FILEPATH + sensor_ip_list[count] +'/'+ date +'/') == False:
            os.makedirs(FILEPATH + sensor_ip_list[count] + '/'+ date)
        complete_filename = FILEPATH + sensor_ip_list[count] +'/' + date +'/' +filename
        print(complete_filename)
        datafile = open(complete_filename,'wb')

        datafile.write(data_list[count])
        datafile.close()

def get_time_tag():

    timenow = datetime.datetime.now()
    filename = str(timenow)
    filename = filename.replace(' ','_')
    filename = filename.replace(':','-')
    return filename


def sensor_config_start(sensor_ip, GAIN, data_time):

    ZERO = chr(0)+chr(0)
    RATE = 10000
    state = 0
   
    reset_com = 'r' + ZERO
    test_com ='t' + ZERO
    send_data(sensor_ip, reset_com)
    send_data(sensor_ip, test_com)
    if receive_data(sensor_ip, 'T'):
#        print 'test success'
        state = 1
    else:
        print ('%s test err'%sensor_ip)
    
    config_com = 'c' + chr(0) +chr(0) + chr(4)+chr(0) +chr(16) + chr(39)+chr(GAIN) +chr(0)
    send_data(sensor_ip, config_com)
    if receive_data(sensor_ip, 'Co'):
#        print 'config success'
        state = state + 1
    else:
        print ('%s config fail'%sensor_ip)
    
    start_com  = 's' + ZERO + chr(1)+chr(0) + 't'
    if state == 2:
        send_data(sensor_ip, start_com)
        if receive_data(sensor_ip ,'St'): # it means it start to update data
            print("%s start upload data!"%sensor_ip)
#            all_receive_data(data_time)
        else:
            print( "%s can not start"%sensor_ip)
            
def sensor_stop(sensor_ip_list):

    stop_com  = 's' + chr(0)+chr(0)+ chr(1)+chr(0) + 'p'
    for ii in sensor_ip_list:
        send_data(ii, stop_com)
#print ("%s stoped"%ii)
 
def my_receive(): 
    
    print ("\n*****config information***** \nGain =  %d , record time = %d seconds \nstarted sensor are : %s \n**************************\n" % (GAIN, data_time, str(sensor_ip_list)))

    for ii in sensor_ip_list:
        sensor_config_start(ii, GAIN,data_time)

    start_time = get_time_tag()
    time.sleep(1)
    all_receive_data(sensor_ip_list, data_time)
    time.sleep(1)

    server_socket.close() 
    finish_time = get_time_tag()
    print(start_time)
    print(finish_time)


if __name__ == "__main__":
     
    
    my_receive()

    ss= input('wait')
