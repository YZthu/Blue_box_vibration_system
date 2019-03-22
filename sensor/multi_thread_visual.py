import socket
import types
import time
import datetime
import threading
import os
import decode_data
import copy
import numpy as np
#import scipy.signal
import matplotlib.pyplot as plt
import Queue
import errno
###info
# this file utilize multi thread to solve the delay of visualition.

#ServerIP and port config.
PORT = 5000    #udp protocol port
ServerIp = '192.168.1.193'

# file saved path.
FILEPATH = './'  #data saved path

#plot config.
PLOT_NUM =160  # x-axis totally number is 600*PLOT_NUM
PLOT_COUNT = 10 # figure is updated every 0.06*PLOT_COUNT s

# sensor config
sensor_ip_list =[]

sensor_ip_list.append('192.168.1.117')
sensor_ip_list.append('192.168.1.150')

data_time = 60 #receiv data time limit, the unit is seconds, 0 means receive data all the time.

GAIN = 60

#*************config end*************

queue = []
for ii in range(len(sensor_ip_list)):
    queue.append(Queue.Queue(0))

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
    thread = threading.Thread(target=myplot, args=(len(sensor_ip_list),))
    thread.setDaemon(True)
    thread.start()
    
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

            break
       
       
        # save file
        if new_min != old_min:
            filename = file_date + old_min + '.txt'
            old_min = new_min
            file_date = time_tag[0:14]
            writ_data = copy.deepcopy(all_data)
            threading.Thread(target=save_file, args=(sensor_ip_list,filename,writ_data,)).start()
   
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
        
        # begin plot
        if plot_count[data_location_num] >= PLOT_COUNT:
            queue[data_location_num].put(filter_data[data_location_num])
            plot_count[data_location_num] =0
            print(queue[data_location_num].qsize())        
     
        t2 = time.clock()
#       print("data process time is %f"%(t2-t1))


def myplot(number):
   
    time_x = np.linspace(0, PLOT_NUM*0.06, 600*PLOT_NUM) 
    plot_data = [[0*x for x in range(600*PLOT_NUM)] for j in range(len(sensor_ip_list))]
    raw_data = [[0*x for x in range(600*PLOT_NUM)] for j in range(len(sensor_ip_list))]
    plt.rcParams['figure.figsize'] =(8,4)

    name_list =[]
    f = plt.figure(0)
    ax =[]
    for ii in range(number +1):
        ax.append(f.add_subplot(2,2,ii+1))
        if ii < number:
            name_list.append('Sensor ' + str(ii +1))
    wid = 0.4
    x1 = list(range(number))
    x2 = list(range(number))
    for i in range(number):
        x2[i] = x2[i] + wid

    print(name_list)
    while True:
        for ii in range(number):
            if not queue[ii].empty():
                data = queue[ii].get()
                raw_data[ii] = raw_data[ii] + data
                new_len = len( data )
                raw_data[ii][0:new_len] = []
                filter_data = raw_data[ii][300*PLOT_NUM :600*PLOT_NUM]
 #               filtered_sig = scipy.signal.wiener(filter_data, 501).tolist()
                filtered_sig = filter_data
                used_data =filtered_sig[(300*(PLOT_NUM -1)- new_len):300*(PLOT_NUM-1)]
                plot_data[ii] = plot_data[ii] + used_data
                tmplen= len(used_data)
                plot_data[ii][0:tmplen] = []
    
                s='''              
                t1 = time.clock()
                plt.figure(ii)
		plt.clf()
		plt.ylim([0, 45000])
                plt.ylabel('Digital amplitude')
		plt.xlabel('Time(s)')
                plt.plot(plot_data[ii])
                plt.pause(0.001)
                t2 = time.clock()
		     '''
                
                t1 = time.clock()
                ax[ii].cla()
                ax[ii].set_ylim([0, 45000])
                ax[ii].set_ylabel('Digital amplitude')
                ax[ii].set_xlabel('Time(s)')
                ax[ii].set_title('Sensor ' + str(ii+1))
                ax[ii].plot(time_x, plot_data[ii])
                plt.pause(0.001)
                t2 = time.clock()
    
#   print("all time is %f"%(t2-t1))
            if ii == (number -1):
                his_list = [1.5]
                new_list = [ 4 ]
                ax[ii +1].cla()
                ax[ii +1].set_title('Occupant Activity Level in Different regions')
                ax[ii +1].set_ylabel('Footstep Number')
                ax[ii +1].bar( x1, his_list, width=wid, label='past', fc='y')
                ax[ii +1].bar( x2, new_list, width=wid, label='now', tick_label= name_list, fc='b')
                plt.legend()
                plt.pause(0.001)

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
