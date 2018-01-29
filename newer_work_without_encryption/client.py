#udp cleint from https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-client-protocol

import asyncio as asyncio
import time
import queue
import json
import reedsolo


fps = [30, 30, 30]
timeout_time = 5
tick_length = .01
latency_time_allowed = .01 #second, target for ml models
e = latency_time_allowed / tick_length
time_delay_client_timestamps = 0
fec = 0

def data_generator(original_time, fps):
  current_time = time.time()
  lst = []
  append = lst.append
  for index in range(len(fps)):
    f = fps[index]
    for i in range(f):
      #use i/f instead of wait(1/f) after list append for code to run faster
      append([((current_time + index - original_time + i/f + time_delay_client_timestamps))//tick_length, 100])
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
    reference_queue = pqs.pop()
    times = time.time
    append = t.append
    while reference_queue.qsize() > 0:
            reference_packet = reference_queue.get()
            timeout = times() + timeout_time
            for q in pqs:
                if timeout - times() >= 0:
                    q_packet = sync_packet(reference_packet, q)
                    if q_packet != None:
                        append((reference_packet, q_packet))
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
    print("did not sync data")
    return None

def add_packets_to_queue(queue, data):
    put = queue.put
    p = lambda t: packet(t[0], t[1])
    packets = map(p, data)
    for pack in packets:
        put(pack)        
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
        self.qs = {}

    def connection_made(self, transport):
        # print("udp connction made")
        global udp_time_start
        udp_time_start = time.time()

        self.transport = transport
        # print('Send:', self.message)
        self.transport.sendto("request data".encode())

    def datagram_received(self, data, addr):
        global time_data_recieved_start
        global time_data_recieved_and_loaded
        time_data_recieved_start = time.time()
        print("length recieving data" , len(data))
        time_fec_starts = 0
        if (fec > 0):
            rs = reedsolo.RSCodec(fec)
            time_fec_starts = time.time()
            data =  rs.decode(data)
        time_json_start = time.time()
        original_message = json.loads(data.decode())
        time_for_fec_and_dejson_end = time.time()
        if addr not in self.qs.keys():
            self.qs[addr] = queue.PriorityQueue(maxsize = 2000)
            pqs.append(self.qs[addr])
        # print("recieved data")
        add_packets_to_queue(self.qs[addr], original_message)
        time_data_recieved_and_loaded = time.time()
        time_packet_sync_start = time.time()
        tuples = time_sync()
        end_time = time.time()
        analyze_tuples(tuples, end_time, time_data_recieved_start, \
            time_data_recieved_and_loaded, time_packet_sync_start, \
            time_for_fec_and_dejson_end, time_fec_starts, time_json_start)
        # print("Close the socket")
        self.transport.close()
    def get_time():
        return (time.time() - original_time) // tick_length
    def get_time_from_message(message):
        return int(message)
    def error_received(self, exc):
        print('Error received:', exc)
    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        # self.loop.stop()



class ControllerClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop


    def connection_made(self, transport):
        global time_timesync_started
        self.transport = transport
        self.transport.write("request to sync time".encode())
        self.sync_time = time.time()
        time_timesync_started = time.time()
        #transport.write(self.message.encode())
        #print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        global time_timesync_ended
        message = data.decode()
        # print(message)
        psuedo_time = float(message)
        latency = (time.time() - self.sync_time) / 2
        original_time = ((time.time()- latency)//tick_length - psuedo_time) * tick_length
        time_timesync_ended = time.time()
        local_data(original_time)
        self.transport.close()


    def connection_lost(self, exc):
        print('The server closed the connection')
        print('Stop the event loop')
        self.loop.stop()

# def keep_track_of_tuples(t, end_time, time_data_recieved_start, \
#     time_data_recieved_and_loaded, time_packet_sync_start, \
#     time_for_fec_and_dejson_end, time_fec_starts, time_json_start):
#     lst_end_time.append(end_time)
#     lst_time_data_recieved_start.append(time_data_recieved_start):
def analyze_tuples(t, end_time, time_data_recieved_start, \
    time_data_recieved_and_loaded, time_packet_sync_start, \
    time_for_fec_and_dejson_end, time_fec_starts, time_json_start):
    # print("tuples: ", t)
    # print("client total tuples of frames: ", len(t))
    print("seconds took for time handshake: ", time_timesync_ended - time_timesync_started)
    print("seconds since recieved data to packets being synced: ", end_time - time_data_recieved_start)
    print("seconds from udp connection made to data transfered, loaded in original form, and in queue: ", time_data_recieved_and_loaded - udp_time_start)
    print("seconds from udp connection made to data recieved : ", time_data_recieved_start - udp_time_start)
    print("seconds from udp data transfered to data in queue : ", time_data_recieved_and_loaded - time_data_recieved_start)
    print("time json: ", time_for_fec_and_dejson_end - time_json_start)
    print("time fec: ", time_json_start - time_fec_starts)
    print("seconds for packet sync code to run :", end_time - time_packet_sync_start)
    print("seconds for experiment to run", end_time - protocol_start_time)
    print("average tuples / frames per second combining local and remote: ",len(t)/ (len(fps)))


pqs=[]
original_time = None
time_data_recieved_start = None
time_timesync_ended = None
time_timesync_started = None
protocol_start_time = time.time()



def run_test():
    loop = asyncio.get_event_loop()
    message = 'Hello World!'
    coro = loop.create_connection(lambda: ControllerClientProtocol(message, loop),
                              '127.0.0.1', 8889)
    client = loop.run_until_complete(coro)
    loop.run_forever()
# loop.close()


# loop = asyncio.new_event_loop()
    message = "udp message!"
    connect = loop.create_datagram_endpoint(
        lambda: EchoClientProtocol(message, loop),
        remote_addr=('127.0.0.1', 9999))
    transport, protocol = loop.run_until_complete(connect)
    loop.run_forever()
    transport.close()
    loop.close()
run_test()

