import hashlib
import socket
import sys
from csv import writer


IP = "127.0.0.1" 
PORT = 2700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"Listening for clients at {(IP, PORT)}")

userid_list = []
epwd_list = []


while True:
    data, address = sock.recvfrom(4096)

    print(f"Received {data} from {address}")

    if data.decode()[:3] == "uid":
        userid_list.append(data.decode()[3:])
    if data.decode()[:2] == "pw":
        epwd_list.append(data.decode()[2:])

    if any(epwd_list) and any(userid_list):
        break

message = "Credentials Recieved!"

new_row = [userid_list[0], epwd_list[0]]
with open('users.csv', 'a', newline='') as file:
    writer_obj = writer(file)
    writer_obj.writerow(new_row)

sock.sendto(message.encode(errors='ignore'), address)