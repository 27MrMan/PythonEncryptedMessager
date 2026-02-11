import socket
import sys

IP = "127.0.0.1" 
PORT = 2700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"Listening for clients at {(IP, PORT)}")

address_list = []

while True:
    data, address = sock.recvfrom(4096)

    print(f"Received {data} from {address}")

    if address not in address_list:
        address_list.append(address)

    message = input("Reply? ")

    for i in address_list:
        sock.sendto(message.encode(errors='ignore'), i)
