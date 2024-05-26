import struct
from utils.interface.winDefines import *
from utils.interface.winController import *
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 8889))  # 绑定到本地12345端口

while True:
    data, addr = sock.recvfrom(1024)  # 接收最多1024字节的数据
    event_count = int(data[0])
    for i in range(event_count):
        type,code,value = struct.unpack('<HHi', data[2+i*8:2+(i+1)*8])
        print(f"Event {i}: type={type}, code={code}, value={value}")