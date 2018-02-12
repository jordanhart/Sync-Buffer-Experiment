#udp cleint from https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-client-protocol

import asyncio as asyncio
import time
import numpy as np

protocol_start_time = time.time()
tick_length = .0001
times = []
count = 0

class ControllerClientProtocol(asyncio.Protocol):
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop
        self.tick_length = tick_length


    def connection_made(self, transport):
        self.transport = transport
        self.transport.write("request to sync time".encode())
        self.sync_time = time.time()

    def data_received(self, data):
        global protocol_start_time
        latency = (time.time() - self.sync_time) / 2
        message = data.decode()
        psuedo_time = float(message)
        original_time = time.time() - latency/2 - psuedo_time * tick_length
        while (time.time() - protocol_start_time < 3):
            continue
        times.append((time.time() - original_time)//self.tick_length)
        protocol_start_time = time.time()

        self.transport.close()


    def connection_lost(self, exc):
        global count
        count += 1
        print("client count: ", count)
        # print('The server closed the connection')
        # print('Stop the event loop')
        self.loop.stop()
def run_test():
    global loop
    loop = asyncio.get_event_loop()
    message = 'Hello World!'
    coro = loop.create_connection(lambda: ControllerClientProtocol(message, loop),
                              '127.0.0.1', 8890)
    loop.run_until_complete(coro)
    loop.run_forever()
    # loop.close()

for i in range(100):
    run_test()
loop.close()

times_array = np.array(times)
np.save("client_times", times_array)

