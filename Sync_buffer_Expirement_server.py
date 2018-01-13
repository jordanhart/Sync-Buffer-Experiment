#defining packet as a list, in order of 
#(for data packet) protocol code, session ID, Time Stamp, Flag, Payload Size
#(for control packet) protocol code, session ID, Opcode, Payload size

import socket  
import time    
import json         

data_packet = 0
control_packet = 1
SessionID = 5346245
max_time = 2147483647
tick_length = 1


fps = 60

#code below generates data to be sent in test

def data_generator(original_time, fps):
  lst = []
  for i in range(fps):
    lst.append(((time.time()- original_time)/tick_length, "100"))
  return lst
# def setFlag():
#      if time > max_time:
#      	 return 1
#      return 0
#def make_time()


def start_server(s, port = 1242):
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
    s.bind(('', port))        
    print("socket binded to %s" %(port))

    # put the socket into listening mode
    s.listen(5)     
    print("socket is listening")

    # a forever loop until we interrupt it or 
    # an error occurs
    original_time = None  

    def send_time(s):#s is a socket
        psuedotime=(time.time() - original_time)/tick_length
        s.send(str(psuedotime).encode("utf-8")) #sending current psuedotime
        return original_time  

    while True:
       # Establish connection with client.
       c, addr = s.accept()     
       print('Got connection from', addr)
       print('c', c)
       # t = s.recv(1024)
       # original_time = time.time() - int(t) * tick_length
       if (original_time == None):
          original_time = time.time()
       send_time(c)
       data = data_generator(original_time, fps)
       json_data = json.dumps(data)
       print(json_data)
       print('data', json_data)
       # send a thank you message to the client. 
       c.send(json_data.encode('utf-8'))
       #data_to_send = str((time.time() - original_time)/tick_length) + ',' +  data           
       #c.send(data_to_send.encode('utf-8'))

       # Close the connection with the client
       c.close()                         


s = socket.socket()
start_server(s)

#stripped down synchronized reciever instance

