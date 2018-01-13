#defining packet as a list, in order of 
#(for data packet) protocol code, session ID, Time Stamp, Flag, Payload Size
#(for control packet) protocol code, session ID, Opcode, Payload size
import socket               
import queue
import time
import json

# Create a socket object


data_packet = 0
control_packet = 1
SessionID = 5346245
max_time = 2147483647
server_ip = '127.0.0.1'
tick_length = .0000001
e = .01
timeout_time = 1
original_time = None
pqs=[]
fps = [15,15,15]




#code below generates data to be sent in test

def data_generator(original_time, fps):
  lst = []
  for f in fps:
    for i in range(f):
      lst.append(((time.time()- original_time)//tick_length, "100"))
  return lst
# def setFlag():
#      if time > max_time:
#      	 return 1
#      return 0

#def make_time()
    

#stripped down transmitted. 
#Assume negotiated time and encryption out of scope
#sends packets via sockets instead of network for this expirament

class packet(object):
    def __init__(self, time, data):
    	self.time = time
    	self.data = data
    def __eq__(self, other):
    	return other != None or  self.time == other.time
    def __ne__(self,other):
    	return other == None or self.time != other.time
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


def recieve_data(port = 1242):
    #testing with only 1 transmitter
    #socket code from https://pythontips.com/2013/08/06/python-socket-network-programming/

    pq = queue.PriorityQueue(maxsize = 2000)
    pqs.append(pq) 
    s.connect((server_ip, port))
    server_psuedo_time = float(str(s.recv(1024)).replace("'","").replace("b",""))
    print("server psuedo_time",server_psuedo_time)
    original_time = time.time() - server_psuedo_time * tick_length
    json_data = s.recv(4098)    
    data = json.loads(json_data)
    #original_time = time.time()
    #print("data" , data)
    # receive data from the server
    # close the connection
    #pq.put(packet(time_diff, data))
    add_packets_to_queue(pq, data)

    s.close()
    return original_time           

def add_packets_to_queue(queue, data):
    for each_tuple in data:
        queue.put(packet(each_tuple[0], each_tuple[1]))        
#only one queue here in current test
def time_sync():
    t = []
    if len(pqs) == 0:
    	return t
    if len(pqs) == 1:
    	return list(pqs[0].queue)
    #while queue_not_empty(pqs) == True:
    reference_queue = pqs.pop()
    while reference_queue.qsize() > 0:
        	reference_packet = reference_queue.get()
        	timeout = time.time() + timeout_time
        	for q in pqs:
        		if timeout - time.time() >= 0:
        			q_packet = sync_packet(reference_packet, q)
        			if q_packet != None:
        				t.append(reference_packet)
        				t.append(q_packet)
    return t

def queue_not_empty(lst_queues):
	for q in lst_queues:
		if q.qsize() > 0:
			return True
	return False

def local_data(original_time=None):
	data = data_generator(original_time, fps)
	pq = queue.PriorityQueue(maxsize = 2000)
	pqs.insert(0,pq)#tuples empty without this. Why doesnt time_sync work when reference_queue isnt local queue?
	add_packets_to_queue(pq, data)
	return original_time

def sync_packet(reference_packet, queue):
	for p in queue.queue:
		if abs(p.time - reference_packet.time) <= e / tick_length:
			queue.get(p)
			return p
		else:
			print("not here")
	return None
s = socket.socket()
#original_time = recieve_data()
#local_data(original_time)
original_time = recieve_data()
local_data(original_time)
t = time_sync()
print("tuples: ", t)
print("client total frames, including local and remote: ", len(t))
print("client frames per second combining local and remote: ",len(t)/ (2 * len(fps)) )