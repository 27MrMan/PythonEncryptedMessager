import socket
import sys
import hashlib
import getpass

#SERVER_IP = "127.0.0.1"
SERVER_IP = 'yellow-custody.gl.at.ply.gg'
#SERVER_PORT = 2700
SERVER_PORT = 46163

#moderately high security user validation
def uid_hash(uid,psw):
    combined = f"{uid}|owo-{psw}"
    hash_object = hashlib.sha384(combined.encode('utf-8'))
    return hash_object.hexdigest()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#password = getpass.getpass(prompt="Enter your password ", echo_char = '*').strip()

while True:
    message = input("Enter message: ")
    sock.sendto(message.encode(errors='ignore'), (SERVER_IP, SERVER_PORT))

    print("Awaiting reply...")
    data, address = sock.recvfrom(4096) 
    print(f"Server echoed: {data.decode(errors='ignore')}")