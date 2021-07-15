"""
This is a simple program to record the data for SRT when both the
SRT Daemon and Dashboard are running. 

Run this program using 

python record_time_pwr_azel.py (with no arguments)

To stop and save the recorded file, press Ctrl-C. 

The data will be saved in the current directory with the 
filename derived from the start of the recording time.
"""

import zmq
import json
import time
import csv
import numpy as np

MAX_LEN = 3600

def main():
    my_data = np.zeros((MAX_LEN, 4), dtype=np.float64)

    # Add by jhl for receiving update of az_el
    context = zmq.Context()
    time_pwr_azel_port = 5566
    time_pwr_azel_socket = context.socket(zmq.SUB)
    time_pwr_azel_socket.connect("tcp://localhost:%s" % time_pwr_azel_port)
    time_pwr_azel_socket.subscribe("")

    # Initialize a pollre
    poller = zmq.Poller()
    poller.register(time_pwr_azel_socket, zmq.POLLIN)

    rec_num = 0
    while True:
        try:
            socks = dict(poller.poll(10))
        except KeyboardInterrupt:
            break

        if time_pwr_azel_socket in socks:
            rec = time_pwr_azel_socket.recv()
            time_pwr_azel = json.loads(rec)
            print(time_pwr_azel)
            rec_time = time_pwr_azel["time"]
            print("My rec_time= ", rec_time)
            print("My rec_num = ", rec_num)
            my_data[rec_num, 0] = rec_time
            print(my_data[rec_num, 0])
            print(time.ctime(rec_time))
            rec_pwr = time_pwr_azel["power"]
            my_data[rec_num, 1] = rec_pwr
            motor_az_el = time_pwr_azel["motor_azel"]
            my_data[rec_num, 2] = motor_az_el[0]
            my_data[rec_num, 3] = motor_az_el[1]
            rec_num += 1

        if rec_num >= MAX_LEN:
            break

    time_pwr_azel_socket.close()
    context.term()
    print("Saving results.")

    tm = my_data[0,0]
    print("There are {rec_num} data samples.")
    print("Starting time is: ", time.ctime(tm))

    # Resize the data matrix according to the true size
    my_data = my_data[:rec_num,:]
    
    # Remove the start recording time
    my_data[:,0] = my_data[:,0] - tm
    
    # Keel only ONE significant digit after the decimal point.
    my_data = np.rint(my_data * 10.0)
    my_data = my_data/10
    # print(my_data)

    filename = time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(tm))
    my_file = filename+'.csv'

    csv_fields = ['Time', 'Power', 'Azimuth', 'Elevation']
    with open(my_file, 'w') as csvfile:
        #csvwriter = csv.writer(csvfile, fieldnames = csv_fields)
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(csv_fields)
        #csvwriter.writeheader()
        for i in range(rec_num):
            row = [my_data[i,j] for j in range(4)]
            csvwriter.writerow(row)

if __name__ == '__main__':
    main()
