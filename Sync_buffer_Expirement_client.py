#defining packet as a list, in order of 
#(for data packet) protocol code, session ID, Time Stamp, Flag, Payload Size
#(for control packet) protocol code, session ID, Opcode, Payload size
import socket               

# Create a socket object


data_packet = 0
control_packet = 1
SessionID = 5346245
max_time = 2147483647
server_ip = '127.0.0.1'
time = 0
fps = 60



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

def recieve_data(port = 12344):
    #socket code from https://pythontips.com/2013/08/06/python-socket-network-programming/
    s.connect((server_ip, port))
    print(s.recv(1024))
    # receive data from the server
    print(s.recv(1024))
    # close the connection
    s.close()                     



s = socket.socket()
recieve_data()

