#udp server from https://docs.python.org/3/library/asyncio-protocol.html#udp-echo-client-protocol

import asyncio
import time
import json
import reedsolo


pqs=[]
fps = [30, 30, 30]
tick_length = .01
time_delay_transmitter_timestamps = 0
network_delay_transmitter_to_client_over_udp = 0
data = None
json_data = None


def data_generator(original_time, fps):
  current_time = time.time()
  lst = []
  for index in range(len(fps)):
    f = fps[index]
    for i in range(f):
      #use i/f instead of wait(1/f) after list append for code to run faster
      lst.append([int((current_time + index - original_time + i/f + time_delay_transmitter_timestamps))//tick_length, 100])
  return lst


class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
        self.connection_made_time = time.time() // tick_length
        self.tick_length = tick_length
        self.original_time = {}
        print("json_data in echoserver not None", json_data != None)

    def datagram_received(self, data, addr):
        message = data.decode()
        # print('Received %r from %s' % (message, addr))
        # print("sending json_data", json_data)
        rs = reedsolo.RSCodec(10)
        reed_data = rs.encode(json_data)
        if network_delay_transmitter_to_client_over_udp > 0:
            time.sleep(network_delay_transmitter_to_client_over_udp)
        self.transport.sendto(reed_data, addr)
        # print('Received %r from %s' % (message, addr))
        # print('Send %r to %s' % (message, addr))
        # self.transport.sendto(data, addr)
    



class EchoServerControllerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport
        self.tick_length = tick_length

    def data_received(self, data):
        global json_data
        message = data.decode()
        if (self.request_to_sync_message(message)):
            self.transport.write(str((time.time() - original_time)//self.tick_length).encode())
        # print('Data received: {!r}'.format(message))

        # print('Send: {!r}'.format(message))
        # self.transport.write(data)
        data = data_generator(original_time, fps)
        json_data = json.dumps(data)
        # print("json_data", json_data)
        print("json_data in control server not None: ", json_data!= None)
        
        print('Close the client socket')
        self.transport.close()
    def connection_lost(self, exc):
        # The socket has been closed, stop the event loop
        loop.stop()


        # print('Close the client socket')
        # self.transport.close()
    def request_to_sync_message(self, message):
        return message == "request to sync time"
original_time = time.time()
loop = asyncio.get_event_loop()
print("starting tcp server")
# Each client connection will create a new protocol instance
coro = loop.create_server(EchoServerControllerProtocol, '127.0.0.1', 8889)
server = loop.run_until_complete(coro)

# Serve requests until Ctrl+C is pressed
# print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# # Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

loop = asyncio.new_event_loop()
print("Starting UDP server")
# One protocol instance will be created to serve all client requests

listen = loop.create_datagram_endpoint(
    EchoServerProtocol, local_addr=('127.0.0.1', 9999))
transport, protocol = loop.run_until_complete(listen)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
