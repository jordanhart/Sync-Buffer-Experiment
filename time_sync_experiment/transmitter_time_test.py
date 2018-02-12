#defining packet as a list, in order of 
#(for data packet) protocol code, session ID, Time Stamp, Flag, Payload Size
#(for control packet) protocol code, session ID, Opcode, Payload size

import socket  
import time    
import numpy as np
protocol_start_time = time.time()
tick_length = .0001
times = []
counter_init = 1000
counter = counter_init #update with number of trials
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

def start_server(s, port = 1257):
    global counter
    global protocol_start_time
    #socket code from https://pythontips.com/2013/08/06/python-socket-network-programming/
    # next create a socket object
    print("Socket successfully created")

    # reserve a port on your computer in our
    # case it is 12345 but it can be anything


    # Next bind to the port
    # we have not typed any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests 
    # coming from other computers on the network
    s.bind(('127.0.0.1', port))        
    print("socket binded to %s" %(port))

    # put the socket into listening mode
    s.listen(1)     
    print("socket is listening")

    time.sleep(1)

    # a forever loop until we interrupt it or 
    # an error occurs
    original_time = None  

    def send_time(s):#s is a socket
        psuedotime=(time.time() - original_time)//tick_length
        s.send(str(psuedotime).encode("utf-8")) #sending current psuedotime
        return original_time  

    while (counter > 0):
       # Establish connection with client.
       c, addr = s.accept()     
       print('Got connection from', addr)
       print('c', c)

       data = c.recv(BUFFER_SIZE)
       # t = s.recv(1024)
       # original_time = time.time() - int(t) * tick_length
       if (original_time == None):
          original_time = time.time()
          send_time(c)
          while (time.time() - protocol_start_time < 3):
        	    continue
          times.append((time.time() - original_time)//tick_length)
          counter -= 1
          print("server counter: ", counter_init - counter)
          protocol_start_time = time.time()
          original_time = None
      

       # Close the connection with the client
       c.close()                         

       times_array = np.array(times)
       np.save("server_times", times_array)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start_server(s)

#stripped down synchronized reciever instance

