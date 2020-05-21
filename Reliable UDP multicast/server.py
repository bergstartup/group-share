#Required libraries for server
import socket
import os
import pickle
import time
import threading
"""
Key points:
#For debugging refers line added for debugging and to understand behaivour of code, purely for testing purpose
"""

"""
Ports to be noted in server
1000 - Participant acceptor port [udp]
1001 - Mcast port [udp]
1002 - Token send port [tcp]
"""

"""
List of communication with sender and reciever:
1.Server waits for udp packets from partcipants
2.Server multicasts init_packet contains [session_id,filename,segment_size,no_of_segments]
3.Server multicasts file data in segments
4.Server makes tcp connection with a reciever
5.Reciever sends the lost_segments as list
6.Server multicasts lost_segments and sends pulse msg to note reciever that requested data has been multicasted, repeat step5 till server recieves [-1]
7.Server closes tcp connection
8.Repeat steps 4-7 for all recievers
"""


#Section1
"""
Concept:
    Code for getting udp packet from reciever as a token of participation
Description:
    A socket to recv tokens from the desired file reciever, till user arbitarly closes the port
Implementation:
A udp socket binded to port:1000, which listens to incomming tokens. A thread which listen for user input, makes mutex variable false, if input provided. Mutex is a shared varibale between thread and main process
"""
participation_collector_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
participation_collector_socket.bind(("0.0.0.0",1000))
#participation_collector_socket.listen()
participants=[]
def p_listner():
    print("Listnin for participants") #For debugging
    while True:
        try:
            _,participant_addr=participation_collector_socket.recvfrom(1024)#A tuple with 4 val is returned, we consider only the address. 1024 reffers kernel buffer address.
        except:
            break
        participation_collector_socket.sendto("yes".encode(),participant_addr)
        print(participant_addr)
        participants.append(participant_addr[0])
    participation_collector_socket.close()

pl=threading.Thread(target=p_listner)
pl.start()
input()
participation_collector_socket.close()
print("Participants reciv is over") #For debugging

#Section2
"""
Concept:
Create a multicast port
"""
multicaster=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
multicaster.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
mcast_addr="224.1.1.1"
mcast_port=1001
multicaster.bind(("0.0.0.0",mcast_port))


#Section3
"""
Concept:
Get filename from user. Get its size, calculate no of segments and multicast
"""
segment_size=1 #Yet to decide
filename=input("Enter file name : ")
filesize=os.stat(filename).st_size #Returns in bytes
session_id=filename+"_"+str(filesize)
no_of_segments=filesize//segment_size #Rounded no_of_segment, final segment contains equal or more
init_send_digest=pickle.dumps([session_id,filename,segment_size,no_of_segments])
multicaster.sendto(init_send_digest,(mcast_addr,mcast_port))
time.sleep(1) #Waiting for reciever to get ready with threads
#Section4
"""
Concept:
Read file and multicast, for each msg update the pointer.
Data_to_send=file[fileptr:fileptr+pointer*segment_size]
"""
#Content format : segment_no;file_data

#Function decl for multicasting filesegments
flag=False #For debugging
def multicaster_file_data(file_ptr,segment_size,no_of_segments,multicaster,segments):
    global flag#For debugging
    for i in segments:
        content=str(i)+";"
        file_ptr.seek(i*segment_size,0)
        if i!=no_of_segments-1:
            content+=file_ptr.read(segment_size)
        else:
            content+=file_ptr.read()
        if ((i not in [2,3,10])or(flag)):
            print("Message sent : ",content)
            multicaster.sendto(content.encode(),(mcast_addr,mcast_port))
    flag=True #For debugging
file_ptr=open(filename,"r")
multicaster_file_data(file_ptr,segment_size,no_of_segments,multicaster,[i for i in range(no_of_segments)])
print("Segment sent")#For debugging


#Section5
"""
Concept:
Send a special token to recievers in order.
"""
#Here token is a tcp connection.
for i in range(len(participants)):
    token_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    token_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    token_socket.bind(("0.0.0.0",1002))
    token_socket.connect((participants[i],1002))
    while True:
        print("TCP connection has been established, yet to recv segments")#For debugging
        lost_segments_digest=token_socket.recv(1024)
        lost_segments=pickle.loads(lost_segments_digest)
        if lost_segments[-1]==-1:
            break
        multicaster_file_data(file_ptr,segment_size,no_of_segments,multicaster,lost_segments)
        token_socket.send(" ".encode())#To intimate data has been multicasted
    #token_socket.shutdown("SHUT_RDWR")#Close curr connnection
    print("Taking connetion to next")#for debugging
    token_socket.detach()
token_socket.close()
    



