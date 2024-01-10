from controller import *
import socket



udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('0.0.0.0', 12345) 
udp_socket.bind(address)
while True:
        udp_socket.sendto(b'', client_address)
        print("Response sent to", ("192.168.3.43",8888))

        data, client_address = udp_socket.recvfrom(1024)
        print("Received message from", client_address)
        response = b'Hello, UDP client!'
        
    udp_socket.close()



# x = xbox_controller(controller=controller("192.168.3.43:8889"))
# x.clickBTN(BTN_A)

