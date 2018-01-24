#udp cleint from https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-client-protocol

import asyncio as asyncio
import time
import queue
import json

pqs=[]
fps = [30, 30, 30]
tick_length = 1
timeout_time = 5
e = 1
tuples = None

def data_generator(original_time, fps):
  lst = []
  for f in fps:
    for i in range(f):
      lst.append(((time.time()- original_time)//tick_length, "100"))
      time.sleep(1/f)
  return lst

def local_data(original_time=None):
    data = data_generator(original_time, fps)
    pq = queue.PriorityQueue(maxsize = 2000)
    pqs.insert(0,pq)#tuples empty without this. Why doesnt time_sync work when reference_queue isnt local queue?
    add_packets_to_queue(pq, data)
    return original_time
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
                        t.append((reference_packet, q_packet))
    return t

def queue_not_empty(lst_queues):
    for q in lst_queues:
        if q.qsize() > 0:
            return True
    return False
def sync_packet(reference_packet, queue):
    for p in queue.queue:
        if abs(p.time - reference_packet.time) <= e :
            queue.get(p)
            return p
        else:
            print("not here")
    return None

def add_packets_to_queue(queue, data):
    for each_tuple in data:
        queue.put(packet(each_tuple[0], each_tuple[1]))        
#only one queue here in current test

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

class EchoClientProtocol:
    def __init__(self, message, loop, tick_length = 1):
        self.message = message
        self.loop = loop
        self.transport = None
        self.connection_time = time.time()
        self.tick_length = tick_length
        self.sync_latency = {}
        self.qs = {}

    def connection_made(self, transport):
        print("udp connction made")
        self.transport = transport
        print('Send:', self.message)
        self.transport.sendto("request data".encode())

    def datagram_received(self, data, addr):
        global tuples
        json_data =  data.decode()
        original_message = json.loads(json_data)
        print("recieved data", message)
        if addr not in self.qs.keys():
            self.qs[addr] = queue.PriorityQueue(maxsize = 2000)
            pqs.append(self.qs[addr])
        print("recieved data")
        add_packets_to_queue(self.qs[addr], original_message)
        tuples = time_sync()
        analyze_tuples(tuples)
        print("Close the socket")
        # self.transport.close()
    def get_time():
        return (time.time() - original_time) // tick_length
    def get_time_from_message(message):
        return int(message)
    def error_received(self, exc):
        print('Error received:', exc)


class ControllerClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop


    def connection_made(self, transport):
        self.transport = transport
        self.transport.write("request to sync time".encode())
        self.sync_time = time.time()
        #transport.write(self.message.encode())
        #print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        message = data.decode()
        print(message)
        psuedo_time = float(message)
        latency = (time.time() - self.sync_time) / 2
        original_time = (time.time()- latency - psuedo_time)
        local_data(original_time)
        self.transport.close()


    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()
def analyze_tuples(t):
    print("tuples: ", t)
    print("client total tuples of frames: ", len(t))
    print("client tuples of frames per second combining local and remote: ",len(t)/ (len(fps)))


original_time = None
loop = asyncio.get_event_loop()
message = 'Hello World!'
coro = loop.create_connection(lambda: ControllerClientProtocol(message, loop),
                              '127.0.0.1', 8889)
client = loop.run_until_complete(coro)
loop.run_forever()
loop.close()


loop = asyncio.new_event_loop()
message = "udp message!"
connect = loop.create_datagram_endpoint(
    lambda: EchoClientProtocol(message, loop),
    remote_addr=('127.0.0.1', 9999))
transport, protocol = loop.run_until_complete(connect)
loop.run_forever()
transport.close()
loop.close()


