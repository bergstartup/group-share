"""
import os
segment_size=8 #Yet to decide
filename="sample.txt"
filesize=os.stat(filename).st_size #Returns in bytes
print(filesize)
no_of_segments=filesize//segment_size #Rounded no_of_segment, final segment contains equal or more

#Content format : segment_no;file_data
file_ptr=open(filename,"rb")
curr_ptr_position=0
for i in range(no_of_segments):
    content=str(i)+";"
    file_ptr.seek(i*segment_size,0)
    if i!=no_of_segments-1:
        content+=str(file_ptr.read(segment_size))
    else:
        content+=str(file_ptr.read())
    print(content)
"""
import socket
import time
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.bind(("localhost",500))
print("Socket ready")
time.sleep(5)
s.setblocking(0)
a,b=s.recv(1024)
print(a,b)

