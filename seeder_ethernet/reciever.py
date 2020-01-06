import socket
from ftplib import FTP
import threading
from server import ftp_server
import pickle
import os
import datetime
    
#To give a request
get_sender_ip=input("Get ip : ")
request_port=9000
message="_"
udp_socket=socket.socket(family=socket.AF_INET,type=socket.SOCK_DGRAM)
udp_socket.sendto(str.encode(message),(get_sender_ip,request_port))

#Creating ftp server to recieve file
ser=ftp_server()
ser.start()


#Creating TCP port and Recieve table and close the tcp socket
local_ip=""
tcp_socket=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)#An Server TCP socket
tcp_port=8000#An TCP port
tcp_socket.bind((local_ip,tcp_port))#Server binded
print("Listenening to connections")
tcp_socket.listen(1)
connection,_=tcp_socket.accept()
print("Waiting for data")
data=connection.recv(1024)
address_table = pickle.loads(data)
tcp_socket.close()
print(address_table)

#Stop the ftp server
ser.stop()

#Create a TCP port
node_connect=socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)#An TCP socket to send addr table
node_connect_port=8000#An TCP port

#Changing into seeder
filepath=ser.get_filename() #Retriving file
print("In reciever : ",filepath)
filename=filepath.split("\\")[-1]
filesize=os.stat(filepath).st_size
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
