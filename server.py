import socket
import sys, os

#RSA encryption >///<
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import string, secrets
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

#key used to show messages to server: Ÿ
spec_key = 'Ÿ'

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



IP = "127.0.0.1" 
PORT = 2700

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"Listening for clients at {(IP, PORT)}")


users_dict = {}
decode_data = None

while True:
    data, address = sock.recvfrom(4096)
    decode_data = data.decode(errors='ignore')
    cleaned_data = decode_data.replace('Ÿ', '')

    if address not in users_dict:
        users_dict[address] = []
    
    match decode_data.count("Ÿ"):
        case 1: 
            charset = string.ascii_letters + string.digits + string.punctuation
            temp_skey = secrets.token_urlsafe(32)
            #temp_skey = os.urandom(32)

            #DEBUG
            print(temp_skey)

            users_dict[address] = users_dict[address].append(temp_skey)
            temp_ekey = rsa_encrypt(temp_skey, RSA.import_key(cleaned_data))
            
            sock.sendto(temp_ekey, address)



            

'''    print(f"Received {data} from {address}")

    if address not in address_list:
        address_list.append(address)

    message = input("Reply? ")

    for i in address_list:
        sock.sendto(message.encode(errors='ignore'), i)'''
