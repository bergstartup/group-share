import threading
import socket
import pickle
import struct
import time
"""
1.Send a udp req to the server ip in port 1000
2.Create a multicast reciever listing to port 1001 addr:224.1.1.1
3.Receive init_packet [session_id,seg_size,no_seg]
4.Recieve filesegments from multicast reciever and store it in list
5.Simultaneously, list for tcp connection in port 1002
6.If tcp connection is made, send the lost segments if there. If not, send [-1] and to step 9
7.Recieve filesegments from multicast reciever and store it in list of matching index
8.send the lost segments if there. If not, send [-1] and to step 9 or to step 7
9.Close everyconnection and terminate.
"""


#Section1
"""
Concept:
Send a request to server for partcipation, a "Hello" msg will do good
"""
server_addr=input("Enter server ip : ")
participation_requester=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
participation_requester.bind(("0.0.0.0",1000))
participation_requester.settimeout(4)
while True:
    participation_requester.sendto("hello".encode(),(server_addr,1000))
    try:
        participation_requester.recv(1024)
        break
    except:
        print("Trying again")#For debugging
        continue
print("accepted")#For debugging
participation_requester.close()


#Section2
"""
Concept:
Recieve the init_packet containing [session_id,filename,seg_size,no_seg] from multicaster in port 1001
"""
multicast_recv=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,socket.IPPROTO_UDP)
multicast_recv.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
mcast_grp="224.1.1.1"
mcast_port=1001
multicast_recv.bind(("0.0.0.0",mcast_port))
mreq = struct.pack("4sl", socket.inet_aton(mcast_grp), socket.INADDR_ANY)
multicast_recv.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

init_packet_digest=multicast_recv.recv(1024)
print("Rcv init packet")
init_packet=pickle.loads(init_packet_digest)
session_id=init_packet[0]
filename=init_packet[1]
seg_size=init_packet[2]
no_of_segments=init_packet[3]


#Section3
"""
Concept:
Multicastor_recv recieves file segments and simultaneously a tcp socket which recieves for connections,if conn recieved stop recving file segments and get lost list of lost segments
"""
file_data=[i for i in range(no_of_segments)]
recv_segments=[i for i in range(no_of_segments)]
tcp_conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
tcp_conn.bind(("0.0.0.0",1002))
mutex=True
def multicast_listner():
    global file_data
    global recv_segments
    multicast_recv.settimeout(2)
    while len(recv_segments)!=0:
        try:
            data_digest=multicast_recv.recv(1024)
        except:
            continue
        data=data_digest.decode()
        seg_no,seg_data=data.split(";")
        try:
            del recv_segments[recv_segments.index(int(seg_no))]
        except:
            continue
        file_data[int(seg_no)]=seg_data
        print("Recieved msg : ",data)#For debugging
        

def listen_tcp_connections():
    tcp_conn.listen(1)
    server_tcp,_=tcp_conn.accept()#Blocking process
    time.sleep(0.5)#For sync
    print("Unrecieved segments : ",recv_segments)#For debugging
    while len(recv_segments)!=0:
        server_tcp.send(pickle.dumps(recv_segments))
        server_tcp.recv(1024)#Blocking
        time.sleep(0.5)#for sync
    server_tcp.send(pickle.dumps([-1]))

    
tcp_thread=threading.Thread(target=listen_tcp_connections)
multicast_listner_thread=threading.Thread(target=multicast_listner)
multicast_listner_thread.start()
tcp_thread.start()
multicast_listner_thread.join()
"""
tcp_thread.join()
tcp_conn.close()
"""
#Shutdown tcp connection and close all sokets


#Section4
"""
conept:
Write the data to file
"""
print(file_data)
fileptr=open(filename,"w")
for data in file_data:
    fileptr.write(data)
fileptr.close()
tcp_thread.join()
