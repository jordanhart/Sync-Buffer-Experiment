#defining packet as a list, in order of 
#(for data packet) protocol code, session ID, Time Stamp, Flag, Payload Size
#(for control packet) protocol code, session ID, Opcode, Payload size
import socket               
import time
import numpy as np

# Create a socket object

protocol_start_time = time.time()
original_time = None
counter = 0
times = []
tick_length = .0001
server_ip = '127.0.0.1'
BUFFER_SIZE = 1024

time.sleep(1)


def recieve_data(port = 1257):
    #testing with only 1 transmitter
    #socket code from https://pythontips.com/2013/08/06/python-socket-network-programming/
    global counter
    global protocol_start_time
    MESSAGE = "request to sync time"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))
    latency_time_start = time.time()
    s.send(MESSAGE.encode('utf-8'))
    data = s.recv(BUFFER_SIZE)
    latency = (time.time() - latency_time_start) / 2
    server_psuedo_time = float(str(data).replace("'","").replace("b",""))
    original_time = time.time() - latency / 2 - server_psuedo_time * tick_length
    while (time.time() - protocol_start_time < 3):
        continue
    times.append((time.time() - original_time)//tick_length)
    counter +=1
    print("client counter: ", counter)
    protocol_start_time = time.time()

    s.close()

for i in range(1000):
    recieve_data()
times_array = np.array(times)
np.save("client_times", times_array)
