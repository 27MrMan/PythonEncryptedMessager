from nicegui import ui
import asyncio
import socket
import sys
import hashlib
import getpass
import time

#RSA encryption ~w~
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
import base64

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

#AES stuff
def encrypt_AES_GCM(msg, secretKey):
    aesCipher = AES.new(secretKey, AES.MODE_GCM)
    ciphertext, authTag = aesCipher.encrypt_and_digest(msg.encode())
    blob = aesCipher.nonce + ciphertext + authTag
    return base64.b64encode(blob).decode('utf-8')
    #return (ciphertext, aesCipher.nonce, authTag)

def decrypt_AES_GCM(encryptedMsg, secretKey):
    #encryptedMsg = base64.b64encode(encryptedMsg)
    encryptedMsg = base64.b64decode(encryptedMsg.encode())
    nonce = encryptedMsg[:16]
    ciphertext = encryptedMsg[16:-16]
    authTag = encryptedMsg[-16:]

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
skey = skey.encode()

def uid_hash(uid,psw):
    combined = f"{uid}|owo-{psw}"
    hash_object = hashlib.sha384(combined.encode('utf-8'))
    return hash_object.hexdigest()

username, password = None, None
loadin = False
user_input = ''
pass_input = ''
sip1,spt1 = '',''

async def submit_auth():
    global username
    global password
    global loadin
    
    username = user_input.value.strip()
    password = pass_input.value.strip()

    print(username, password)
    print(type(username))

    payload = "ŸŸŸ"+username+'|'+uid_hash(username, password)
    loadin = True
    sock.sendto(payload.encode(), (SERVER_IP, SERVER_PORT))

    data2, address = sock.recvfrom(4096)
    data2= data2.decode()
    if data2 == "pass":
        pass

async def submit_addr():
    global SERVER_IP
    global SERVER_PORT
    global spt1
    global sip1

    if not(spt1.value.strip() == '' and sip1.value.strip() == ''):
        SERVER_IP = spt1.value.strip()
        SERVER_PORT = spt1.value.strip()



@ui.page('/')
def auth_page():
    global user_input
    global pass_input
    global sip1
    global spt1
    global loadin
    
    ui.label("Hiii :3 Welcome!").style('text-align: center; font-size: 300%; color: #7851A9').classes("w-full center")
    with ui.splitter(value=50).classes("w-full") as splitter:
        with splitter.before:
            uinput = ui.input(label = "Username ~w~",
                    placeholder = "enter your username",
            ).classes("w-3/4 mx-auto")
            pinput = ui.input(label = "Password Please :3",
                            password = True,
                            password_toggle_button= True,
                            placeholder = 'enter your password'
            ).classes('w-3/4 mx-auto')
            user_input = uinput
            pass_input = pinput
            ui.button('Submit',
                    on_click=lambda: submit_auth()
            ).classes('w-3/4 mx-auto')
        with splitter.after:
            sip_input = ui.input(label = "Server IP",
                                 placeholder="Leave blank for default ~w~"
            ).classes('w-3/4 mx-auto')
            spt_input = ui.input(label = "Server Port",
                                 placeholder="Also leave blank for default"
            ).classes('w-3/4 mx-auto')
            sip1,spt1 = sip_input, spt_input
            ui.button("Submit Address",
                      on_click=lambda:submit_addr()
            ).classes('w-3/4 mx-auto')




async def debug1():
    global user_input
    try:
        print(user_input.value)
    except:
        print("pass")
        pass

    await asyncio.sleep(1)

#asyncio.run(debug1())

ui.run(dark = True)