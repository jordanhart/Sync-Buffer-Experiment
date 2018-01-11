#defining packet as a list, in order of 
#(for data packet) protocol code, session ID, Time Stamp, Flag, Payload Size
#(for control packet) protocol code, session ID, Opcode, Payload size
import socket               
import queue
import time
# Create a socket object


data_packet = 0
control_packet = 1
SessionID = 5346245
max_time = 2147483647
server_ip = '127.0.0.1'
tick_length = 1
e = 25
timeout_time = 5
original_time = None
pqs=[]
combined_pq = queue.PriorityQueue(maxsize = 2000)



#code below generates data to be sent in test

def data_generator(time, fps):
	return [setFlag(time + i) for i in range(fps)]
def setFlag(time):
     if time > max_time:
     	return 1
     return 0
#def make_time()
    

#stripped down transmitted. 
#Assume negotiated time and encryption out of scope
#sends packets via sockets instead of network for this expirament

class packet(object):
    def __init__(self, time, data):
    	self.time = time
    	self.data = data
    def __eq__(self, other):
    	return self.time == other.time
    def __ne__(self,other):
    	return self.time != other.time
    def __lt__(self,other):
    	return self.time < other.time
    def __le__(self,other):
    	return self.time <= other.time
    def __gt__(self,other):
    	return self.time > other.time
    def __ge__(self,other):
    	return self.time >= other.time
    def __repr__(self):
    	return "time" + ": "+str(self.time) + ", data: " + str(self.data)


def recieve_data(port = 1235, original_time=None):
    #testing with only 1 transmitter
    #socket code from https://pythontips.com/2013/08/06/python-socket-network-programming/
    s.connect((server_ip, port))
    if original_time == None:
        original_time = time.time()
    pq = queue.PriorityQueue(maxsize = 2000)
    pqs.append(pq)            
    data = s.recv(1024)
    print(data)
    timestamp, packet_data = str(data).split(',')
    print(timestamp)
    timestamp = timestamp[2:] #gets rid of the b'
    time_diff = abs((time.time() - original_time) - float(timestamp))/tick_length
    # receive data from the server
    # close the connection
    #pq.put(packet(time_diff, data))
    combined_pq.put(packet(time_diff, data))
    s.close()
    return original_time, data                   

#only one queue here in current test
def time_sync():
    t = ()
    while combined_pq.qsize() > 0:
        reference_queue = pqs.pop()
        reference_packet = combined_pq.get()
        timeout = time.time() + timeout_time
        for q in pqs:
             if timeout - time.time() >= 0:
                 q_packet = sync_packet(reference_packet, q)
                 if q_packet != None:
                      t.append(q_packet)
    return t


def sync_packet(reference_packet, queue):
    for p in queue:
    	if abs(p.time - reference_packet.time) <= e + tick_length:
    		queue.remove(p)
    		combined_pq.remove(p)
    		return p
s = socket.socket()
recieve_data()
#recieve_data()
time_sync()


