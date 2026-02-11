import socket
import sys
import hashlib
import getpass


SERVER_IP = 'yellow-custody.gl.at.ply.gg'
SERVER_PORT = 46163

#moderately high security user validation
def uid_hash(uid,psw):
    combined = f"{uid}|owo-{psw}"
    hash_object = hashlib.sha384(combined.encode('utf-8'))
    return hash_object.hexdigest()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

userid = input("Create your username ").strip()
password = getpass.getpass(prompt="Create a password ").strip()

a = uid_hash(userid, password)

userid = 'uid'+userid
sock.sendto(userid.encode(), (SERVER_IP, SERVER_PORT))
password = 'pw'+a
sock.sendto(password.encode(), (SERVER_IP, SERVER_PORT))

print("credentials sent, awaiting reply...")
data, address = sock.recvfrom(4096) 
print(f"Server echoed: {data.decode(errors='ignore')}")