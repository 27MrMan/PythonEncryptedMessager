import socket
import sys
import hashlib
import getpass

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

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


SERVER_IP = 'yellow-custody.gl.at.ply.gg'
SERVER_PORT = 46163

#moderately high security user validation
def uid_hash(uid,psw):
    combined = f"{uid}|owo-{psw}"
    hash_object = hashlib.sha384(combined.encode('utf-8'))
    return hash_object.hexdigest()


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto('getkey'.encode(), (SERVER_IP, SERVER_PORT))

key1, address = sock.recvfrom(4096)
key1 = RSA.import_key(key1.decode())

userid = input("Create your username ").strip()
password = getpass.getpass(prompt="Create a password ").strip()

a = uid_hash(userid, password)

userid = 'uid'+userid
userid = rsa_encrypt(userid, key1)

sock.sendto(userid, (SERVER_IP, SERVER_PORT))

password = 'pw'+a
password = rsa_encrypt(password, key1)

sock.sendto(password, (SERVER_IP, SERVER_PORT))

print("credentials sent, awaiting reply...")
data, address = sock.recvfrom(4096) 
print(f"Server echoed: {data.decode(errors='ignore')}")