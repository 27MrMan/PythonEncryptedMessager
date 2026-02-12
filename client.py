import socket
import sys
import hashlib
import getpass

#RSA encryption ~w~
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes

# Generate RSA keys
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

# Example usage:
'''
message = "HELLO"
ciphertext = rsa_encrypt(message, public_key)
decrypted_message = rsa_decrypt(ciphertext, private_key)
print("RSA - Encrypted:", ciphertext)
print("RSA - Decrypted:", decrypted_message)'''

#AES stuff
def encrypt_AES_GCM(msg, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg)
    return (ciphertext, aesCipher.nonce, authTag)

def decrypt_AES_GCM(encryptedMsg, secretKey):
    (ciphertext, nonce, authTag) = encryptedMsg
    aesCipher = AES.new(secretKey, AES.MODE_GCM, nonce)
    plaintext = aesCipher.decrypt_and_verify(ciphertext, authTag)
    return plaintext



#SERVER_IP = "127.0.0.1"
SERVER_IP = 'yellow-custody.gl.at.ply.gg'
#SERVER_PORT = 2700
SERVER_PORT = 46163

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


#obtaining the aes256 key#
msg1 = "Ÿ"+pub_key_str
sock.sendto(msg1.encode(), (SERVER_IP, SERVER_PORT))

data1, address = sock.recvfrom(4096)

skey = rsa_decrypt(data1, pkey)

#DEBUG
print(skey)


localMessageBuffer = 512

#moderately high security user validation
def uid_hash(uid,psw):
    combined = f"{uid}|owo-{psw}"
    hash_object = hashlib.sha384(combined.encode('utf-8'))
    return hash_object.hexdigest()



#password = getpass.getpass(prompt="Enter your password ", echo_char = '*').strip()

while True:
    message = input("Enter message: ")
    sock.sendto(message.encode(errors='ignore'), (SERVER_IP, SERVER_PORT))

    print("Awaiting reply...")
    data, address = sock.recvfrom(4096) 
    print(f"Server echoed: {data.decode(errors='ignore')}")