import socket
import types
import time
import datetime
import thread
import os
import copy
import errno
from struct import *

#*************config*********************
FILEPATH = './'  #data saved path

data_time = 80 # seconds
 
sensor_ip_list =[]
sensor_ip_list.append('192.168.1.205')
#sensor_ip_list.append('192.168.1.177')

#sensor_ip_list.append('192.168.1.181')

#****************************************
success_com ='G>o'
fail_com = 'G>e'

PORT = 4000    #udp protocol port
#PORT = 5000    #udp protocol port
ServerIp = '192.168.1.193'
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (ServerIp, 4000)
#server_address = (ServerIp, 5000)

server_socket.bind(server_address)

def all_receive_data(sensor_ip_list):
    time_tag = get_time_tag()
    old_min = time_tag[14:16]
    file_date = time_tag[0:14]
 
    all_data  = []
    
    for ii in range(len(sensor_ip_list)):
        all_data.append([])  #initial data list
        all_data[ii] = ''
    server_socket.setblocking(0)
    while True:
        
        time_tag = get_time_tag()
        new_min = time_tag[14:16] 
        if new_min != old_min:
            
            filename = file_date + old_min + '.txt'
            old_min = new_min
            file_date = time_tag[0:14]
            writ_data = copy.deepcopy(all_data)
            thread.start_new_thread(save_file,(sensor_ip_list,filename,writ_data))
            #time correct
#for ii in sensor_ip_list:
#               time_now = get_current_time()
#               time_com = 'y>' + time_now 
#               print(time_com)
#send_data( ii, time_com);
          
#            time_correct(sensor_ip_list);
            for ii in range(len(sensor_ip_list)):
                all_data[ii] = ''
        #receive data
        try:
            receive_data, client_address = server_socket.recvfrom(2048)
        except IOError as e:
            if e.errno == errno.EWOULDBLOCK:
                pass
            continue
        if len(receive_data) < 10:
	    continue
#print(len(receive_data))
	receive_data = decode_data(receive_data)
        
        data_ip = str(client_address[0])
        print ("%s %s"%(client_address, receive_data))
        if data_ip in sensor_ip_list:
            data_location_num = sensor_ip_list.index(data_ip)
        else:
            print ('%s sensor still upload data!'%data_ip)
            continue
        
        #respond to ground truth node

        send_data(data_ip, success_com)
       
#        print len(receive_data)
        all_data[data_location_num] =all_data[data_location_num] + receive_data
        #break 
        #print receive_data

def receive_data(sensor_ip, target_str):
    
    flag = False
    start_time = time.time()
    while True:

        receive_data, client_address = server_socket.recvfrom(1024)
        real_data = receive_data
        sensor_ip = str(client_address[0])
        send_data(sensor_ip, success_com)
#        print("%s configuration reply"%real_data)        
#    print ('%s  message is %s'%(str(client_address[0]), real_data))
        
        if (cmp(str(client_address[0]), sensor_ip)== 0) and (target_str in real_data):
#        print ('%s and message is %s'%(client_address, real_data))
            flag = True
            break
        now_time = time.time()
        if abs(now_time - start_time) > 1:
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
        print complete_filename
        datafile = open(complete_filename,'wb')

        datafile.write(data_list[count])
        datafile.close()

def get_time_tag():

    timenow = datetime.datetime.now()
    filename = str(timenow)
    filename = filename.replace(' ','_')
    filename = filename.replace(':','-')
    return filename

def get_current_time():
    timenow = time.time()
    before_now = time.strftime("%Y:%m:%d_%H:%M:%S",time.localtime(timenow))
    
    time_now = before_now.split('_')[1]
    time_sec = str(int(round((timenow - long(timenow))*1000)))
    all_time = time_now + ':' + time_sec
    return all_time

def time_correct(sensor_ip_list):
    for ii in sensor_ip_list:
        time_now = get_current_time()
        time_com = 'y>' + time_now 
        print(time_com)
        send_data( ii, time_com);
        print(receive_data(ii,'Y>o'))

def decode_data(bin_data):
    head_info = bin_data[0:5]
    head = unpack('<cHH', head_info)
    data = bin_data[7::]
    real_data = unpack('<II', data)
    s1 = ord(bin_data[5])
    s2 = ord(bin_data[6])
#return str(head) +'-'+str(s1) + '-'+str(s2)+'-'+ str(real_data)    
    return str(s1) + ':'+str(s2)+'-'+ str(real_data)+'\n'   

if __name__ == "__main__":
    
    
#time_correct(sensor_ip_list);
#    time.sleep(1)
    start_time = get_time_tag()
    thread.start_new_thread(all_receive_data,(sensor_ip_list,))
    time.sleep(data_time)

    server_socket.close() 
    finish_time = get_time_tag()
    print start_time
    print finish_time
