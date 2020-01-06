import socket
from ftplib import FTP
import threading
import pickle
import os

check=int(input("Enter no of request : "))
address_table=[]
point=1
def recieve_req():
    input()
    global check
    check=False
    
def getip(udp_socket):
    global check
    global address_table
    for i in range(check):
        print("list")
        msg_addr_pair=udp_socket.recvfrom(buffer_size)
        print(msg_addr_pair[1][0]) #For debug
        address_table.append(msg_addr_pair[1][0])
    print("Stopped listening")

def pointer(neg):
    global point
    print(point)
    point+=1
    

local_ip=""
udp_socket=socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)#AN UDP socket for recieving request
request_port= 9000#An udp port to recieve request
buffer_size=1024
udp_socket.bind((local_ip,request_port))
print("UDP server is listenin in port ",request_port)
getip(udp_socket)

#Create a TCP port
node_connect=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)#An TCP socket to send addr table
node_connect_port=8000#An TCP port 


#File to send to addr
filename=input("Enter Filename : ")
filesize=os.stat(filename).st_size
no_of_blocks=(filesize//8192)+1
print("Blocks to send : ",no_of_blocks)
while len(address_table)!=0:
    node_addr=address_table[0]
    print("To addr : ",node_addr)
    ftp=FTP(node_addr,"user", "12345")
    ftp.login()
    start=datetime.datetime.now()
    ftp.storbinary('STOR '+filename, open(filepath, 'rb'))
    end=datetime.datetime.now()
    print("Time taken for transfer",end-start)
    del address_table[0]
    node_connect.connect((node_addr,node_connect_port))
    data = pickle.dumps(address_table[len(address_table)//2:])
    node_connect.send(data)
    del address_table[len(address_table)//2:]
    node_connect.close()
    #ftp.quit()
