import hashlib
import socket
import sys
from csv import writer

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

key = RSA.generate(2048)
pkey = key
public_key = key.publickey()
pub_key_str = key.publickey().export_key().decode('utf-8')

# Encrypt
def rsa_encrypt(plaintext, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    encrypted = cipher.encrypt(plaintext.encode())
    return encrypted

# Decrypt
def rsa_decrypt(ciphertext, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    decrypted = cipher.decrypt(ciphertext)
    return decrypted.decode()

IP = "127.0.0.1" 
PORT = 2700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"Listening for clients at {(IP, PORT)}")

userid_list = []
epwd_list = []

'''
while True:
    data, address = sock.recvfrom(4096)

    print(f"Received {data} from {address}")

    if data.decode() == 'getkey':
        sock.sendto(pub_key_str.encode(), address)
    else:
        data = rsa_decrypt(data, pkey)

    if data[:3] == "uid":
        userid_list.append(data.decode()[3:])
    if data[:2] == "pw":
        epwd_list.append(data.decode()[2:])

    if any(epwd_list) and any(userid_list):
        break
'''
#temporary adjustment until i figure out better solution
data, address = sock.recvfrom(4096)

if data.decode() == 'getkey':
    sock.sendto(pub_key_str.encode(), address)

data, address = sock.recvfrom(4096)
data = rsa_decrypt(data, pkey)
print(data, "added")

if data[:3] == "uid":
    userid_list.append(data[3:])

data, address = sock.recvfrom(4096)
data = rsa_decrypt(data, pkey)

if data[:2] == "pw":
    epwd_list.append(data[2:])


message = "Credentials Recieved!"

new_row = [userid_list[0], epwd_list[0]]
with open('users.csv', 'a', newline='') as file:
    writer_obj = writer(file)
    writer_obj.writerow(new_row)

sock.sendto(message.encode(errors='ignore'), address)