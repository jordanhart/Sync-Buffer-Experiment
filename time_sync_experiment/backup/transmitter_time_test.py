#udp server from https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-client-protocol

import asyncio
import time
import numpy as np


protocol_start_time = time.time()
tick_length = .0001
times = []
counter_init = 100
counter = counter_init #update with number of trials

class EchoServerControllerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        # print('Connection from {}'.format(peername))
        self.transport = transport
        self.tick_length = tick_length

    def data_received(self, data):
        global protocol_start_time
        global counter
        message = data.decode()
        original_time = time.time()
        if (self.request_to_sync_message(message)):
            self.transport.write(str((time.time() - original_time)//self.tick_length).encode())
            while (time.time() - protocol_start_time < 3):
        	    continue
            times.append((time.time() - original_time)//self.tick_length)
            protocol_start_time = time.time()
            counter -= 1

        # print('Data received: {!r}'.format(message))

        # print('Send: {!r}'.format(message))
        # self.transport.write(data)
        # print("json_data", json_data)
        # print("json_data in control server not None: ", json_data!= None)
        
        # print('Close the client socket')
        self.transport.close()
    def connection_lost(self, exc):
        # The socket has been closed, stop the event loop
        # loop.stop()
        print("server counter: ",counter_init-counter)
        if (counter <= 0):
        	loop.stop()
        	raise KeyboardInterrupt()


        print('Close the client socket')
        # self.transport.close()
    def request_to_sync_message(self, message):
        return message == "request to sync time"

def start_server():
   global loop
   global server
   loop = asyncio.get_event_loop()
   # print("starting tcp server")
   # Each client connection will create a new protocol instance
   coro = loop.create_server(EchoServerControllerProtocol, '127.0.0.1', 8891)
   server = loop.run_until_complete(coro)

   # Serve requests until Ctrl+C is pressed
   # print('Serving on {}'.format(server.sockets[0].getsockname()))
   try:
       loop.run_forever()
   except KeyboardInterrupt:
       times_array = np.array(times)
       np.save("server_times", times_array)
       # loop.stop()
       server.close()
       loop.close()
       pass
   server.close()
   # loop.close()

   # # Close the server
   # if (time.time() - protocol_start_time > 6 * 10):
while (counter > 0):
    start_server()
